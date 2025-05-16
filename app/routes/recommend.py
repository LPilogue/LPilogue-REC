import pprint

from flask import jsonify, request, Blueprint

from app.function_impl.insert_cocktailData import insert_cocktail
from app.function_impl.predict_emotions import predict_emotions
from app.function_impl.recommend_cocktail import recommend_cocktail
from app.function_impl.recommend_song import recommend_songs
from app.model.emotion_music_mapper import EmotionMusicMapper

recommend_bp=Blueprint("recommend", __name__)

mapper = EmotionMusicMapper()

@recommend_bp.route("/", methods=["GET"])
def hello():
    return "Server is running!"



@recommend_bp.route("/api/recommendations/cocktails", methods=["POST"])
def cocktail_recommendation():
    """
    칵테일 추천 API
    """
    try:
        data = request.get_json()
        if data is None:
            return jsonify({"error": "No data provided."}), 400

        content = data['content']
        # 감정 예측
        emotions = predict_emotions(content)
        pprint.pprint(emotions)
        # 칵테일 추천
        cocktail = recommend_cocktail(emotions)
        pprint.pprint(cocktail)

        if cocktail is None:
            return jsonify({"error": "No cocktail provided."}), 400

        return jsonify(cocktail)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recommend_bp.route("/api/recommendations/songs", methods=["POST"])
def song_recommendation():
    """
    노래 추천 API
    """
    try:
        data = request.get_json()
        if data is None:
            return jsonify({"error": "No data provided."}), 400

        content = data['content']
        badSongList = data['badSongList']

        # 감정 예측
        emotions = predict_emotions(content)
        pprint.pprint(emotions)

        # 노래 추천
        song_features = mapper.process_emotion_data(emotions)

        if song_features is None:
            return jsonify({"error": "No song features provided."}), 400

        songs = recommend_songs(song_features, badSongList)

        if songs is None:
            return jsonify({"error": "No songs provided."}), 400

        return jsonify(songs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500