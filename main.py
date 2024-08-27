import streamlit as st
from dotenv import load_dotenv
import os
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
import base64
import PyPDF2

# Load environment variables
load_dotenv()
api_key = os.getenv('groq_api_key')

# Initialize the Groq model
model = ChatGroq(api_key='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', model_name='llama3-8b-8192')
parser = StrOutputParser()

def generate_questions(content, question_type):
    template = """
As an expert in educational content creation, generate a set of {question_type} questions related to the following content:

- **Content:** {content}

Provide the results in the following structured format:
----------------------------------------------------
Multiple Choice Questions (MCQ):
----------------------------------------------------
1: [Question]

[A]

[B]

[C]

[D]

Answer: [A]

----------------------------------------------------
Short Answer Questions (Short Q/A):
----------------------------------------------------
1: [Question]
Answer: [Answer in paragraph]
----------------------------------------------------

----------------------------------------------------
Long Answer Questions (Long Q/A):
----------------------------------------------------
1: [Question]
Answer: [Answer in detailed paragraph]
----------------------------------------------------

Ensure that the output is well-organized and easy to understand.
    """
    prompt = PromptTemplate.from_template(template=template)
    chain = prompt | model | parser

    content_payload = {"content": content, "question_type": question_type}
    result = chain.invoke(content_payload)
    return result

def pdftotext(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ''
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def set_background(image_path):
    # Encode the image to base64
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    # CSS to set the background image
    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded_string}");
        background-repeat: no-repeat;
        background-size: cover;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Streamlit Initialization
if "generated_content" not in st.session_state:
    st.session_state.generated_content = None
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

# Set the background image
set_background('login.jpeg')  # Update this path with your local image file

# Streamlit app
st.title("EduQuest")

# Source selection
source_type = st.radio("Select Content Source:", ["PDF File", "Web Content"])
question_type = st.selectbox("Select Question Type:", ["MCQ", "Short Q/A", "Long Q/A"])

content = ""
if source_type == "PDF File":
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    if uploaded_file is not None:
        content = pdftotext(uploaded_file)
        st.write("PDF content:")
        st.write(content)
elif source_type == "Web Content":
    content = st.text_area("Enter a topic:")

if content and st.button("Generate Content"):
    with st.spinner("Generating questions and exam details..."):
        try:
            generated_content = generate_questions(content, question_type)
            st.session_state.generated_content = generated_content
            st.session_state.show_answer = (question_type == "MCQ")
            st.success("Content generated successfully!")
        except Exception as e:
            st.error(f"An error occurred: {e}")

if st.session_state.generated_content:
    st.write("### Generated Content")
    st.write(st.session_state.generated_content)
