# 🔥 GitHub Trending Dashboard & CLI

<div align="center">
  <p><strong>Discover the future of code before it trends. An AI-powered SaaS dashboard & CLI to track community hype, perform dependency security audits, and generate Cursor prompts in 1-click.</strong></p>
  
  <p>
    <a href="https://github.com/Mironsbl/Github-Trending-CLI/stargazers"><img src="https://img.shields.io/github/stars/Mironsbl/Github-Trending-CLI?style=for-the-badge&color=gold" alt="Stars"></a>
    <a href="https://github.com/Mironsbl/Github-Trending-CLI/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Mironsbl/Github-Trending-CLI?style=for-the-badge&color=blue" alt="License"></a>
    <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python">
    <img src="https://img.shields.io/badge/Flask-3.0%2B-emerald?style=for-the-badge&logo=flask" alt="Flask">
  </p>
</div>

---

## ✨ Key Features

### 📊 1. Hype Index & Live Metrics
* **Hype Velocity:** Sort repositories by real-time growth velocity rather than just static star counts. Find obscure developer gems before they reach big tech lists.
* **Translucent Glass UI:** A gorgeous, responsive zinc-themed dashboard (inspired by Linear and Vercel) featuring visual grids, metrics, keyboard shortcuts, and full EN/RU localization.

### 🤖 2. Gemini 2.5 AI Integrations
* **1-Click Summaries:** Gemini AI condenses complex repos into 3 simple bullet points.
* **Auto-Command Extractor:** Instantly finds and displays the exact installation and run commands.
* **Cursor AI Prompt Builder:** Generates copy-paste prompts tailored for Cursor AI or GitHub Copilot to help you start hacking instantly.
* **Security Audits:** Performs automated dependency audits to check for supply-chain risks, broad permissions, and malware vectors.

### 💬 3. Community Buzz Aggregator
* **Integrated Feed:** Scrapes and displays mentions, sentiment scores, and reviews from HackerNews, X/Twitter (via Nitter proxies), and Reddit in a single unified project timeline.

### 🧪 4. Zero-Auth Sandbox Demo
* **Interactive Sandbox:** Let users search, filter, and run full test runs directly from the landing page without registering or logging in.

### 👑 5. Pro Developer Features
* **Persistent Watchlists:** Save and track your favorite repositories, backed by a SQLite database.
* **Weekly Digests:** Get automatic newsletters/digests of your watchlist.
* **Export & RSS:** Download JSON/CSV reports or subscribe via a built-in RSS feed (`/api/feed.xml`).

---

## 🛠️ Tech Stack
* **Backend:** Python 3.14, Flask, Waitress (Production-grade WSGI), SQLite
* **Frontend:** HTML5, Vanilla JS, CSS Glassmorphism
* **AI:** Google Gemini 2.5 API
* **Testing:** Pytest (81 test suite covering full CLI, API, Scraper, and Web endpoints)

---

## 🚀 Installation & Setup

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/Mironsbl/Github-Trending-CLI.git
cd Github-Trending-CLI
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory:
```env
PORT=5050
HOST=127.0.0.1
FLASK_SECRET_KEY=some-random-key-here
GEMINI_API_KEY=your_gemini_api_key
GITHUB_TOKEN=your_github_token
```

### 3. Run the Application

#### A. Web Dashboard (Flask + Waitress)
```bash
python main.py --web
```
Open **`http://127.0.0.1:5050`** in your browser.

#### B. CLI Mode
```bash
# Fetch top 10 trending repositories for the week
python main.py

# Fetch top 5 trending repos today
python main.py --duration day --limit 5
```

---

## 🧪 Running Tests
The project comes with a comprehensive testing suite with 81 unit & integration tests.
```bash
pytest
```

---

## ⭐️ Support & Feedback
If you like this project, please **give it a star ⭐️** on GitHub!
