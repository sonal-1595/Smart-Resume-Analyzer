import streamlit as st
import pdfplumber
import pandas as pd
import re
import time
import matplotlib.pyplot as plt
import io

# --- Configuration & Styling ---
st.set_page_config(page_title="AI Resume Pro", layout="wide", page_icon="🚀")

# Custom CSS for a modern look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #4caf50, #8bc34a); }
    </style>
    """, unsafe_allow_html=True)

# --- Helper Functions ---

def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
    return text

def analyze_resume(text, role_skills):
    extracted_data = {}
    
    # 1. Name Extraction (Improved)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    extracted_data["Name"] = lines[0] if lines else "Not Found"

    # 2. Email Extraction
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    extracted_data["Email"] = email_match.group(0) if email_match else "Not Found"

    # 3. Phone Extraction (Supports multiple formats)
    phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    extracted_data["Phone"] = phone_match.group(0) if phone_match else "Not Found"

    # 4. Skills Match
    found_skills = {skill for skill in role_skills if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE)}
    extracted_data["Skills"] = list(found_skills)
    
    return extracted_data

# --- Main App ---

def main():
    st.title("🚀 AI-Powered Resume Analyzer")
    st.markdown("Optimize your resume for ATS (Applicant Tracking Systems) in seconds.")
    
    # Sidebar: Role & Upload
    st.sidebar.header("Settings")
    job_role = st.sidebar.selectbox("Target Job Role", 
                                    ["Data Scientist", "Full Stack Developer", "Data Analyst", "DevOps Engineer","QA Engineer"])
    
    # Pre-defined skill sets per role
    skill_map = {
        "Data Scientist": ["Python", "Machine Learning", "Data Science", "SQL", "Statistics", "PyTorch", "Pandas", "Scikit-learn"],
        "Full Stack Developer": ["React", "Node.js", "JavaScript", "HTML", "CSS", "SQL", "MongoDB", "Express", "API"],
        "Data Analyst": ["Excel", "Tableau", "Power BI", "SQL", "Python", "Data Visualization", "Statistics"],
        "DevOps Engineer": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Terraform", "Jenkins", "Git"],
        "QA Engineer": ["Manual Testing", "Test case and Scenario writing", "Bug Reporting and Bug Life Cycle", "Functional", "Smoke", "Sanity and Regression Testing", "SDLC and STLC Knowledge"]
    }
    
    target_skills = set(skill_map[job_role])
    uploaded_file = st.sidebar.file_uploader("Upload Resume (PDF)", type=["pdf"])

    if uploaded_file:
        with st.status("Analyzing Resume...", expanded=True) as status:
            st.write("Reading PDF content...")
            text = extract_text_from_pdf(uploaded_file)
            st.write("Scanning for contact info & skills...")
            extracted_data = analyze_resume(text, target_skills)
            time.sleep(1)
            status.update(label="Analysis Complete!", state="complete", expanded=False)

        # UI Layout
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📋 Candidate Profile")
            # Display info in a nice card-like format
            st.info(f"**Name:** {extracted_data['Name']}\n\n**Email:** {extracted_data['Email']}\n\n**Phone:** {extracted_data['Phone']}")
            
            # Export to CSV
            df_export = pd.DataFrame([extracted_data])
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Analysis", csv, "resume_analysis.csv", "text/csv")

        with col2:
            st.subheader("📊 Skill Match Analysis")
            resume_skills = set(extracted_data.get("Skills", []))
            matched_skills = target_skills.intersection(resume_skills)
            missing_skills = target_skills - resume_skills
            
            # Gauge Score
            score = int((len(matched_skills) / len(target_skills)) * 100)
            st.metric(label="ATS Match Score", value=f"{score}%")
            st.progress(score / 100)

            # Chart
            fig, ax = plt.subplots(figsize=(4, 3))
            colors = ['#2ecc71', '#e74c3c']
            ax.pie([len(matched_skills), len(missing_skills)], 
                   labels=['Matched', 'Missing'], 
                   autopct='%1.1f%%', startangle=90, colors=colors)
            st.pyplot(fig)

        st.divider()

        # Detailed Breakdown
        tab1, tab2 = st.tabs(["✅ Skills Found", "🚩 Skills Missing"])
        
        with tab1:
            if matched_skills:
                st.write("Excellent! You have these key skills:")
                st.success(", ".join(matched_skills))
            else:
                st.write("No matching skills found for this role.")

        with tab2:
            if missing_skills:
                st.write(f"To rank higher for **{job_role}**, consider adding:")
                for skill in missing_skills:
                    st.warning(f"💡 {skill}")
                
                st.subheader("📚 Recommended Learning Path")
                for skill in list(missing_skills)[:3]: # Top 3 missing
                    st.markdown(f"- **{skill}**: Check out [YouTube](https://www.youtube.com/results?search_query={skill}+tutorial) or [Coursera](https://www.coursera.org/search?query={skill})")
            else:
                st.balloons()
                st.success("Perfect Match! You have all the core skills.")

if __name__ == "__main__":
    main()
