from flask import Flask
from flasgger import Swagger
from app.routes.recommend import recommend_bp
from app.routes.chatbot import chatbot_bp



app = Flask(__name__, static_url_path="/api/rec/flasgger_static")

# Swagger 설정
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/rec/docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "LPilogue Recommendation API",
        "description": "감정 및 날씨 기반 음악 추천 API",
        "version": "1.0.0"
    }
    
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Blueprint 등록
app.register_blueprint(recommend_bp, url_prefix="/api/rec")
app.register_blueprint(chatbot_bp, url_prefix="/api/rec")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
