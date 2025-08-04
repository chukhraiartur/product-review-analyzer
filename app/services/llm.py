"""LLM service for sentiment analysis using OpenAI API."""

import json
import logging
from typing import Any

import openai
from openai import OpenAI

from app.core.config import settings
from app.core.exceptions import LLMException

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with OpenAI LLM for sentiment analysis."""

    def __init__(self) -> None:
        """Initialize the LLM service."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def analyze_sentiment(self, text: str) -> dict[str, Any]:
        """
        Analyze sentiment of the given text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary containing sentiment analysis results
        """
        try:
            logger.debug(f"Analyzing sentiment for text: {text[:100]}...")

            prompt = self._create_sentiment_prompt(text)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a sentiment analysis expert. Analyze the sentiment of product reviews and provide a structured response.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,  # Low temperature for consistent results
                max_tokens=150,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI API")
            result = self._parse_sentiment_response(content)
            logger.debug(f"Sentiment analysis result: {result}")

            return result

        except openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            # Return fallback sentiment analysis instead of raising exception
            return self._fallback_sentiment_analysis(text)

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            raise LLMException("Failed to analyze sentiment", str(e))

    def _create_sentiment_prompt(self, text: str) -> str:
        """Create a prompt for sentiment analysis."""
        return f"""
Analyze the sentiment of the following product review text and provide a JSON response with the following structure:
{{
    "sentiment": "positive|negative|neutral",
    "confidence": 0.0-1.0,
    "score": -1.0 to 1.0,
    "reasoning": "brief explanation"
}}

Review text: "{text}"

Rules:
- "positive": Clearly favorable, happy, satisfied
- "negative": Clearly unfavorable, unhappy, dissatisfied
- "neutral": Mixed feelings, factual, no clear sentiment
- confidence: How certain you are about the classification (0.0-1.0)
- score: Sentiment score from -1.0 (very negative) to 1.0 (very positive)
- reasoning: Brief explanation of your classification

Respond only with valid JSON:
"""

    def _parse_sentiment_response(self, response_text: str) -> dict[str, Any]:
        """Parse the LLM response and extract sentiment information."""
        try:
            # Clean the response text
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]

            cleaned_text = cleaned_text.strip()

            # Parse JSON response
            result = json.loads(cleaned_text)

            # Validate required fields
            required_fields = ["sentiment", "confidence", "score", "reasoning"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")

            # Validate sentiment value
            valid_sentiments = ["positive", "negative", "neutral"]
            if result["sentiment"] not in valid_sentiments:
                raise ValueError(f"Invalid sentiment: {result['sentiment']}")

            # Validate numeric fields
            if (
                not isinstance(result["confidence"], (int, float))
                or not 0 <= result["confidence"] <= 1
            ):
                raise ValueError("Confidence must be a number between 0 and 1")

            if (
                not isinstance(result["score"], (int, float))
                or not -1 <= result["score"] <= 1
            ):
                raise ValueError("Score must be a number between -1 and 1")

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Response text: {response_text}")
            # Return default neutral sentiment
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "score": 0.0,
                "reasoning": "Failed to parse LLM response",
            }

        except ValueError as e:
            logger.error(f"Invalid response format: {str(e)}")
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "score": 0.0,
                "reasoning": f"Invalid response format: {str(e)}",
            }

    def batch_analyze_sentiment(self, texts: list[str]) -> list[dict[str, Any]]:
        """
        Analyze sentiment for multiple texts in batch.

        Args:
            texts: List of texts to analyze

        Returns:
            List of sentiment analysis results
        """
        results = []

        for text in texts:
            try:
                result = self.analyze_sentiment(text)
                results.append(result)
            except Exception as e:
                logger.error(f"Error analyzing sentiment for text: {str(e)}")
                # Add default result for failed analysis
                results.append(
                    {
                        "sentiment": "neutral",
                        "confidence": 0.0,
                        "score": 0.0,
                        "reasoning": f"Analysis failed: {str(e)}",
                    }
                )

        return results

    def get_sentiment_label(self, sentiment_data: dict[str, Any]) -> str:
        """Get sentiment label from sentiment analysis data."""
        return sentiment_data.get("sentiment", "neutral")

    def get_sentiment_score(self, sentiment_data: dict[str, Any]) -> float:
        """Get sentiment score from sentiment analysis data."""
        return sentiment_data.get("score", 0.0)

    def _fallback_sentiment_analysis(self, text: str) -> dict[str, Any]:
        """
        Fallback sentiment analysis using keyword-based approach.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with sentiment analysis results
        """
        text_lower = text.lower()

        # Positive keywords
        positive_words = [
            "great",
            "excellent",
            "amazing",
            "love",
            "perfect",
            "awesome",
            "fantastic",
            "wonderful",
            "outstanding",
            "superb",
            "brilliant",
            "fabulous",
            "terrific",
            "best",
            "good",
            "nice",
            "beautiful",
            "satisfied",
            "happy",
            "pleased",
        ]

        # Negative keywords
        negative_words = [
            "bad",
            "terrible",
            "awful",
            "hate",
            "worst",
            "horrible",
            "disappointing",
            "poor",
            "useless",
            "waste",
            "disgusting",
            "annoying",
            "frustrated",
            "angry",
            "upset",
            "disappointed",
            "unhappy",
            "dissatisfied",
        ]

        # Count positive and negative words
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        # Determine sentiment
        if positive_count > negative_count:
            sentiment = "positive"
            score = min(0.8, 0.2 + (positive_count * 0.1))
        elif negative_count > positive_count:
            sentiment = "negative"
            score = max(-0.8, -0.2 - (negative_count * 0.1))
        else:
            sentiment = "neutral"
            score = 0.0

        return {
            "sentiment": sentiment,
            "confidence": 0.6,  # Lower confidence for fallback
            "score": score,
            "reasoning": f"Fallback analysis: {positive_count} positive, {negative_count} negative keywords",
        }
