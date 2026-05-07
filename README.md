# AI Recruitment & Resume Screening System

A simple Streamlit university project that helps HR upload resumes, rank candidates, detect biased job-description wording, generate synthetic CV data, rewrite resume text, and ask questions over uploaded CVs.

## Features

- Upload PDF or DOCX CVs and extract resume text.
- Rank candidates using OpenAI embeddings, with simple keyword fallback mode.
- Generate short LLM explanations for candidate matches.
- Detect possible bias in job descriptions using readable rules.
- Generate simple synthetic CV records for demos.
- Transform resume writing style using OpenAI.
- Ask questions over uploaded CVs using a simple RAG assistant.
- View project statistics in a dashboard.

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

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Then add your real OpenAI API key:

```bash
OPENAI_API_KEY=your_real_key_here
OPENAI_MODEL=gpt-4.1
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

Run the app:

```bash
streamlit run app.py
```

If `OPENAI_API_KEY` is missing, the app still opens and uses simple fallback logic where possible.

## Streamlit Pages

- `Upload CVs`: Upload PDF/DOCX resumes and save extracted text.
- `Resume Ranking`: Rank candidates against a job description.
- `Bias Detection`: Find biased wording and optional neutral rewrite.
- `Synthetic CV Generation`: Generate demo CV data.
- `Style Transformation`: Rewrite resume text in a selected style.
- `RAG Assistant`: Ask questions over uploaded CVs.
- `Dashboard`: Show simple metrics and charts.

This system is a decision-support tool. Final recruitment decisions should be made by a human reviewer.
