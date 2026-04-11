import os
import resend
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static'))
CORS(app)

# ── API Keys (read from .env file automatically) ─────────────────────────────
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
resend.api_key = os.environ.get("RESEND_API_KEY")

# ✏️ YOUR EMAIL — change this to the email where YOU receive enquiries
AGENT_EMAIL = os.environ.get("AGENT_EMAIL", "fayzanbhat4498@gmail.com")


# ── Helper: remove special characters so emails never break ──────────────────
def clean(text):
    return str(text).encode('ascii', errors='ignore').decode('ascii').strip()


# ── Serve main page ───────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ── AI Analysis ───────────────────────────────────────────────────────────────
@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json(force=True)
        prompt = data.get("prompt", "").strip()

        if not prompt:
            return jsonify({"error": "Prompt is required."}), 400

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return jsonify({"result": response.choices[0].message.content})

    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500


# ── Send Enquiry Emails ───────────────────────────────────────────────────────
@app.route("/api/enquire", methods=["POST"])
def enquire():
    try:
        data = request.get_json(force=True)

        # Read and clean all fields (cleaning removes special chars that break emails)
        name       = clean(data.get("name", ""))
        email      = data.get("email", "").strip()  # keep email as-is
        phone      = clean(data.get("phone", "Not provided"))
        location   = clean(data.get("location", ""))
        prop_type  = clean(data.get("propType", ""))
        bhk        = clean(data.get("bhk", ""))
        budget     = clean(data.get("budget", ""))
        purpose    = clean(data.get("purpose", ""))
        furnishing = clean(data.get("furnishing", ""))
        notes      = clean(data.get("notes", "None"))
        ai_summary = clean(data.get("aiSummary", "")[:800])

        if not name or not email or not phone:
            return jsonify({"error": "Name, email and phone are required."}), 400

        # ─────────────────────────────────────────────────────────────────────
        # EMAIL 1: Goes to YOU (the agent) with full client + property details
        # ─────────────────────────────────────────────────────────────────────
        agent_html = f"""
        <div style="font-family:Arial,sans-serif;max-width:620px;margin:0 auto;background:#0A0A0F;color:#F0EDE6;padding:36px;border-radius:14px;border:1px solid rgba(201,168,76,0.3)">

          <h2 style="color:#C9A84C;font-size:26px;margin:0 0 6px">New Property Enquiry</h2>
          <p style="color:#8a876e;margin:0 0 28px;font-size:14px">Submitted via Dubai Property AI</p>

          <!-- Client Details -->
          <div style="background:#111118;border-radius:10px;padding:22px;margin-bottom:16px;border:1px solid rgba(201,168,76,0.15)">
            <h3 style="color:#C9A84C;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin:0 0 14px">Client Details</h3>
            <table style="width:100%;border-collapse:collapse">
              <tr><td style="padding:5px 0;color:#8a876e;width:120px">Name</td><td style="padding:5px 0;color:#F0EDE6;font-weight:600">{name}</td></tr>
              <tr><td style="padding:5px 0;color:#8a876e">Email</td><td style="padding:5px 0;color:#F0EDE6;font-weight:600">{email}</td></tr>
              <tr><td style="padding:5px 0;color:#8a876e">Phone</td><td style="padding:5px 0;color:#F0EDE6;font-weight:600">{phone}</td></tr>
            </table>
          </div>

          <!-- Property Requirements -->
          <div style="background:#111118;border-radius:10px;padding:22px;margin-bottom:16px;border:1px solid rgba(201,168,76,0.15)">
            <h3 style="color:#C9A84C;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin:0 0 14px">Property Requirements</h3>
            <table style="width:100%;border-collapse:collapse">
              <tr><td style="padding:5px 0;color:#8a876e;width:120px">Location</td><td style="padding:5px 0;color:#F0EDE6">{location}</td></tr>
              <tr><td style="padding:5px 0;color:#8a876e">Type</td><td style="padding:5px 0;color:#F0EDE6">{prop_type}</td></tr>
              <tr><td style="padding:5px 0;color:#8a876e">BHK</td><td style="padding:5px 0;color:#F0EDE6">{bhk}</td></tr>
              <tr><td style="padding:5px 0;color:#8a876e">Budget</td><td style="padding:5px 0;color:#F0EDE6">{budget} AED</td></tr>
              <tr><td style="padding:5px 0;color:#8a876e">Purpose</td><td style="padding:5px 0;color:#F0EDE6">{purpose}</td></tr>
              <tr><td style="padding:5px 0;color:#8a876e">Furnishing</td><td style="padding:5px 0;color:#F0EDE6">{furnishing}</td></tr>
              <tr><td style="padding:5px 0;color:#8a876e">Notes</td><td style="padding:5px 0;color:#F0EDE6">{notes}</td></tr>
            </table>
          </div>

          <!-- AI Summary -->
          <div style="background:#111118;border-radius:10px;padding:22px;border:1px solid rgba(201,168,76,0.15)">
            <h3 style="color:#C9A84C;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin:0 0 14px">AI Analysis Summary</h3>
            <p style="color:#8a876e;font-size:13px;line-height:1.8;margin:0">{ai_summary}...</p>
          </div>

          <p style="color:#8a876e;font-size:12px;margin-top:24px;text-align:center">Dubai Property AI</p>
        </div>
        """

        # ✏️ "to" is your AGENT_EMAIL from .env — no need to change here
        resend.Emails.send({
            "from": "Dubai Property AI <onboarding@resend.dev>",
            "to": AGENT_EMAIL,
            "subject": f"New Enquiry: {bhk} {prop_type} in {location} — {name}",
            "html": agent_html
        })
        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"error": f"Failed to send enquiry: {str(e)}"}), 500


# ── Run server ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n Dubai Property AI running on http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=True)
