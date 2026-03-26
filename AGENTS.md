# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

Single-service Python/Streamlit app — an Arabic-language e-commerce product management dashboard for a perfume store. All code lives in `app.py` (~4 000 lines). No database, no background workers, no monorepo.

### Running the dev server

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
```

The app will be available at `http://localhost:8501`.

### Dependencies

```bash
pip install -r requirements.txt
```

`streamlit` installs to `~/.local/bin` — ensure that directory is on `PATH` (already configured in `~/.bashrc` for cloud VMs).

### Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | For AI features | Claude-powered Arabic product description generation |
| `GOOGLE_API_KEY` | Optional | Google Custom Search image fetching |
| `GOOGLE_CSE_ID` | Optional | Google Custom Search Engine ID |

The app starts and is fully navigable without any API keys; AI-dependent features simply won't fire.

### Linting / Testing

There are no automated tests or linting configurations in this repository. Manual testing via the Streamlit UI is the primary verification method.

### Gotchas

- The Dockerfile targets Python 3.11-slim, but the cloud VM ships Python 3.12. All dependencies install and run fine on 3.12.
- `rapidfuzz` and `anthropic` are imported with `try/except`; the app gracefully degrades if either is missing (but both are in `requirements.txt`).
- Static reference data (brands, categories) lives in `data/brands.csv` and `data/categories.csv`.
