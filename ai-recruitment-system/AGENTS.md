# Repository Guidelines

## Project Structure & Module Organization

This is a simple Streamlit application for AI recruitment and resume screening.

- `app.py`: main Streamlit landing page.
- `pages/`: Streamlit multipage UI files, named with numeric prefixes such as `1_Upload_CVs.py`.
- `services/`: reusable Python logic for OpenAI calls, parsing, ranking, bias detection, RAG, storage, and synthetic CV generation.
- `data/`: local runtime data. Uploaded CVs, processed CSVs, synthetic data, and vector cache live here.
- `assets/`: small static project assets, such as sample job descriptions.
- `DE-CV/`: local test CV dataset.
- No formal `tests/` directory exists yet; current validation is done with import checks and service-level scripts.

## Build, Test, and Development Commands

Use a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

Validate imports and syntax:

```bash
python -m compileall app.py pages services
python -c "import services.openai_service, services.ranking_service"
pip check
```

## Coding Style & Naming Conventions

Use simple, readable Python. Prefer 4-space indentation, clear function names, and small service functions. Keep Streamlit page files focused on UI and call logic from `services/`. Use snake_case for functions, variables, and module names. Keep page filenames compatible with Streamlit multipage discovery, for example `2_Resume_Ranking.py`.

Do not add Docker, authentication, LangChain, cloud deployment, or production architecture unless explicitly requested.

## Testing Guidelines

Before submitting changes, run compile and import checks. For feature changes, test the related Streamlit page and the corresponding service function. Use the 20 unique Data Engineer CVs from `DE-CV/` for parsing, ranking, RAG, and dashboard validation.

Check both modes:

- With `.env` containing `OPENAI_API_KEY`.
- With `OPENAI_API_KEY=` empty to confirm fallback behavior.

## Commit & Pull Request Guidelines

There is no existing commit history yet. Use short imperative commit messages, such as:

```bash
Add resume ranking validation
Fix RAG source display
Improve CV parsing warning
```

Pull requests should include a brief summary, tested commands, affected pages/services, and screenshots for UI-visible changes.

## Security & Configuration Tips

Never commit `.env` or real API keys. Keep `.env.example` as the only environment template. Runtime files in `data/` may contain uploaded CV text, so avoid sharing them publicly unless they are sanitized demo data.
