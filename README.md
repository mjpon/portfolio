# Portfolio site

A static portfolio for five projects: the derelict vessel map, the abandoned vehicle map, the collectible theft map, the car maker identifier and the PPE inspection report. It is plain HTML, CSS and a little JavaScript, so there is nothing to build before it goes live.

```
site/                 The website: pages, styles and images.
site/motion.js        The home page's animations.
site/theme.js         The light and dark switch.
site/vendor/          A trimmed copy of anime.js, which motion.js uses.
tools/build_site.py   Optional. Rewrites the pages in site/ from the project list inside it.
tools/vendor_anime.sh Rebuilds site/vendor/anime.js. Needs Node.
LICENSE               All rights reserved.
```

Preview it on your computer:

```
cd site
python3 -m http.server 8000
```

Then open http://localhost:8000.

## Projects

Each project has its own GitHub repo, and the portfolio only links to them. All five are shown as **Alpha (preview)**. They are proofs of concept, meant to show ideas and not finished products.

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

## Motion

The home page opens with a network map: every project is a station on its line, and the lines run out of one interchange. When the page loads, trains lay out each line once. After that, motion only answers what a visitor does:

- Pointing at a station, or tabbing to it, sends a train to it, and the other lines fall back.
- Pointing at a line's chip under the map brings that line forward.
- In the Work list, a red ring rides the rail to the row in use.
- A line beside the page works as a map of the page itself. Each section is a stop, a train moves down it as you scroll, and through the Work section it takes each project line's color. Wide screens show it in the left margin with stop names; smaller screens show a slim line at the right edge. Clicking a stop jumps to that section.
- Opening a project carries its name into the project page's heading, in browsers that support cross-page view transitions.

With "reduce motion" turned on, the map shows up finished and nothing travels. The map is drawn by `build_site.py` from the project list, so a new project gets a station when the script runs. Its layout is set in `NET_LAYOUTS`, one for wide screens and one for phones.

The header has a light and dark switch on every page (`site/theme.js`). Until someone uses it, the site follows the device's setting. A choice is saved in that browser and applied before the page paints, and the new colors roll down from the header.

The site serves its own copy of anime.js because the security policy only runs scripts from this domain. To update it, change `VERSION` in `tools/vendor_anime.sh` and run it.

## Security

- To report a problem, see `SECURITY.md`.
- Keep secrets out of the repo. `.gitignore` already skips `.env` files.
- Anything a browser can load can be read, however it is packaged. Minifying or obfuscating JavaScript only slows a reader down, so it is not used. Anything that has to stay private needs to run on a server and not in the page.
- `LICENSE` says all rights reserved. A public repo can always be viewed and forked on GitHub itself, whatever the license says.
