from domain.models import Citation
import re

class QuoteVerifier:
    """Verifies that quotes extracted by the LLM are exact substrings of the raw transcript."""
    
    @staticmethod
    def verify_quote(quote: str, raw_text: str) -> bool:
        """
        Cleans the quote (normalizes whitespace) and checks if it's an exact substring
        of the similarly cleaned raw text.
        """
        def normalize_whitespace(text: str) -> str:
            return re.sub(r'\s+', ' ', text).strip().lower()
            
        clean_quote = normalize_whitespace(quote)
        clean_text = normalize_whitespace(raw_text)
        
        return clean_quote in clean_text
    
    @staticmethod
    def verify_citations(citations: list[Citation], raw_text: str) -> list[Citation]:
        for citation in citations:
            citation.is_verified = QuoteVerifier.verify_quote(citation.quote, raw_text)
        return citations
