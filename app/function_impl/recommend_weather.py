import requests
import datetime
import os
import logging
from dotenv import load_dotenv
from app.resource.server import get_db_connection, DB_CONFIG
from app.function_impl.recommend_song import recommend_songs

load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 상수 정의
WEATHER_CONFIG = {
    'TEMP_MIN': 10,
    'TEMP_MAX': 35,
    'WIND_MIN': 0,
    'WIND_MAX': 15,
    'HUMIDITY_MIN': 30,
    'HUMIDITY_MAX': 100,
    'TEMPO_MIN': 60,
    'TEMPO_MAX': 211,
    'LOUDNESS_MIN': -21,
    'LOUDNESS_MAX': 0
}

weather_api_key = os.getenv("OPENWEATHER_API_KEY")

# 한글 도시명 → 영문 도시명 변환 딕셔너리
KOR_TO_ENG_CITY = {
    "서울": "Seoul",
    "부산": "Busan",
    "대구": "Daegu",
    "인천": "Incheon",
    "광주": "Gwangju",
    "대전": "Daejeon",
    "울산": "Ulsan",
    "세종": "Sejong",
    "경기": "Gyeonggi-do",
    "강원": "Gangwon-do",
    "충북": "Chungcheongbuk-do",
    "충남": "Chungcheongnam-do",
    "전북": "Jeollabuk-do",
    "전남": "Jeollanam-do",
    "경북": "Gyeongsangbuk-do",
    "경남": "Gyeongsangnam-do",
    "제주": "Jeju-do",
    "성남": "Seongnam",
    "수원": "Suwon",
    "고양": "Goyang",
    "용인": "Yongin",
    # 필요시 추가 도시명...
}

# ✅ 1️⃣ 데이터베이스에서 회원 정보(city) 가져오기
def get_user_city(user_id):
    """ 데이터베이스에서 사용자 city 정보 가져오기 """
    if not user_id:
        raise ValueError("user_id는 필수입니다.")
    
    connection = None
    try:
        connection = get_db_connection(DB_CONFIG)
        with connection.cursor() as cursor:
            query = "SELECT city FROM User WHERE id = %s"
            cursor.execute(query, (int(user_id),))
            result = cursor.fetchone()
            return result[0] if result else None
    except Exception as e:
        logger.error(f"데이터베이스 조회 실패: {e}")
        raise
    finally:
        if connection:
            connection.close()

# ✅ 2️⃣ 날씨 정보 받아오기
def get_weather_data(city, api_key):
    """ 외부 API를 사용하여 날씨 정보를 가져옴 """
    if not city or not api_key:
        raise ValueError("city와 api_key는 필수입니다.")
    
    # 한글 도시명 → 영문 도시명 변환
    city_eng = KOR_TO_ENG_CITY.get(city, city)
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_eng}&appid={api_key}&units=metric&lang=kr"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # 필수 데이터 검증
        if 'weather' not in data or not data['weather']:
            raise ValueError("날씨 정보가 없습니다.")
        if 'main' not in data:
            raise ValueError("기본 날씨 데이터가 없습니다.")
        if 'wind' not in data:
            data['wind'] = {'speed': 0}  # 기본값 설정
        
        weather_main = data['weather'][0]['main']
        temp = float(data['main']['temp'])
        wind = float(data['wind'].get('speed', 0))
        humidity = float(data['main']['humidity'])
        
        # 데이터 유효성 검증
        if not (-50 <= temp <= 60):  # 현실적인 온도 범위
            logger.warning(f"비정상적인 온도값: {temp}")
        if not (0 <= humidity <= 100):
            raise ValueError(f"비정상적인 습도값: {humidity}")
        if wind < 0:
            raise ValueError(f"비정상적인 풍속값: {wind}")
        
        hour = datetime.datetime.now().hour
        
        return {
            "main": weather_main,
            "temp": temp,
            "wind": wind,
            "humidity": humidity,
            "hour": hour
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"날씨 API 호출 실패: {e}")
        raise ValueError(f"날씨 API 호출 실패: {e}")
    except (KeyError, IndexError, ValueError) as e:
        logger.error(f"날씨 데이터 파싱 실패: {e}")
        raise ValueError(f"날씨 데이터 파싱 실패: {e}")

