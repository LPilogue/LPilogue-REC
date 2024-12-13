import pprint

from flask import Flask, jsonify, request

from app.function_impl.insert_cocktailData import insert_cocktail
from app.function_impl.predict_emotions import predict_emotions
from app.function_impl.recommend_cocktail import recommend_cocktail
from app.function_impl.recommend_song import recommend_songs
from app.model.emotion_music_mapper import EmotionMusicMapper

app = Flask(__name__)




@app.route("/")
def hello():
    return "Server is running!"

@app.route("/recommend", methods=["POST"])
def recommend(content):

    data = request.get_json()
    if data is None:
        return jsonify({"error": "No data provided."}), 400

    content=data['content']
    # 감정 예측
    emotions = predict_emotions(content)
    pprint.pprint(emotions)
    # 칵테일 추천
    cocktail = recommend_cocktail(emotions)

    # 노래 추천
    mapper = EmotionMusicMapper()
    song_features = mapper.process_emotion_data(emotions)
    songs = recommend_songs(song_features)

    response = {"cocktail": cocktail, "songs": songs}

    return jsonify(response)



if __name__ == "__main__":
    app.run(host="localhost", port=5000)
    # insert_cocktail()







