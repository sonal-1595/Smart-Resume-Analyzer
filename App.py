import streamlit as st
import pdfplumber
import pandas as pd
import re
import time
import matplotlib.pyplot as plt

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Function to analyze resume using regex
def analyze_resume(text):
    extracted_data = {}

    # Extract Name (Assuming first line is the name)
    lines = text.strip().split("\n")
    extracted_data["Name"] = lines[0] if lines else "Not Found"

    # Extract Email
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    extracted_data["Email"] = email_match.group(0) if email_match else "Not Found"

    # Extract Phone Number
    phone_match = re.search(r"\b\d{10}\b", text)
    extracted_data["Phone"] = phone_match.group(0) if phone_match else "Not Found"

    # Extract Skills (Keyword-based Matching)
    skills_list = {"Python", "Machine Learning", "Data Science", "SQL", "Java", "C++", "HTML", "CSS", "JavaScript"}
    found_skills = {skill for skill in skills_list if skill.lower() in text.lower()}
    extracted_data["Skills"] = list(found_skills)
    
    return extracted_data

# Streamlit App
def main():
    st.set_page_config(page_title="Smart Resume Analyzer", layout="wide")
    st.title("📄 Smart Resume Analyzer")
    st.sidebar.title("Upload Your Resume")
    uploaded_file = st.sidebar.file_uploader("Upload your Resume (PDF only)", type=["pdf"])

    if uploaded_file:
        with st.spinner("Extracting information..."):
            time.sleep(2)
            text = extract_text_from_pdf(uploaded_file)
            extracted_data = analyze_resume(text)

        if extracted_data:
            st.success("✅ Resume Successfully Analyzed!")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📌 Extracted Information:")
                df = pd.DataFrame(list(extracted_data.items()), columns=["Attribute", "Value"])
                st.dataframe(df)
            
            with col2:
                st.subheader("📊 Skill Analysis")
                required_skills = {"Python", "Machine Learning", "Data Science", "SQL", "Java"}
                resume_skills = set(extracted_data.get("Skills", []))
                matched_skills = required_skills.intersection(resume_skills)
                missing_skills = required_skills - resume_skills
                
                st.write(f"✅ Matched Skills: {', '.join(matched_skills)}")
                st.write(f"❌ Missing Skills: {', '.join(missing_skills)}")
                
                # Skill Graph
                labels = ["Matched Skills", "Missing Skills"]
                sizes = [len(matched_skills), len(missing_skills)]
                fig, ax = plt.subplots()
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=['#4CAF50', '#FF6347'])
                st.pyplot(fig)

            # Resume Rating System
            resume_score = int((len(matched_skills) / len(required_skills)) * 100)
            st.subheader("📌 Resume Score: ")
            st.progress(resume_score / 100)
            st.write(f"🔹 Your Resume Score: **{resume_score}%**")
            
            if resume_score >= 80:
                st.success("🎉 Great job! Your resume is strong.")
            elif resume_score >= 50:
                st.warning("⚠️ Your resume is decent, but there's room for improvement.")
            else:
                st.error("❌ Your resume needs significant improvements.")
                
            # Course Recommendations
            if missing_skills:
                st.subheader("📚 Recommended Courses:")
                for skill in missing_skills:
                    st.write(f"- Learn {skill} from [Coursera](https://www.coursera.org), [Udemy](https://www.udemy.com), or [edX](https://www.edx.org).")

if __name__ == "__main__":
    main()
