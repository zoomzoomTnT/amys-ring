# Deploying Amy's Ring

Live at **https://amysring.duckdns.org** (Aliyun ECS `47.79.37.206`).

The site is served by a Caddy container that gets and renews a free Let's Encrypt
certificate automatically. Plain HTTP and the bare IP redirect to the HTTPS domain.

Server layout (`/opt/amys-ring`):

| Path | What |
|---|---|
| `site/` | static files (copy of this repo's `site/`) |
| `Caddyfile` | copy of `deploy/Caddyfile` |
| `caddy_data/`, `caddy_config/` | certificates and Caddy state (keep these, so restarts don't re-issue) |
| `default.conf` | old nginx config, only kept for rollback |

Container:

```sh
docker run -d --name amys-ring --restart unless-stopped \
  -p 80:80 -p 443:443 -p 443:443/udp \
  -v /opt/amys-ring/Caddyfile:/etc/caddy/Caddyfile:ro \
  -v /opt/amys-ring/site:/srv:ro \
  -v /opt/amys-ring/caddy_data:/data -v /opt/amys-ring/caddy_config:/config \
  caddy:2-alpine
```

Update the site: copy changed files into `/opt/amys-ring/site/` (no restart needed;
everything is served with `Cache-Control: no-cache`, so browsers revalidate).

Change the Caddyfile: copy it to `/opt/amys-ring/Caddyfile`, then
`docker exec amys-ring caddy reload --config /etc/caddy/Caddyfile`.

Requirements: the DuckDNS name must point at the server, and TCP 80 and 443 must be open
inbound in the ECS security group (Let's Encrypt validates over them).

Rollback to plain HTTP nginx:

```sh
docker rm -f amys-ring
docker run -d --name amys-ring --restart unless-stopped -p 80:80 \
  -v /opt/amys-ring/site:/usr/share/nginx/html:ro \
  -v /opt/amys-ring/default.conf:/etc/nginx/conf.d/default.conf:ro nginx:alpine
```
