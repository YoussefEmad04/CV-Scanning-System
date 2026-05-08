# Repository Guidelines

## Project Structure & Module Organization

- `app.py`: main Streamlit landing page.
- `pages/`: Streamlit multipage UI files, named with numeric prefixes such as `1_Upload_CVs.py`.
- `services/`: reusable Python logic for OpenAI calls, parsing, ranking, bias detection, RAG, storage, and synthetic CV generation.
- `data/`: local runtime data such as processed CSV files, uploaded CVs, synthetic records, and vector cache. Treat this as private runtime data.
- `assets/`: static project assets.
- `docs/`: final documentation, screenshots, diagrams, HTML, and PDF report outputs.
- `scripts/`: documentation/export helper scripts.
- `DE-CV/`: local test CV dataset.

No formal `tests/` directory exists yet; validation is currently done with compile, import, service, and Streamlit checks.

## Build, Test, and Development Commands

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

```bash
streamlit run app.py
```

Validate syntax and imports:

```bash
python -m compileall app.py pages services scripts
python -c "import services.openai_service, services.ranking_service, services.rag_service"
pip check
```

Regenerate documentation artifacts:

```bash
python3 scripts/generate_diagram_images.py
python3 scripts/export_documentation_pdf.py
```

## Coding Style & Naming Conventions

Use simple, readable Python with 4-space indentation. Keep Streamlit page files focused on UI and call reusable logic from `services/`. Use `snake_case` for functions, variables, and module names. Preserve Streamlit page filename numbering, for example `2_Resume_Ranking.py`.

Do not add Docker, authentication, LangChain, cloud deployment, or production architecture unless explicitly requested.

## Testing Guidelines

Before submitting changes, run compile and import checks. For UI-visible changes, run the Streamlit page and capture or update screenshots when relevant. Test both OpenAI-enabled behavior and fallback behavior with `OPENAI_API_KEY` missing or empty.

Use the 20 local Data Engineer CVs only for local validation. Do not expose private CV details in docs, screenshots, commits, or pull requests.

## Commit & Pull Request Guidelines

Git history uses short imperative messages such as `Move project files to repository root` and `Remove uploaded CVs from repository`. Follow that style.

Pull requests should include a concise summary, affected files or modules, commands run, and screenshots for UI or documentation changes. Mention any known limitations or skipped checks.

## Security & Configuration Tips

Never commit `.env`, real API keys, or private CV content. Keep runtime data under `data/` private unless sanitized. This project is a decision-support tool, not a final hiring decision maker; keep that limitation clear in documentation and demos.
