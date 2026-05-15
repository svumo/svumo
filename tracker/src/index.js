// Profile-view tracker for github.com/svumo
//
// The profile README embeds <img src=".../p.gif">. GitHub's camo proxy
// fetches it; this Worker logs one data point per fetch into Workers
// Analytics Engine, then returns a 1x1 transparent GIF.
//
// Honest limitation: GitHub caches/dedupes the image through camo, so this
// is an approximate daily trend, not an exact view count. Geo is unreliable
// too — the request comes from GitHub's proxy, not the real visitor.

// 1x1 transparent GIF
const PIXEL = Uint8Array.from(
  atob("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"),
  (c) => c.charCodeAt(0)
);

const NO_CACHE = {
  "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
  Pragma: "no-cache",
  Expires: "0",
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // --- tracking pixel -------------------------------------------------
    if (url.pathname === "/p.gif" || url.pathname === "/pixel") {
      try {
        env.AE.writeDataPoint({
          blobs: [request.cf?.country || "XX"],
          doubles: [1],
          indexes: ["view"],
        });
      } catch (_) {
        // never let logging break the pixel
      }
      return new Response(PIXEL, {
        headers: { "Content-Type": "image/gif", ...NO_CACHE },
      });
    }

    // --- private stats (per day, last 30 days) --------------------------
    if (url.pathname === "/stats") {
      if (url.searchParams.get("key") !== env.STATS_KEY) {
        return new Response("forbidden\n", { status: 403 });
      }

      const sql = `
        SELECT
          formatDateTime(toStartOfDay(timestamp), '%Y-%m-%d') AS day,
          SUM(_sample_interval) AS views
        FROM svumo_profile_views
        WHERE timestamp > NOW() - INTERVAL '30' DAY
        GROUP BY day
        ORDER BY day ASC
      `;

      const res = await fetch(
        `https://api.cloudflare.com/client/v4/accounts/${env.CF_ACCOUNT_ID}/analytics_engine/sql`,
        {
          method: "POST",
          headers: { Authorization: `Bearer ${env.CF_API_TOKEN}` },
          body: sql,
        }
      );

      const body = await res.text();
      return new Response(body, {
        status: res.status,
        headers: { "Content-Type": "application/json", ...NO_CACHE },
      });
    }

    return new Response("ok\n", { headers: NO_CACHE });
  },
};
