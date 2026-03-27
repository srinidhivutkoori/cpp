"""
Amazon Comprehend service for NLP analysis of paper abstracts.
Extracts keywords, detects sentiment, and identifies named entities.
"""

import random
from datetime import datetime


class ComprehendService:
    """
    Performs NLP analysis using Amazon Comprehend in production
    and returns realistic mock results in development mode.

    Attributes:
        use_aws (bool): Whether to connect to real Comprehend.
        client: Boto3 Comprehend client (None in mock mode).
        analysis_cache (dict): Cache of analysis results.
    """

    def __init__(self, use_aws=False, region='eu-west-1'):
        """
        Initialize the Comprehend service.

        Args:
            use_aws (bool): If True, connect to real AWS Comprehend.
            region (str): AWS region.
        """
        self.use_aws = use_aws
        self.region = region
        self.client = None
        self.analysis_cache = {}

        if self.use_aws:
            import boto3
            self.client = boto3.client('comprehend', region_name=region)

    def extract_key_phrases(self, text, language='en'):
        """
        Extract key phrases from the given text using NLP.

        Args:
            text (str): Input text to analyze (typically a paper abstract).
            language (str): Language code.

        Returns:
            list: List of extracted key phrases with confidence scores.
        """
        if self.use_aws:
            response = self.client.detect_key_phrases(
                Text=text, LanguageCode=language
            )
            return [
                {'text': kp['Text'], 'score': round(kp['Score'], 4)}
                for kp in response['KeyPhrases']
            ]
        else:
            # Mock mode: extract significant words and phrases from the text
            words = text.split()
            phrases = []
            # Extract noun-like segments (simplified heuristic)
            common_words = {
                'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                'would', 'could', 'should', 'may', 'might', 'can', 'shall',
                'of', 'in', 'to', 'for', 'with', 'on', 'at', 'from', 'by',
                'about', 'as', 'into', 'through', 'during', 'before', 'after',
                'and', 'but', 'or', 'nor', 'not', 'so', 'yet', 'both',
                'this', 'that', 'these', 'those', 'it', 'its', 'we', 'our',
                'they', 'their', 'which', 'who', 'whom', 'what', 'where'
            }
            significant = [
                w.strip('.,;:!?()[]') for w in words
                if len(w) > 3 and w.lower().strip('.,;:!?()[]') not in common_words
            ]
            # Create bigram phrases from significant words
            seen = set()
            for i in range(len(significant)):
                word = significant[i]
                if word.lower() not in seen and word:
                    seen.add(word.lower())
                    phrases.append({
                        'text': word,
                        'score': round(random.uniform(0.75, 0.99), 4)
                    })
                    if len(phrases) >= 10:
                        break

            return sorted(phrases, key=lambda x: x['score'], reverse=True)

    def detect_sentiment(self, text, language='en'):
        """
        Detect the sentiment of the given text.

        Args:
            text (str): Input text to analyze.
            language (str): Language code.

        Returns:
            dict: Sentiment result with label and confidence scores.
        """
        if self.use_aws:
            response = self.client.detect_sentiment(
                Text=text, LanguageCode=language
            )
            return {
                'sentiment': response['Sentiment'],
                'scores': {
                    'positive': round(response['SentimentScore']['Positive'], 4),
                    'negative': round(response['SentimentScore']['Negative'], 4),
                    'neutral': round(response['SentimentScore']['Neutral'], 4),
                    'mixed': round(response['SentimentScore']['Mixed'], 4)
                }
            }
        else:
            # Academic abstracts typically have neutral-positive sentiment
            return {
                'sentiment': 'NEUTRAL',
                'scores': {
                    'positive': round(random.uniform(0.15, 0.35), 4),
                    'negative': round(random.uniform(0.01, 0.08), 4),
                    'neutral': round(random.uniform(0.55, 0.75), 4),
                    'mixed': round(random.uniform(0.02, 0.10), 4)
                }
            }

    def detect_entities(self, text, language='en'):
        """
        Detect named entities in the given text.

        Args:
            text (str): Input text to analyze.
            language (str): Language code.

        Returns:
            list: List of detected entities with type and confidence.
        """
        if self.use_aws:
            response = self.client.detect_entities(
                Text=text, LanguageCode=language
            )
            return [
                {'text': ent['Text'], 'type': ent['Type'],
                 'score': round(ent['Score'], 4)}
                for ent in response['Entities']
            ]
        else:
            # Mock mode: detect patterns typical of academic text
            mock_entities = []
            words = text.split()
            for i, word in enumerate(words):
                clean = word.strip('.,;:!?()')
                if clean and clean[0].isupper() and len(clean) > 2:
                    entity_type = random.choice([
                        'ORGANIZATION', 'PERSON', 'OTHER', 'TITLE'
                    ])
                    mock_entities.append({
                        'text': clean,
                        'type': entity_type,
                        'score': round(random.uniform(0.70, 0.98), 4)
                    })
                    if len(mock_entities) >= 8:
                        break

            return mock_entities

    def analyze_abstract(self, abstract_text):
        """
        Perform a complete NLP analysis of a paper abstract.
        Combines key phrase extraction, sentiment analysis, and entity detection.

        Args:
            abstract_text (str): The paper abstract to analyze.

        Returns:
            dict: Combined analysis results.
        """
        return {
            'key_phrases': self.extract_key_phrases(abstract_text),
            'sentiment': self.detect_sentiment(abstract_text),
            'entities': self.detect_entities(abstract_text),
            'analyzed_at': datetime.utcnow().isoformat(),
            'word_count': len(abstract_text.split()),
            'character_count': len(abstract_text)
        }

    def get_status(self):
        """
        Check Comprehend service status.

        Returns:
            dict: Service status information.
        """
        if self.use_aws:
            try:
                self.client.detect_dominant_language(Text='test')
                return {'service': 'Comprehend', 'status': 'connected', 'mode': 'aws'}
            except Exception as e:
                return {'service': 'Comprehend', 'status': 'error', 'error': str(e)}
        else:
            return {
                'service': 'Comprehend',
                'status': 'running',
                'mode': 'mock',
                'analyses_cached': len(self.analysis_cache)
            }
