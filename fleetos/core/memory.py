"""
Memory Manager: Persistent knowledge store for the fleet.

Manages:
- Vector database (Chroma) for semantic search
- GraphRAG knowledge graph for entity relationships
- Redis cache for session data
- Company context and historical artifacts
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Manages persistent fleet memory and knowledge.

    Example:
        memory = MemoryManager()
        memory.store_artifact("newsletter_copy", artifact_data)
        similar = memory.search("successful newsletters")
    """

    def __init__(self, chroma_path: str = "./company_memory"):
        """
        Initialize memory manager.

        Args:
            chroma_path: Path to Chroma database
        """
        self.chroma_path = chroma_path
        self.artifacts = {}  # In-memory cache (Phase 2: replace with Chroma)
        self.graph = {}  # In-memory graph (Phase 3: replace with GraphRAG)
        logger.info(f"MemoryManager initialized (path: {chroma_path})")

    def store_artifact(
        self,
        artifact_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store an artifact in memory.

        Args:
            artifact_type: Type of artifact (e.g., "newsletter_copy", "email")
            content: Artifact content
            metadata: Additional metadata

        Returns:
            Artifact ID
        """
        artifact_id = f"{artifact_type}_{datetime.utcnow().timestamp()}"

        self.artifacts[artifact_id] = {
            "type": artifact_type,
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "embedding": None  # Phase 2: Add embeddings via Ollama
        }

        logger.info(f"Stored artifact: {artifact_id}")
        return artifact_id

    def search(
        self,
        query: str,
        artifact_type: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar artifacts.

        Args:
            query: Search query
            artifact_type: Filter by artifact type
            top_k: Number of results to return

        Returns:
            List of relevant artifacts
        """
        # Phase 1: Simple string matching
        # Phase 2+: Replace with Chroma semantic search
        results = []

        for artifact_id, artifact in self.artifacts.items():
            if artifact_type and artifact["type"] != artifact_type:
                continue

            # Simple relevance scoring
            relevance = self._calculate_relevance(query, artifact["content"])
            if relevance > 0:
                results.append({
                    "artifact_id": artifact_id,
                    "relevance": relevance,
                    **artifact
                })

        # Sort by relevance and return top-k
        results.sort(key=lambda x: x["relevance"], reverse=True)
        logger.info(f"Search '{query}' returned {len(results[:top_k])} results")
        return results[:top_k]

    def add_entity_relationship(
        self,
        entity1: str,
        relationship: str,
        entity2: str,
        confidence: float = 1.0
    ):
        """
        Add relationship to knowledge graph.

        Args:
            entity1: Source entity
            relationship: Relationship type
            entity2: Target entity
            confidence: Confidence score (0-1)
        """
        key = f"{entity1}_{relationship}_{entity2}"

        self.graph[key] = {
            "entity1": entity1,
            "relationship": relationship,
            "entity2": entity2,
            "confidence": confidence,
            "created_at": datetime.utcnow().isoformat()
        }

        logger.info(f"Added relationship: {entity1} -{relationship}-> {entity2}")

    def get_company_context(self) -> Dict[str, Any]:
        """
        Get current company context and state.

        Returns:
            Company context dictionary
        """
        return {
            "artifacts_count": len(self.artifacts),
            "relationships_count": len(self.graph),
            "recent_artifacts": list(self.artifacts.keys())[-5:],
            "timestamp": datetime.utcnow().isoformat()
        }

    def _calculate_relevance(self, query: str, text: str) -> float:
        """
        Simple relevance calculation (Phase 2: replace with embeddings).

        Args:
            query: Search query
            text: Text to score

        Returns:
            Relevance score (0-1)
        """
        query_lower = query.lower()
        text_lower = text.lower()

        # Count word matches
        query_words = set(query_lower.split())
        text_words = set(text_lower.split())
        matches = len(query_words & text_words)

        # Simple score: matches / total query words
        return matches / len(query_words) if query_words else 0.0

    def cleanup(self, keep_days: int = 30):
        """
        Clean up old artifacts.

        Args:
            keep_days: Keep artifacts newer than N days
        """
        # Phase 3: Implement cleanup based on age
        logger.info(f"Cleanup: keeping artifacts from last {keep_days} days")


# TODO: Phase 2 - Integrate Chroma for vector storage
# TODO: Phase 2 - Add Ollama embeddings
# TODO: Phase 3 - Integrate GraphRAG for knowledge graph
# TODO: Phase 3 - Add data validation and cleanup routines
