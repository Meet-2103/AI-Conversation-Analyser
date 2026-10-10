from core.verification import QuoteVerifier
from domain.models import Citation

def test_verify_quote_exact():
    raw_text = "The biggest issue is still capital budget approval. Hospitals may like the technology clinically."
    quote = "The biggest issue is still capital budget approval."
    assert QuoteVerifier.verify_quote(quote, raw_text) == True

def test_verify_quote_hallucinated():
    raw_text = "The biggest issue is still capital budget approval."
    quote = "The biggest issue is the capital budget approval."
    assert QuoteVerifier.verify_quote(quote, raw_text) == False
    
def test_verify_citations():
    raw_text = "The biggest issue is still capital budget approval. Hospitals may like the technology clinically."
    citations = [
        Citation(quote="The biggest issue is still capital budget approval.", timestamp="01:20", expert_name="Dr. Martin"),
        Citation(quote="Hospitals love the technology.", timestamp="01:25", expert_name="Dr. Martin")
    ]
    
    verified = QuoteVerifier.verify_citations(citations, raw_text)
    assert verified[0].is_verified == True
    assert verified[1].is_verified == False
