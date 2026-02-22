import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="AI Resume Screening Platform", layout="wide")

st.title("AI Resume Screening Platform")

API_URL = "http://127.0.0.1:8000/analyze"

role = st.radio("Select User Type", ["Job Seeker", "Recruiter"])

if role == "Job Seeker":
    st.header("Job Seeker Dashboard")

    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    jd = st.text_area("Paste Job Description")

    if st.button("Analyze Resume"):
        if uploaded_file and jd:
            with st.spinner("Analyzing..."):
                try:
                    response = requests.post(
                        API_URL,
                        files={"file": uploaded_file},
                        data={"jd": jd}
                    )

                    if response.status_code == 200:
                        result = response.json()
                        score = result["match_score"]

                        st.metric("Match Score", f"{score:.2f}%")
                        st.progress(min(int(score), 100))

                        if score >= 80:
                            st.success("Strong match for this role.")
                        elif score >= 50:
                            st.info("Moderate match. Improve missing skills.")
                        else:
                            st.warning("Low match. Significant skill gaps detected.")

                        st.subheader("Matched Skills")
                        st.write(", ".join(result["matched_skills"]) if result["matched_skills"] else "None")

                        st.subheader("Missing Skills")
                        st.write(", ".join(result["missing_skills"]) if result["missing_skills"] else "None")

                        if result["missing_skills"]:
                            st.subheader("Improvement Suggestion")
                            st.write(
                                "Consider strengthening the following areas: "
                                + ", ".join(result["missing_skills"])
                            )

                    else:
                        st.error(response.text)

                except Exception as e:
                    st.error(f"Connection error: {e}")
        else:
            st.warning("Upload resume and paste job description.")

if role == "Recruiter":
    st.header("Recruiter Dashboard")

    jd = st.text_area("Paste Job Description")
    uploaded_files = st.file_uploader(
        "Upload Candidate Resumes (PDF)",
        type=["pdf"],
        accept_multiple_files=True
    )

    if st.button("Rank Candidates"):
        if uploaded_files and jd:
            results = []

            with st.spinner("Analyzing candidates..."):
                for file in uploaded_files:
                    try:
                        response = requests.post(
                            API_URL,
                            files={"file": file},
                            data={"jd": jd}
                        )

                        if response.status_code == 200:
                            result = response.json()
                            results.append({
                                "Candidate": file.name,
                                "Match Score (%)": round(result["match_score"], 2)
                            })
                    except:
                        continue

            if results:
                df = pd.DataFrame(results)
                df = df.sort_values(by="Match Score (%)", ascending=False)

                st.subheader("Candidate Ranking")
                st.dataframe(df, use_container_width=True)

                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download Ranking Report",
                    csv,
                    "candidate_ranking.csv",
                    "text/csv"
                )
            else:
                st.error("No candidates could be analyzed.")
        else:
            st.warning("Upload resumes and paste job description.")