from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re

model = None

def load_model():
    global model
    model = SentenceTransformer("all-MiniLM-L6-v2")


TECH_SKILLS = {
    "python", "java", "c", "c++", "sql", "mysql", "postgresql",
    "mongodb", "pandas", "numpy", "tensorflow", "pytorch",
    "machine learning", "deep learning",
    "django", "flask", "fastapi",
    "aws", "azure", "docker", "kubernetes",
    "html", "css", "javascript", "react", "node",
    "git", "linux", "excel", "powerbi"
}


def extract_skills(text):
    text = text.lower()
    found_skills = set()

    for skill in TECH_SKILLS:
        if skill in text:
            found_skills.add(skill)

    return found_skills


def calculate_similarity(resume_text, jd_text):
    if model is None:
        raise ValueError("Model not loaded. Call load_model() first.")

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    if not jd_skills:
        return 0.0

    matched = resume_skills.intersection(jd_skills)

    score = (len(matched) / len(jd_skills)) * 100

    return score