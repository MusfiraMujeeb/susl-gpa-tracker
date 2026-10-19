# 🎓 SUSL GPA Tracker

A **multi-user web application** for tracking GPA for the **BSc (Hons) in Information Systems** programme at Sabaragamuwa University of Sri Lanka (SUSL).

🌐 **Live Demo:** [https://susl-gpa-tracker.streamlit.app](https://susl-gpa-tracker.streamlit.app)

---

## ✨ Features

- 📚 **Complete curriculum pre-loaded** — All 8 semesters from the official Faculty of Computing handbook
- 🧮 **Accurate GPA calculation** — Uses the official SUSL grade points (A+ = 4.0 through E = 0.0)
- ⚖️ **Year-weighted Final GPA (FGPA)** — Y1 = 20%, Y2 = 30%, Y3 = 30%, Y4 = 20%
- 🚫 **NGPA module handling** — Non-GPA courses (English, Communication Skills, etc.) are excluded from GPA but tracked for credits
- 📝 **Auto-grade from marks** — Enter raw marks and the grade is picked automatically
- 🔐 **Multi-user authentication** — Email/password signup and login via Supabase Auth
- 🛡️ **Row-Level Security (RLS)** — Every user sees only their own data; complete privacy between accounts
- ☁️ **Cloud-persistent storage** — Grades are saved to Supabase (PostgreSQL) and survive restarts
- 📱 **Responsive UI** — Works seamlessly on desktop, tablet, and mobile
- ⏳ **Pending results tracking** — Courses without grades yet are tracked separately

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | [Streamlit](https://streamlit.io/) |
| **Backend** | Python 3.11 |
| **Database** | [Supabase](https://supabase.com/) (PostgreSQL) |
| **Authentication** | Supabase Auth (Email / Password) |
| **Security** | Row-Level Security (RLS) policies |
| **Version Control** | Git + GitHub |
| **Hosting** | [Streamlit Community Cloud](https://share.streamlit.io/) |

---



## 🚀 Run Locally

### Prerequisites
- Python 3.11 or newer
- A Supabase account (free tier works)

### 1. Clone the repository
```bash
git clone https://github.com/MusfiraMujeeb/susl-gpa-tracker.git
cd susl-gpa-tracker
