import pymysql
from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일에서 환경 변수 불러오기

DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'port': int(os.getenv("DB_PORT")),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_NAME")
}

def get_db_connection(db_config):
    return pymysql.connect(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        charset='utf8mb4'
    )


# 파일 서버 URL
file_server_url="https://lpilogue-cocktail.s3.us-east-2.amazonaws.com/"
# Spotify API 관련 정보
Spotify_token_url="https://accounts.spotify.com/api/token"
Client_id="be13acc55dd6485f8b0d4734f58fe17c"
Client_secret="1c5134749ae94218b0063d241cfac930"
youtube_api="AIzaSyDi7vXulvSaQrfAd3Kc-Qx0WYMpZLiyytE"
