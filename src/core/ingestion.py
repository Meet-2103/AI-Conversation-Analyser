import os
from core.parsers.transcript_parser import TranscriptParser
from infrastructure.container import Container
from domain.exceptions import DataIngestionError
from infrastructure.logger import get_logger

logger = get_logger(__name__)

def ingest_data(data_dir: str = "data"):
    vector_store = Container.get_vector_store()
    transcript_repo = Container.get_transcript_repository()
    
    
    if transcript_repo.count() == 0:
        transcripts = []
        try:
            for filename in os.listdir(data_dir):
                if filename.endswith(".txt") and "expert" in filename.lower():
                    file_path = os.path.join(data_dir, filename)
                    with open(file_path, "r", encoding="utf-8") as f:
                        raw_text = f.read()
                    
                    transcript = TranscriptParser.parse(file_path, raw_text)
                    
                    
                    transcript_repo.save(transcript, raw_text)
                    transcripts.append(transcript)
                    
            
            vector_store.add_transcripts(transcripts)
            logger.info(f"Successfully ingested {len(transcripts)} transcripts into both databases.")
            return transcripts
        except Exception as e:
            logger.error(f"Failed to ingest transcripts from {data_dir}: {str(e)}", exc_info=True)
            raise DataIngestionError("Failed to ingest transcripts. Check if data directory and files are valid.", e)
    return []
