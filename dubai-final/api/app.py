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

# ── API Clients ──────────────────────────────────────────────────────────────
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
resend.api_key = os.environ.get("RESEND_API_KEY")

# ✏️ CHANGE THIS — the email address where YOU want to receive enquiries
AGENT_EMAIL = os.environ.get("AGENT_EMAIL", "fayzanbhat4498@gmail.com")


# ── Helper: strips special characters so emails never break ─────────────────
# ── Helper: strips special characters so emails never break ─────────────────
# ── Helper: strips special characters so emails never break ─────────────────
def clean(text):
    if text is None:
        return ""
    
    # Convert to string
    text = str(text)
    
    # Replace common problematic characters manually
    replacements = {
        '\u02c0': "'",  # Modifier letter triangular colon
        '\u2018': "'",  # Left single quote
        '\u2019': "'",  # Right single quote
        '\u201c': '"',  # Left double quote
        '\u201d': '"',  # Right double quote
        '\u2013': '-',  # En dash
        '\u2014': '-',  # Em dash
        '\u2026': '...', # Ellipsis
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Then encode to ASCII, ignoring any remaining non-ASCII characters
    try:
        return text.encode('ascii', errors='ignore').decode('ascii').strip()
    except:
        # Last resort - remove all non-ASCII characters
        return ''.join(char for char in text if ord(char) < 128).strip()


# ── Route: Serve the main page ───────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ── Route: AI Property Analysis ──────────────────────────────────────────────
@app.route("/api/analyze", methods=["POST"])
# Replace your analyze function with this version that has better error logging:

@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json(force=True)
        prompt = data.get("prompt", "").strip()

        if not prompt:
            return jsonify({"error": "Prompt is required."}), 400

        print(f"Received prompt: {prompt[:100]}...")  # Debug log

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = response.choices[0].message.content
        print(f"Got response from Groq: {result[:100]}...")  # Debug log
        
        # Clean the AI response before sending back
        result = clean_ai_text(result)
        
        return jsonify({"result": result})

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Full error in analyze: {error_details}")  # This will show in terminal
        return jsonify({"error": f"Error: {str(e)}"}), 500

# ── Route: Send Enquiry Email ────────────────────────────────────────────────
@app.route("/api/enquire", methods=["POST"])
def enquire():
    try:
        data = request.get_json(force=True)

        # Clean all inputs to remove special characters that break emails
        name       = clean(data.get("name", ""))
        email      = data.get("email", "").strip()
        phone      = clean(data.get("phone", "Not provided"))
        location   = clean(data.get("location", ""))
        prop_type  = clean(data.get("propType", ""))
        bhk        = clean(data.get("bhk", ""))
        budget     = clean(data.get("budget", ""))
        purpose    = clean(data.get("purpose", ""))
        furnishing = clean(data.get("furnishing", ""))
        notes      = clean(data.get("notes", "None"))
        ai_summary = clean(data.get("aiSummary", "")[:800])

        if not name or not email:
            return jsonify({"error": "Name and email are required."}), 400

        # ── Email 1: Sent TO YOU (the agent) when someone enquires ───────────
        agent_html = f"""
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto;background:#0A0A0F;color:#F0EDE6;padding:32px;border-radius:12px;border:1px solid rgba(201,168,76,0.3)">
          <h2 style="color:#C9A84C;margin-bottom:4px">New Property Enquiry</h2>
          <p style="color:#8a876e;margin-bottom:24px">Submitted via Dubai Property AI</p>
          <div style="background:#111118;border-radius:8px;padding:20px;margin-bottom:16px;border:1px solid rgba(201,168,76,0.15)">
            <h3 style="color:#C9A84C;font-size:12px;letter-spacing:2px;text-transform:uppercase;margin-bottom:12px">Client Details</h3>
            <p style="margin:6px 0"><strong style="color:#C9A84C">Name:</strong> {name}</p>
            <p style="margin:6px 0"><strong style="color:#C9A84C">Email:</strong> {email}</p>
            <p style="margin:6px 0"><strong style="color:#C9A84C">Phone:</strong> {phone}</p>
          </div>
          <div style="background:#111118;border-radius:8px;padding:20px;margin-bottom:16px;border:1px solid rgba(201,168,76,0.15)">
            <h3 style="color:#C9A84C;font-size:12px;letter-spacing:2px;text-transform:uppercase;margin-bottom:12px">Property Requirements</h3>
            <p style="margin:6px 0"><strong style="color:#C9A84C">Location:</strong> {location}</p>
            <p style="margin:6px 0"><strong style="color:#C9A84C">Type:</strong> {prop_type}</p>
            <p style="margin:6px 0"><strong style="color:#C9A84C">BHK:</strong> {bhk}</p>
            <p style="margin:6px 0"><strong style="color:#C9A84C">Budget:</strong> {budget} AED</p>
            <p style="margin:6px 0"><strong style="color:#C9A84C">Purpose:</strong> {purpose}</p>
            <p style="margin:6px 0"><strong style="color:#C9A84C">Furnishing:</strong> {furnishing}</p>
            <p style="margin:6px 0"><strong style="color:#C9A84C">Notes:</strong> {notes}</p>
          </div>
          <div style="background:#111118;border-radius:8px;padding:20px;border:1px solid rgba(201,168,76,0.15)">
            <h3 style="color:#C9A84C;font-size:12px;letter-spacing:2px;text-transform:uppercase;margin-bottom:12px">AI Analysis Summary</h3>
            <p style="color:#8a876e;font-size:13px;line-height:1.7">{ai_summary}...</p>
          </div>
        </div>
        """

        resend.Emails.send({
            "from": "Dubai Property AI <onboarding@resend.dev>",
            "to": AGENT_EMAIL,
            "subject": f"New Enquiry: {bhk} {prop_type} in {location} from {name}",
            "html": agent_html
        })

        # ── Email 2: Confirmation sent TO THE CLIENT automatically ───────────
        client_html = f"""
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto;background:#0A0A0F;color:#F0EDE6;padding:32px;border-radius:12px;border:1px solid rgba(201,168,76,0.3)">
          <h2 style="color:#C9A84C;margin-bottom:4px">Enquiry Received!</h2>
          <p style="color:#8a876e;margin-bottom:24px">Thank you {name}, our agent will contact you shortly.</p>
          <div style="background:#111118;border-radius:8px;padding:20px;border:1px solid rgba(201,168,76,0.15)">
            <h3 style="color:#C9A84C;font-size:12px;letter-spacing:2px;text-transform:uppercase;margin-bottom:12px">Your Requirements</h3>
            <p style="margin:6px 0"><strong style="color:#C9A84C">Location:</strong> {location}</p>
            <p style="margin:6px 0"><strong style="color:#C9A84C">Property:</strong> {bhk} {prop_type}</p>
            <p style="margin:6px 0"><strong style="color:#C9A84C">Budget:</strong> {budget} AED</p>
            <p style="margin:6px 0"><strong style="color:#C9A84C">Purpose:</strong> {purpose}</p>
          </div>
          <p style="margin-top:24px;color:#8a876e;font-size:13px">We look forward to helping you find your dream property in Dubai.</p>
        </div>
        """

        resend.Emails.send({
            "from": "Dubai Property AI <onboarding@resend.dev>",
            "to": email,
            "subject": "Your Dubai Property Enquiry - Received!",
            "html": client_html
        })

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"error": f"Failed to send enquiry: {str(e)}"}), 500


# ── Start Server ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n Dubai Property AI running on http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=True)