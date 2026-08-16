"""
Knowledge Module: General knowledge question answering.
Uses direct Wikipedia REST API (more reliable than the `wikipedia` library),
with a curated local knowledge base as primary fast lookup.
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import requests as _requests
except ImportError:
    _requests = None


class KnowledgeService:
    """Answers general knowledge questions using a local KB + Wikipedia REST API."""

    # ── Curated offline knowledge base ────────────────────────────────────────
    LOCAL_KB = {
        "who created python": "Python was created by Guido van Rossum and first released in 1991.",
        "who invented python": "Python was created by Guido van Rossum.",
        "who developed python": "Python was developed by Guido van Rossum and the Python Software Foundation.",
        "what is python": (
            "Python is a popular, high-level, interpreted programming language known for "
            "its clean syntax, readability, and a rich ecosystem of libraries."
        ),
        "who are you": (
            "I am your Python Voice Assistant, Nova. I can help with date and time, "
            "web searches, weather, reminders, emails, and general knowledge questions."
        ),
        "what is ai": (
            "Artificial intelligence refers to the simulation of human intelligence in machines "
            "programmed to think, learn, and solve problems."
        ),
        "what is artificial intelligence": (
            "Artificial intelligence is a branch of computer science focused on building "
            "smart machines capable of performing tasks that typically require human intelligence."
        ),
        "what is machine learning": (
            "Machine learning is a subset of AI where systems learn and improve from experience "
            "without being explicitly programmed, by recognising patterns in data."
        ),
        "what is the speed of light": (
            "The speed of light in a vacuum is approximately 299,792 kilometres per second, "
            "or about 186,282 miles per second."
        ),
        "what is the capital of france": "The capital of France is Paris.",
        "what is the capital of india": "The capital of India is New Delhi.",
        "what is the capital of the united states": "The capital of the United States is Washington D.C.",
        "what is the capital of england": "The capital of England is London.",
        "who is elon musk": (
            "Elon Musk is a technology entrepreneur known for founding or co-founding "
            "Tesla, SpaceX, Neuralink, and X (formerly Twitter)."
        ),
        "what is paithani": (
            "Paithani is a variety of sari from Maharashtra, India, handwoven with silk and zari "
            "(gold or silver thread). It is famous for its colourful peacock, lotus, and floral motifs "
            "on the border and pallu, and has a GI tag to protect its heritage."
        ),
        "what is blockchain": (
            "Blockchain is a distributed digital ledger technology that records transactions "
            "across many computers in a way that makes them secure, transparent, and tamper-resistant."
        ),
        "what is the internet": (
            "The internet is a global system of interconnected computer networks that use the "
            "TCP/IP protocol suite to communicate and share information worldwide."
        ),
    }

    # ── Wikipedia REST API endpoint (more reliable than wikipedia library) ────
    WIKI_API = "https://en.wikipedia.org/api/rest_v1/page/summary/{}"
    WIKI_SEARCH_API = "https://en.wikipedia.org/w/api.php"

    @classmethod
    def clean_query(cls, query: str) -> str:
        """Extract the core topic from a natural-language question."""
        cleaned = query.strip()
        prefixes = [
            r"^(?:who|what|where|when|why|how)\s+"
            r"(?:is|was|are|were|do|does|did|invented|created|developed|wrote|discovered|built|founded)\s+",
            r"^(?:tell me about|tell me who is|tell me what is|explain|search for|lookup)\s+",
            r"^(?:can you tell me|do you know)\s+",
        ]
        for pattern in prefixes:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"[?!.]+$", "", cleaned).strip()
        return cleaned

    @classmethod
    def _wikipedia_rest(cls, topic: str) -> Optional[str]:
        """
        Call the Wikipedia REST summary API directly.
        More reliable than the wikipedia PyPI package on Python 3.14.
        """
        if _requests is None:
            return None

        # Normalise: replace spaces with underscores
        slug = topic.strip().replace(" ", "_")
        url = cls.WIKI_API.format(slug)

        try:
            resp = _requests.get(url, timeout=6, headers={"User-Agent": "VoiceAssistant/1.0"})
            if resp.status_code == 200:
                data = resp.json()
                extract = data.get("extract", "").strip()
                if extract:
                    # Trim to 2 sentences
                    sentences = re.split(r"(?<=[.!?])\s+", extract)
                    summary = " ".join(sentences[:2]).strip()
                    # Remove any citation-style brackets
                    summary = re.sub(r"\[\d+\]", "", summary).strip()
                    return summary
            elif resp.status_code == 404:
                # Try a search to find the closest article title
                return cls._wikipedia_search_fallback(topic)
        except Exception as e:
            logger.error(f"Wikipedia REST API error for '{topic}': {e}")

        return None

    @classmethod
    def _wikipedia_search_fallback(cls, query: str) -> Optional[str]:
        """Search Wikipedia for the best matching article title, then fetch its summary."""
        if _requests is None:
            return None
        try:
            params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "srlimit": 1,
            }
            resp = _requests.get(
                cls.WIKI_SEARCH_API, params=params, timeout=6,
                headers={"User-Agent": "VoiceAssistant/1.0"}
            )
            if resp.status_code == 200:
                results = resp.json().get("query", {}).get("search", [])
                if results:
                    best_title = results[0]["title"]
                    return cls._wikipedia_rest(best_title)
        except Exception as e:
            logger.error(f"Wikipedia search fallback error: {e}")
        return None

    def answer_question(self, query: str) -> str:
        """
        Answer a general question.
        Priority: local KB → Wikipedia REST API.
        """
        clean_text = query.lower().strip()

        # 1. Check local knowledge base (instant, offline)
        for key, answer in self.LOCAL_KB.items():
            if key in clean_text:
                return answer

        # 2. Extract topic and query Wikipedia REST API
        topic = self.clean_query(query)
        if not topic:
            topic = query

        answer = self._wikipedia_rest(topic)
        if answer:
            return answer

        return (
            f"I don't have information about '{topic}' right now. "
            "You can say 'search {topic}' to find out online."
        ).replace("{topic}", topic)
