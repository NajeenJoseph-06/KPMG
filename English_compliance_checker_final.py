
import streamlit as st
import pdfplumber
from docx import Document
from tika import parser
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import os
import uuid
import time
import schedule
import threading
import json
from datetime import datetime

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize session state variables
if "document_text" not in st.session_state:
    st.session_state.document_text = None
if "compliance_report" not in st.session_state:
    st.session_state.compliance_report = None
if "modified_content" not in st.session_state:
    st.session_state.modified_content = None
if "show_modify_ui" not in st.session_state:
    st.session_state.show_modify_ui = False
if "modify_clicked" not in st.session_state:
    st.session_state.modify_clicked = False
if "analyze_complete" not in st.session_state:
    st.session_state.analyze_complete = False
if "user_dir" not in st.session_state:
    unique_id = str(uuid.uuid4())  # Generate a unique ID for the user
    st.session_state.user_dir = f"user_files/{unique_id}"
    os.makedirs(st.session_state.user_dir, exist_ok=True)  # Create user directory

# Metadata file to track file creation times
METADATA_FILE = os.path.join("user_files", "metadata.json")

# Function to load metadata
def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    return {}

# Function to save metadata
def save_metadata(metadata):
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f)

# Function to clean up user files older than 1 hour
def cleanup_old_files():
    """Delete files older than 1 hour."""
    metadata = load_metadata()
    current_time = time.time()
    for user_id, file_data in list(metadata.items()):
        if current_time - file_data["timestamp"] > 3600:  # 1 hour in seconds
            user_dir = os.path.join("user_files", user_id)
            if os.path.exists(user_dir):
                for file in os.listdir(user_dir):
                    os.remove(os.path.join(user_dir, file))
                os.rmdir(user_dir)
                del metadata[user_id]
                save_metadata(metadata)
                print(f"Deleted files for user {user_id}")

# Schedule cleanup task to run every hour
def schedule_cleanup():
    schedule.every().hour.do(cleanup_old_files)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start the cleanup scheduler in a separate thread
if not hasattr(st.session_state, "cleanup_thread"):
    cleanup_thread = threading.Thread(target=schedule_cleanup, daemon=True)
    cleanup_thread.start()
    st.session_state.cleanup_thread = cleanup_thread

# Function to clean up user files
def cleanup_user_files():
    """Delete all files in the user's directory."""
    if os.path.exists(st.session_state.user_dir):
        for file in os.listdir(st.session_state.user_dir):
            os.remove(os.path.join(st.session_state.user_dir, file))
        os.rmdir(st.session_state.user_dir)  # Remove the directory itself

# Function to reset session state and refresh the page
def reset_app():
    """Reset the app and refresh the page."""
    cleanup_user_files()  # Delete user files
    st.session_state.clear()  # Clear all session state variables
    st.rerun()  # Refresh the page

# Streamlit page setup
st.set_page_config(page_title="📄 AI English Compliance Agent", layout="wide")
st.title("📄 AI English Compliance Checker")
st.write("Upload a **PDF, DOCX, or DOC** file, and the AI will check if it follows English writing guidelines.")

# File uploader
uploaded_file = st.file_uploader("Upload your document", type=["pdf", "docx", "doc"])

# Set a file size limit (e.g., 10 MB)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Function to extract text
def extract_text(file):
    try:
        if file.size > MAX_FILE_SIZE:
            st.error("File size exceeds the limit of 10 MB. Please upload a smaller file.")
            return None

        if file.name.endswith(".pdf"):
            with pdfplumber.open(file) as pdf:
                text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        elif file.name.endswith(".docx"):
            doc = Document(file)
            text = "\n".join([para.text for para in doc.paragraphs])
        else:  # DOC files
            parsed = parser.from_buffer(file)
            text = parsed["content"].strip() if parsed["content"] else None
        return text
    except Exception as e:
        st.error(f"Error extracting text: {e}")
        return None

# Function to split text into chunks
def split_text_into_chunks(text, chunk_size=4000):
    """Split text into smaller chunks for processing."""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# Agent to analyze compliance
def analyze_compliance(text):
    """AI-based compliance analysis."""
    prompt_template = PromptTemplate(
        input_variables=["document_text"],
        template="""
        You are an AI expert in English guidelines compliance. Analyze the document for:
        - Grammar mistakes
        - Passive voice overuse
        - Clarity issues
        - Adherence to formal writing guidelines
        - Sentence structure problems
        Return a structured compliance report highlighting any mistakes found.
        Document Text:
        {document_text}
        """
    )

    try:
        llm = ChatGroq(api_key=GROQ_API_KEY, model="mixtral-8x7b-32768", temperature=0.0)
        chain = LLMChain(llm=llm, prompt=prompt_template)
        response = chain.run(document_text=text)
        return response
    except Exception as e:
        st.error(f"Groq API Error: {e}")
        return None
    
