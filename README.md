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

Each project has its own GitHub repo and its own Cloudflare Worker (a Worker with static assets), on its own subdomain. The portfolio only links to them. Three of the project repos are private, and that is fine: Cloudflare can build from a private repo, and nothing from them is copied into this public one.

| Address | GitHub repo | Worker name |
| --- | --- | --- |
| `mitchell-pon.com` | `mjpon/portfolio` | `portfolio` |
| `ppe.mitchell-pon.com` | `mjpon/ppe-inspection-v2` | `ppe-inspection-v2` |
| `vehicles.mitchell-pon.com` | `mjpon/abandoned-vehicle-map` | `abandoned-vehicle-map` |
| `boats.mitchell-pon.com` | `mjpon/derelict-vessel-map` | `derelict-vessel-map` |
| `cars.mitchell-pon.com` | `mjpon/car-maker-identifier` | `car-maker-identifier` |

Every repo has its own `wrangler.jsonc` that names the Worker and the folder to serve, so the build command stays empty and the deploy command is the default (`npx wrangler deploy`) for all five.

## Part 1. Deploy a project

Repeat this for each row in the table. You need a free Cloudflare account with mitchell-pon.com already on it.

1. In the Cloudflare dashboard, go to **Workers & Pages**, then **Create**, then import a repository from GitHub. Choose **Only select repositories** and pick the repo from the table.
2. Name the Worker exactly as in the table. It has to match the `name` in that repo's `wrangler.jsonc`. Leave **Root directory** empty and set the production branch to `main`.
3. Leave the **Build command** empty and the **Deploy command** as `npx wrangler deploy`.
4. Save and deploy. Open the Worker, then **Deployments** (or **Builds**) and check that the build is green. It is live at `https://<worker-name>.<your-subdomain>.workers.dev`.
5. Attach the address: in the Worker, go to **Settings**, then **Domains & Routes**, then **Add**, then **Custom Domain**, and enter the address from the table. Because mitchell-pon.com is on Cloudflare, it creates the DNS record for you. If it refuses because the name already has a DNS record, delete that record under the site's **DNS** page and add the domain again.

A Worker lives under **Workers & Pages** at the account level. It only shows up under the website (mitchell-pon.com, then **DNS**) once a custom domain is attached to it.

After that, every `git push` to `main` rebuilds and updates that site.

The derelict vessel map keeps its site files at the top of the repo, next to tests, scripts and import notes. A script (`sh scripts/stage_public.sh`) copies only the site into `public/`, leaving out the manual exclusion list, and `public/` is committed because that is the folder the Worker serves. After changing the site there, run the script again and commit `public/`.

## Part 2. These are proofs of concept

All four projects are shown as **Alpha (preview)** and are meant to show ideas, not finished products. A few things to know:

- **Derelict vessel map.** The BoatUS MyCoast data does not have confirmed reuse terms. The project page says it is a preview and may be taken down. If the data owner objects, remove the custom domain from the Worker (or put it behind Cloudflare Access) and comment out its line in `LIVE`.
- **Abandoned vehicle map.** The repo's README lists open items, such as reuse terms for the city data and the default-location spots in San José.
- **Car maker identifier.** The site is a static rebuild of the original Streamlit app, and both read the same data file. The Streamlit app is still in the repo.

## Part 3. Links from the portfolio to the live sites

Every project page has an **Open the live version** button, and it opens the project in a new tab. The addresses come from `LIVE` near the top of `tools/build_site.py`.

1. To change or remove a link, edit `LIVE` in `tools/build_site.py`. A line with a `#` in front of it is off, and that project page shows no button.
2. Run `python3 tools/build_site.py`.
3. Statuses all come from `STATUS` in the same file. Change it, or set `status=` on a single project, and run the script again.
4. Commit and push:

   ```
   git add .
   git commit -m "Update live links"
   git push
   ```

The buttons point at the subdomains in the table, so each one shows an error page until its Worker is deployed and its custom domain is attached.

## Protecting the code

- Anything a browser can load can be read, however it is packaged. Minifying or obfuscating JavaScript only slows a reader down.
- Keep secrets out of the repo. Keys and tokens belong in environment variables (each Worker has a **Variables & Secrets** settings page). `.gitignore` already skips `.env` files.
- Anything that has to stay private needs to run on a server and not in the page, or sit behind Cloudflare Access.
- `LICENSE` says all rights reserved. On GitHub, a public repo can always be viewed and forked on GitHub itself, whatever the license says. A private repo keeps the source out of sight, and Cloudflare builds from private repos.
