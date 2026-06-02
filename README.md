# AI Recruitment & Resume Screening System

A Streamlit university project for AI-assisted recruitment screening. The system helps reviewers upload CVs, rank resumes against job descriptions, detect biased wording, generate synthetic demo CVs, transform resume style, ask questions over uploaded CVs with RAG, and review summary metrics in a dashboard.

This project is a **decision-support tool**. It helps organize and explain recruitment review, but it is not a final hiring decision maker. Final hiring decisions must remain under human review.


## Features

- Upload PDF or DOCX CVs and extract resume text.
- Store parsed CV records locally for ranking, RAG, and dashboard review.
- Rank candidates against a job description using OpenAI embeddings when available.
- Use keyword-based fallback ranking when `OPENAI_API_KEY` is not configured.
- Generate match explanations with an OpenAI LLM when configured.
- Detect biased or exclusionary wording in job descriptions.
- Suggest neutral wording and optionally rewrite job descriptions.
- Generate synthetic CV records for demo and testing.
- Transform resume text into professional, ATS-friendly, or short summary styles.
- Ask questions over uploaded CVs using a RAG assistant with source snippets.
- View dashboard metrics and charts for uploaded CVs, ranking results, synthetic CVs, and RAG chunks.

## Project Structure

```text
.
|-- app.py                         # Streamlit landing page
|-- pages/                         # Streamlit multipage UI
|-- services/                      # Parsing, ranking, bias, RAG, OpenAI, storage services
|-- data/                          # Local runtime data and processed CSV files
|-- DE-CV/                         # Local test CV dataset
|-- assets/                        # Static project assets
|-- docs/
|   |-- final_documentation.md     # Main final project documentation
|   |-- final_documentation.html   # Rendered report HTML
|   |-- final_documentation.pdf    # Final report PDF
|   |-- screenshots/               # Streamlit run screenshots
|   `-- diagrams/                  # Static PNG diagrams used in the report
`-- scripts/
    |-- generate_diagram_images.py # Generates report diagram PNGs
    `-- export_documentation_pdf.py# Exports Markdown documentation to HTML/PDF
```

## Streamlit Pages

- **Home Page:** Project overview and navigation entry point.
- **Upload CVs:** Upload PDF/DOCX resumes and save extracted text.
- **Resume Ranking:** Compare uploaded CVs against a job description and rank candidates.
- **Bias Detection:** Find biased wording and suggest neutral alternatives.
- **Synthetic CV Generation:** Generate fake structured CV records for demo/testing.
- **Style Transformation:** Rewrite resume text in selected styles without inventing facts.
- **RAG Assistant:** Ask questions over uploaded CV content with retrieved sources.
- **Dashboard:** Show project metrics, ranking charts, synthetic CV charts, and skill summaries where data is available.

## Services

- `services/openai_service.py`: OpenAI API integration for LLM and embedding calls.
- `services/resume_parser.py`: PDF/DOCX resume text extraction.
- `services/ranking_service.py`: Resume/job-description matching and ranking logic.
- `services/bias_detection_service.py`: Bias term detection and neutral alternatives.
- `services/synthetic_cv_service.py`: Synthetic CV record generation.
- `services/style_transformer_service.py`: Resume style rewriting.
- `services/rag_service.py`: CV chunking, retrieval, and grounded Q&A.
- `services/storage_service.py`: Local CSV and file storage helpers.

All implemented services are connected to the Streamlit UI through the page files in `pages/`.

## Data

The project uses 20 unique Data Engineer CVs for local testing. Uploaded CVs are processed locally, and extracted text is saved for ranking and RAG workflows. Synthetic CV records are generated for demo and testing with fields such as name, job category, skills, education, experience, projects, and certifications.

Private personal details from CV files should not be exposed in public documentation, screenshots, or shared outputs.

## Validated Results

The final documentation records the following validation results:

| Metric | Result |
| --- | ---: |
| CV records | 20 |
| Ranking results | 20 |
| Synthetic CVs | 35 |
| RAG chunks | 111 |
| Cached RAG chunks | 111 |
| Average match score | 52.8% |
| Streamlit HTTP check | 200 OK |
| CV parsing | 20 successful, 0 failed |

These results confirm that the implemented services work end-to-end through the Streamlit UI for the local academic/demo dataset.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file from `.env.example` if the template exists:

```bash
cp .env.example .env
```

Then add your OpenAI configuration:

```bash
OPENAI_API_KEY=your_real_key_here
OPENAI_MODEL=gpt-4.1
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

If `OPENAI_API_KEY` is missing, the app still opens and uses fallback logic where implemented.

## Run the App

```bash
streamlit run app.py
```

Open the Streamlit app at:

```text
http://localhost:8501
```

## Documentation and PDF Report

The final documentation artifacts are stored in `docs/`:

- `docs/final_documentation.md`
- `docs/final_documentation.html`
- `docs/final_documentation.pdf`
- `docs/screenshots/`
- `docs/diagrams/`

Regenerate the static diagram PNG files:

```bash
python3 scripts/generate_diagram_images.py
```

Regenerate the HTML and PDF report:

```bash
python3 scripts/export_documentation_pdf.py
```

The PDF export uses Playwright to render the generated HTML and save the final report as `docs/final_documentation.pdf`.

## Validation Commands

Run basic syntax and import checks:

```bash
python -m compileall app.py pages services scripts
python -c "import services.openai_service, services.ranking_service, services.rag_service"
pip check
```

Check the Streamlit HTTP response while the app is running:

```bash
curl -I http://localhost:8501
```

## Limitations

- The dataset is limited to 20 local CVs.
- Synthetic CV generation is simulated for academic/demo use and is not a trained GAN.
- LLM outputs may vary between runs.
- Ranking scores and explanations should be reviewed by humans.
- The project is not production hiring software.
- Local CSV storage is simple and suitable for demo scope, not production-scale recruitment data.

## Future Work

- Use a larger and more diverse CV dataset.
- Replace simulated synthetic generation with a real GAN or advanced generator.
- Add advanced fairness metrics and evaluation reports.
- Add authentication and user roles.
- Replace CSV-only storage with a database.
- Deploy the app online.
- Add stronger ranking evaluation metrics.

## Security Notes

- Never commit `.env` or real API keys.
- Runtime files in `data/` may contain uploaded CV text and should be handled as private data.
- Do not publish real candidate CVs or extracted personal details.
