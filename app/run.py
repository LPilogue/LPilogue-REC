from flask import Flask

from app.function_impl.insert_cocktailData import insert_cocktail
from app.function_impl.predict_emotions import predict_emotions
from app.function_impl.recommend_cocktail import recommend_cocktail

app = Flask(__name__)




@app.route("/")
def hello():
    return "Server is running!"

@app.route("/recommend/<sentence>")
def recomhmend(sentence):
    emotions = predict_emotions(sentence)
    recommend_cocktail(emotions)


if __name__ == "__main__":
    # app.run(host="localhost", port=5000)
    # insert_cocktail()
    emotions=[('불안', 0.9832584857940674), ('당황', 0.005890038330107927), ('분노', 0.0058568562380969524)]
    print(recommend_cocktail(emotions))




