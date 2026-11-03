import re
from pathlib import Path
import pdfplumber
from docx import Document
import spacy
from spacy.matcher import PhraseMatcher

# A lightweight spaCy English pipeline; no separate language-model download is needed.
nlp = spacy.blank('en')
skill_matcher = PhraseMatcher(nlp.vocab, attr='LOWER')

# This starter skill list can be extended for your department or project domain.
SKILLS = [
    "Python", "Java", "C", "C++", "JavaScript", "HTML", "CSS", "SQL",
    "SQLite", "PostgreSQL", "Flask", "Django", "Streamlit", "React",
    "Machine Learning", "Deep Learning", "Data Science", "Pandas",
    "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", " spaCy ",
    "Git", "GitHub", "Excel", "Power BI", "Tableau", " communication",
    "Teamwork", "Problem Solving", "Leadership"
]

skill_patterns = [nlp.make_doc(skill.strip()) for skill in SKILLS if skill.strip()]
skill_matcher.add('SKILLS', skill_patterns)

EDUCATION_TERMS = [
    "B.Tech", "B.E.", "Bachelor of Technology", "Bachelor of Engineering",
    "BCA", "B.Sc", "B.Com", "BA", "M.Tech", "MCA", "M.Sc",
    "MBA", "Ph.D", "Intermediate", "Class XII", "Class 12", "High School",
    "Class X", "Class 10", "Diploma"
]

def extract_resume_text(file_path):
    """Extract selectable text from PDF or DOCX. Scanned PDFs need OCR."""
    path = Path(file_path)
    ext = path.suffix.lower()
    if ext == ".pdf":
        pages = []
        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages:
                pages.append(page.extract_text() or "")
        return "\n".join(pages)
    if ext == ".docx":
        doc = Document(str(path))
        parts = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                parts.append(" | ".join(cell.text for cell in row.cells))
        return "\n".join(parts)
    raise ValueError("Unsupported file type. Please upload a PDF or DOCX.")

def clean_lines(text):
    return [re.sub(r"\s+", " ", line).strip() for line in text.splitlines() if line.strip()]

def extract_name(text):
    """Simple heuristic: first plausible non-contact line near the top."""
    ignored = ("resume", "curriculum vitae", "cv", "profile", "objective")
    for line in clean_lines(text)[:8]:
        low = line.lower()
        if any(word in low for word in ignored):
            continue
        if "@" in line or re.search(r"\d{5,}", line):
            continue
        words = line.split()
        if 2 <= len(words) <= 5 and not any(ch in line for ch in "@:/"):
            if sum(ch.isalpha() for ch in line) >= 4:
                return line[:100]
    return "Not detected"

def parse_resume(text):
    email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text)
    phone_match = re.search(r"(?<!\w)(?:\+?\d{1,3}[-.\s]?)?(?:\d[-.\s]?){9,12}\d(?!\w)", text)

    found_skills = []
    doc = nlp(text)
    matched_spans = skill_matcher(doc)
    matched_terms = {doc[start:end].text.lower() for _, start, end in matched_spans}
    for skill in SKILLS:
        normalized = skill.strip()
        if normalized and normalized.lower() in matched_terms:
            # Preserve the display spelling and dictionary order.
            found_skills.append(normalized)

    lines = clean_lines(text)
    education = []
    for line in lines:
        if any(term.lower() in line.lower() for term in EDUCATION_TERMS):
            education.append(line[:250])
    education = list(dict.fromkeys(education))[:10]

    experience_lines = []
    experience_pattern = re.compile(
        r"\b(\d+(?:\.\d+)?)\s*\+?\s*(years?|yrs?)\b|\b(intern|internship|worked|employment|experience)\b",
        re.IGNORECASE
    )
    for line in lines:
        if experience_pattern.search(line):
            experience_lines.append(line[:250])
    experience_lines = list(dict.fromkeys(experience_lines))[:10]

    return {
        "name": extract_name(text),
        "email": email_match.group(0) if email_match else "Not detected",
        "phone": phone_match.group(0).strip() if phone_match else "Not detected",
        "skills": ", ".join(found_skills) if found_skills else "Not detected",
        "education": "\n".join(education) if education else "Not detected",
        "experience": "\n".join(experience_lines) if experience_lines else "Not detected",
    }
