import chromadb
from typing import List, Dict, Any
from domain.interfaces import IVectorStore
from domain.models import Transcript

from domain.exceptions import VectorStoreError
from infrastructure.logger import get_logger

logger = get_logger(__name__)

class ChromaVectorStore(IVectorStore):
    def __init__(self, persist_directory: str = "./chroma_db"):
        try:
            self.client = chromadb.PersistentClient(path=persist_directory)
            self.collection = self.client.get_or_create_collection(name="transcripts")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}", exc_info=True)
            raise VectorStoreError("Failed to connect to the vector database.", e)
        
    def add_transcripts(self, transcripts: List[Transcript]) -> None:
        documents = []
        metadatas = []
        ids = []
        
        for transcript in transcripts:
            for i, chunk in enumerate(transcript.chunks):
                documents.append(chunk.text)
                metadatas.append({
                    "expert_name": transcript.expert_name,
                    "timestamp": chunk.timestamp,
                    "speaker": chunk.speaker
                })
                ids.append(f"{transcript.id}_chunk_{i}")
                
        if documents:
            try:
                self.collection.upsert(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
            except Exception as e:
                logger.error(f"Failed to upsert documents to ChromaDB: {str(e)}", exc_info=True)
                raise VectorStoreError("Failed to store transcripts in the vector database.", e)
            
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit
            )
        except Exception as e:
            logger.error(f"Failed to query ChromaDB: {str(e)}", exc_info=True)
            raise VectorStoreError("Failed to search transcripts in the vector database.", e)
        
        output = []
        if results["documents"] and results["metadatas"]:
            for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
                output.append({
                    "text": doc,
                    "metadata": meta
                })
        return output
