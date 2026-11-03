import os
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from werkzeug.utils import secure_filename
from parser import extract_resume_text, parse_resume
from database import init_db, add_candidate, get_candidates, get_candidate, delete_candidate, get_dashboard_stats

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx"}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-for-a-real-deployment")
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

UPLOAD_FOLDER.mkdir(exist_ok=True)
init_db()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    stats = get_dashboard_stats()
    return render_template("index.html", stats=stats)

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files.get("resume")
        if not file or file.filename == "":
            flash("Please choose a resume file.", "error")
            return redirect(url_for("upload"))
        if not allowed_file(file.filename):
            flash("Only PDF and DOCX files are supported.", "error")
            return redirect(url_for("upload"))

        original_name = secure_filename(file.filename)
        suffix = Path(original_name).suffix.lower()
        # Use a random temporary name; do not trust the original filename as a path.
        import uuid
        temp_path = UPLOAD_FOLDER / f"{uuid.uuid4().hex}{suffix}"
        try:
            file.save(temp_path)
            text = extract_resume_text(temp_path)
            if not text.strip():
                flash("No readable text was found. If this is a scanned PDF, run OCR first.", "error")
                return redirect(url_for("upload"))
            details = parse_resume(text)
            details["filename"] = original_name
            candidate_id = add_candidate(details)
            flash("Resume parsed and candidate saved successfully.", "success")
            return redirect(url_for("candidate_detail", candidate_id=candidate_id))
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("upload"))
        except Exception:
            app.logger.exception("Resume processing failed")
            flash("Could not process this file. Check that it is a valid PDF or DOCX.", "error")
            return redirect(url_for("upload"))
        finally:
            # The uploaded document is processed temporarily and then removed.
            if temp_path.exists():
                temp_path.unlink()

    return render_template("upload.html")

@app.route("/candidates")
def candidates():
    query = request.args.get("q", "").strip()
    rows = get_candidates(query)
    return render_template("candidates.html", candidates=rows, query=query)

@app.route("/candidate/<int:candidate_id>")
def candidate_detail(candidate_id):
    candidate = get_candidate(candidate_id)
    if candidate is None:
        abort(404)
    return render_template("candidate_detail.html", candidate=candidate)

@app.route("/candidate/<int:candidate_id>/delete", methods=["POST"])
def candidate_delete(candidate_id):
    delete_candidate(candidate_id)
    flash("Candidate record deleted.", "success")
    return redirect(url_for("candidates"))

@app.errorhandler(413)
def too_large(_error):
    flash("File is too large. Maximum upload size is 5 MB.", "error")
    return redirect(url_for("upload"))

if __name__ == "__main__":
    app.run(debug=True)
