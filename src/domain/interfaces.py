from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from .models import Transcript, QAAnswer

class ITranscriptRepository(ABC):
    @abstractmethod
    def save(self, transcript: Transcript, raw_text: str) -> None:
        pass
    
    @abstractmethod
    def get_by_id(self, transcript_id: str) -> Optional[Transcript]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[Transcript]:
        pass
    
    @abstractmethod
    def get_raw_text(self, transcript_id: str) -> Optional[str]:
        pass
        
    @abstractmethod
    def get_raw_text_by_expert(self, expert_name: str) -> Optional[str]:
        pass

    @abstractmethod
    def get_all_raw_texts(self) -> Dict[str, str]:
        pass
    
    @abstractmethod
    def count(self) -> int:
        pass


class IVectorStore(ABC):
    @abstractmethod
    def add_transcripts(self, transcripts: List[Transcript]) -> None:
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        pass

class ILLMClient(ABC):
    @abstractmethod
    def ask_question(self, question: str, context: str, raw_text: str = "") -> QAAnswer:
        pass
    
    @abstractmethod
    def synthesize_themes(self, transcripts: List[Transcript]) -> str:
        pass
