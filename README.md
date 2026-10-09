# Portfolio site

A static portfolio for four projects: the derelict vessel map, the abandoned vehicle map, the car maker identifier and the PPE inspection report. It is plain HTML and CSS, so there is nothing to build before it goes live. Everything is hosted on Cloudflare, under mitchell-pon.com.

```
site/                 The website. Cloudflare serves this folder.
wrangler.jsonc        Tells Cloudflare which folder to serve and to use site/404.html for unknown addresses.
tools/build_site.py   Optional. Rewrites the pages in site/ from the project list inside it.
LICENSE               All rights reserved.
```

Preview it on your computer:

```
cd site
python3 -m http.server 8000
```

Then open http://localhost:8000.

## Where everything lives

Each project has its own GitHub repo and its own Cloudflare Worker (a Worker with static assets), on its own subdomain. The portfolio only links to them. The three private repos stay private, because Cloudflare can build from a private repo and nothing from them is copied into this public one.

| Address | GitHub repo | Worker name | Status |
| --- | --- | --- | --- |
| `mitchell-pon.com` | `mjpon/portfolio` | `portfolio` | ready |
| `ppe.mitchell-pon.com` | `mjpon/ppe-inspection-v2` | `ppe-inspection` | ready |
| `vehicles.mitchell-pon.com` | `mjpon/abandoned-vehicle-map` | `abandoned-vehicle-map` | ready |
| `boats.mitchell-pon.com` | `mjpon/derelict-vessel-map` | `derelict-vessel-map` | hold, see Part 2 |
| `cars.mitchell-pon.com` | `mjpon/car-maker-identifier` | not decided | needs a static rebuild, see Part 2 |

## Part 1. Deploy a project

Repeat this for each project marked ready. You need a free Cloudflare account with mitchell-pon.com already on it.

1. In the Cloudflare dashboard, go to **Workers & Pages**, then **Create**, then import a repository from GitHub. Choose **Only select repositories** and pick the repo from the table.
2. Name the Worker exactly as in the table. Leave **Root directory** empty and set the production branch to `main`.
3. Fill in the build and deploy commands for that project:

   | Project | Build command | Deploy command |
   | --- | --- | --- |
   | portfolio | empty | `npx wrangler deploy` (the settings are in `wrangler.jsonc`) |
   | ppe-inspection | empty | `npx wrangler deploy --assets ./dist --name ppe-inspection --compatibility-date 2026-10-09` |
   | abandoned-vehicle-map | empty | `npx wrangler deploy --assets ./site --name abandoned-vehicle-map --compatibility-date 2026-10-09` |

4. Save and deploy. Open the Worker, then **Deployments** (or **Builds**) and check that the build is green. It is live at `https://<worker-name>.<your-subdomain>.workers.dev`.
5. Attach the address: in the Worker, go to **Settings**, then **Domains & Routes**, then **Add**, then **Custom Domain**, and enter the address from the table. Because mitchell-pon.com is on Cloudflare, it creates the DNS record for you. If it refuses because the name already has a DNS record, delete that record under the site's **DNS** page and add the domain again.

A Worker lives under **Workers & Pages** at the account level. It only shows up under the website (mitchell-pon.com, then **DNS**) once a custom domain is attached to it.

After that, every `git push` to `main` rebuilds and updates that site.

## Part 2. The two that need a decision

**Derelict vessel map.** Its own README says not to publish it yet, because the BoatUS MyCoast data has no confirmed reuse terms. Two ways to go:

- Keep it off the internet until the terms are settled.
- Deploy it now, but put it behind Cloudflare Access (Zero Trust, then Access, then Applications) so only people you list can open `boats.mitchell-pon.com`.

Its site files sit at the top of the repo next to tests, scripts and import notes, so use this build command to publish only the site:

```
mkdir public && cp -r index.html about.html data.html styles.css favicon.svg js lib fonts data public/ && rm -f public/data/exclude_ids.txt
```

and this deploy command:

```
npx wrangler deploy --assets ./public --name derelict-vessel-map --compatibility-date 2026-10-09
```

**Car maker identifier.** It is a Streamlit app, which needs a running Python server, and a Worker with static assets only serves files. To host it on Cloudflare it has to be rebuilt as a static page: the processed data (`data/nhtsa_data.csv`) becomes a JSON file and the charts are drawn in the browser. Until then the portfolio shows its page and a link to the source code, and no live link.

## Part 3. Link the live sites from the portfolio

1. Open `tools/build_site.py` and find `LIVE`.
2. Remove the `#` from the line of each project whose address now loads. Leave the others commented out.
3. Run `python3 tools/build_site.py`. Each of those project pages now has an **Open the live version** button.
4. Statuses all come from `STATUS` near the top of the same file. Change it, or set `status=` on a single project, and run the script again.
5. Commit and push:

   ```
   git add .
   git commit -m "Link live sites"
   git push
   ```

## Protecting the code

- Anything a browser can load can be read, however it is packaged. Minifying or obfuscating JavaScript only slows a reader down.
- Keep secrets out of the repo. Keys and tokens belong in environment variables (each Worker has a **Variables & Secrets** settings page). `.gitignore` already skips `.env` files.
- Anything that has to stay private needs to run on a server and not in the page, or sit behind Cloudflare Access.
- `LICENSE` says all rights reserved. On GitHub, a public repo can always be viewed and forked on GitHub itself, whatever the license says. A private repo keeps the source out of sight, and Cloudflare builds from private repos.
- ProGuard works on Java bytecode, and none of these four projects is Java, so it has nothing to do here.
