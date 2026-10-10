import re
from typing import List, Optional
from domain.models import Transcript, Chunk

class TranscriptParser:
    """Parses raw text transcripts into domain models."""
    
    @staticmethod
    def parse(file_path: str, raw_text: str) -> Transcript:
        lines = raw_text.strip().split('\n')
        
        expert_name = "Unknown"
        role = "Unknown"
        market = "Unknown"
        
        
        for line in lines[:5]:
            if line.startswith("Expert"):
                expert_name = line.split("–")[-1].strip()
            elif line.startswith("Role:"):
                role = line.split("Role:")[-1].strip()
            elif line.startswith("Market:"):
                market = line.split("Market:")[-1].strip()
                
        
        chunks = []
        
        
        timestamp_pattern = re.compile(r"^\d{2}:\d{2}$")
        
        current_timestamp = ""
        current_speaker = ""
        current_text = []
        
        in_dialogue = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if timestamp_pattern.match(line):
                if in_dialogue and current_text:
                    chunks.append(Chunk(
                        text=" ".join(current_text),
                        timestamp=current_timestamp,
                        speaker=current_speaker
                    ))
                
                current_timestamp = line
                current_text = []
                in_dialogue = True
            elif in_dialogue:
                if ":" in line and len(line.split(":", 1)[0]) < 25:
                    parts = line.split(":", 1)
                    current_speaker = parts[0].strip()
                    current_text.append(parts[1].strip())
                else:
                    current_text.append(line)
                    
        if in_dialogue and current_text:
            chunks.append(Chunk(
                text=" ".join(current_text),
                timestamp=current_timestamp,
                speaker=current_speaker
            ))
            
        transcript_id = file_path.split("\\")[-1].split("/")[-1].replace(".txt", "")
        
        return Transcript(
            id=transcript_id,
            expert_name=expert_name,
            role=role,
            market=market,
            chunks=chunks,
            raw_text=raw_text
        )
