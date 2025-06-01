import pprint
import os
import logging
from flask import jsonify, request, Blueprint

from app.function_impl.insert_cocktailData import insert_cocktail
from app.function_impl.predict_emotions import predict_emotions
from app.function_impl.recommend_cocktail import recommend_cocktail
from app.function_impl.recommend_song import recommend_songs
from app.model.emotion_music_mapper import EmotionMusicMapper
from app.function_impl.recommend_weather import (
    get_user_city,
    get_weather_data,
    weather_to_features_continuous
)
from dotenv import load_dotenv

load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

weather_api_key = os.getenv("OPENWEATHER_API_KEY")

recommend_bp = Blueprint("recommend", __name__)
mapper = EmotionMusicMapper()


@recommend_bp.route("/", methods=["GET"])
def hello():
    return "Server is running!"


@recommend_bp.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "JSON 데이터가 제공되지 않았습니다."}), 400

    recommend_type = data.get("type")
    bad_song_list = data.get("badSongList", [])

    if not recommend_type:
        return jsonify({"error": "추천 타입이 필요합니다."}), 400

    if not isinstance(bad_song_list, list):
        bad_song_list = []

    if recommend_type == "emotion":
        return handle_emotion_recommendation(data, bad_song_list)
    elif recommend_type == "weather":
        return handle_weather_recommendation(data, bad_song_list)
    else:
        return jsonify({
            "error": "유효하지 않은 타입입니다. 'emotion' 또는 'weather'를 사용하세요."
        }), 400


def handle_emotion_recommendation(data, bad_song_list):
    """ 감정 기반 추천 처리 """
    try:
        content = data.get("content")
        if not content:
            return jsonify({
                "error": "감정 추천을 위해서는 content가 필요합니다."
            }), 400

        if not isinstance(content, str) or len(content.strip()) == 0:
            return jsonify({
                "error": "content는 비어있지 않은 문자열이어야 합니다."
            }), 400

        # 감정 분석
        emotions = predict_emotions(content)
        if not emotions:
            return jsonify({
                "error": "감정 분석에 실패했습니다."
            }), 500

        logger.info(f"감정 분석 결과: {emotions}")

        # 칵테일 추천
        cocktail = recommend_cocktail(emotions)

        # 음악 특성 매핑
        mapper_local = EmotionMusicMapper()
        song_features = mapper_local.process_emotion_data(emotions)

        if not song_features:
            return jsonify({
                "error": "음악 특성 변환에 실패했습니다."
            }), 500

        # 노래 추천
        songs = recommend_songs(song_features, bad_song_list)

        return jsonify({
            "type": "emotion",
            "emotions": emotions,
            "cocktail": cocktail,
            "songs": songs,
            "total_songs": len(songs) if songs else 0
        })

    except Exception as e:
        logger.error(f"감정 기반 추천 처리 중 오류: {e}")
        return jsonify({
            "error": "감정 기반 추천 처리 중 오류가 발생했습니다.",
            "details": str(e)
        }), 500


def handle_weather_recommendation(data, bad_song_list):
    """ 날씨 기반 추천 처리 """
    try:
        user_id = data.get("user_id")
        if not user_id:
            return jsonify({
                "error": "날씨 추천을 위해서는 user_id가 필요합니다."
            }), 400

        if not isinstance(user_id, str) or len(user_id.strip()) == 0:
            return jsonify({
                "error": "user_id는 비어있지 않은 문자열이어야 합니다."
            }), 400

        if not weather_api_key:
            return jsonify({
                "error": "날씨 API 키가 설정되지 않았습니다."
            }), 500

        # DB에서 city 가져오기
        try:
            city = get_user_city(int(str(user_id).strip()))
        except Exception as e:
            logger.error(f"사용자 도시 조회 실패: {e}")
            return jsonify({
                "error": "사용자 정보를 가져오는데 실패했습니다.",
                "details": str(e)
            }), 500

        if not city:
            return jsonify({
                "error": "해당 사용자의 도시 정보를 찾을 수 없습니다."
            }), 404

        # OpenWeather API 호출
        try:
            weather = get_weather_data(city, weather_api_key)
        except Exception as e:
            logger.error(f"날씨 정보 조회 실패: {e}")
            return jsonify({
                "error": "날씨 정보를 가져오는데 실패했습니다.",
                "details": str(e)
            }), 500

        # 날씨 → 음악 특성 변환
        try:
            song_features = weather_to_features_continuous(
                temp=weather['temp'],
                wind=weather['wind'],
                humidity=weather['humidity'],
                weather_main=weather['main'],
                hour=weather['hour']
            )
        except Exception as e:
            logger.error(f"음악 특성 변환 실패: {e}")
            return jsonify({
                "error": "음악 특성 변환에 실패했습니다.",
                "details": str(e)
            }), 500

        # 노래 추천
        try:
            songs = recommend_songs(song_features, bad_song_list)
        except Exception as e:
            logger.error(f"날씨 기반 노래 추천 실패: {e}")
            return jsonify({
                "error": "노래 추천에 실패했습니다.",
                "details": str(e)
            }), 500

        return jsonify({
            "type": "weather",
            "city": city,
            "weather": {
                "main":     weather['main'],
                "temp":     weather['temp'],
                "wind":     weather['wind'],
                "humidity": weather['humidity'],
                "hour":     weather['hour']
            },
            "song_features": song_features,
            "songs": songs,
            "total_songs": len(songs) if songs else 0
        })

    except Exception as e:
        logger.error(f"날씨 기반 추천 처리 중 오류: {e}")
        return jsonify({
            "error": "날씨 기반 추천 처리 중 오류가 발생했습니다.",
            "details": str(e)
        }), 500


@recommend_bp.route("/api/recommendations/cocktails", methods=["POST"])
def cocktail_recommendation():
    """ 칵테일 단독 추천 """
    data = request.get_json()
    content = data['content']
    emotions = predict_emotions(content)
    cocktail = recommend_cocktail(emotions)
    return jsonify({"emotion": emotions[0], "cocktail": cocktail})


@recommend_bp.route("/api/recommendations/songs", methods=["POST"])
def song_recommendation():
    """ 노래 단독 추천 """
    data = request.get_json()
    content = data['content']
    bad_song_list = data['badSongList']
    emotions = predict_emotions(content)
    song_features = mapper.process_emotion_data(emotions)
    songs = recommend_songs(song_features, bad_song_list)
    return jsonify(songs)