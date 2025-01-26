import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf

from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# gemini function
def get_gemini_response(input):
    model = genai.GenerativeModel(
        model_name = "gemini-2.0-flash-exp",
    )
    response = model.generate_content(input)
    return response.text

# convert a pdf to text
def input_pdf_text(file):
    reader = pdf.PdfReader(file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text


# create an input prompt to pass to Gemini
input_prompt = """
As a skilled ATS equipped with a profound understanding of technology leadership, your task is to rigorously evaluate a given resume against a specific job description (JD). Please provide the following outputs in a concise and structured format:

1. **Match Percentage**: Calculate and present the percentage indicating how well the resume aligns with the JD based on key skills, qualifications, and relevant experience.

2. **Strengths Summary**: Craft a detailed summary highlighting the key strengths of the resume that directly correlate with the JD requirements, focusing on technical and leadership competencies.

3. **Missing Keywords**: Identify and list crucial industry-specific keywords and phrases that are notably absent from the resume but are essential for meeting the JD criteria.

4. **Actionable Improvements**: Provide a targeted list of actionable recommendations to enhance the resume, aimed at increasing its alignment with the JD and boosting the match percentage.

5. **ATS Readability Assessment**: Evaluate how well the resume is likely to be processed by an automated ATS, considering factors such as formatting, keyword placement, and overall clarity, to maximize the applicant's visibility in ATS scans.

6. **Cover Letter Suggestion**: Customize the provided cover letter. This letter should emphasize the applicant's suitability for the role by highlighting their relevant experiences and qualifications in relation to the most critical elements of the JD.

Remember to adopt a tone that reflects both professionalism and relatability throughout your response. Your expertise in technology leadership should inform your evaluations and suggestions, ensuring they are aligned with current industry standards.

text={text}

jd={jd}

cover_letter={cover_letter}

"""


# some initial page config to set a title and increase the width
st.set_page_config(page_title="Resume/Job Description Comparison Tool", layout="wide", )

# streamlit
st.title("Resume/Job Description Comparison Tool")
st.caption("Improve your ATS resume score match while creating a cover letter to consider using.")
st.caption("Important Note: this application is experimental.  The creator and contributors accept no liability for the accuracy of the app or its behavior.  This application is provided &quot;as-is&quot; without any guarantees or warranties. The programmer is not responsible for any damage, loss of data, or any other negative consequences that may arise from using this software. Use at your own risk.  No data is stored or retained by the creator of the app.  Please refer to Gemini's privacy policy for detailed information about data retention.")

# form inputs for the job description, the resume uploader, the cover letter uploader, and the submit button
st.header("Inputs")
job_desc = st.text_area("Paste the job description here:")

# put the inputs for file uploading in two columns
col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("Upload your resume:", type="pdf", help="Please upload your resume in PDF format.")
with col2:
    uploaded_cover_letter = st.file_uploader("Upload a cover letter that we can customize:", type="pdf", help="Please upload your template cover letter in PDF format.")

submit = st.button("Analyze the Resume")

# as long as a resume has been uploaded, 
if submit:
    if job_desc is not None and uploaded_cover_letter is not None and uploaded_file is not None:
        with st.spinner("Analyzing the resume, please wait a moment..."):
            resume = input_pdf_text(uploaded_file)
            cover_letter_example = input_pdf_text(uploaded_cover_letter)
            input = input_prompt.format(text=resume, jd=job_desc, cover_letter=cover_letter_example)
            response = get_gemini_response(input)
            st.subheader(response)
    else:
        st.error("Please provide a job description, a resume, and a cover letter.")