import os

import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
SYNTHETIC_DIR = os.path.join(BASE_DIR, "data", "synthetic")

CVS_PATH = os.path.join(PROCESSED_DIR, "cvs.csv")
RANKING_PATH = os.path.join(PROCESSED_DIR, "ranking_results.csv")
SYNTHETIC_PATH = os.path.join(SYNTHETIC_DIR, "synthetic_cvs.csv")


def ensure_data_dirs():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(SYNTHETIC_DIR, exist_ok=True)


def save_cv_record(record):
    ensure_data_dirs()
    df = load_cv_records()
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    df.to_csv(CVS_PATH, index=False)


def load_cv_records():
    ensure_data_dirs()
    columns = ["candidate_id", "file_name", "candidate_name", "extracted_text", "upload_time"]
    if not os.path.exists(CVS_PATH):
        return pd.DataFrame(columns=columns)
    return pd.read_csv(CVS_PATH).fillna("")


def save_ranking_results(df):
    ensure_data_dirs()
    df.to_csv(RANKING_PATH, index=False)


def load_ranking_results():
    ensure_data_dirs()
    if not os.path.exists(RANKING_PATH):
        return pd.DataFrame()
    return pd.read_csv(RANKING_PATH).fillna("")


def save_synthetic_cvs(df):
    ensure_data_dirs()
    existing = load_synthetic_cvs()
    combined = pd.concat([existing, df], ignore_index=True)
    combined.to_csv(SYNTHETIC_PATH, index=False)


def load_synthetic_cvs():
    ensure_data_dirs()
    if not os.path.exists(SYNTHETIC_PATH):
        return pd.DataFrame()
    return pd.read_csv(SYNTHETIC_PATH).fillna("")
