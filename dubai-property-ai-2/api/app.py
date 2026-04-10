import os
import sys
import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from groq import Groq
import resend
from dotenv import load_dotenv

# ── UTF-8 Fix (IMPORTANT) ───────────────────────
sys.stdout.reconfigure(encoding='utf-8')

# ── Load ENV ────────────────────────────────────
load_dotenv()

# ── Logging Setup ───────────────────────────────
logging.basicConfig(level=logging.INFO)

# ── Flask Setup ────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)

CORS(app)

# ── API Clients ────────────────────────────────
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
resend.api_key = os.environ.get("RESEND_API_KEY")

AGENT_EMAIL = os.environ.get("AGENT_EMAIL", "your@email.com")


# ── Utility: Clean text (fix encoding issues) ──
def clean_text(text):
    if not text:
        return ""
    return str(text).encode("utf-8", "ignore").decode("utf-8")


# ── Routes ─────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json(force=True)
        prompt = clean_text(data.get("prompt", "").strip())

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )

        result = clean_text(response.choices[0].message.content)

        return jsonify({"result": result})

    except Exception as e:
        logging.error(f"Analyze Error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500


@app.route("/api/enquire", methods=["POST"])
def enquire():
    try:
        data = request.get_json(force=True)

        # ── Clean all inputs ────────────────────
        name = clean_text(data.get("name", ""))
        email = clean_text(data.get("email", ""))
        phone = clean_text(data.get("phone", "Not provided"))
        location = clean_text(data.get("location", ""))
        prop_type = clean_text(data.get("propType", ""))
        bhk = clean_text(data.get("bhk", ""))
        budget = clean_text(data.get("budget", ""))
        purpose = clean_text(data.get("purpose", ""))
        furnishing = clean_text(data.get("furnishing", ""))
        notes = clean_text(data.get("notes", "None"))
        ai_summary = clean_text(data.get("aiSummary", "")[:800])

        if not name or not email:
            return jsonify({"error": "Name and Email required"}), 400

        # ── Email HTML ─────────────────────────
        agent_html = f"""
        <div style="font-family:sans-serif">
            <h2>New Property Enquiry</h2>
            <p><b>Name:</b> {name}</p>
            <p><b>Email:</b> {email}</p>
            <p><b>Phone:</b> {phone}</p>
            <hr>
            <p><b>Location:</b> {location}</p>
            <p><b>Type:</b> {bhk} {prop_type}</p>
            <p><b>Budget:</b> {budget} AED</p>
            <p><b>Purpose:</b> {purpose}</p>
            <p><b>Furnishing:</b> {furnishing}</p>
            <p><b>Notes:</b> {notes}</p>
            <hr>
            <p><b>AI Summary:</b><br>{ai_summary}</p>
        </div>
        """

        client_html = f"""
        <div style="font-family:sans-serif">
            <h2>Enquiry Received</h2>
            <p>Thank you {name}, we will contact you soon.</p>
            <p><b>{bhk} {prop_type}</b> in {location}</p>
        </div>
        """

        # ── Send Emails Safely ──────────────────
        try:
            resend.Emails.send({
                "from": "Dubai Property AI <onboarding@resend.dev>",
                "to": AGENT_EMAIL,
                "subject": f"New Enquiry: {bhk} {prop_type}",
                "html": agent_html
            })

            resend.Emails.send({
                "from": "Dubai Property AI <onboarding@resend.dev>",
                "to": email,
                "subject": "Enquiry Received",
                "html": client_html
            })

        except Exception as mail_error:
            logging.error(f"Email Error: {str(mail_error)}")
            return jsonify({"error": "Email sending failed"}), 500

        return jsonify({"success": True})

    except Exception as e:
        logging.error(f"Enquiry Error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500


# ── Run Server ─────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Server running on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port)