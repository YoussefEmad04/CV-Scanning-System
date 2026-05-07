# Demo Checklist

Use this checklist before presenting the app.

## 1. Start the App

Run:

```bash
streamlit run app.py
```

Expected: the landing page opens with the title `AI Recruitment & Resume Screening System`.

## 2. Upload CVs

Open `Upload CVs`.

- Confirm the 20 unique Data Engineer CV records appear in the table.
- Select a CV from the preview dropdown.
- Expected: extracted resume text appears in the preview box.

## 3. Resume Ranking

Open `Resume Ranking`.

- Paste a Data Engineer job description.
- Click `Rank Candidates`.
- Expected: candidates appear sorted by match score, with matched skills, missing skills, explanations, and a bar chart.

## 4. Bias Detection

Open `Bias Detection`.

- Paste: `We need a young energetic male data engineer who is a rockstar and native speaker.`
- Click `Detect Bias`.
- Expected: biased terms, categories, alternatives, warning messages, and a chart appear.
- Optional: click neutral rewrite and confirm a cleaner version appears.

## 5. Synthetic CV Generation

Open `Synthetic CV Generation`.

- Choose `Data Engineer`.
- Generate 5 CVs.
- Expected: table updates and category/experience charts display.

## 6. Style Transformation

Open `Style Transformation`.

- Upload a resume PDF/DOCX or paste a short resume paragraph.
- Test all three styles.
- Expected: rewritten text appears without invented experience.
- Click `Download transformed resume as PDF`.
- Expected: a new PDF downloads with the transformed resume text.

## 7. RAG Assistant

Open `RAG Assistant`.

- Ask: `Which candidates mention Airflow?`
- Expected: answer appears with source CV names and retrieved snippets.
- First run may show: `Building CV search index for the first time. This may take a moment.`

## 8. Dashboard

Open `Dashboard`.

Expected: uploaded CV count, ranked candidate count, average score, synthetic CV count, and charts load without errors.
