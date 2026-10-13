# ResearchMate AI

**ResearchMate AI** is a Streamlit-based research paper assistant. Users can upload a PDF research paper, generate an AI-powered summary, download the summary as a PDF, and ask questions about the paper through a chat interface.

> **Project type:** MCA AI Final-Year Project  
> **Interface:** Streamlit web application  
> **AI service:** Google Gemini API

## Features

- **PDF upload:** Upload a research paper in PDF format.
- **Text extraction:** Extract selectable text from PDF pages using PyMuPDF.
- **AI-generated summary:** Create a structured summary with:
  - Objective
  - Methodology
  - Main Findings
  - Limitations
  - Conclusion
- **Download summary:** Export the generated summary as a PDF file.
- **Question-answer chat:** Ask questions about the uploaded research paper.
- **PDF-aware session reset:** When a different PDF is uploaded, the app resets the previous summary and chat.
- **Model discovery:** The app checks the Gemini models available to the configured API key and looks for models supporting `generateContent`.
- **Error handling:** Displays useful messages when PDF extraction or an AI request fails.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | Web interface and interactive controls |
| Google Gen AI SDK | Connects the app to Gemini models |
| Gemini API | Generates summaries and answers questions |
| PyMuPDF (`pymupdf`) | Extracts text from PDF documents |
| python-dotenv | Loads the API key from a local `.env` file |
| ReportLab | Creates the downloadable summary PDF |
| `hashlib` | Detects when the uploaded PDF changes |
| `BytesIO` | Keeps the generated PDF in memory before download |

## Project Structure

Create your project folder with this structure:

```text
ResearchMate-AI/
├── app.py
├── requirements.txt
├── README.md
├── .env
└── .gitignore
```

- `app.py` — the Streamlit application code.
- `requirements.txt` — Python packages needed to run the application.
- `README.md` — project documentation.
- `.env` — your private Gemini API key; do not share or upload this file.
- `.gitignore` — prevents private files and generated clutter from being committed to Git.

## Prerequisites

Before starting, install:

1. Python 3.10 or newer (a currently supported Python version is recommended).
2. Visual Studio Code or another code editor.
3. An internet connection for Gemini API requests.
4. A Gemini API key from Google AI Studio, subject to Google's current availability, usage limits, and terms.

Check that Python and pip are available in your terminal:

```bash
python --version
python -m pip --version
```

## Installation and Setup

### 1. Open the project folder

Open the `ResearchMate-AI` folder in VS Code. Make sure `app.py` and `requirements.txt` are in the same folder.

### 2. Create a virtual environment (recommended)

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

If PowerShell blocks activation, you can use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install the dependencies

Run this command in the project terminal:

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a file named `.env` in the same folder as `app.py`.

Add this line to `.env`:

```dotenv
GEMINI_API_KEY=put_your_own_api_key_here
```

Replace the example value with your own API key. Do not add quotation marks unless required by your environment, and do not put the key directly into `app.py`.

**Security reminders:**
- Never publish your `.env` file.
- Never share screenshots or messages that reveal the key.
- If a key is accidentally exposed, revoke it and create a replacement.
- Do not commit API keys to GitHub.
- If deploying the app, configure the key using the hosting platform's secrets or environment-variable settings.

### 5. Create `.gitignore`

Create a `.gitignore` file in the project folder with:

```gitignore
.env
.venv/
__pycache__/
*.py[cod]
.streamlit/secrets.toml
```

This helps prevent private keys and local environment files from being committed. Always review files before pushing to a public repository.

### 6. Run the application

From the project folder, with the virtual environment activated, run:

```bash
python -m streamlit run app.py
```

Streamlit normally opens the application in your browser. If it does not, open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## How to Use ResearchMate AI

1. Start the application.
2. Use the sidebar to upload a research paper in PDF format.
3. Wait for the PDF text to be extracted.
4. Click **Generate Summary**.
5. Read the generated summary in the application.
6. Click **Download Summary as PDF** to save the summary.
7. Enter a question in the chat box, such as:
   - What is the main objective of this research paper?
   - Which methodology does the paper use?
   - What are the main findings?
   - What limitations are mentioned by the authors?
8. Upload another PDF to start a new paper-specific summary and chat.

## Troubleshooting

### API key missing

- Confirm that `.env` is in the same folder as `app.py`.
- Check that the variable is named exactly `GEMINI_API_KEY`.
- Restart Streamlit after changing environment configuration.
- Never paste the API key into public issue reports or screenshots.

### Model not found or unsupported

The available models depend on the API key, account, region, and current Google API support. The app attempts to discover models that advertise `generateContent` support, but discovery does not guarantee that every model is usable for every account or request. Review the current Gemini API documentation and the error returned by the service.

### `503 UNAVAILABLE`

This usually indicates temporary service unavailability or high demand. Try again later. The application retries some temporary errors and may try another discovered model, but it cannot guarantee service availability.

### `429 RESOURCE_EXHAUSTED`

This may indicate a rate limit or quota restriction. Check the API project's current quota and usage limits, wait if appropriate, and retry according to the service guidance.

### PDF has no readable text

Some PDFs are scanned images rather than text-based documents. The current application extracts embedded/selectable text and does **not** include OCR. Use a text-based PDF or add an OCR pipeline in a future version.

### Download does not work

Check the browser's downloads list and its download settings. If a third-party download manager intercepts the download, temporarily disable its browser integration or use the browser's built-in download handling.

### Package installation fails

- Confirm that the correct Python version is active.
- Activate `.venv` before installing packages.
- Run `python -m pip install --upgrade pip`.
- Then run `python -m pip install -r requirements.txt` again.

## Limitations

- Only PDF uploads are accepted by the current interface.
- The application extracts text; scanned PDFs may require OCR.
- The current code sends up to the first 30,000 characters of extracted text to the model. Important content later in a long paper may be omitted.
- Model responses can contain mistakes or omit relevant details. Verify important claims against the original paper.
- Answers and summaries depend on the quality of the extracted text and the model's availability.
- Gemini API access may have quotas, rate limits, costs, and regional or model restrictions.
- The current PDF export uses standard ReportLab fonts, so some Unicode characters may be replaced.
- This is a project/demo application, not a substitute for reading the original research paper or for expert review.
- The app does not currently provide user authentication, persistent database storage, or OCR.

## Privacy and Responsible Use

- Upload only documents you are allowed to process.
- Review the API provider's current privacy terms and data-handling policies before sending confidential or unpublished research.
- Keep API credentials private.
- Check AI-generated summaries and answers against the original source before using them in academic work.
- Do not present generated text as a substitute for proper citation or academic integrity.

## Future Enhancements

- OCR support for scanned PDFs.
- Page-aware citations and source excerpts in answers.
- Support for multiple papers and document formats.
- More robust chunking and retrieval for long papers.
- Chat history export and session persistence.
- Improved PDF formatting and Unicode font support.
- User authentication and secure deployment.
- Automated tests and logging.

## Author / Academic Details

- **Project:** ResearchMate AI
- **Program:** MCA AI
- **Institution:** Add your institution's official name
- **Student:** Add your name
- **Academic year:** Add your academic year

## License

Add a license if you plan to distribute the project publicly. If this is an academic submission, follow your institution's rules for source-code sharing and attribution.
