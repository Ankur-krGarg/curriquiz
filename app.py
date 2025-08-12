import os
import streamlit as st
import requests
from dotenv import load_dotenv
from pdf_utlis import create_pdf_for_question

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"
SUBJECT = "Quantitative Math"

# Curriculum dict - Units and their topics (topics chosen internally)
CURRICULUM = {
    "Problem Solving": [
        "Numbers and Operations",
        "Algebra",
        "Geometry",
        "Problem Solving",
        "Probability and Statistics",
        "Data Analysis",
    ],
    "Algebra": [
        "Algebraic Word Problems",
        "Interpreting Variables",
        "Polynomial Expressions (FOIL/Factoring)",
        "Rational Expressions",
        "Exponential Expressions (Product rule, negative exponents)",
        "Quadratic Equations & Functions (Finding roots/solutions, graphing)",
        "Functions Operations",
    ],
    "Geometry and Measurement": [
        "Area & Volume",
        "Perimeter",
        "Lines, Angles, & Triangles",
        "Right Triangles & Trigonometry",
        "Circles (Area, circumference)",
        "Coordinate Geometry",
        "Slope",
        "Transformations (Dilating a shape)",
        "Parallel & Perpendicular Lines",
        "Solid Figures (Volume of Cubes)",
    ],
    "Numbers and Operations": [
        "Basic Number Theory",
        "Prime & Composite Numbers",
        "Rational Numbers",
        "Order of Operations",
        "Estimation",
        "Fractions, Decimals, & Percents",
        "Sequences & Series",
        "Computation with Whole Numbers",
        "Operations with Negatives",
    ],
    "Data Analysis & Probability": [
        "Interpretation of Tables & Graphs",
        "Trends & Inferences",
        "Probability (Basic, Compound Events)",
        "Mean, Median, Mode, & Range",
        "Weighted Averages",
        "Counting & Arrangement Problems",
    ],
    "Reasoning": [
        "Word Problems",
    ],
}

def build_prompt(subject: str, unit: str, difficulty: str) -> str:
    topics = CURRICULUM.get(unit, [])
    topics_str = ", ".join(topics)
    return f"""
You are an expert Quantitative Math question generator specializing in educational assessments.

Your task:
- Given the unit "{unit}" with the following topics:
  {topics_str}
- Choose exactly ONE topic from the above list internally.
- Generate ONE multiple-choice question strictly on that topic.
- The question must be clear, unambiguous, and appropriate for {difficulty} difficulty.
- Format the output EXACTLY as follows (including the delimiter lines):

---QUESTION START---
Q1. Title: [Write a concise title]
Description: [Brief description or context]
Question: [Write the full question here, including any equations in LaTeX if needed]
Instructions: [How the student should answer]
Difficulty: {difficulty}
Options:
(A) [Option A]
(B) [Option B]
(C) [Option C]
(D) [Option D]

Your answer: _______

---ANSWER KEY START---
Correct Answer: [One of A, B, C, D]
Explanation: [Detailed explanation of the correct answer, step-by-step]
Curriculum Mapping: {subject} → {unit} → [Chosen topic]
Marks: 1
""".strip()

def call_groq_api_chat(prompt: str) -> str:
    if not API_KEY:
        raise RuntimeError("GROQ_API_KEY not set in environment")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 700,
        "temperature": 0.7,
    }
    response = requests.post(API_URL, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]

def parse_question_answer(raw_output):
    if "---QUESTION START---" in raw_output and "---ANSWER KEY START---" in raw_output:
        q_part, a_part = raw_output.split("---ANSWER KEY START---")
        q_part = q_part.replace("---QUESTION START---", "").strip()
        a_part = a_part.strip()
        return q_part, a_part
    else:
        return None, None

