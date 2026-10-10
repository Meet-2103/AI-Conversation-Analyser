from core.parsers.transcript_parser import TranscriptParser

def test_parse_transcript():
    raw = """Expert 1 – Dr. Jean Martin
Role: Head of Urology
Market: France

00:00
Interviewer: Hello.

00:18
Dr. Martin: Hi there.
"""
    transcript = TranscriptParser.parse("expert_1_dr_jean_martin.txt", raw)
    assert transcript.expert_name == "Dr. Jean Martin"
    assert transcript.role == "Head of Urology"
    assert transcript.market == "France"
    assert len(transcript.chunks) == 2
    
    assert transcript.chunks[0].timestamp == "00:00"
    assert transcript.chunks[0].speaker == "Interviewer"
    assert transcript.chunks[0].text == "Hello."
    
    assert transcript.chunks[1].timestamp == "00:18"
    assert transcript.chunks[1].speaker == "Dr. Martin"
    assert transcript.chunks[1].text == "Hi there."
