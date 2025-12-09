import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import pandas as pd
import json
import os
from dotenv import load_dotenv
import plotly.express as px

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
# You need a Google API Key. Get it from https://aistudio.google.com/
# Ideally, set this in a .env file or input it in the UI
if "GOOGLE_API_KEY" not in st.session_state:
    st.session_state["GOOGLE_API_KEY"] = ""

# --- AGENT CLASSES ---

class PDFTool:
    """Tool to extract text from PDF files."""
    @staticmethod
    def extract_text(uploaded_file):
        try:
            reader = PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            return None

class ExamAgent:
    """
    The main agent that uses Gemini-1.5-Pro to perform
    Exam Generation and Paper Analysis.
    """
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        # Using gemini-1.5-pro for best reasoning capabilities
        self.model = genai.GenerativeModel('gemini-3-pro')

    def generate_paper_cot(self, context_text, marking_scheme):
        """
        Generates a question paper using Chain of Thought prompting.
        """
        
        # Constructing the Chain of Thought Prompt
        prompt = f"""
        You are an expert academic paper setter. Your task is to generate a question paper based on the provided text and marking scheme.
        
        **Context (Chapter Content):**
        {context_text[:50000]} # Truncating to safe limit if extremely large, though 1.5 Pro handles huge context.
        
        **Marking Scheme Constraints:**
        {marking_scheme}
        
        **Instructions:**
        1. **Analyze the Content:** thorough scan of the chapter text.
        2. **Map Difficulty:** specific topics to easy, medium, and hard difficulty levels.
        3. **Draft Questions:** Create questions that strictly follow the marking scheme.
        4. **Review:** Ensure no questions are repeated and the total marks tally up.
        
        **Output Format:**
        Please provide the output in strict JSON format as follows:
        {{
            "paper_title": "Subject Name - Chapter Test",
            "total_marks": "Sum of marks",
            "sections": [
                {{
                    "section_name": "Section A (e.g., 2 Marks)",
                    "questions": [
                        {{"q_no": 1, "question": "The question text", "marks": 2, "blooms_level": "Knowledge/Application"}}
                    ]
                }}
            ]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            return json.loads(response.text)
        except Exception as e:
            return {"error": str(e)}

    def analyze_paper_cot(self, paper_text):
        """
        Analyzes an uploaded question paper to determine topic weightage.
        """
        prompt = f"""
        You are an expert academic auditor. Your task is to reverse-engineer a question paper to understand its structure and coverage.

        **Question Paper Text:**
        {paper_text}

        **Chain of Thought Analysis Instructions:**
        1. **Identify Questions:** Isolate individual questions from the text.
        2. **Extract Topics:** For each question, determine the specific core topic or concept it tests.
        3. **Assign Weightage:** Identify the marks allocated to that question (infer from text if not explicit, usually near the question).
        4. **Aggregate:** Group data by Topic.

        **Output Format:**
        Provide a JSON list of objects:
        [
            {{"question_text": "text...", "topic": "Topic Name", "marks": 5, "cognitive_level": "Analysis"}}
        ]
        """
        
        try:
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            return json.loads(response.text)
        except Exception as e:
            return [{"error": str(e)}]

# --- STREAMLIT UI ---

st.set_page_config(page_title="Gemini Exam Agent", layout="wide")

st.title("🤖 Gemini-Pro Education Agent")
st.markdown("Automated Question Paper Generation & Topic Analysis using Chain-of-Thought.")

# Sidebar for API Key
with st.sidebar:
    st.header("Settings")
    api_input = st.text_input("Enter Gemini API Key", type="password")
    if api_input:
        st.session_state["GOOGLE_API_KEY"] = api_input
    
    st.info("Get your key at aistudio.google.com")

if not st.session_state["GOOGLE_API_KEY"]:
    st.warning("Please enter your API Key to proceed.")
    st.stop()

# Initialize Agent
agent = ExamAgent(st.session_state["GOOGLE_API_KEY"])

# Tabs for Functionality
tab1, tab2 = st.tabs(["📝 Generate Question Paper", "📊 Analyze Existing Paper"])

# --- TAB 1: GENERATE PAPER ---
with tab1:
    st.header("Generate Paper from Chapter PDF")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_chapter = st.file_uploader("Upload Chapter PDF", type="pdf", key="gen_pdf")
        
        st.subheader("Marking Scheme")
        scheme_type = st.radio("Select Scheme Format", ["Simple", "Advanced JSON"])
        
        marking_scheme_str = ""
        if scheme_type == "Simple":
            q_2marks = st.number_input("Count of 2 Mark Questions", 0, 10, 5)
            q_5marks = st.number_input("Count of 5 Mark Questions", 0, 5, 2)
            q_10marks = st.number_input("Count of 10 Mark Questions", 0, 3, 1)
            marking_scheme_str = f"Generate {q_2marks} questions of 2 marks, {q_5marks} questions of 5 marks, and {q_10marks} questions of 10 marks."
        else:
            marking_scheme_str = st.text_area("Enter custom instructions", "Generate 3 sections. Section A: 10 MCQs...")

    with col2:
        if st.button("Generate Paper"):
            if uploaded_chapter:
                with st.spinner("Agent is reading PDF and thinking..."):
                    # 1. Tool Use: Read PDF
                    text_content = PDFTool.extract_text(uploaded_chapter)
                    
                    if text_content:
                        # 2. Agent Action: Generate
                        result = agent.generate_paper_cot(text_content, marking_scheme_str)
                        
                        if "error" not in result:
                            st.success("Paper Generated Successfully!")
                            st.json(result)
                            
                            # Render Printable View
                            st.divider()
                            st.markdown(f"### {result.get('paper_title', 'Exam Paper')}")
                            st.markdown(f"**Total Marks:** {result.get('total_marks', 'N/A')}")
                            
                            for section in result.get('sections', []):
                                st.markdown(f"#### {section['section_name']}")
                                for q in section['questions']:
                                    st.markdown(f"**Q{q.get('q_no')}.** {q['question']} *({q['marks']} Marks)*")
                        else:
                            st.error(f"Generation failed: {result['error']}")
            else:
                st.error("Please upload a PDF first.")

# --- TAB 2: ANALYZE PAPER ---
with tab2:
    st.header("Analyze Topic Weightage")
    uploaded_paper = st.file_uploader("Upload Question Paper PDF", type="pdf", key="ana_pdf")
    
    if st.button("Analyze Paper"):
        if uploaded_paper:
            with st.spinner("Agent is analyzing the paper structure..."):
                # 1. Tool Use: Read PDF
                paper_text = PDFTool.extract_text(uploaded_paper)
                
                if paper_text:
                    # 2. Agent Action: Analyze
                    analysis_result = agent.analyze_paper_cot(paper_text)
                    
                    if isinstance(analysis_result, list) and "error" not in analysis_result[0]:
                        df = pd.DataFrame(analysis_result)
                        
                        # Visuals
                        st.subheader("Topic Weightage Distribution")
                        
                        # Group by Topic
                        topic_counts = df.groupby("topic")['marks'].sum().reset_index()
                        
                        c1, c2 = st.columns([2, 1])
                        
                        with c1:
                            fig = px.pie(topic_counts, values='marks', names='topic', title='Marks by Topic')
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with c2:
                            st.dataframe(topic_counts)
                            st.metric("Total Marks Detected", df['marks'].sum())
                            
                        st.subheader("Detailed Breakdown")
                        st.dataframe(df)
                    else:
                        st.error("Could not parse analysis.")
        else:
            st.error("Please upload a question paper.")