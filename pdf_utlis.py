# pdf_utils.py
import io
import os
from fpdf import FPDF

# Path to your existing font file
FONT_DIR = r"F:\FastAPI\fonts"


def parse_answer_key(answer_key: str):
    """
    Parses explanation, curriculum mapping, and marks from answer_key text.
    Returns a tuple of (explanation, curriculum_mapping, marks)
    """
    lines = answer_key.splitlines()
    explanation_lines = []
    curriculum_lines = []
    marks_line = ""
    explanation_started = False

    for line in lines:
        if line.startswith("Explanation:"):
            explanation_started = True
            explanation_lines.append(line.replace("Explanation:", "").strip())
        elif explanation_started:
            if line.startswith("Curriculum Mapping:"):
                explanation_started = False
                curriculum_lines.append(line.replace("Curriculum Mapping:", "").strip())
            elif line.startswith("Marks:"):
                marks_line = line.replace("Marks:", "").strip()
                break
            else:
                explanation_lines.append(line.strip())
        elif line.startswith("Curriculum Mapping:"):
            curriculum_lines.append(line.replace("Curriculum Mapping:", "").strip())
        elif line.startswith("Marks:"):
            marks_line = line.replace("Marks:", "").strip()

    explanation = "\n".join(explanation_lines).strip()
    curriculum_mapping = "\n".join(curriculum_lines).strip()
    marks = marks_line

    return explanation, curriculum_mapping, marks


def create_pdf_for_question(entry, question_num):
    """
    Creates a PDF for a single question entry using fpdf2 with Unicode support.
    entry: dict containing 'question', 'options' (list), 'answer_key' (str)
    question_num: int question number
    Returns an io.BytesIO buffer containing the PDF.
    """
    pdf = FPDF()
    pdf.add_page()

    # Add both regular and bold fonts
    pdf.add_font("DejaVu", "", os.path.join(FONT_DIR, "DejaVuSans.ttf"), uni=True)
    pdf.add_font("DejaVu", "B", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf"), uni=True)

    pdf.set_font("DejaVu", size=12)

    # Question
    pdf.cell(0, 10, f"Question {question_num}", ln=True)
    pdf.multi_cell(0, 10, entry['question'])
    pdf.ln(5)

    # Options
    options = entry.get('options', [])
    for opt in options:
        pdf.cell(0, 10, opt, ln=True)
    pdf.ln(5)

    # Explanation, Curriculum, Marks
    explanation, curriculum, marks = parse_answer_key(entry['answer_key'])

    pdf.set_font("DejaVu", "B", size=12)
    pdf.cell(0, 10, "Explanation:", ln=True)
    pdf.set_font("DejaVu", size=12)
    pdf.multi_cell(0, 10, explanation)
    pdf.ln(5)

    pdf.set_font("DejaVu", "B", size=12)
    pdf.cell(0, 10, "Curriculum Mapping:", ln=True)
    pdf.set_font("DejaVu", size=12)
    pdf.multi_cell(0, 10, curriculum)
    pdf.ln(5)

    pdf.cell(0, 10, f"Marks: {marks}", ln=True)

    # Output
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output