import pytest
from src.services.rag_service import RAGService

def test_extract_used_citations_explicit_tagging():
    rag = RAGService(db=None)
    chunks = [
        {"document_id": "doc-1", "document_name": "Tejas Patare.pdf", "page_number": 1, "content": "Full Stack Developer at SGBC IIT Madras."},
        {"document_id": "doc-2", "document_name": "Architecture.md", "page_number": 1, "content": "Architecture blueprint."},
        {"document_id": "doc-3", "document_name": "Interview.pdf", "page_number": 5, "content": "Questions and answers."},
    ]
    
    response_text = "Based on the document, Tejas worked at SGBC IIT Madras.\n\n[Sources: Excerpt 1]"

    clean_text, citations = rag.extract_used_citations(response_text, chunks)
    assert clean_text == "Based on the document, Tejas worked at SGBC IIT Madras."
    assert len(citations) == 1
    assert citations[0]["document_name"] == "Tejas Patare.pdf"
    assert citations[0]["page_number"] == 1

def test_extract_used_citations_not_found():
    rag = RAGService(db=None)
    chunks = [
        {"document_id": "doc-1", "document_name": "Doc1.pdf", "page_number": 1, "content": "Random content."}
    ]
    
    response_text = "I cannot find this information in your uploaded documents."
    clean_text, citations = rag.extract_used_citations(response_text, chunks)
    assert clean_text == "I cannot find this information in your uploaded documents."
    assert len(citations) == 0

def test_extract_used_citations_multiple_excerpts():
    rag = RAGService(db=None)
    chunks = [
        {"document_id": "doc-1", "document_name": "Resume1.pdf", "page_number": 1, "content": "Frontend developer."},
        {"document_id": "doc-2", "document_name": "Resume2.pdf", "page_number": 1, "content": "Machine learning engineer."},
        {"document_id": "doc-3", "document_name": "Unrelated.pdf", "page_number": 2, "content": "Unrelated topics."},
    ]
    
    response_text = "Tejas worked on frontend and ML.\n\n[Sources: Excerpt 1, Excerpt 2]"

    clean_text, citations = rag.extract_used_citations(response_text, chunks)
    assert len(citations) == 2
    assert {c["document_name"] for c in citations} == {"Resume1.pdf", "Resume2.pdf"}
