from flask import Flask
from flask_cors import CORS



def create_app():
    app = Flask(__name__)
    CORS(app, resources={
        r"/*": {
            "origins": ["*"],  # 모든 도메인에서의 접근 허용
            "methods": ["GET", "POST", "OPTIONS"],  # 허용할 HTTP 메서드
            "allow_headers": ["Content-Type", "Authorization"]  # 허용할 헤더
        }
    })

    from app.routes.recommend import recommend_bp
    from app.routes.audio_to_text import audio_bp
    from app.routes.chatbot import chatbot_bp

    app.register_blueprint(recommend_bp)
    app.register_blueprint(audio_bp)
    app.register_blueprint(chatbot_bp)

    return app