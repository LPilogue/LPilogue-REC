from flask import Flask, jsonify

from app.function_impl.insert_cocktailData import insert_cocktail
from app.function_impl.predict_emotions import predict_emotions
from app.function_impl.recommend_cocktail import recommend_cocktail
from app.model.emotion_music_mapper import EmotionMusicMapper

app = Flask(__name__)




@app.route("/")
def hello():
    return "Server is running!"

@app.route("/recommend/<sentence>")
def recomhmend(sentence):
    # 감정 예측
    emotions = predict_emotions(sentence)
    # 칵테일 추천
    cocktail = recommend_cocktail(emotions)
    return jsonify(cocktail)
    # 노래 추천



if __name__ == "__main__":
    # app.run(host="localhost", port=5000)
    # insert_cocktail()
    # get_access_token()
    # 사용 예시
    mapper = EmotionMusicMapper()

    # 테스트
    emotions = [
        ('기쁨', 0.9832584857940674),
        ('당황', 0.005890038330107927),
        ('분노', 0.0058568562380969524)
    ]

    result = mapper.process_emotion_data(emotions)
    print("\n감정과 음악 특성 매핑 결과:")
    for feature, value in result.items():
        print(f"{feature}: {value}")




