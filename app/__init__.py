from flask import Flask




def create_app():
    app = Flask(__name__)

    from app.routes.recommend import recommend_bp
    from app.routes.audio_to_text import audio_bp

    app.register_blueprint(recommend_bp)
    app.register_blueprint(audio_bp)

    return app