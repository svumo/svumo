# Profile-view tracker

A tiny Cloudflare Worker that counts profile views per day using Workers
Analytics Engine. The profile README embeds an invisible 1px image pointing
at this Worker; each fetch is logged.

> Approximate by design: GitHub's camo proxy caches/dedupes the image, so
> treat the numbers as a daily *trend*, not an exact count.

## Deploy (one time, ~5 min, free tier)

```bash
cd tracker
npm i -g wrangler          # or use: npx wrangler@latest <cmd>
wrangler login

# 1. Put your Cloudflare account id in wrangler.toml (CF_ACCOUNT_ID).
#    Dashboard → any zone → right sidebar → "Account ID".

# 2. Set the two secrets:
wrangler secret put STATS_KEY      # any random string you choose
wrangler secret put CF_API_TOKEN   # token w/ "Account Analytics: Read"
#    Create the token: Cloudflare Dashboard → My Profile → API Tokens →
#    Create Token → Custom → Permissions: Account · Analytics · Read.

# 3. Ship it
wrangler deploy
```

`wrangler deploy` prints a URL like
`https://svumo-views.<your-subdomain>.workers.dev`.

The Analytics Engine dataset is created automatically on the first view.

## Wire it into the profile

Point the README's hidden pixel at:

```
https://svumo-views.<your-subdomain>.workers.dev/p.gif
```

(Optional, cleaner) If `danielpd.com` is on Cloudflare, add a Worker
**Route** like `danielpd.com/_v.gif*` so the README uses a stable branded
URL instead of the `workers.dev` one.

## Read your numbers

```
https://svumo-views.<your-subdomain>.workers.dev/stats?key=YOUR_STATS_KEY
```

Returns JSON: `{ day, views }` per day for the last 30 days. The `key`
gate keeps it private.
