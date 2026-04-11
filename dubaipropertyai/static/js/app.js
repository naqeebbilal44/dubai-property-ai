'use strict';

let selectedBHK  = '';
let lastFields   = {};
let lastAiResult = '';

// ── Init on page load ──────────────────────────
document.addEventListener('DOMContentLoaded', () => {

  // BHK button selection
  const buttons = document.querySelectorAll('.bhk-btn');
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      selectedBHK = btn.getAttribute('data-val');
    });
  });

  document.getElementById('analyzeBtn').addEventListener('click', analyzeProperty);
  document.getElementById('enquireToggle').addEventListener('click', toggleEnquireForm);
  document.getElementById('enqSubmitBtn').addEventListener('click', submitEnquiry);
});

// ── Helpers ────────────────────────────────────
function getVal(id) {
  const el = document.getElementById(id);
  return el ? el.value.trim() : '';
}

function setLoading(isLoading) {
  const btn     = document.getElementById('analyzeBtn');
  const btnText = document.getElementById('btnText');
  const spinner = document.getElementById('spinner');
  btn.disabled          = isLoading;
  btnText.textContent   = isLoading ? 'Analysing...' : 'Analyse with AI';
  spinner.style.display = isLoading ? 'block' : 'none';
}

function showError(id, msg) {
  const el = document.getElementById(id);
  el.textContent = msg;
  el.classList.add('visible');
}
function clearError(id) {
  const el = document.getElementById(id);
  el.textContent = '';
  el.classList.remove('visible');
}

// ── Convert markdown to HTML ───────────────────
function markdownToHTML(text) {
  let html = text
    .replace(/### (.+)/g, '<h3>$1</h3>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/^\* (.+)/gm, '<li>$1</li>')
    .replace(/^\- (.+)/gm, '<li>$1</li>')
    .replace(/(<li>[\s\S]*?<\/li>\n?)+/g, m => `<ul>${m}</ul>`)
    .replace(/\n\n+/g, '</p><p>');
  html = '<p>' + html + '</p>';
  html = html.replace(/<p>(<h3>)/g, '$1').replace(/(<\/h3>)<\/p>/g, '$1');
  html = html.replace(/<p>(<ul>)/g, '$1').replace(/(<\/ul>)<\/p>/g, '$1');
  html = html.replace(/<p><\/p>/g, '');
  return html;
}

// ── Analyse Property ───────────────────────────
async function analyzeProperty() {
  const fields = {
    location:   getVal('location'),
    propType:   getVal('propType'),
    bhk:        selectedBHK,
    budget:     getVal('budget'),
    purpose:    getVal('purpose'),
    furnishing: getVal('furnishing'),
    notes:      getVal('notes'),
  };

  if (!fields.location || !fields.bhk) {
    showError('errorMsg', 'Please select at least a Location and BHK size.');
    return;
  }

  lastFields = fields;
  clearError('errorMsg');
  setLoading(true);

  // Reset result section
  document.getElementById('resultCard').classList.remove('visible');
  document.getElementById('enquireSection').classList.remove('visible');
  document.getElementById('enquireForm').classList.remove('visible');
  document.getElementById('successMsg').classList.remove('visible');
  document.getElementById('enquireToggle').style.display = '';

  const prompt = `You are an expert Dubai real estate advisor with deep knowledge of Dubai's property market in 2024-2025.

A client is looking for a property with these details:
- Location/Area: ${fields.location}
- Property Type: ${fields.propType || 'Any'}
- Bedrooms (BHK): ${fields.bhk}
- Budget (AED): ${fields.budget || 'Not specified'}
- Purpose: ${fields.purpose || 'Not specified'}
- Furnishing: ${fields.furnishing || 'No preference'}
- Special Notes: ${fields.notes || 'None'}

Provide a detailed, professional property analysis using these exact ### headings:
### Market Overview
### Price Estimate
### Top Recommended Projects or Buildings
### ROI & Investment Potential
### Key Considerations
### Verdict

Use AED currency. Be specific with numbers. Keep tone expert and concise.`;

  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt })
    });
    const data = await response.json();
    if (data.error) throw new Error(data.error);

    lastAiResult = data.result;

    document.getElementById('resultMeta').textContent =
      `${fields.bhk} · ${fields.location}${fields.propType ? ' · ' + fields.propType : ''}`;
    document.getElementById('resultBody').innerHTML = markdownToHTML(data.result);

    const card = document.getElementById('resultCard');
    card.classList.add('visible');
    document.getElementById('enquireSection').classList.add('visible');
    card.scrollIntoView({ behavior: 'smooth', block: 'start' });

  } catch (err) {
    showError('errorMsg', 'Error: ' + (err.message || 'Something went wrong. Please try again.'));
  } finally {
    setLoading(false);
  }
}

// ── Toggle Enquire Form ────────────────────────
function toggleEnquireForm() {
  const form = document.getElementById('enquireForm');
  form.classList.toggle('visible');

  if (form.classList.contains('visible')) {
    // Auto-fill property details from last search
    document.getElementById('enqLocation').value = lastFields.location  || '';
    document.getElementById('enqPropType').value = lastFields.propType  || '';
    document.getElementById('enqBhk').value      = lastFields.bhk       || '';
    document.getElementById('enqBudget').value   = lastFields.budget    || '';
    document.getElementById('enqPurpose').value  = lastFields.purpose   || '';

    // Scroll to form
    setTimeout(() => {
      form.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
  }
}

// ── Submit Enquiry ─────────────────────────────
async function submitEnquiry() {
  const name        = document.getElementById('enqName').value.trim();
  const email       = document.getElementById('enqEmail').value.trim();
  const countryCode = document.getElementById('countryCode').value;
  const phoneNum    = document.getElementById('phoneNumber').value.trim();

  clearError('enqError');

  // All 3 fields are mandatory
  if (!name) {
    showError('enqError', 'Please enter your full name.');
    return;
  }
  if (!email || !email.includes('@')) {
    showError('enqError', 'Please enter a valid email address.');
    return;
  }
  if (!phoneNum) {
    showError('enqError', 'Please enter your phone number.');
    return;
  }

  const fullPhone = `${countryCode} ${phoneNum}`;

  const btn     = document.getElementById('enqSubmitBtn');
  const btnText = document.getElementById('enqBtnText');
  const spinner = document.getElementById('enqSpinner');
  btn.disabled          = true;
  btnText.textContent   = 'Sending...';
  spinner.style.display = 'block';

  try {
    const response = await fetch('/api/enquire', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name,
        email,
        phone:      fullPhone,
        location:   lastFields.location   || '',
        propType:   lastFields.propType   || '',
        bhk:        lastFields.bhk        || '',
        budget:     lastFields.budget     || '',
        purpose:    lastFields.purpose    || '',
        furnishing: lastFields.furnishing || '',
        notes:      lastFields.notes      || '',
        aiSummary:  lastAiResult
      })
    });

    const data = await response.json();
    if (data.error) throw new Error(data.error);

    // Show success, hide form and button
    document.getElementById('enquireForm').classList.remove('visible');
    document.getElementById('enquireToggle').style.display = 'none';
    document.getElementById('successMsg').classList.add('visible');

  } catch (err) {
    showError('enqError', 'Error: ' + (err.message || 'Could not send enquiry. Try again.'));
  } finally {
    btn.disabled          = false;
    btnText.textContent   = 'Send Enquiry to Agent';
    spinner.style.display = 'none';
  }
}
