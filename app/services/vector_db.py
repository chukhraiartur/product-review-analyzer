"""Vector database service using FAISS for storing and searching review embeddings."""

import logging
import os
import pickle
from typing import Optional

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.core.exceptions import VectorDBException

logger = logging.getLogger(__name__)


class VectorDBService:
    """Service for managing vector embeddings using FAISS."""

    def __init__(self) -> None:
        """Initialize the vector database service."""
        self.index_path = settings.faiss_index_path
        self.embedding_model = SentenceTransformer("paraphrase-MiniLM-L3-v2")
        self.dimension = 384  # Dimension of the embedding model (will be updated based on model)

        # Initialize FAISS index with dynamic dimension
        self.index = None  # Will be initialized after model loads
        self.review_ids: list[int] = []
        self.review_texts: list[str] = []

        # Initialize dimension and index after model loads
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dimension)
        
        # Load existing index if available
        self._load_index()

    def add_reviews(self, review_ids: list[int], texts: list[str]) -> None:
        """
        Add reviews to the vector database.

        Args:
            review_ids: List of review IDs
            texts: List of review texts
        """
        try:
            if not review_ids or not texts:
                logger.warning("No reviews to add to vector database")
                return

            logger.info(f"Adding {len(texts)} reviews to vector database")

            # Generate embeddings
            embeddings = self.embedding_model.encode(texts, show_progress_bar=True)

            # Normalize embeddings for cosine similarity using NumPy
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

            # Add to FAISS index
            self.index.add(embeddings.astype("float32"))

            # Store metadata
            self.review_ids.extend(review_ids)
            self.review_texts.extend(texts)

            logger.info(f"Successfully added {len(texts)} reviews to vector database")

            # Save index
            self._save_index()

        except Exception as e:
            logger.error(f"Error adding reviews to vector database: {str(e)}")
            raise VectorDBException("Failed to add reviews to vector database", str(e))

    def search_reviews(
        self, query: str, k: int = 10, filter_ids: Optional[list[int]] = None
    ) -> list[tuple[int, float, str]]:
        """
        Search for similar reviews.

        Args:
            query: Search query
            k: Number of results to return
            filter_ids: Optional list of review IDs to filter by

        Returns:
            List of tuples (review_id, similarity_score, review_text)
        """
        try:
            logger.debug(f"Searching for reviews with query: {query}")

            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            # Normalize using NumPy instead of FAISS
            query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)

            # Check if we have any reviews in the index
            if len(self.review_ids) == 0:
                logger.warning("No reviews in vector database")
                return []

            # Search in FAISS index
            scores, indices = self.index.search(
                query_embedding.astype("float32"), k=min(k * 2, len(self.review_ids))
            )

            results = []
            for i, score in zip(indices[0], scores[0]):
                if i < 0:  # FAISS returns -1 for invalid indices
                    continue
                if filter_ids and self.review_ids[i] not in filter_ids:
                    continue
                results.append(
                    (self.review_ids[i], float(score), self.review_texts[i])
                )
                if len(results) >= k:
                    break

            logger.debug(f"Found {len(results)} similar reviews")
            return results

        except Exception as e:
            logger.error(f"Error searching reviews: {str(e)}")
            raise VectorDBException("Failed to search reviews", str(e))

    def get_review_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding for a single review text.

        Args:
            text: Review text

        Returns:
            Review embedding vector
        """
        try:
            embedding = self.embedding_model.encode([text])
            return embedding[0]

        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise VectorDBException("Failed to generate embedding", str(e))

    def get_review_by_id(self, review_id: int) -> Optional[tuple[int, str]]:
        """
        Get review by ID from the vector database.

        Args:
            review_id: Review ID

        Returns:
            Tuple of (review_id, review_text) or None if not found
        """
        try:
            if review_id in self.review_ids:
                idx = self.review_ids.index(review_id)
                return (review_id, self.review_texts[idx])
            return None

        except Exception as e:
            logger.error(f"Error getting review by ID: {str(e)}")
            return None

    def remove_review(self, review_id: int) -> bool:
        """
        Remove a review from the vector database.

        Args:
            review_id: Review ID to remove

        Returns:
            True if review was removed, False otherwise
        """
        try:
            if review_id not in self.review_ids:
                logger.warning(f"Review ID {review_id} not found in vector database")
                return False

            # Get index of the review
            idx = self.review_ids.index(review_id)

            # Remove from FAISS index (this is a limitation of FAISS - we need to rebuild)
            # For now, we'll mark it as removed in our metadata
            self.review_ids[idx] = -1  # Mark as removed
            self.review_texts[idx] = ""

            logger.info(f"Marked review ID {review_id} as removed from vector database")
            return True

        except Exception as e:
            logger.error(f"Error removing review: {str(e)}")
            return False

    def get_stats(self) -> dict:
        """
        Get vector database statistics.

        Returns:
            Dictionary with statistics
        """
        try:
            total_reviews = len([rid for rid in self.review_ids if rid != -1])
            total_vectors = self.index.ntotal

            return {
                "total_reviews": total_reviews,
                "total_vectors": total_vectors,
                "dimension": self.dimension,
                "index_type": "FAISS FlatIP",
            }

        except Exception as e:
            logger.error(f"Error getting vector database stats: {str(e)}")
            return {}

    def _save_index(self) -> None:
        """Save FAISS index and metadata to disk."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

            # Save FAISS index
            faiss.write_index(self.index, f"{self.index_path}.faiss")

            # Save metadata
            metadata = {
                "review_ids": self.review_ids,
                "review_texts": self.review_texts,
            }

            with open(f"{self.index_path}.meta", "wb") as f:
                pickle.dump(metadata, f)

            logger.debug("Vector database index saved successfully")

        except Exception as e:
            logger.error(f"Error saving vector database index: {str(e)}")
            raise VectorDBException("Failed to save vector database index", str(e))

    def _load_index(self) -> None:
        """Load TF-IDF matrix and metadata from disk."""
        try:
            index_file = f"{self.index_path}.pkl"

            if os.path.exists(index_file):
                # Load metadata
                with open(index_file, "rb") as f:
                    metadata = pickle.load(f)

                self.review_ids = metadata.get("review_ids", [])
                self.review_texts = metadata.get("review_texts", [])
                self.vectorizer = metadata.get("vectorizer", self.vectorizer)
                self.tfidf_matrix = metadata.get("tfidf_matrix", None)

                logger.info(
                    f"Loaded vector database with {len(self.review_ids)} reviews"
                )
            else:
                logger.info("No existing vector database found, starting fresh")

        except Exception as e:
            logger.error(f"Error loading vector database: {str(e)}")
            # Start with fresh data
            self.review_ids = []
            self.review_texts = []
            self.tfidf_matrix = None

    def clear_index(self) -> None:
        """Clear the entire vector database."""
        try:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.review_ids = []
            self.review_texts = []

            # Remove saved files
            index_file = f"{self.index_path}.faiss"
            meta_file = f"{self.index_path}.meta"

            if os.path.exists(index_file):
                os.remove(index_file)
            if os.path.exists(meta_file):
                os.remove(meta_file)

            logger.info("Vector database cleared successfully")

        except Exception as e:
            logger.error(f"Error clearing vector database: {str(e)}")
            raise VectorDBException("Failed to clear vector database", str(e))
