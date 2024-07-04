from flask import Flask, render_template, request
from dotenv import load_dotenv
import os, google.generativeai as genai, PyPDF2 as pdf

app=Flask(__name__)
load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

input_prompt1 = """
You are an experienced Technical Human Resource Manager,your task is to review the provided resume against the job description. 
Please share your detailed professional evaluation in 300 words or more on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
job description:{jd}
resume:{text}
"""

input_prompt2 = """
You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of ATS functionality, 
your task is to evaluate the resume against the provided job description. Always give the percentage of match if the resume matches
the job description and also 300 words or more detailed analysis.
job description:{jd}
resume:{text}
"""

input_prompt3 = """
You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of ATS functionality, 
your task is to evaluate the resume against the provided job description.
Give the keywords missing, detailed analysis and last final thoughts in 300 words or more.
job description:{jd}
resume:{text}
"""


def get_gemini_response(input_prompt):
    model=genai.GenerativeModel('gemini-pro')
    response=model.generate_content(input_prompt)
    return response.text

def input_pdf_text(pdf_file):
    reader=pdf.PdfReader(pdf_file)
    text=""
    for page in range(len(reader.pages)):
        page=reader.pages[page]
        text+=str(page.extract_text())
    return text

def convert_markdown_to_html(text):
    import re
    formatted_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    formatted_text = formatted_text.replace('\n', '<br>')
    return formatted_text

@app.route('/predict',methods=['POST'])
def predict_ats_score():
    pdf_file=request.files['pdf_file']
    text=input_pdf_text(pdf_file)
    button_pressed = request.form.get('button')
    jd=request.form.get('input_jd')
    input_question=request.form.get('input_question')
    prompt=""
    if button_pressed == 'abt_resume':
        prompt=input_prompt1.format(jd=jd,text=text)
    elif button_pressed == 'resume_score':
        prompt=input_prompt2.format(jd=jd,text=text)
    elif button_pressed == 'improve':
        prompt=input_prompt3.format(jd=jd,text=text)
    else :
        input_question+="resume: {text} jd: {jd}"
        prompt=input_question.format(jd=jd,text=text)
    response=get_gemini_response(prompt)
    response=convert_markdown_to_html(response)
    return render_template('index.html',result=response)

@app.route('/')
def index():
    return render_template('index.html')

if __name__=='__main__':
    app.run(debug=False,host="0.0.0.0")