def main():
    # Initialize session state variables
    if "history" not in st.session_state:
        st.session_state.history = []
    if "current_index" not in st.session_state:
        st.session_state.current_index = -1
    if "unit_selected" not in st.session_state:
        st.session_state.unit_selected = None
    if "difficulty" not in st.session_state:
        st.session_state.difficulty = "Easy"
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}  # key: question_index, value: selected option

    # Page config - limit width for better readability, no horizontal scroll
    st.set_page_config(page_title="Quantitative Math Question Generator", layout="centered")

    st.title("Quantitative Math Question Generator - Groq LLM Chat")

    unit = st.selectbox("Select Unit", options=list(CURRICULUM.keys()))
    difficulty = st.selectbox("Select Difficulty", options=["Easy", "Moderate", "Hard"])

    st.session_state.unit_selected = unit
    st.session_state.difficulty = difficulty

    def generate_and_store_question():
        prompt = build_prompt(SUBJECT, st.session_state.unit_selected, st.session_state.difficulty)
        try:
            raw_output = call_groq_api_chat(prompt)
        except Exception as e:
            st.error(f"API Error: {e}")
            return

        question, answer_key = parse_question_answer(raw_output)
        if question and answer_key:
            entry = {
                "question": question,
                "answer_key": answer_key,
            }
            st.session_state.history.append(entry)
            st.session_state.current_index = len(st.session_state.history) - 1
        else:
            st.error("Failed to parse LLM output. Raw output:")
            st.code(raw_output)

    def show_question_and_answer():
        if st.session_state.current_index == -1:
            st.info("Press Start to generate the first question.")
            return

        entry = st.session_state.history[st.session_state.current_index]
        st.markdown(f"### Question {st.session_state.current_index + 1}")
        st.markdown(f"**Question:**\n```\n{entry['question']}\n```")

        # Extract correct answer
        answer_lines = entry["answer_key"].splitlines()
        correct_line = next((line for line in answer_lines if line.startswith("Correct Answer:")), None)
        correct_answer = None
        if correct_line:
            correct_answer = correct_line.split(":")[1].strip()

        # User answer input radio buttons
        user_choice = st.radio("Select your answer:", options=["A", "B", "C", "D"], key=f"answer_{st.session_state.current_index}")

        # Store user's choice
        st.session_state.user_answers[st.session_state.current_index] = user_choice

        # Use columns to put Submit and Download buttons side by side, download aligned right
        col_submit, col_download = st.columns([3, 1])

        with col_submit:
            if st.button("Submit Answer"):
                if user_choice == correct_answer:
                    st.success("Correct! 🎉")
                else:
                    st.error(f"Incorrect. The correct answer is {correct_answer}.")

                # Extract explanation, curriculum mapping, and marks
                explanation_lines = []
                curriculum_lines = []
                marks_line = ""
                explanation_started = False

                for line in answer_lines:
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

                explanation_text = "\n\n".join(explanation_lines).strip()
                curriculum_text = "\n".join(curriculum_lines).strip()

                formatted_text = f"""
    **Explanation:**

    {explanation_text}

    ---

    **Curriculum Mapping:**

    {curriculum_text}

    ---

    **Marks:** {marks_line}
    """

                with st.expander("Explanation and Curriculum Mapping"):
                    st.markdown(formatted_text)

        # Create a column layout so you can position the download button on the right
        col_left, col_right = st.columns([9, 1])  # Adjust proportions as needed

        with col_right:
            # Use st.download_button directly (no need to wrap inside st.button)
            pdf_file = create_pdf_for_question(entry, st.session_state.current_index + 1)
            st.download_button(
                label="Download PDF",
                data=pdf_file,
                file_name=f"question_{st.session_state.current_index + 1}.pdf",
                mime="application/pdf",
                key=f"download_pdf_{st.session_state.current_index}"
            )

    # --- Button logic outside function ---

    if st.session_state.current_index == -1:
        if st.button("Start"):
            generate_and_store_question()
    else:
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            if st.button("Previous"):
                if st.session_state.current_index > 0:
                    st.session_state.current_index -= 1
                else:
                    st.warning("No previous question.")
        with col2:
            if st.button("Next"):
                generate_and_store_question()
        with col3:
            if st.button("Quit"):
                st.session_state.history = []
                st.session_state.current_index = -1
                st.session_state.user_answers = {}
                st.success("Session cleared.")

    show_question_and_answer()

if __name__ == "__main__":
    main()
