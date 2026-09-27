# 🎓 SUSL GPA Tracker

A web application for tracking GPA for the BSc (Hons) in Information Systems programme at Sabaragamuwa University of Sri Lanka.

## Features
- 📚 Full 8-semester curriculum from the official FOC handbook
- 🧮 Automatic GPA calculation with official SUSL grade points
- ⚖️ Year-weighted Final GPA (FGPA): Y1=20%, Y2=30%, Y3=30%, Y4=20%
- 🚫 Non-GPA (NGPA) module handling
- ☁️ Persistent cloud storage with Supabase
- 📱 Responsive — works on desktop and mobile

## Tech Stack
- **Python 3.11**
- **Streamlit** — web UI
- **Supabase (PostgreSQL)** — cloud database

## Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
