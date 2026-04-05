# 🏙️ Dubai Property AI

An AI-powered Dubai real estate advisor. Clients enter their location, BHK size, budget and preferences — Claude analyses the market and returns detailed property recommendations.

---

## 📁 Folder Structure

```
dubai-property-ai/
│
├── templates/              ← HTML files
│   └── index.html          Main page (form + result UI)
│
├── static/
│   ├── css/                ← Stylesheets
│   │   └── styles.css      All styles, variables, animations
│   │
│   ├── js/                 ← JavaScript
│   │   └── app.js          BHK logic, API calls, result rendering
│   │
│   └── assets/             ← Images, icons, fonts (if any)
│
├── api/                    ← Python backend
│   ├── app.py              Flask server + /api/analyze endpoint
│   └── requirements.txt    Python dependencies
│
├── .env.example            Sample environment variables
└── README.md               This file
```

---

## 🚀 Option A — Open directly in browser (no backend needed)

The `templates/index.html` file calls the Anthropic API directly from the browser.

1. Open `templates/index.html` in your browser
2. That's it — works out of the box when served via claude.ai

> ⚠️ For production, always route API calls through the Python backend (Option B) so your API key is never exposed in the browser.

---

## 🐍 Option B — Run with Python Flask backend (recommended for production)

The Flask backend keeps your API key secure on the server.

### 1. Install dependencies

```bash
cd api
pip install -r requirements.txt
```

### 2. Set your API key

```bash
cp ../.env.example ../.env
# Edit .env and paste your Anthropic API key
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

### 3. Run the server

```bash
python app.py
```

### 4. Open in browser

```
http://localhost:5000
```

### How it works (backend mode)

In `static/js/app.js`, uncomment the `callAnthropicAPI` function that uses `/api/analyze` and comment out the direct Anthropic fetch. The JS sends the prompt to Flask → Flask calls Claude → Flask returns the result to the browser.

---

## 🛠️ Tech Stack

| Layer      | Technology              |
|------------|-------------------------|
| Frontend   | HTML5, CSS3, Vanilla JS |
| Backend    | Python 3.10+, Flask     |
| AI Model   | Claude Sonnet (Anthropic) |
| Fonts      | Playfair Display, Syne  |

---

## 📝 Customisation

- **Add more locations** → Edit the `<select id="location">` in `templates/index.html`
- **Change colours** → Edit CSS variables in `static/css/styles.css` under `:root`
- **Change the AI prompt** → Edit `buildPrompt()` in `static/js/app.js`
- **Add new form fields** → Add HTML in `index.html`, read with `getVal()` in `app.js`, inject into the prompt in `buildPrompt()`
