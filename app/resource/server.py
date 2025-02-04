from dotenv import load_dotenv, find_dotenv
import os
import pymysql

# .env 파일 로드
load_dotenv(find_dotenv())

# 환경 변수에서 설정 불러오기
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 3306)),  # 기본값 설정
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def get_db_connection(db_config):
    return pymysql.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database']
    )

file_server_url = os.getenv('FILE_SERVER_URL')
Client_id = os.getenv('SPOTIFY_CLIENT_ID')
Client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
youtube_api = os.getenv('YOUTUBE_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