def calculate_compliance_score(compliance_report):
    """Calculate compliance score based on the number of errors found in the compliance report."""
    
    weights = {
        "grammar mistakes": 3,
        "passive voice": 2,
        "clarity issues": 3,
        "formal writing adherence": 2,
        "sentence structure": 2
    }

    total_possible_score = sum(3 * weight for weight in weights.values())  # Max severity (3) * weight sum
    total_severity_weight = 0

    # Count occurrences of each error type in the compliance report
    for key, weight in weights.items():
        count = compliance_report.lower().count(key)  # Case-insensitive counting
        severity = 3 if "high" in key else 2  # Assign severity dynamically
        total_severity_weight += count * severity * weight

    compliance_score = 100 - ((total_severity_weight / total_possible_score) * 100)
    return max(0, round(compliance_score, 2))  # Ensure score is not negative


# Agent to modify content based on compliance report
def modify_content(text, compliance_report):
    """AI-based content modification."""
    prompt_template = PromptTemplate(
        input_variables=["document_text", "compliance_report"],
        template="""
        You are an AI expert in English writing. Modify the following document to correct the issues found in the compliance report.
        Ensure the modified content is clear, grammatically correct, and adheres to formal writing guidelines.
        Return ONLY the corrected document text. Do not include any additional explanations or headers.
        Compliance Report:
        {compliance_report}
        Document Text:
        {document_text}
        """
    )

    try:
        llm = ChatGroq(api_key=GROQ_API_KEY, model="mixtral-8x7b-32768", temperature=0.0)
        chain = LLMChain(llm=llm, prompt=prompt_template)
        response = chain.run(document_text=text, compliance_report=compliance_report)
        return response
    except Exception as e:
        st.error(f"Groq API Error: {e}")
        return None

# Process uploaded file
if uploaded_file:
    with st.spinner("Extracting text..."):
        if st.session_state.document_text is None:  # Prevent re-extraction on reruns
            st.session_state.document_text = extract_text(uploaded_file)

    if st.session_state.document_text:
        st.subheader("📜 Extracted Text Preview")
        st.text_area("Extracted Content", st.session_state.document_text[:1000] + "...", height=200, disabled=True)

        # Show Analyze button only if analysis is not complete
        if not st.session_state.analyze_complete:
            if st.button("Analyze Compliance"):
                with st.spinner("Analyzing document..."):
                    # Split text into chunks and process each chunk
                    chunks = split_text_into_chunks(st.session_state.document_text)
                    compliance_reports = []
                    for i, chunk in enumerate(chunks):
                        st.write(f"Processing chunk {i + 1} of {len(chunks)}...")
                        report = analyze_compliance(chunk)
                        if report:
                            compliance_reports.append(report)
                    st.session_state.compliance_report = "\n\n".join(compliance_reports)
                    st.session_state.show_modify_ui = False
                    st.session_state.modify_clicked = False
                    st.session_state.analyze_complete = True

                    # Save compliance report to a file
                    report_filename = os.path.join(st.session_state.user_dir, "compliance_report.txt")
                    with open(report_filename, "w") as report_file:
                        report_file.write(st.session_state.compliance_report)

                    # Update metadata with file creation time
                    metadata = load_metadata()
                    metadata[st.session_state.user_dir] = {"timestamp": time.time()}
                    save_metadata(metadata)

                    st.subheader("✅ Compliance Report")
                    st.write(st.session_state.compliance_report)

                    if st.session_state.compliance_report:
                        st.session_state.compliance_score = calculate_compliance_score(st.session_state.compliance_report)

                        st.subheader("📊 Compliance Score")
                        st.write(f"Overall Compliance Score: **{st.session_state.compliance_score}%**")    

                    # If issues are found, show modify option
                    if "mistakes found" in st.session_state.compliance_report.lower() or "issues" in st.session_state.compliance_report.lower():
                        st.session_state.show_modify_ui = True

        # Show Modify and Clear/Exit buttons only if analysis is complete and modify is not clicked
        if st.session_state.show_modify_ui and not st.session_state.modify_clicked:
            col1, col2 = st.columns(2)

            with col1:
                if st.button("Modify"):
                    st.session_state.modify_clicked = True
                    with st.spinner("Modifying document..."):
                        modified_content = modify_content(st.session_state.document_text, st.session_state.compliance_report)
                        if modified_content:
                            st.session_state.modified_content = modified_content

                            # Save modified content to a file
                            modified_filename = os.path.join(st.session_state.user_dir, "modified_document.txt")
                            with open(modified_filename, "w") as modified_file:
                                modified_file.write(modified_content)
                            st.success(f"Modified content saved to {modified_filename}")

                            st.subheader("✍️ Modified Content")
                            st.write(modified_content)

                            # Download button for the modified file
                            with open(modified_filename, "rb") as file:
                                st.download_button(
                                    label="📥 Download Modified Document (TXT)",
                                    data=file,
                                    file_name="modified_document.txt",
                                    mime="text/plain"
                                )

            with col2:
                if st.button("Clear / Exit", key="clear_exit_modify"):
                    reset_app()
