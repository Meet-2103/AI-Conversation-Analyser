from typing import List
from domain.models import QAAnswer, Transcript
from infrastructure.container import Container
from infrastructure.logger import get_logger

logger = get_logger(__name__)

class QAEngine:
    def __init__(self):
        self.llm_client = Container.get_llm_client()
        self.vector_store = Container.get_vector_store()
        self.transcript_repo = Container.get_transcript_repository()
        
    def answer_question(self, question: str, limit: int = 5) -> QAAnswer:
        logger.info(f"Answering question: {question}")
        results = self.vector_store.search(query=question, limit=limit)
        
        context = ""
        expert_names = set()
        for res in results:
            expert_name = res['metadata']['expert_name']
            expert_names.add(expert_name)
            context += f"[{res['metadata']['timestamp']}] {expert_name} ({res['metadata']['speaker']}): {res['text']}\n"
            
        full_raw_text = ""
        for expert in expert_names:
            raw = self.transcript_repo.get_raw_text_by_expert(expert)
            if raw:
                full_raw_text += f"\n--- {expert} Transcript ---\n{raw}\n"
            
        answer = self.llm_client.ask_question(question=question, context=context, raw_text=full_raw_text or context)
        logger.info("Successfully generated answer.")
        return answer
        
    def answer_interview_guide(self, questions: List[str]) -> List[QAAnswer]:
        answers = []
        for q in questions:
            answers.append(self.answer_question(q, limit=8))
        return answers

    def synthesize_cross_call(self) -> str:
        transcripts = self.transcript_repo.get_all()
        logger.info(f"Synthesizing cross call themes for {len(transcripts)} transcripts.")
        return self.llm_client.synthesize_themes(transcripts)
