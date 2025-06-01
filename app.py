from flask import Flask
from app.routes.recommend import recommend_bp

app = Flask(__name__)
app.register_blueprint(recommend_bp, url_prefix="/")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
