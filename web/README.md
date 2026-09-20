# Indoor CO₂ Steady-State Calculator — web version

A static web version of [`IndoorCO2-steady_state.py`](../IndoorCO2-steady_state.py).
No server, no build step, no dependencies: three files that any static host can serve.

| File | Purpose |
|---|---|
| `index.html` | Page structure |
| `style.css` | Layout and theming (light + dark) |
| `model.js` | The physics — a port of the Python model |
| `app.js` | Form, results panel and the SVG comfort gauge |
| `parity-test.html` | Checks `model.js` against the Python original |
| `parity-cases.json` | Generated test cases (do not edit by hand) |

## Running it locally

From the **project root**:

```bash
python -m http.server 8000 --directory web
```

Then open <http://localhost:8000>.

Opening `index.html` directly as a `file://` path also works for the calculator,
but `parity-test.html` needs `http://` because it fetches a JSON file.

## Keeping the Python and JavaScript models in step

The model exists twice: `../IndoorCO2-steady_state.py` is the reference
implementation, `model.js` is the port that runs in the browser. To stop them
drifting apart, `parity-test.html` replays a grid of 2160 input combinations
through the JavaScript and compares every result against the Python output.

After changing the model **in either language**:

```bash
python tools/generate_parity_cases.py
```

then reload <http://localhost:8000/parity-test.html> and confirm it says PASS.

## Deploying

The site is fully static, so the publish directory is just `web`.

### Cloudflare Pages (recommended)

1. Push this project to a GitHub repository.
2. At <https://dash.cloudflare.com> → Workers & Pages → Create → Pages →
   Connect to Git, and pick the repository.
3. Build settings:
   - Framework preset: **None**
   - Build command: *(leave empty)*
   - Build output directory: `web`
4. Save and Deploy. You get `https://<project>.pages.dev` with HTTPS.

Every later `git push` redeploys automatically.

### Netlify

Same idea: New site from Git, build command empty, publish directory `web`.
Netlify also accepts a drag-and-drop of the `web` folder at
<https://app.netlify.com/drop> if you would rather not use Git at all.

### GitHub Pages

GitHub Pages can only publish from the repository root or a `/docs` folder, so
either rename `web` to `docs`, or push the contents of `web` to a `gh-pages`
branch. Then: repository Settings → Pages → pick the branch and folder.

### Custom domain

All three hosts let you point your own domain at the site and issue the HTTPS
certificate for free, under the project's domain settings.

## Notes

- Everything runs in the visitor's browser. No input is uploaded or stored, so
  there is no database, no account system and no personal data to protect.
- The gauge is inline SVG built in `drawGauge()`, following the same
  coordinates as `draw_en16798_gauge()` in the Python file.
- Category thresholds are the EN 16798-1:2019 CO₂ increase above outdoor
  concentration: I ≤ 550, II ≤ 800, III ≤ 1350, IV > 1350 ppm.
