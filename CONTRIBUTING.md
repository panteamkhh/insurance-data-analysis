# Contributing

Thanks for taking a look! This is a portfolio project, but issues and pull
requests are welcome.

## Getting started

```bash
git clone https://github.com/panteamkhh/insurance-data-analysis.git
cd insurance-data-analysis

python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

pip install -e ".[dev]"
```

## Running the project

```bash
python -m src.run_analysis     # regenerate every chart and CSV export
python -m pytest               # run the test suite
pytest --cov=src               # with coverage
```

## Code style

This project uses [ruff](https://docs.astral.sh/ruff/) for linting and
[black](https://github.com/psf/black) for formatting (both configured in
`pyproject.toml`, line length 100).

```bash
ruff check . --fix
black .
pre-commit install     # optional: run the checks automatically on commit
```

## Adding a new analysis question

1. Add a focused function to `src/analysis.py` that accepts the enriched
   DataFrame and returns plain pandas objects.
2. Add a matching chart function to `src/visualization.py` that saves a PNG and
   returns the figure.
3. Wire both into `src/run_analysis.py`.
4. Add a test to `tests/test_analysis.py`.

Keep calculation logic out of `visualization.py` and plotting out of
`analysis.py` so each stays independently testable.

## Pull requests

- Keep changes focused and describe the "why" in the PR description.
- Ensure `ruff check .`, `black --check .` and `pytest` all pass.
- Do not commit anything inside `output/` or `.venv/`.
