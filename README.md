# Portfolio site

A static portfolio for four projects: the derelict vessel map, the abandoned vehicle map, the car maker identifier and the PPE inspection report. It is plain HTML and CSS, so there is nothing to build before it goes live.

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

## Part 1. Put the site on GitHub and Cloudflare Pages

You need a GitHub account, a free Cloudflare account, `git`, and the GitHub CLI (https://cli.github.com).

1. Sign in to GitHub from the terminal: `gh auth login`.
2. Unzip this folder, open a terminal in it, and run:

   ```
   git init -b main
   git add .
   git commit -m "Initial portfolio site"
   gh repo create portfolio --private --source=. --remote=origin --push
   ```

3. In the Cloudflare dashboard, go to **Workers & Pages**, then **Create**, then the **Pages** tab, then **Connect to Git**.
4. Authorize GitHub. Choose **Only select repositories** and pick `portfolio`.
5. Use these settings:

   | Setting | Value |
   | --- | --- |
   | Production branch | `main` |
   | Framework preset | None |
   | Build command | leave empty |
   | Build output directory | `site` |

6. Choose **Save and Deploy**. The site goes live at `https://<project-name>.pages.dev`.

From then on, every `git push` to `main` updates the live site. Other branches get their own preview addresses.

Optional: to use your own domain, open the project in Cloudflare, then **Custom domains**.

## Part 2. Host the apps

Cloudflare Pages only serves static files, so the apps that need more are hosted where they can run. Each one gets its own link.

**Car maker identifier** (Streamlit). The repo is `mjpon/car-maker-identifier`, and it already has `app.py` and `requirements.txt`.

1. Go to https://share.streamlit.io and sign in with GitHub.
2. Choose **Create app**, then pick the repo `mjpon/car-maker-identifier` and the branch `main`.
3. Set the main file to `app.py` and deploy.
4. Copy the address it gives you, which ends in `.streamlit.app`.

Free Streamlit apps go to sleep when nobody is using them, so the first visit after a quiet spell is slow.

**PPE inspection report.** It is already on Vercel. Copy its address.

**Abandoned vehicle map.** It is a static map, so it can be its own Cloudflare Pages project. Put the map's folder (the one holding `index.html` and the GeoJSON file) in its own GitHub repo, then repeat Part 1 with the build output directory set to that folder.

**Derelict vessel map.** Leave this one unpublished. Its page says it is in private preview because the source data does not have confirmed reuse terms. Do not host it publicly until that is settled.

## Part 3. Link the live apps from the portfolio

1. Open `tools/build_site.py` and find `LIVE`.
2. Add one line per hosted app, using the project name shown here:

   ```python
   LIVE = {
       "car-maker-identifier": "https://your-app-name.streamlit.app",
       "ppe-inspection-report": "https://your-project.vercel.app",
   }
   ```

3. Run `python3 tools/build_site.py`. Each of those project pages now has an **Open the live version** button.
4. If a status changes (for example, "In development" to "Working app"), edit `status` in the same file and run the script again.
5. Commit and push:

   ```
   git add .
   git commit -m "Link live apps"
   git push
   ```

## Protecting the code

- Anything a browser can load can be read, however it is packaged. Minifying or obfuscating JavaScript only slows a reader down.
- Keep secrets out of the repo. Keys and tokens belong in environment variables (Cloudflare, Vercel and Streamlit all have a settings page for them). `.gitignore` already skips `.env` files.
- Anything that has to stay private needs to run on a server and not in the page.
- `LICENSE` says all rights reserved. On GitHub, a public repo can always be viewed and forked on GitHub itself, whatever the license says. A private repo keeps the source out of sight, and Cloudflare Pages deploys from private repos.
- ProGuard works on Java bytecode, and none of these four projects is Java, so it has nothing to do here.
