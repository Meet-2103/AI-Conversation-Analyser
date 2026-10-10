import os
import sys

# Ensure src root is in sys.path
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

import streamlit as st

from core.ingestion import ingest_data
from core.synthesis.qa_engine import QAEngine
from core.parsers.transcript_parser import TranscriptParser
from domain.exceptions import AppError
from infrastructure.logger import get_logger

logger = get_logger(__name__)

def main():
    st.set_page_config(page_title="Transcript Analysis", layout="wide")
    
    # Inject Custom CSS
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as css_file:
            st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
            
    st.title("Expert Transcript Analysis App")
    
    # Initialize
    try:
        with st.spinner("Initializing system and loading data..."):
            ingest_data()
            qa_engine = QAEngine()
    except AppError as e:
        st.error(f"Application Error: {e.message}")
        logger.error("Initialization failed", exc_info=True)
        return
    except Exception as e:
        st.error("An unexpected error occurred during initialization.")
        logger.error(f"Unexpected initialization error: {str(e)}", exc_info=True)
        return
        
    tab1, tab2, tab3 = st.tabs(["Interview Guide", "Cross-Call Synthesis", "Free Q&A"])
    
    with tab1:
        st.header("Interview Guide Responses")
        if st.button("Generate Answers for Guide"):
            try:
                with open("data/interview_guide.txt", "r", encoding="utf-8") as f:
                    guide_text = f.read()
                
                # Simple extraction of questions
                questions = [line for line in guide_text.split('\n') if line.strip() and line[0].isdigit()]
                
                with st.spinner("Analyzing transcripts against guide..."):
                    for q in questions:
                        st.subheader(q)
                        answer = qa_engine.answer_question(q, limit=8)
                        st.write(answer.answer)
                        
                        if answer.citations:
                            st.markdown("**Supporting Quotes (Verified):**")
                            for citation in answer.citations:
                                icon = "✅" if citation.is_verified else "❌ (Hallucination Detected)"
                                st.markdown(f"""
                                <div class="citation-card">
                                    <div class="citation-text">"{citation.quote}"</div>
                                    <div class="citation-meta">{icon} {citation.expert_name} [{citation.timestamp}]</div>
                                </div>
                                """, unsafe_allow_html=True)
            except AppError as e:
                st.error(f"Operation failed: {e.message}")
            except Exception as e:
                st.error("An unexpected error occurred while processing the interview guide.")
                logger.error(f"Error in Interview Guide tab: {str(e)}", exc_info=True)
                            
    with tab2:
        st.header("Cross-Call Synthesis")
        if st.button("Synthesize Themes"):
            try:
                with st.spinner("Synthesizing..."):
                    synthesis = qa_engine.synthesize_cross_call()
                    st.write(synthesis)
            except AppError as e:
                st.error(f"Synthesis failed: {e.message}")
            except Exception as e:
                st.error("An unexpected error occurred during synthesis.")
                logger.error(f"Error in Synthesis tab: {str(e)}", exc_info=True)
                
    with tab3:
        st.header("Free Q&A")
        user_q = st.text_input("Ask a question across all transcripts:")
        if st.button("Ask") and user_q:
            try:
                with st.spinner("Searching..."):
                    answer = qa_engine.answer_question(user_q, limit=5)
                    st.write(answer.answer)
                    
                    if answer.citations:
                        st.markdown("**Supporting Quotes (Verified):**")
                        for citation in answer.citations:
                            icon = "✅" if citation.is_verified else "❌ (Hallucination Detected)"
                            st.markdown(f"""
                            <div class="citation-card">
                                <div class="citation-text">"{citation.quote}"</div>
                                <div class="citation-meta">{icon} {citation.expert_name} [{citation.timestamp}]</div>
                            </div>
                            """, unsafe_allow_html=True)
            except AppError as e:
                st.error(f"Search failed: {e.message}")
            except Exception as e:
                st.error("An unexpected error occurred during search.")
                logger.error(f"Error in Free Q&A tab: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
