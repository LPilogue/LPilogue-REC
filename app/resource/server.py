import pymysql

# 데이터베이스 연결 설정
DB_CONFIG = {
    'host': '%',
    'port': 3306,
    'user': 'root',
    'password': '2501',
    'database': 'lpilogue'
}

def get_db_connection(db_config):
    return pymysql.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database']
    )

# 파일 서버 URL
file_server_url="https://lpilogue-cocktail.s3.us-east-2.amazonaws.com/"
# Spotify API 관련 정보
Spotify_token_url="https://accounts.spotify.com/api/token"
Client_id="be13acc55dd6485f8b0d4734f58fe17c"
Client_secret="1c5134749ae94218b0063d241cfac930"
youtube_api="AIzaSyDi7vXulvSaQrfAd3Kc-Qx0WYMpZLiyytE"
