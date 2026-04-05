# 🏙️ Dubai Property AI

An AI-powered Dubai real estate advisor built with Flask and Groq AI.
Clients enter their location, BHK size, budget and preferences — 
the AI analyses the market and returns detailed property recommendations.

## Features
- Location selector with 15+ Dubai communities
- BHK size selection (Studio to 5+ BHK)
- Budget, purpose and furnishing filters
- AI-generated market analysis, price estimates and ROI insights

## Tech Stack
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **Backend:** Python, Flask
- **AI:** Groq API (LLaMA 3.3 70B)

## Setup

1. Clone the repo
2. Install dependencies:
   cd api
   pip install -r requirements.txt
3. Create a .env file in the root folder:
   GROQ_API_KEY=your-key-here
4. Run the app:
   PORT=8080 python3 app.py
5. Open http://127.0.0.1:8080

## Live Demo
Deployed on Render: [your-link-here]
