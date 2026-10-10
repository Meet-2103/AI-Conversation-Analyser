from typing import List
import concurrent.futures
from domain.interfaces import ILLMClient
from domain.models import Transcript, QAAnswer, Citation
from infrastructure.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from core.verification import QuoteVerifier

from domain.exceptions import LLMProviderError
from infrastructure.logger import get_logger

logger = get_logger(__name__)

class GoogleLLMClient(ILLMClient):
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model=settings.MODEL_NAME, google_api_key=settings.GOOGLE_API_KEY, temperature=0.1)
        
    def ask_question(self, question: str, context: str, raw_text: str = "") -> QAAnswer:
        parser = PydanticOutputParser(pydantic_object=QAAnswer)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert analyst. Answer the user's question based on the provided transcript context. Extract exact quotes and supporting timestamps to back up your answer. \n{format_instructions}"),
            ("user", "Context:\n{context}\n\nQuestion: {question}")
        ])
        
        chain = prompt | self.llm | parser
        
        try:
            response = chain.invoke({
                "context": context,
                "question": question,
                "format_instructions": parser.get_format_instructions()
            })
        except Exception as e:
            logger.error(f"Failed to ask question via LLM: {str(e)}", exc_info=True)
            raise LLMProviderError("Failed to get a response from the AI model.", e)
            
        
        response.question = question
        
        if raw_text:
            response.citations = QuoteVerifier.verify_citations(response.citations, raw_text)
            
        return response

    def synthesize_themes(self, transcripts: List[Transcript]) -> str:
        map_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert analyst. Read the following interview transcript and extract the key themes, insights, and important exact quotes (with timestamps)."),
            ("user", "Expert: {expert_name}\nTranscript:\n{raw_text}")
        ])
        map_chain = map_prompt | self.llm
        
        def process_transcript(t: Transcript) -> str:
            try:
                res = map_chain.invoke({"expert_name": t.expert_name, "raw_text": t.raw_text})
                return f"--- Summary for {t.expert_name} ---\n{res.content}\n"
            except Exception as e:
                logger.error(f"Failed to process transcript for {t.expert_name}: {e}")
                return f"--- Summary for {t.expert_name} ---\n[Failed to extract summary]\n"

        try:
            logger.info(f"Starting map phase: extracting themes from {len(transcripts)} individual transcripts.")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                individual_summaries = list(executor.map(process_transcript, transcripts))
                
            combined_summaries = "\n".join(individual_summaries)
            
            logger.info("Starting reduce phase: synthesizing combined summaries.")
            reduce_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert analyst. You will be given summaries of interviews from multiple experts. Synthesize these into a cohesive final report identifying common cross-call themes, agreements, and disagreements. Include exact quotes with timestamps from the summaries to back up your synthesis."),
                ("user", "Expert Summaries:\n{context}")
            ])
            reduce_chain = reduce_prompt | self.llm
            
            final_response = reduce_chain.invoke({"context": combined_summaries})
            return str(final_response.content)
            
        except Exception as e:
            logger.error(f"Failed to synthesize themes via LLM: {str(e)}", exc_info=True)
            raise LLMProviderError("Failed to synthesize themes using the AI model.", e)
