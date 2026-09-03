# 🧠 AI-Driven Customer Support Triage API

A production-ready microservice that integrates deeply with the Gmail API to autonomously intercept, classify, and physically route incoming customer support tickets using Deep Learning.

## 🚀 Architecture overview

- **API Framework:** FastAPI
- **AI/NLP Engine:** Sentence Transformers (`all-MiniLM-L6-v2`) & Scikit-Learn
- **Database:** SQLAlchemy (SQLite/PostgreSQL)
- **Integration:** Google OAuth2.0 & Gmail API
- **Deployment:** Docker & Docker Compose

## ⚡ Key Features

- **Deep Learning Embeddings:** Shifted from traditional TF-IDF to dense vector embeddings for superior semantic understanding of customer intent, achieving a **90% F1-score**.
- **Autonomous Action:** Doesn't just predict—it physically alters the state of the real world by pulling unread emails, applying structured `[AI]` labels, and marking them as read.
- **Containerized Environment:** Fully isolated and optimized lightweight Linux deployment bypassing heavyweight GPU drivers for fast CPU-bound inference.

## 🛠️ Quick Start (Docker)

1. Clone the repository and add your `credentials.json` from Google Cloud Console.
2. Spin up the container:

```bash
docker compose up --build
```
