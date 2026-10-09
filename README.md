# Portfolio site

A static portfolio for four projects: the derelict vessel map, the abandoned vehicle map, the car maker identifier and the PPE inspection report. It is plain HTML and CSS, so there is nothing to build before it goes live. Everything is hosted on Cloudflare, under mitchell-pon.com.

```
site/                 The website. Cloudflare Pages serves this folder.
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

Each project has its own GitHub repo and its own Cloudflare Pages project, on its own subdomain. The portfolio only links to them. The three private repos stay private, because Pages can deploy from a private repo and nothing from them is copied into this public one.

| Address | GitHub repo | Build command | Build output directory | Status |
| --- | --- | --- | --- | --- |
| `mitchell-pon.com` | `mjpon/portfolio` | empty | `site` | ready |
| `ppe.mitchell-pon.com` | `mjpon/ppe-inspection-v2` | empty | `dist` | ready |
| `vehicles.mitchell-pon.com` | `mjpon/abandoned-vehicle-map` | empty | `site` | ready |
| `boats.mitchell-pon.com` | `mjpon/derelict-vessel-map` | see below | `public` | hold, see below |
| `cars.mitchell-pon.com` | `mjpon/car-maker-identifier` | not decided | not decided | needs a static rebuild, see below |

## Part 1. Deploy a project on Cloudflare Pages

Repeat this for each row of the table above that is ready. You need a free Cloudflare account with mitchell-pon.com already on it.

1. In the Cloudflare dashboard, go to **Workers & Pages**, then **Create**, then the **Pages** tab, then **Connect to Git**.
2. Authorize GitHub. Choose **Only select repositories** and add the repo from the table.
3. Use these settings:

   | Setting | Value |
   | --- | --- |
   | Production branch | `main` |
   | Framework preset | None |
   | Build command | from the table |
   | Build output directory | from the table |

4. Choose **Save and Deploy**. The project goes live at `https://<project-name>.pages.dev`.
5. Open the project, go to **Custom domains**, choose **Set up a custom domain**, and enter the address from the table. Because mitchell-pon.com is already on Cloudflare, it adds the DNS record for you.

After that, every `git push` to `main` updates that site. Other branches get their own preview addresses.

If the dashboard offers Workers instead of a Pages tab, a Workers project with static assets also works. Point its assets directory at the same folder.

## Part 2. The two that need a decision

**Derelict vessel map.** Its own README says not to publish it yet, because the BoatUS MyCoast data has no confirmed reuse terms. Two ways to go:

- Keep it off the internet until the terms are settled.
- Deploy it now, but put it behind Cloudflare Access (Zero Trust, then Access, then Applications) so only people you list can open `boats.mitchell-pon.com`.

Its site files sit at the top of the repo next to tests, scripts and import notes, so use this build command to publish only the site, with output directory `public`:

```
mkdir public && cp -r index.html about.html data.html styles.css favicon.svg js lib fonts data public/ && rm -f public/data/exclude_ids.txt
```

**Car maker identifier.** It is a Streamlit app, which needs a running Python server, and Cloudflare Pages only serves static files. To host it on Cloudflare it has to be rebuilt as a static page: the processed data (`data/nhtsa_data.csv`) becomes a JSON file and the charts are drawn in the browser. Until then the portfolio shows its page and a link to the source code, and no live link.

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
- Keep secrets out of the repo. Keys and tokens belong in environment variables (each Cloudflare Pages project has a settings page for them). `.gitignore` already skips `.env` files.
- Anything that has to stay private needs to run on a server and not in the page, or sit behind Cloudflare Access.
- `LICENSE` says all rights reserved. On GitHub, a public repo can always be viewed and forked on GitHub itself, whatever the license says. A private repo keeps the source out of sight, and Cloudflare Pages deploys from private repos.
- ProGuard works on Java bytecode, and none of these four projects is Java, so it has nothing to do here.
