
import os
import hashlib
import time
from io import BytesIO

import streamlit as st
import pymupdf
from dotenv import load_dotenv
from google import genai
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth


# ---------------------------------------
# 1. Load API key
# ---------------------------------------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


# ---------------------------------------
# 2. Page configuration
# ---------------------------------------
st.set_page_config(
    page_title="ResearchMate AI",
    page_icon="📚",
    layout="wide"
)

st.title("📚 ResearchMate AI")
st.caption("Your AI Research Paper Analysis Assistant")

st.write(
    "Upload a research paper, generate its summary, "
    "create a literature review, download your report, "
    "and ask questions about the paper."
)


# ---------------------------------------
# 3. Check API key
# ---------------------------------------
if not api_key:
    st.error("API key missing. Please check your .env file.")
    st.stop()

client = genai.Client(api_key=api_key)


# ---------------------------------------
# 4. Find supported text-generation models
# ---------------------------------------
@st.cache_data(ttl=300)
def get_text_models():
    models = client.models.list()
    available = []

    for model in models:
        name = getattr(model, "name", "") or ""
        actions = getattr(model, "supported_actions", []) or []

        if (
            name
            and any(
                action.lower() == "generatecontent"
                for action in actions
            )
        ):
            available.append(name.replace("models/", ""))

    preferred = [
        "gemini-3.8-flash",
        "gemini-flash-latest",
        "gemini-3.6-flash",
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash",
    ]

    ordered = [
        name for name in preferred
        if name in available
    ]

    ordered += [
        name for name in available
        if name not in ordered
    ]

    return ordered


# ---------------------------------------
# 5. Generate AI response
# ---------------------------------------
def generate_ai_response(prompt):
    """Try available text models if one is unavailable."""

    models = get_text_models()

    if not models:
        raise RuntimeError(
            "No model supporting generateContent was found. "
            "Check your Gemini API access and available models."
        )

    errors = []

    for model_name in models[:3]:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                answer = response.text

                if answer and answer.strip():
                    return answer.strip()

                raise RuntimeError(
                    "The model returned an empty response."
                )

            except Exception as error:
                message = str(error)
                errors.append(f"{model_name}: {message}")

                temporary = (
                    "503" in message
                    or "UNAVAILABLE" in message
                    or "429" in message
                    or "RESOURCE_EXHAUSTED" in message
                    or "500" in message
                    or "INTERNAL" in message
                )

                if temporary and attempt == 0:
                    time.sleep(2)
                    continue

                recoverable = (
                    temporary
                    or "404" in message
                    or "NOT_FOUND" in message
                    or "400" in message
                    or "INVALID_ARGUMENT" in message
                )

                if recoverable:
                    break

                raise

    raise RuntimeError(
        "No available model completed the request. "
        "Please try again later. Details: "
        + " | ".join(errors[-3:])
    )


# ---------------------------------------
# 6. Upload research paper
# ---------------------------------------
st.sidebar.header("📄 Upload Research Paper")

uploaded_file = st.sidebar.file_uploader(
    "Upload a research paper PDF",
    type=["pdf"]
)

if uploaded_file is None:
    st.info("Please upload a research paper PDF from the sidebar.")
    st.stop()


# ---------------------------------------
# 7. Reset results for a new PDF
# ---------------------------------------
pdf_bytes = uploaded_file.getvalue()
pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()

if st.session_state.get("current_pdf_hash") != pdf_hash:
    st.session_state["current_pdf_hash"] = pdf_hash
    st.session_state["messages"] = []
    st.session_state["summary"] = ""
    st.session_state["literature_review"] = ""


# Initialize session-state values if missing
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "summary" not in st.session_state:
    st.session_state["summary"] = ""

if "literature_review" not in st.session_state:
    st.session_state["literature_review"] = ""


# ---------------------------------------
# 8. Extract text from PDF
# ---------------------------------------
try:
    with pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf"
    ) as pdf:
        pages = []

        for number, page in enumerate(pdf, start=1):
            page_text = page.get_text().strip()

            if page_text:
                pages.append(
                    f"[Page {number}]\n{page_text}"
                )

    paper_text = "\n\n".join(pages)

except Exception as error:
    st.error(f"Could not read PDF: {error}")
    st.stop()


# ---------------------------------------
# 9. Validate extracted text
# ---------------------------------------
if not paper_text.strip():
    st.error(
        "No readable text was found. "
        "This may be a scanned PDF that needs OCR."
    )
    st.stop()

st.success("PDF uploaded and processed successfully!")
st.caption(f"Extracted text from {len(pages)} page(s).")

# Limit context sent to the AI model
paper_context = paper_text[:30000]


# ---------------------------------------
# 10. Generate summary
# ---------------------------------------
st.divider()
st.subheader("📝 Research Paper Summary")

if st.button("Generate Summary", type="primary"):

    summary_prompt = f"""
You are ResearchMate AI, an academic research assistant.

Summarize the research paper under these headings:

1. Objective
2. Methodology
3. Main Findings
4. Limitations
5. Conclusion

Use simple academic English.
Use only information present in the paper.
Do not invent facts, results, or citations.
Mention when information is not available.

Research paper:
{paper_context}
"""

    try:
        with st.spinner("Generating summary..."):
            summary = generate_ai_response(summary_prompt)

        st.session_state["summary"] = summary
        st.success("Summary generated successfully!")

    except Exception as error:
        st.error(f"Summary failed: {error}")


