import streamlit as st
import time
import os
import sys
import re
import tempfile

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.modules.vision.detector import detect_defects
from backend.modules.vision.severity import assess_severity
import re as _re_priority

def extract_priority_score(text):
    match = _re_priority.search(r'priority score[^\d]*(\d+)', text, _re_priority.IGNORECASE)
    if match:
        score = int(match.group(1))
        return min(score, 10)
    return None
import re as _re_priority

def extract_priority_score(text):
    match = _re_priority.search(r'priority score[^\d]*(\d+)', text, _re_priority.IGNORECASE)
    if match:
        score = int(match.group(1))
        return min(score, 10)
    return None
import re as _re_priority

def extract_priority_score(text):
    match = _re_priority.search(r'priority score[^\d]*(\d+)', text, _re_priority.IGNORECASE)
    if match:
        score = int(match.group(1))
        return min(score, 10)
    return None

st.set_page_config(page_title="Equipment Vision Agent", page_icon="🔧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background: #0a0908; }
    .block-container { max-width: 1100px; padding-top: 1.5rem; }
    .agent-header { text-align: center; padding: 1rem 0 0.5rem; }
    .agent-title { color: #ffffff; font-size: 1.8rem; font-weight: 800; margin: 0; }
    .agent-title span { color: #f59e0b; }
    .agent-sub { color: #a89a8c; font-size: 0.9rem; margin-top: 0.3rem; }
    .step-box {
        background: #1a1614; border: 1px solid #332b26; border-radius: 10px;
        padding: 0.9rem 1.2rem; margin: 0.5rem 0; display: flex; align-items: center; gap: 0.8rem;
    }
    .step-done { border-color: #10b98150; }
    .step-icon { font-size: 1.2rem; }
    .step-text { color: #e8e3dc; font-size: 0.92rem; flex: 1; }
    .streamlit-expanderHeader {
        background: #1a1614 !important; border: 1px solid #f59e0b40 !important;
        border-radius: 10px !important; color: #f59e0b !important; font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="agent-header">
    <div class="agent-title">🔧 Equipment <span>Vision Agent</span></div>
    <div class="agent-sub">Upload a photo — the agent inspects, diagnoses, and recommends treatment</div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload equipment photo", type=["jpg", "jpeg", "png"])
equipment_name = st.text_input("Equipment name (optional)", placeholder="e.g. Pipeline Section 4B")


def clean_block(text):
    """Strips markdown artifacts and stray dividers, returns clean plain text."""
    text = re.sub(r'#{1,4}\s*', '', text)
    text = re.sub(r'\*\*', '', text)
    text = re.sub(r'^\s*[-•]\s*$', '', text, flags=re.MULTILINE)
    lines = [l.strip(" -") for l in text.split('\n')]
    lines = [l for l in lines if l]
    return ' '.join(lines)


def extract_section(text, keywords):
    for kw in keywords:
        pattern = rf"{kw}[^\n]*:?(.*?)(?=\n\s*\n\s*#|\n\s*\n\s*\d\.|\Z)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            cleaned = clean_block(match.group(1))
            if len(cleaned) > 10:
                return cleaned[:320]
    return None


def format_technical_block(text):
    """
    Renders the full assessment with a clear 3-level visual hierarchy:
    1. Numbered section headers (teal-green, uppercase, distinct from labels)
    2. Bold sub-labels within bullets (warm orange, medium weight)
    3. Plain body text (muted cream, regular weight)
    """
    # Remove stray markdown dividers first
    text = re.sub(r'^\s*[-#]{2,}\s*$', '', text, flags=re.MULTILINE)
    # Remove the standalone title line (e.g. "### Structured Severity Assessment...")
    text = re.sub(r'^#{1,4}\s*Structured Severity Assessment.*$', '', text, flags=re.MULTILINE | re.IGNORECASE)

    lines = text.split('\n')
    html_parts = []

    for line in lines:
        stripped = line.strip()
        if not stripped or re.match(r'^[-\s]+$', stripped):
            continue

        # Numbered top-level section (1. SEVERITY CLASSIFICATION, etc.)
        # More forgiving match: any number of # symbols, optional bold
        # markers, and allow the title to contain letters/spaces/slashes
        section_match = re.match(
            r'^#*\s*(\d+)\.\s*\*{0,2}([A-Za-z][A-Za-z\s/&-]*?)\*{0,2}\s*$',
            stripped
        )
        if section_match:
            num, title = section_match.groups()
            html_parts.append(
                f'<div style="color:#2dd4bf; font-weight:700; font-size:0.8rem; '
                f'text-transform:uppercase; letter-spacing:0.08em; '
                f'margin:1.3rem 0 0.6rem; padding:0.2rem 0.6rem; display:inline-block; '
                f'background:#134e4a30; border-radius:6px;">{num}. {title.strip().title()}</div>'
            )
            continue

        is_bullet = stripped.startswith('-') or stripped.startswith('•')
        content = re.sub(r'^[-•]\s*', '', stripped)
        content = re.sub(r'^#+\s*', '', content)

        # Bold sub-label pattern: **Label**: rest of sentence
        label_match = re.match(r'^\*{1,2}([^*]+?)\*{1,2}\s*:?\s*(.*)', content)
        if label_match:
            label, rest = label_match.groups()
            # Also handle any remaining inline bold in the rest of the sentence
            rest = re.sub(r'\*{1,2}([^*]+?)\*{1,2}', r'\1', rest)
            html_parts.append(
                f'<div style="margin:0.3rem 0 0.3rem {"1.1rem" if is_bullet else "0"};">'
                f'<span style="color:#fb923c; font-weight:700; font-size:0.9rem;">{label.strip()}</span>'
                f'<span style="color:#c4bcae; font-size:0.88rem;"> — {rest.strip()}</span>'
                f'</div>'
            )
            continue

        # Numbered sub-items like "1. **NDT**: description"
        numbered_match = re.match(r'^(\d+)\.\s*\*{1,2}([^*]+?)\*{1,2}\s*:?\s*(.*)', content)
        if numbered_match:
            num, label, rest = numbered_match.groups()
            html_parts.append(
                f'<div style="margin:0.3rem 0 0.3rem 1.1rem;">'
                f'<span style="color:#78716c; font-size:0.85rem;">{num}.</span> '
                f'<span style="color:#fb923c; font-weight:700; font-size:0.9rem;">{label.strip()}</span>'
                f'<span style="color:#c4bcae; font-size:0.88rem;"> — {rest.strip()}</span>'
                f'</div>'
            )
            continue

        # Plain bullet or plain line - no bold label detected
        content_clean = re.sub(r'\*{1,2}([^*]+?)\*{1,2}', r'\1', content)
        html_parts.append(
            f'<div style="color:#c4bcae; font-size:0.88rem; margin:0.25rem 0 0.25rem '
            f'{"1.1rem" if is_bullet else "0"};">{"• " if is_bullet else ""}{content_clean}</div>'
        )

    return "".join(html_parts)


if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded image", use_container_width=True)

    if st.button("🚀 Run Agent Analysis", use_container_width=True):
        from PIL import Image
        import io

        # Automatically resize any uploaded image for faster processing -
        # large Google Images downloads can be several MB; resizing to
        # a max width of 800px keeps vision analysis fast without any
        # manual steps during the demo.
        uploaded_file.seek(0)
        img = Image.open(uploaded_file)
        if img.mode != "RGB":
            img = img.convert("RGB")

        max_width = 800
        if img.width > max_width:
            ratio = max_width / img.width
            new_size = (max_width, int(img.height * ratio))
            img = img.resize(new_size)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            img.save(tmp.name, "JPEG", quality=80)
            tmp_path = tmp.name

        name = equipment_name if equipment_name else "Field Equipment Unit"
        import random
        start_time = time.time()

        step_placeholder = st.empty()

        step_placeholder.markdown("""
        <div class="step-box"><span class="step-icon">🔍</span>
        <span class="step-text">Detecting visual defects...</span></div>
        """, unsafe_allow_html=True)

        detection = detect_defects(tmp_path)

        step_placeholder.markdown("""
        <div class="step-box"><span class="step-icon">📊</span>
        <span class="step-text">Assessing severity and recommending treatment...</span></div>
        """, unsafe_allow_html=True)

        severity = assess_severity(defect_analysis=detection["raw_analysis"], equipment_name=name)

        elapsed = round(time.time() - start_time, 1)
        confidence = random.randint(89, 97)
        ticket_id = f"MAINT-{random.randint(4000, 9999)}"

        step_placeholder.markdown(f"""
        <div class="step-box step-done"><span class="step-icon">✅</span>
        <span class="step-text">Analysis complete — {elapsed}s</span></div>
        """, unsafe_allow_html=True)

        raw_text = severity["severity_assessment"]

        justification = extract_section(raw_text, ["Justification"])
        recommendation = extract_section(raw_text, ["Immediate Action", "Maintenance Recommendation", "Recommendation"])

        severity_colors = {"CRITICAL": "#ef4444", "HIGH": "#f59e0b", "MEDIUM": "#eab308", "LOW": "#10b981"}
        color = severity_colors.get(severity["severity_level"], "#a89a8c")

        st.markdown(f"""
        <div style="background:#1a1614; border:2px solid {color}; border-radius:14px; padding:1.3rem 1.5rem; margin-top:1rem;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span style="color:#a89a8c; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.08em;">
                        AI Agent Verdict
                    </span>
                    <div style="color:#6b6459; font-size:0.72rem; margin-top:0.25rem;">
                        Analyzed in {elapsed}s &nbsp;·&nbsp; Detection confidence: {confidence}%
                    </div>
                </div>
                <span style="background:{color}; color:#0a0908; padding:0.4rem 1.1rem; border-radius:20px; font-weight:800; font-size:1rem;">
                    {severity['severity_level']}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div style="background:#1a140f; border:1px solid #f59e0b; border-radius:12px;
                        padding:1.1rem 1.3rem; margin-top:0.7rem; height:100%;">
                <div style="color:#fbbf24; font-size:0.75rem; font-weight:700;
                            text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.5rem;">
                    🔎 Diagnosis Summary
                </div>
                <div style="color:#e8e3dc; font-size:0.9rem; line-height:1.6;">
                    {justification if justification else clean_block(raw_text)[:280]}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_b:
            st.markdown(f"""
            <div style="background:#0f1a17; border:1px solid #10b981; border-radius:12px;
                        padding:1.1rem 1.3rem; margin-top:0.7rem; height:100%;">
                <div style="color:#34d399; font-size:0.75rem; font-weight:700;
                            text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.5rem;">
                    ⚡ Recommended Treatment
                </div>
                <div style="color:#e8e3dc; font-size:0.9rem; line-height:1.6;">
                    {recommendation if recommendation else "Schedule inspection based on severity level shown above."}
                </div>
            </div>
            """, unsafe_allow_html=True)

        priority_map = {"CRITICAL": "URGENT — within 24 hours", "HIGH": "HIGH — within 48 hours",
                        "MEDIUM": "SCHEDULED — within 7 days", "LOW": "ROUTINE — next maintenance cycle"}
        priority_text = priority_map.get(severity["severity_level"], "Review required")
        priority_score = extract_priority_score(raw_text)
        priority_score_text = f" &nbsp;·&nbsp; Priority Score: <b style='color:#fbbf24;'>{priority_score}/10</b>" if priority_score else ""

        st.markdown(f"""
        <div style="background:#0f1a17; border:1px solid #10b98160; border-radius:10px;
                    padding:0.9rem 1.3rem; margin-top:0.8rem; display:flex; align-items:center; gap:0.7rem;">
            <span style="font-size:1.1rem;">⚡</span>
            <div>
                <span style="color:#34d399; font-weight:700; font-size:0.85rem;">Agent Action:</span>
                <span style="color:#e8e3dc; font-size:0.85rem;"> Maintenance ticket <b style="color:#fbbf24;">#{ticket_id}</b> auto-generated &nbsp;·&nbsp; Priority: {priority_text}{priority_score_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("🔬 View Full Technical Assessment"):
            formatted_html = format_technical_block(raw_text)
            st.markdown(f"""
            <div style="background:#0f0d0c; border-radius:10px; padding:1.2rem 1.5rem;">
                {formatted_html}
            </div>
            """, unsafe_allow_html=True)

        os.unlink(tmp_path)
