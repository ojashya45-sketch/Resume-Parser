# Automated Resume Parser

A beginner-friendly Flask project that extracts basic information from PDF and DOCX resumes and stores the results in SQLite.

## Features
- Upload PDF and DOCX resumes
- Extract selectable PDF text and DOCX text
- Extract likely name, email, phone, skills, education and experience snippets
- Store extracted fields in SQLite
- Search candidate records
- View and delete candidate records

## Requirements
- Python 3.11 or 3.12 recommended
- Windows, macOS or Linux

## Setup on Windows PowerShell

1. Open this folder in VS Code.
2. Create a virtual environment:

   ```powershell
   py -3.12 -m venv .venv
   ```

   If Python 3.12 is not installed, install a supported Python version and use its launcher command. You can check with `py --list`.

3. Activate it:

   ```powershell
   .venv\\Scripts\\Activate.ps1
   ```

   If PowerShell blocks activation, run this for the current terminal only:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .venv\\Scripts\\Activate.ps1
   ```

4. Install packages:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Run the app:

   ```powershell
   python app.py
   ```

6. Open http://127.0.0.1:5000 in your browser.

## Setup on macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

## Project structure

```text
automated_resume_parser/
├── app.py
├── parser.py
├── database.py
├── requirements.txt
├── resume_parser.db       # created automatically
├── uploads/               # temporary files; processed files are removed
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── upload.html
│   ├── candidates.html
│   └── candidate_detail.html
└── static/
    ├── css/style.css
    └── js/main.js
```

## How extraction works
- PDFPlumber reads text from selectable-text PDFs.
- python-docx reads paragraphs and tables from DOCX files.
- Regular expressions find email and phone-like strings.
- A small editable skill dictionary finds matching skills.
- Keyword matching collects education and experience-related lines.

spaCy's lightweight English tokenizer and PhraseMatcher are used to identify skills from an editable skills dictionary. No separate spaCy language-model download is required. This is NLP-assisted, rule-based extraction, not a trained machine-learning model.

## Limitations
- Scanned/image-only PDFs need OCR; this version reports that no readable text was found.
- Name, education and experience extraction are heuristic and must be reviewed.
- The skill list is only a starter list. Add terms relevant to your use case.
- This is a local educational demo, not a production recruitment system.

## Privacy and security notes
- Use sample or consented resumes for demonstrations.
- Uploaded files are temporarily written to `uploads/` and removed after parsing.
- The database stores extracted contact details and resume fields. Keep the database private and delete records when no longer needed.
- Before public deployment, add authentication, CSRF protection, stronger file validation, HTTPS, secure secrets, access controls and a privacy notice.
- Never use extracted data alone to make hiring decisions.
