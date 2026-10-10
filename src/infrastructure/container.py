from infrastructure.llm_provider import GoogleLLMClient
from infrastructure.vector_store import ChromaVectorStore
from infrastructure.transcript_repository import SQLiteTranscriptRepository

class Container:
    _llm_client = None
    _vector_store = None
    _transcript_repository = None
    
    @classmethod
    def get_llm_client(cls):
        if cls._llm_client is None:
            cls._llm_client = GoogleLLMClient()
        return cls._llm_client
        
    @classmethod
    def get_vector_store(cls):
        if cls._vector_store is None:
            cls._vector_store = ChromaVectorStore()
        return cls._vector_store

    @classmethod
    def get_transcript_repository(cls):
        if cls._transcript_repository is None:
            cls._transcript_repository = SQLiteTranscriptRepository()
        return cls._transcript_repository
