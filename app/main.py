from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from app.services.pdf_parser import extract_text_from_pdf
from app.services.similarity import calculate_similarity, load_model, extract_skills
import shutil
import os

app = FastAPI()


# Load AI model once when server starts
@app.on_event("startup")
def startup_event():
    load_model()


@app.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    jd: str = Form(...)
):
    try:
        # Save uploaded file temporarily
        with open("temp.pdf", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract resume text
        resume_text = extract_text_from_pdf("temp.pdf")

        # Validate extracted text
        if not resume_text:
            raise HTTPException(
                status_code=400,
                detail="Resume text is empty or unreadable."
            )

        # Calculate similarity score
        score = calculate_similarity(resume_text, jd)

        # -----------------------------
        # NEW: Skill Matching Logic
        # -----------------------------
        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd)

        matched = list(resume_skills.intersection(jd_skills))
        missing = list(jd_skills - resume_skills)

        # Return everything
        return {
            "match_score": round(score, 2),
            "matched_skills": matched[:20],
            "missing_skills": missing[:20]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        # Clean up temp file
        if os.path.exists("temp.pdf"):
            os.remove("temp.pdf")