from flask import Flask

from app.function_impl.insert_cocktailData import insert_cocktail
from app.function_impl.predict_emotions import predict_emotions


app = Flask(__name__)




@app.route("/")
def hello():
    return "Server is running!"

@app.route("/recommend/<sentence>")
def recomhmend(sentence):
    emotions = predict_emotions(sentence)



if __name__ == "__main__":
    # app.run(host="localhost", port=5000)
    insert_cocktail()



