# 📊 CurriQuiz

An **interactive AI-based learning application** built with **Streamlit** that dynamically generates *Quantitative Math* questions, evaluates answers, explains solutions, maps to curriculum, and allows users to download each question with its explanation as a **PDF**.

---

## 🚀 Features

### 🧠 AI-Generated Questions
- Automatically generates **topic-specific** questions using an LLM (Groq API).
- Curriculum-based generation: Subject → Unit → Topic.
- No manual topic selection — AI chooses based on the selected unit.

### 🎯 Interactive Learning
- **Multiple-choice format** (A, B, C, D).
- Instant feedback on answers: Correct / Incorrect.
- Detailed explanation for every question.
- Curriculum Mapping + Marks distribution.

### 📑 PDF Export
- Download any question with:
  - The question statement
  - All answer options
  - Correct answer
  - Detailed explanation
  - Curriculum mapping
  - Marks
- **Unicode support** for mathematical symbols.

### 🔄 Question Navigation
- **Start** button to begin.
- **Previous** & **Next** navigation.
- **Quit** to reset the session.
- Keeps track of user's answers in the current session.

### 🖥️ Clean UI
- Built with **Streamlit** for a modern, responsive interface.
- Fixed-width layout to avoid horizontal scrolling.
- Download button integrated directly in the interface.

---

### 🛠️ Tech Stack
- Frontend/UI: Streamlit
- Backend/AI: Groq LLM API
- PDF Generation: fpdf2
- Python: 3.10+

### 📌 Future Improvements
- ✅ Support for saving full session history to PDF.
- ✅ Option to retry incorrect answers.
- ✅ Multi-language question generation.
- ✅ User performance tracking dashboard.
