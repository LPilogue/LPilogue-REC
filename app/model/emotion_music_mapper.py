import pickle

import numpy as np
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine

class EmotionMusicMapper:
    def __init__(self):

        # 더 가벼운 모델로 변경
        self.model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2', device='cpu')


        # 음악 특성에 대한 설명적 단어들 정의
        self.feature_descriptions = {
            'popularity': ['인기 있는', '대중적인', '유명한', '히트한'],
            'danceability': ['댄서블한', '리듬감 있는', '춤추기 좋은'],
            'energy': ['에너지 넘치는', '활기찬', '파워풀한'],
            'loudness': ['큰 소리의', '시끄러운', '강한 볼륨의'],
            'speechiness': ['대사가 많은', '보컬 중심의', '말하는 듯한'],
            'acousticness': ['어쿠스틱한', '자연스러운', '악기 소리의'],
            'liveness': ['라이브같은', '현장감 있는', '콘서트 같은'],
            'valence': ['긍정적인', '희망적인', '밝은 느낌의'],
            'tempo': ['빠른', '템포가 빠른', '경쾌한']
        }

        # 각 특성의 범위
        self.feature_ranges = {
            'popularity': (0, 100),
            'danceability': (0, 1),
            'energy': (0, 1),
            'loudness': (-21, 1.3),
            'speechiness': (0, 1),
            'acousticness': (0, 1),
            'liveness': (0, 1),
            'valence': (0, 1),
            'tempo': (37, 215)
        }



    def get_embeddings(self, words):
        """노래 features의 임베딩을 반환"""
        embeddings = self.model.encode(words)
        return np.mean(embeddings, axis=0)

    def calculate_feature_similarity(self, emotion_embedding, feature_words, ):
        """감정과 노래 features들 간의 유사도 계산"""
        feature_embedding = self.get_embeddings(feature_words)
        return 1 - cosine(emotion_embedding, feature_embedding)

    def process_emotion_data(self, emotion_data):
        result = {}

        # 전체 감정의 임베딩 계산
        weighted_emotion_embedding = np.zeros(384)  # SBERT 임베딩 차원
        for emotion, weight in emotion_data:
            emotion_embedding = self.model.encode(emotion)
            weighted_emotion_embedding += emotion_embedding * weight

        # 각 특성에 대한 유사도 계산 및 스케일링
        for feature, description_words in self.feature_descriptions.items():
            similarity = self.calculate_feature_similarity(
                weighted_emotion_embedding,
                description_words
            )

            # 특성별 범위로 스케일링
            min_val, max_val = self.feature_ranges[feature]



            # 유사도를 해당 특성의 범위로 스케일링
            scaled_value = (similarity * (max_val - min_val)) + min_val
            result[feature]=float(np.clip(scaled_value, min_val, max_val))

        return result



