import uuid
import re
from typing import List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.document import Document, Chunk
from src.services.embedding_service import EmbeddingService

STRICT_REFERENCE_SYSTEM_PROMPT = """You are DocuMind AI, a strict and secure document reference assistant. Your sole responsibility is to answer user queries using EXCLUSIVELY the provided document excerpts below.

STRICT GROUNDING & CITATION RULES:
1. Ground every claim directly and factually in the provided Context excerpts.
2. If the provided excerpts do NOT contain the answer, you MUST state exactly:
   "I cannot find this information in your uploaded documents."
   Do NOT output any Sources line if the information was not found.
3. If the question is general chit-chat (e.g. "tell me a joke" or "what is the weather"), politely reply that you can only answer questions about the user's uploaded documents, and do NOT output any Sources line.
4. When answering factually from the excerpts, on the very last line of your response, specify ONLY the excerpts that directly supplied the facts used in your answer, formatted exactly as:
   [Sources: Excerpt X, Excerpt Y]
5. Do NOT use external general knowledge, guess, or hallucinate facts not present in the context.
6. Format your answers clearly with concise markdown paragraphs or bullet points where appropriate.
"""

class RAGService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = EmbeddingService()

    async def search_similar_chunks(
        self,
        user_id: uuid.UUID,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        # 1. Generate query embedding
        query_vector = await self.embedding_service.embed_query(query)

        # 2. Strict tenant-scoped pgvector similarity search
        stmt = (
            select(
                Chunk.id,
                Chunk.document_id,
                Document.filename.label("document_name"),
                Chunk.page_number,
                Chunk.content,
                (Chunk.embedding.cosine_distance(query_vector)).label("distance")
            )
            .join(Document, Document.id == Chunk.document_id)
            .where(
                Chunk.user_id == user_id,
                Document.user_id == user_id,
                Document.status == "ready"
            )
            .order_by("distance")
            .limit(top_k)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        results = []
        for row in rows:
            results.append({
                "chunk_id": str(row.id),
                "document_id": str(row.document_id),
                "document_name": row.document_name,
                "page_number": row.page_number,
                "content": row.content,
                "distance": float(row.distance)
            })
        return results

    def build_prompt_with_context(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]] = None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        if not chunks:
            context_block = "No relevant document excerpts found."
        else:
            context_pieces = []
            for i, c in enumerate(chunks, start=1):
                page_str = f"Page {c['page_number']}" if c.get('page_number') else "Document Section"
                context_pieces.append(f"[Excerpt {i}] (Source: {c['document_name']}, {page_str}):\n{c['content']}\n")

            context_block = "\n".join(context_pieces)

        history_block = ""
        if conversation_history:
            formatted_history = []
            for msg in conversation_history[-4:]: # recent 4 messages for conversational continuity
                formatted_history.append(f"{msg['role'].capitalize()}: {msg['content']}")
            history_block = "Recent Conversation Context:\n" + "\n".join(formatted_history) + "\n\n"

        full_prompt = f"""DOCUMENT CONTEXT:
{context_block}

{history_block}USER QUESTION:
{query}

ANSWER (grounded strictly in the document excerpts above):"""
        return full_prompt, chunks

    def extract_used_citations(
        self,
        response_text: str,
        chunks: List[Dict[str, Any]]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        clean_text = response_text
        
        # 1. Negative / Not Found / Chit-chat check
        lowered = response_text.lower()
        if "cannot find this information in your uploaded documents" in lowered:
            clean_text = re.sub(r'\[Sources?:.*?\]', '', clean_text, flags=re.IGNORECASE).strip()
            clean_text = re.sub(r'Sources\s*(Used)?:.*', '', clean_text, flags=re.IGNORECASE).strip()
            return clean_text, []
            
        if "only answer questions about your uploaded documents" in lowered or "i can only answer questions about" in lowered:
            clean_text = re.sub(r'\[Sources?:.*?\]', '', clean_text, flags=re.IGNORECASE).strip()
            clean_text = re.sub(r'Sources\s*(Used)?:.*', '', clean_text, flags=re.IGNORECASE).strip()
            return clean_text, []

        cited_indices = set()

        # 2. Extract explicit [Sources: Excerpt X, Excerpt Y]
        source_line_match = re.search(r'\[Sources?:\s*([^\]]+)\]', response_text, flags=re.IGNORECASE)
        if source_line_match:
            source_content = source_line_match.group(1)
            nums = re.findall(r'\b(\d+)\b', source_content)
            for n in nums:
                cited_indices.add(int(n))
            clean_text = re.sub(r'\n*\[Sources?:\s*[^\]]+\]\s*$', '', clean_text, flags=re.IGNORECASE).strip()

        # Check for Sources Used: [Excerpt X] or Sources: Excerpt X without square brackets
        if not cited_indices:
            sources_used_match = re.search(r'Sources\s*(?:Used)?:\s*([^\n]+)', response_text, flags=re.IGNORECASE)
            if sources_used_match:
                source_content = sources_used_match.group(1)
                nums = re.findall(r'\b(\d+)\b', source_content)
                for n in nums:
                    cited_indices.add(int(n))
                clean_text = re.sub(r'\n*Sources\s*(?:Used)?:\s*[^\n]+\s*$', '', clean_text, flags=re.IGNORECASE).strip()

        # Also check for inline [Excerpt X] mentions
        inline_excerpts = re.findall(r'\[Excerpt\s*(\d+)\]', clean_text, flags=re.IGNORECASE)
        for n in inline_excerpts:
            cited_indices.add(int(n))

        used_citations: List[Dict[str, Any]] = []
        seen_sources = set()

        # If LLM explicitly tagged excerpts, map them to chunks
        if cited_indices:
            for idx in sorted(cited_indices):
                if 1 <= idx <= len(chunks):
                    c = chunks[idx - 1]
                    source_key = (c['document_id'], c.get('page_number'))
                    if source_key not in seen_sources:
                        seen_sources.add(source_key)
                        snippet = c['content'][:150] + ("..." if len(c['content']) > 150 else "")
                        used_citations.append({
                            "document_id": c['document_id'],
                            "document_name": c['document_name'],
                            "page_number": c.get('page_number'),
                            "snippet": snippet
                        })

        # Fallback if no explicit indices were found: lexical overlap verification
        if not used_citations and chunks:
            words = set(re.findall(r'\b[a-zA-Z0-9_-]{4,}\b', clean_text.lower()))
            stopwords = {
                'this', 'that', 'with', 'from', 'your', 'have', 'were', 'which', 'their',
                'about', 'there', 'based', 'provided', 'documents', 'document', 'information',
                'answer', 'below', 'excerpts', 'excerpt', 'work', 'done', 'experience',
                'worked', 'performed', 'using', 'also', 'following', 'system', 'used', 'would'
            }
            content_words = words - stopwords

            for c in chunks:
                source_key = (c['document_id'], c.get('page_number'))
                if source_key in seen_sources:
                    continue
                chunk_words = set(re.findall(r'\b[a-zA-Z0-9_-]{4,}\b', c['content'].lower())) - stopwords
                overlap = content_words.intersection(chunk_words)
                
                # Check if significant distinctive overlap exists
                if len(overlap) >= 5:
                    seen_sources.add(source_key)
                    snippet = c['content'][:150] + ("..." if len(c['content']) > 150 else "")
                    used_citations.append({
                        "document_id": c['document_id'],
                        "document_name": c['document_name'],
                        "page_number": c.get('page_number'),
                        "snippet": snippet
                    })

        return clean_text, used_citations

