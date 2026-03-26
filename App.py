import streamlit as st
import pdfplumber
import pandas as pd
import re
import time
import matplotlib.pyplot as plt
import io

# --- Configuration & Styling ---
st.set_page_config(page_title="AI Resume Pro Max", layout="wide", page_icon="🚀")

# Custom CSS for a modern look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #4caf50, #8bc34a); }
    .summary-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4caf50;
        margin-bottom: 20px;
    }
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

def generate_ai_summary(name, skills, role):
    """Simple AI-style summary logic"""
    top_skills = ", ".join(skills[:3]) if skills else "technical skills"
    return f"✨ **Professional Profile:** {name} is an aspiring **{role}** with expertise in **{top_skills}**. A dedicated professional with a strong foundation in modern industry tools and a proven ability to adapt to complex technical environments."

def analyze_resume(text, role_skills):
    extracted_data = {}
    
    # 1. Name Extraction
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    extracted_data["Name"] = lines[0] if lines else "Not Found"

    # 2. Email Extraction
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    extracted_data["Email"] = email_match.group(0) if email_match else "Not Found"

    # 3. Phone Extraction
    phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    extracted_data["Phone"] = phone_match.group(0) if phone_match else "Not Found"

    # 4. LinkedIn Profile Extraction
    linkedin_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-\_]+/?", text, re.IGNORECASE)
    extracted_data["LinkedIn"] = linkedin_match.group(0) if linkedin_match else None

    # 5. GitHub Profile Extraction
    github_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/[\w\-\_]+/?", text, re.IGNORECASE)
    extracted_data["GitHub"] = github_match.group(0) if github_match else None

    # 6. Skills Match
    found_skills = {skill for skill in role_skills if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE)}
    extracted_data["Skills"] = list(found_skills)
    
    return extracted_data

# --- Main App ---

def main():
    st.title("🚀 AI-Powered Resume Analyzer Pro Max")
    st.markdown("Optimize your resume for ATS (Applicant Tracking Systems) and get an AI-powered summary.")
    
    # Sidebar
    st.sidebar.header("Settings")
    job_role = st.sidebar.selectbox("Target Job Role", 
                                    ["Data Scientist", "Full Stack Developer", "Data Analyst", "DevOps Engineer","QA Engineer"])
    
    skill_map = {
        "Data Scientist": ["Python", "Machine Learning", "Data Science", "SQL", "Statistics", "PyTorch", "Pandas", "Scikit-learn"],
        "Full Stack Developer": ["React", "Node.js", "JavaScript", "HTML", "CSS", "SQL", "MongoDB", "Express", "API"],
        "Data Analyst": ["Excel", "Tableau", "Power BI", "SQL", "Python", "Data Visualization", "Statistics"],
        "DevOps Engineer": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Terraform", "Jenkins", "Git"],
        "QA Engineer": ["Manual Testing", "Test case and Scenario writing", "Bug Reporting", "Functional Testing", "Smoke Testing", "Sanity Testing", "Regression Testing", "SDLC", "STLC"]
    }
    
    target_skills = set(skill_map[job_role])
    uploaded_file = st.sidebar.file_uploader("Upload Resume (PDF)", type=["pdf"])

    if uploaded_file:
        with st.status("Analyzing Resume...", expanded=True) as status:
            st.write("Reading PDF content...")
            raw_text = extract_text_from_pdf(uploaded_file)
            st.write("Scanning details...")
            extracted_data = analyze_resume(raw_text, target_skills)
            time.sleep(1)
            status.update(label="Analysis Complete!", state="complete", expanded=False)

        # UI Layout
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📋 Candidate Profile")
            st.markdown(f"**Name:** {extracted_data['Name']}")
            st.markdown(f"**Email:** {extracted_data['Email']}")
            st.markdown(f"**Phone:** {extracted_data['Phone']}")
            
            # Social Links as Buttons
            st.write("---")
            l_col, g_col = st.columns(2)
            if extracted_data['LinkedIn']:
                l_col.link_button("🔗 LinkedIn Profile", extracted_data['LinkedIn'])
            else:
                l_col.info("LinkedIn not found")
                
            if extracted_data['GitHub']:
                g_col.link_button("💻 GitHub Profile", extracted_data['GitHub'])
            else:
                g_col.info("GitHub not found")
            
            # Export to CSV
            df_export = pd.DataFrame([{k: v for k, v in extracted_data.items() if k != 'Skills'}])
            df_export['Skills'] = ", ".join(extracted_data['Skills'])
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Analysis CSV", csv, "resume_analysis.csv", "text/csv")

        with col2:
            st.subheader("📊 ATS Match Score")
            matched_skills = set(extracted_data["Skills"])
            missing_skills = target_skills - matched_skills
            
            score = int((len(matched_skills) / len(target_skills)) * 100) if target_skills else 0
            st.metric(label="Match Quality", value=f"{score}%")
            st.progress(score / 100)

            # Pie Chart
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.pie([len(matched_skills), len(missing_skills)], 
                   labels=['Matched', 'Missing'], 
                   autopct='%1.1f%%', startangle=90, colors=['#2ecc71', '#e74c3c'])
            st.pyplot(fig)

        st.divider()

        # AI Summary Section
        st.subheader("🤖 AI-Generated Summary")
        summary = generate_ai_summary(extracted_data['Name'], extracted_data['Skills'], job_role)
        st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)

        # Detailed Breakdown Tabs
        st.subheader("🛠️ Deep Skill Analysis & Learning Roadmap")
        tab1, tab2, tab3 = st.tabs(["✅ Skills Found", "🚩 Skills Gap Analysis", "🗺️ Personalized Roadmap"])
        
        with tab1:
            if matched_skills:
                st.write("### Key Strengths:")
                m_list = list(matched_skills)
                cols = st.columns(min(len(m_list), 4))
                for i, s in enumerate(m_list):
                    cols[i % 4].success(f"🏆 {s}")
            else:
                st.error("No matching skills found. Time to upskill!")

        with tab2:
            if missing_skills:
                st.write("### Missing Skills Priority:")
                missing_data = [{"Skill": m, "Priority": "🔴 High" if i < 2 else "🟡 Medium"} for i, m in enumerate(missing_skills)]
                st.table(missing_data)
            else:
                st.balloons()
                st.success("Perfect Match! You have all core skills.")

        with tab3:
            if missing_skills:
                st.write("### 🚀 Learning Path")
                for i, skill in enumerate(list(missing_skills)[:3]):
                    with st.expander(f"Step {i+1}: Master {skill}", expanded=(i==0)):
                        st.write(f"Improve your profile by learning **{skill}**.")
                        st.markdown(f"- 📺 [Free Course](https://www.youtube.com/results?search_query={skill}+tutorial)")
                        st.select_slider(f"Difficulty Level", options=["Easy", "Moderate", "Hard"], value="Moderate", key=f"diff_{skill}")
            else:
                st.write("You're ready for the role! Start applying.")

if __name__ == "__main__":
    main()
