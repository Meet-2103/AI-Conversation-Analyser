from pydantic import BaseModel, Field
from typing import List, Optional

class Chunk(BaseModel):
    text: str
    timestamp: str
    speaker: str

class Transcript(BaseModel):
    id: str
    expert_name: str
    role: str
    market: str
    chunks: List[Chunk] = Field(default_factory=list)
    raw_text: str

class Citation(BaseModel):
    quote: str
    timestamp: str
    expert_name: str
    is_verified: bool = False

class QAAnswer(BaseModel):
    question: str
    answer: str
    citations: List[Citation] = Field(default_factory=list)
