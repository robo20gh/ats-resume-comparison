import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf

from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Pass a prompt to Gemini and returns the response
def get_gemini_response(input):
    model = genai.GenerativeModel(
        model_name = "gemini-2.0-flash-exp",
    )
    response = model.generate_content(input)
    return response.text

# Convert a PDF to text
def input_pdf_text(file):
    reader = pdf.PdfReader(file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text


# Create an input prompt to pass to Gemini
cto_input_prompt = """As a skilled ATS equipped with a profound understanding of technology leadership, your task is to rigorously evaluate a given resume against a specific job description (JD). Please provide the following outputs in a concise and structured format:

1. **Match Percentage**: Calculate and present the percentage indicating how well the resume aligns with the JD based on key skills, qualifications, and relevant experience.

2. **Strengths Summary**: Craft a detailed summary highlighting the key strengths of the resume that directly correlate with the JD requirements, focusing on technical and leadership competencies.

3. **Missing Keywords**: Identify and list crucial industry-specific keywords and phrases that are notably absent from the resume but are essential for meeting the JD criteria.

4. **Actionable Improvements**: Provide a targeted list of actionable recommendations to enhance the resume, aimed at increasing its alignment with the JD and boosting the match percentage.

5. **ATS Readability Assessment**: Evaluate how well the resume is likely to be processed by an automated ATS, considering factors such as formatting, keyword placement, and overall clarity, to maximize the applicant's visibility in ATS scans.

6. **Cover Letter Suggestion**: Customize the provided cover letter. This letter should emphasize the applicant's suitability for the role by highlighting their relevant experiences and qualifications in relation to the most critical elements of the JD.

Remember to adopt a tone that reflects both professionalism and relatability throughout your response. Your expertise in technology leadership should inform your evaluations and suggestions, ensuring they are aligned with current industry standards.

resume={resume}

role_description={role_description}

cover_letter={cover_letter}"""
chemistry_input_prompt = """Your task is to simulate a skilled Application Tracking System (ATS) that specializes in evaluating resumes for physical sciences internships. Please analyze the provided resume in relation to the attached internship description and deliver the following insights:

1. **Match Evaluation:** Calculate and report the overall match percentage between the resume and the internship description, explaining the criteria used in your assessment.

2. **Strengths Summary:** Identify and summarize the key strengths of the resume as they align with the specific requirements and qualifications outlined in the internship description. Highlight any relevant academic achievements, technical skills, projects, or experiences.

3. **Keyword Analysis:** Generate a list of critical keywords and phrases from the internship description that are absent from the resume. Focus on technical terminology, skills, and competencies that are essential for the role.

4. **Actionable Improvements:** Recommend at least five actionable strategies to enhance the resume's alignment with the internship. These should focus on incorporating relevant experiences, emphasizing appropriate skills, and using targeted language that resonates with the internship's requirements.

5. **ATS Readability Assessment:** Evaluate the resume's structure and format to determine how effectively it would be parsed by an automated ATS. Provide insights into any formatting issues, layout concerns, or content organization that could hinder visibility in applicant tracking systems, along with tips for optimizing the resume for better recognition.

resume={resume}

role_description={role_description}"""


# Some initial page config to set a title and increase the width
st.set_page_config(page_title="Resume/Job Description Comparison Tool", layout="wide", )

# Page header, description, and disclaimer
st.title("Resume/Job Description Comparison Tool")
st.caption("Improve your ATS resume score match while creating a cover letter to consider using.")
st.caption("Important Note: This application is experimental.  The creator and contributors accept no liability for the accuracy of the app or its behavior.  This application is provided &quot;as-is&quot; without any guarantees or warranties. The programmer is not responsible for any damage, loss of data, or any other negative consequences that may arise from using this software. Use at your own risk.  No data is stored or retained by the creator of the app.  Please refer to Gemini's privacy policy for detailed information about data retention.")

# Start the Inputs section
st.header("Inputs")

# Add a select box that allows the user to choose which type of role they are comparing.
# The main point here is to control which prompt is used in the query to Gemini.
application_type = st.selectbox(
    "What kind of role are you applying for?", 
    ("Chief Technology Officer", "Chemistry Internship")
)

# Based on the selected role, set some variables that will control page labels and whether or not a cover letter should be required.
role_description = ""
show_coverletter = False
prompt = ""

if application_type == "Chief Technology Officer":
    role_description = "job description"
    show_coverletter = True
    prompt = cto_input_prompt
else:
    role_description = "internship description"
    show_coverletter = False
    prompt = chemistry_input_prompt

# Add an expander to allow the user to view and potentially edit the prompt template
with st.expander("If interested, click to see and customize the exact AI prompt"):
    customized_prompt = st.text_area(
        "The following is the actual prompt that will be sent to Gemini.  Feel free to customize it, but remember that the default prompt is probably pretty good:", 
        value = prompt,
        height = 300
    )

# Add a text area for the user to paste the job description into
job_desc_text = st.text_area("Paste the {type} here:".format(type = role_description))

# Add the inputs for file uploading in two columns
col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("Upload your resume:", type="pdf", help="Please upload your resume in PDF format.")

if show_coverletter == True:
    with col2:
        uploaded_cover_letter = st.file_uploader("Upload a cover letter that we can customize:", type="pdf", help="Please upload your template cover letter in PDF format.")

# Add a submit button
submit = st.button("Analyze the Resume")

# When the submit button is clicked, send the prompt to Gemini.
if submit:
    # Make sure that the required inputs have been provided, otherwise show an error
    if job_desc_text is not None and (show_coverletter == False or uploaded_cover_letter is not None) and uploaded_file is not None:
        # Add a spinner so that the user knows that the page is working and not hung up.
        with st.spinner("Your resume is being compared to the {type}.  This may take 30 seconds or longer depending on the size of the resume you submitted.".format(type = role_description)):
            # Get the resume text out of the PDF
            resume_text = input_pdf_text(uploaded_file)
            
            # Get the cover letter text out of the PDF, but only if the cover letter upload control was present
            cover_letter_example = ""
            if show_coverletter == True:
                cover_letter_example = input_pdf_text(uploaded_cover_letter)
            
            # Build the final prompt
            input = customized_prompt.format(resume=resume_text, role_description=job_desc_text, cover_letter=cover_letter_example)
            
            # Send the prompt to Gemini and output the response
            response = get_gemini_response(input)
            st.subheader(response)
    else:
        st.error("Please provide a job description, a resume, and a cover letter.")