import pprint

from flask import jsonify, request, Blueprint

from app.function_impl.predict_emotions import predict_emotions
from app.function_impl.recommend_cocktail import recommend_cocktail
from app.function_impl.recommend_song import recommend_songs
from app.model.emotion_music_mapper import EmotionMusicMapper

recommend_bp=Blueprint("recommend", __name__)

@recommend_bp.route("/", methods=["GET"])
def hello():
    return "Server is running!"

@recommend_bp.route("/recommend", methods=["POST"])
def recommend():

    data = request.get_json()
    if data is None:
        return jsonify({"error": "No data provided."}), 400

    content=data['content']
    badSongList=data['badSongList']

    # 감정 예측
    emotions = predict_emotions(content)
    pprint.pprint(emotions)
    # 칵테일 추천
    cocktail = recommend_cocktail(emotions)

    # 노래 추천

    mapper = EmotionMusicMapper()
    song_features = mapper.process_emotion_data(emotions)
    songs = recommend_songs(song_features, badSongList)

    response = {"cocktail": cocktail, "songs": songs}

    return jsonify(response)