# ---------------------------------------
# 11. Create downloadable summary PDF
# ---------------------------------------
def create_summary_pdf(summary):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    page_width, page_height = A4
    left = 50
    right = page_width - 50
    y = page_height - 55

    def new_page():
        nonlocal y
        pdf.showPage()
        pdf.setFont("Helvetica", 10)
        y = page_height - 50

    def write_line(line, font="Helvetica", size=10):
        nonlocal y

        if y < 55:
            new_page()

        pdf.setFont(font, size)

        safe_line = line.encode(
            "latin-1", errors="replace"
        ).decode("latin-1")

        pdf.drawString(left, y, safe_line)
        y -= size + 6

    write_line("ResearchMate AI", "Helvetica-Bold", 18)
    y -= 8
    write_line("Research Paper Summary", "Helvetica-Bold", 13)
    y -= 12

    for paragraph in summary.splitlines():
        paragraph = paragraph.strip()

        if not paragraph:
            y -= 7
            continue

        safe_paragraph = paragraph.encode(
            "latin-1", errors="replace"
        ).decode("latin-1")

        words = safe_paragraph.split()
        line = ""

        for word in words:
            candidate = f"{line} {word}".strip()

            if stringWidth(
                candidate, "Helvetica", 10
            ) <= right - left:
                line = candidate
            else:
                if line:
                    write_line(line)
                line = word

        if line:
            write_line(line)

        y -= 4

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


# Display summary and download button
if st.session_state.get("summary"):
    st.markdown("### Research Paper Summary")
    st.markdown(st.session_state["summary"])

    try:
        summary_pdf = create_summary_pdf(
            st.session_state["summary"]
        )

        st.download_button(
            label="📥 Download Summary as PDF",
            data=summary_pdf,
            file_name="ResearchMate_Summary.pdf",
            mime="application/pdf",
            key="download_summary_pdf"
        )

    except Exception as error:
        st.error(f"Could not create summary PDF: {error}")


# ---------------------------------------
# 12. Literature Review Generator
# ---------------------------------------
st.divider()
st.subheader("📚 Literature Review Generator")

st.write(
    "Generate an academic literature review draft "
    "based on the uploaded research paper."
)

if st.button("Generate Literature Review"):

    review_prompt = f"""
You are ResearchMate AI, an academic research assistant.

Write a structured literature review draft based ONLY
on the supplied research paper.

Include these headings:

1. Research Background
2. Research Problem
3. Methodology
4. Key Findings
5. Research Limitations
6. Research Gap and Future Scope

Use clear academic English.
Do not invent authors, publication years, citations,
research findings, or unsupported research gaps.
Clearly mention when information is unavailable.
This is a review of one paper, not a complete
multi-paper literature review.

Research paper:
{paper_context}
"""

    try:
        with st.spinner("Generating literature review..."):
            review = generate_ai_response(review_prompt)

        st.session_state["literature_review"] = review
        st.success("Literature review generated successfully!")

    except Exception as error:
        st.error(f"Literature review failed: {error}")


# Display literature review and download button
if st.session_state.get("literature_review"):

    st.markdown("### Generated Literature Review")
    st.markdown(st.session_state["literature_review"])

    st.download_button(
        label="📥 Download Literature Review",
        data=st.session_state["literature_review"],
        file_name="ResearchMate_Literature_Review.txt",
        mime="text/plain",
        key="download_literature_review"
    )


# ---------------------------------------
# 13. Chat with research paper
# ---------------------------------------
st.divider()
st.subheader("💬 Chat with Your Research Paper")

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input(
    "Ask a question about your research paper..."
)

if question:
    st.session_state["messages"].append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    history = st.session_state["messages"][:-1]

    conversation = ""

    for message in history[-6:]:
        role = (
            "User" if message["role"] == "user"
            else "ResearchMate AI"
        )

        conversation += (
            f"{role}: {message['content']}\n"
        )

    chat_prompt = f"""
You are ResearchMate AI, an academic research assistant.

Answer the latest question using the research paper below.
Use simple, clear academic English.
Do not invent findings, facts, or citations.
Mention page numbers when identifiable.
If the answer is not in the supplied text, say so.

Previous conversation:
{conversation}

Research paper:
{paper_context}

Latest user question:
{question}
"""

    with st.chat_message("assistant"):
        try:
            with st.spinner("Analyzing the research paper..."):
                answer = generate_ai_response(chat_prompt)

            st.markdown(answer)

        except Exception as error:
            answer = (
                "I could not get a response from the AI service. "
                "Please try again later. "
                f"Details: {error}"
            )
            st.error(answer)

    st.session_state["messages"].append({
        "role": "assistant",
        "content": answer
    })


# ---------------------------------------
# 14. Footer
# ---------------------------------------
st.divider()
st.caption("MCA AI Final-Year Project | ResearchMate AI")
