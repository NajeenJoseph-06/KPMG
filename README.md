# AI English Compliance Checker

## 1. Project Overview

### 1.1 Purpose
The **AI English Compliance Checker** is a web-based application designed to help users ensure their documents adhere to English writing guidelines. It analyzes uploaded documents (**PDF, DOCX, or DOC**) for:
- Grammar mistakes
- Passive voice overuse
- Clarity issues
- Adherence to formal writing guidelines
- Sentence structure problems  

The app provides a **detailed compliance report** and suggests modifications to improve the document if necessary.

### 1.2 Key Features
- **File Upload:** Supports **PDF, DOCX, and DOC** file formats.
- **Text Extraction:** Extracts text from uploaded documents.
- **Compliance Analysis:** Uses AI to analyze the document for English writing compliance.
- **Content Modification:** Provides AI-generated suggestions to correct issues found in the document.
- **User-Friendly Interface:** Built using **Streamlit**, offering an intuitive and interactive experience.
- **File Management:** Automatically cleans up user files older than 1 hour to manage storage.
- **Handling Large Files:** Efficiently processes large documents using text chunking, pagination for PDFs, and a **10 MB file size limit**.

### 1.3 Target Audience
- Writers, editors, and content creators.
- Professionals who need to ensure their documents adhere to formal writing standards.
- Organizations requiring compliance checks for internal or external documents.

## 2. Technical Architecture

### 2.1 Technology Stack
- **Frontend:** Streamlit (Python-based web framework).
- **Backend:** Python.
- **Text Extraction Libraries:**
  - `pdfplumber` for **PDF** files.
  - `python-docx` for **DOCX** files.
  - `tika` for **DOC** files.
- **AI Model:** Groq API (using the `mixtral-8x7b-32768` model).
- **Environment Management:** `dotenv` for loading environment variables.
- **File Management:** `UUID` for unique user directories, `os` for file operations.
- **Scheduling:** `schedule` and `threading` for background cleanup tasks.

### 2.2 Workflow
1. **User Uploads a Document:** PDF, DOCX, or DOC file.
2. **File Size Check:** Rejects files larger than **10 MB**.
3. **Text Extraction:** Extracts text using appropriate libraries.
4. **Text Chunking:** Splits text into **4000-character** chunks.
5. **Compliance Analysis:** Uses Groq API to analyze each chunk.
6. **Report Generation:** Combines compliance reports and displays results.
7. **Content Modification (Optional):** AI-generated corrections.
8. **File Cleanup:** Deletes files older than **1 hour** to manage storage.

## 3. Key Components

### 3.1 File Upload and Text Extraction
- **File Uploader:** Accepts **PDF, DOCX, or DOC** files.
- **File Size Limit:** Rejects files larger than **10 MB**.
- **Text Extraction:**
  - **PDF:** `pdfplumber` extracts text page by page.
  - **DOCX:** `python-docx` extracts text from paragraphs.
  - **DOC:** `tika` extracts text.

### 3.2 Text Chunking
- **Chunk Size:** **4000 characters** per chunk.
- **Benefits:**
  - Ensures full document analysis.
  - Avoids exceeding API token limits.
  - Improves performance by processing smaller sections.

### 3.3 Compliance Analysis
- **Prompt Template:** Guides AI to check for grammar, clarity, passive voice, etc.
- **Groq API:** Processes each chunk and generates a compliance report.

### 3.4 Content Modification
- **Modification Prompt:** AI suggests corrections based on compliance issues.
- **Groq API:** Generates corrected text and displays it to the user.

### 3.5 File Management
- **User Directory:** Each user gets a unique directory.
- **Metadata Tracking:** Tracks file creation time.
- **Cleanup Scheduler:** Deletes files older than **1 hour**.

## 4. Handling Large Files

### 4.1 File Size Limit
- **Limit:** Files larger than **10 MB** are rejected.
- **Purpose:** Ensures smooth operation and prevents performance issues.

### 4.2 Text Chunking
- **Chunk Size:** **4000 characters** per chunk.
- **Process:**
  - Splits extracted text into chunks.
  - Processes each chunk individually via Groq API.
  - Combines compliance reports for final display.
- **Benefits:**
  - Efficient large document handling.
  - Avoids exceeding API token limits.
  - Ensures complete document analysis.

### 4.3 Pagination for PDFs
- **Process:** Extracts text **page by page** using `pdfplumber`.
- **Benefits:**
  - Reduces memory usage.
  - Handles multi-page PDFs efficiently.

### 4.4 Progress Feedback
- **Feature:** Real-time feedback during text extraction, analysis, and modification.
- **Implementation:** Displays a progress message for each chunk.
- **Benefits:**
  - Improves user experience.
  - Provides transparency during processing.

## 5. Installation and Setup

### 5.1 Prerequisites
- Python **3.8 or higher**.
- Install required libraries:
  ```sh
  pip install streamlit pdfplumber python-docx tika langchain-groq python-dotenv schedule streamlit langchain-community
  ```

### 5.2 Environment Setup
1. Create a `.env` file in the project directory:
   ```sh
   GROQ_API_KEY=your_groq_api_key
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

### 5.3 Running the Application
1. Navigate to the project directory.
2. Run the Streamlit app:
   ```sh
   streamlit run English_compliance_checker_final.py
   ```
3. Access the app in your browser at `http://localhost:8501`.

## 6. Usage Instructions

### 6.1 Uploading a Document
- Click **"Upload your document"**.
- Select a **PDF, DOCX, or DOC** file.

### 6.2 Analyzing Compliance
- Click **"Analyze Compliance"**.
- The app extracts text and performs compliance analysis.
- A **compliance report** is displayed.

### 6.3 Modifying Content
- If issues are found, click **"Modify"**.
- The AI generates corrected text.
- The modified content can be **downloaded as a TXT file**.

### 6.4 Clearing/Exiting
- Click **"Clear / Exit"** to reset the app and start over.

## 7. Limitations and Future Improvements

### 7.1 Limitations
- **API Rate Limits:** Groq API may impose rate limits.
- **Performance:** Large files may take time to process, despite chunking.

### 7.2 Future Improvements
- **Dynamic Chunk Size:** Adjust chunk size dynamically based on API token limits.
- **Asynchronous Processing:** Use async API calls for better performance.
- **Enhanced UI:** Add progress bars and improve UI/UX.
- **More File Formats:** Add support for **TXT, ODT**, and other formats.

## 8. Maintenance and Support

### 8.1 File Cleanup
- Deletes files older than **1 hour** to manage storage.
- Cleanup task runs in the background **every hour**.

### 8.2 Error Handling
- Error handling for **text extraction, API calls, and file operations**.
- Users receive **Streamlit error messages** when issues occur.

### 8.3 Logging
- Track **user activity, errors, and system performance**.
- Store logs in a file or send to a monitoring system.

## 9. Conclusion
The **AI English Compliance Checker** is a powerful tool for ensuring documents adhere to English writing standards. With planned enhancements, it will handle **larger documents** and provide even more robust compliance analysis.


Content Modification: Provides AI-generated suggestions to correct issues found in the document. 

User-Friendly Interface: Built using Streamlit, offering an intuitive and interactive experience. 

File Management: Automatically cleans up user files older than 1 hour to manage storage. 

Handling Large Files: Efficiently processes large documents using text chunking, pagination for PDFs, and a 10 MB file size limit
