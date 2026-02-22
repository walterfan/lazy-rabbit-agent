# Project Knowledge Pack (Sphinx)

Documentation source lives in **`source/`**. Sphinx output is written to **`build/`**.

## Build

From this directory (`docs/`):

```bash
pip install -r requirements.txt
make html
```

Open **`build/html/index.html`** in a browser.

## Commands

| Command     | Description                    |
|------------|--------------------------------|
| `make html` | Build HTML into `build/html/`  |
| `make clean` | Remove `build/`                |
| `make serve` | Build then serve on port 8000  |

## Structure

- **`source/`** — Sphinx source: `conf.py`, `index.md`, `00-overview.md` … `07-testing.md`, `ai-guide.md`, `adr/`, `_static/`.
- **`build/`** — Generated output (gitignored). HTML in `build/html/`.

See [PROJECT-KNOWLEDGE-PACK.md](PROJECT-KNOWLEDGE-PACK.md) for a one-page project cheat sheet.