# ✅ 3️⃣ 날씨 → 음악 특성 변환 함수
def normalize(value, min_val, max_val):
    """ 값을 0~1 범위로 정규화 """
    if min_val >= max_val:
        raise ValueError("min_val은 max_val보다 작아야 합니다.")
    
    norm = (value - min_val) / (max_val - min_val)
    return max(0, min(norm, 1))

def weather_to_features_continuous(temp, wind, humidity, weather_main, hour):
    """ 날씨 정보를 음악 특성으로 변환 """
    try:
        # 정규화
        temp_score = normalize(temp, WEATHER_CONFIG['TEMP_MIN'], WEATHER_CONFIG['TEMP_MAX'])
        wind_score = normalize(wind, WEATHER_CONFIG['WIND_MIN'], WEATHER_CONFIG['WIND_MAX'])
        humidity_score = normalize(humidity, WEATHER_CONFIG['HUMIDITY_MIN'], WEATHER_CONFIG['HUMIDITY_MAX'])
        
        # 시간대 및 날씨 조건
        is_night = (hour >= 18 or hour <= 5)
        is_clear = (weather_main == 'Clear')
        is_rain = (weather_main == 'Rain')
        is_late_night = (hour >= 22 or hour <= 5)
        
        # 음악 특성 계산
        danceability = 100 * (0.5 * temp_score + 0.5 * (1 - wind_score))
        popularity = 100 * (0.3 * temp_score + 0.7 * (1 - humidity_score))
        liveness = 100 * (0.4 * is_night + 0.6 * is_clear)
        valence = 100 * (0.6 * is_clear + 0.2 * (1 - wind_score) + 0.2 * (1 - humidity_score))
        energy = 100 * (0.5 * temp_score + 0.5 * (1 - wind_score))
        acousticness = 100 * (0.5 * is_rain + 0.3 * (1 - temp_score) + 0.2 * is_late_night)
        tempo = WEATHER_CONFIG['TEMPO_MIN'] + (temp_score * (WEATHER_CONFIG['TEMPO_MAX'] - WEATHER_CONFIG['TEMPO_MIN']))
        loudness = WEATHER_CONFIG['LOUDNESS_MIN'] + (1 - wind_score) * (WEATHER_CONFIG['LOUDNESS_MAX'] - WEATHER_CONFIG['LOUDNESS_MIN'])
        speechiness = 55 * humidity_score
        
        return {
            "popularity": round(max(0, min(popularity, 100)), 2),
            "danceability": round(max(0, min(danceability, 100)), 2),
            "energy": round(max(0, min(energy, 100)), 2),
            "loudness": round(max(WEATHER_CONFIG['LOUDNESS_MIN'], min(loudness, WEATHER_CONFIG['LOUDNESS_MAX'])), 2),
            "speechiness": round(max(0, min(speechiness, 100)), 2),
            "acousticness": round(max(0, min(acousticness, 100)), 2),
            "liveness": round(max(0, min(liveness, 100)), 2),
            "valence": round(max(0, min(valence, 100)), 2),
            "tempo": round(max(WEATHER_CONFIG['TEMPO_MIN'], min(tempo, WEATHER_CONFIG['TEMPO_MAX'])), 2)
        }
    except Exception as e:
        logger.error(f"음악 특성 변환 실패: {e}")
        raise ValueError(f"음악 특성 변환 실패: {e}")

# # ✅ 6️⃣ 전체 실행 예시
# if __name__ == "__main__":
#     try:
#         # 데이터베이스에서 회원 정보 가져오기
#         user_id = "user123"  # 예제 ID
#         user_city = get_user_city(user_id)

#         if user_city:
#             weather_data = get_weather_data(user_city, weather_api_key)
#             print(f"날씨 데이터: {weather_data}")

#             features = weather_to_features_continuous(
#                 temp=weather_data['temp'],
#                 wind=weather_data['wind'],
#                 humidity=weather_data['humidity'],
#                 weather_main=weather_data['main'],
#                 hour=weather_data['hour']
#             )
#             print(f"음악 특성: {features}")

#             # recommend_song.py 함수 활용
#             recommended = recommend_songs(features, bad_song_list=[])
#             print(f"추천 노래 수: {len(recommended)}")

#             for song in recommended:
#                 print(f"- {song['name']} by {song['artist']}")
#         else:
#             print("사용자 도시 정보를 가져오지 못했습니다.")
            
#     except Exception as e:
#         logger.error(f"실행 중 오류 발생: {e}")
#         print(f"오류: {e}")