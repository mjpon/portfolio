# Portfolio site

A static portfolio for four projects: the derelict vessel map, the abandoned vehicle map, the car maker identifier and the PPE inspection report. It is plain HTML and CSS, so there is nothing to build before it goes live.

```
site/                 The website: pages, styles and images.
tools/build_site.py   Optional. Rewrites the pages in site/ from the project list inside it.
LICENSE               All rights reserved.
```

Preview it on your computer:

```
cd site
python3 -m http.server 8000
```

Then open http://localhost:8000.

## Projects

Each project has its own GitHub repo, and the portfolio only links to them. All four are shown as **Alpha (preview)**. They are proofs of concept, meant to show ideas and not finished products.

## Editing the site

Everything on the pages comes from `tools/build_site.py`. Edit it, run it, and commit the result.

- **Live links.** Every project page has an **Open the live version** button that opens the project in a new tab. The addresses come from `LIVE` near the top of the script. A line with a `#` in front of it is off, and that project page shows no button.
- **Statuses.** They all come from `STATUS` in the same file. Change it, or set `status=` on a single project.
- **Contact.** The email address on the Contact section comes from `EMAIL` near the top of the script.

1. Edit `tools/build_site.py`.
2. Run `python3 tools/build_site.py`.
3. Commit and push:

   ```
   git add .
   git commit -m "Update the site"
   git push
   ```

## Security

- To report a problem, see `SECURITY.md`.
- Keep secrets out of the repo. `.gitignore` already skips `.env` files.
- Anything a browser can load can be read, however it is packaged. Minifying or obfuscating JavaScript only slows a reader down, so it is not used. Anything that has to stay private needs to run on a server and not in the page.
- `LICENSE` says all rights reserved. A public repo can always be viewed and forked on GitHub itself, whatever the license says.
