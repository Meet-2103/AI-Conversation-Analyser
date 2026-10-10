from domain.models import Citation

def test_citation_model():
    c = Citation(quote="Hello", timestamp="00:00", expert_name="Dr. X")
    assert c.is_verified == False
