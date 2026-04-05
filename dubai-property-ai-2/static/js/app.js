'use strict';

let selectedBHK = '';

document.addEventListener('DOMContentLoaded', () => {
  // BHK buttons
  const buttons = document.querySelectorAll('.bhk-btn');
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      selectedBHK = btn.getAttribute('data-val');
    });
  });

  // Analyse button
  document.getElementById('analyzeBtn').addEventListener('click', analyzeProperty);
});

function getVal(id) {
  const el = document.getElementById(id);
  return el ? el.value.trim() : '';
}

function setLoading(isLoading) {
  const btn     = document.getElementById('analyzeBtn');
  const btnText = document.getElementById('btnText');
  const spinner = document.getElementById('spinner');
  btn.disabled          = isLoading;
  btnText.textContent   = isLoading ? 'Analysing…' : 'Analyse with AI';
  spinner.style.display = isLoading ? 'block' : 'none';
}

function showError(msg) {
  const el = document.getElementById('errorMsg');
  el.textContent = msg;
  el.classList.add('visible');
}

function clearError() {
  const el = document.getElementById('errorMsg');
  el.textContent = '';
  el.classList.remove('visible');
}

function buildPrompt(f) {
  return `You are an expert Dubai real estate advisor with deep knowledge of Dubai's property market in 2024-2025.

A client is looking for a property with these details:
- Location/Area: ${f.location}
- Property Type: ${f.propType || 'Any'}
- Bedrooms (BHK): ${f.bhk}
- Budget (AED): ${f.budget || 'Not specified'}
- Purpose: ${f.purpose || 'Not specified'}
- Furnishing: ${f.furnishing || 'No preference'}
- Special Notes: ${f.notes || 'None'}

Provide a detailed, professional property analysis using these exact ### headings:

### Market Overview
### Price Estimate
### Top Recommended Projects or Buildings
### ROI & Investment Potential
### Key Considerations
### Verdict

Use AED currency. Be specific with numbers. Keep tone expert and concise.`;
}

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
    showError('Please select at least a Location and BHK size.');
    return;
  }

  clearError();
  setLoading(true);
  document.getElementById('resultCard').classList.remove('visible');

  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: buildPrompt(fields) })
    });
    const data = await response.json();
    if (data.error) throw new Error(data.error);

    document.getElementById('resultMeta').textContent =
      `${fields.bhk} · ${fields.location}${fields.propType ? ' · ' + fields.propType : ''}`;
    document.getElementById('resultBody').innerHTML = markdownToHTML(data.result);

    const card = document.getElementById('resultCard');
    card.classList.add('visible');
    card.scrollIntoView({ behavior: 'smooth', block: 'start' });

  } catch (err) {
    showError('Error: ' + (err.message || 'Something went wrong. Please try again.'));
  } finally {
    setLoading(false);
  }
}
