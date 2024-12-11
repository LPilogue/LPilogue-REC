from app.resource.colors import get_color, EMOTION_COLORS
from app.resource.server import DB_CONFIG, get_db_connection


def recommend_cocktail(emotions):

    weighted_color=[]
    total_weight=0
    # 감정들의 색상 가져옴
    for emotion in emotions:
        # 감정 색상 가져오기
        emotion_color=get_color(emotion[0])
        # 가중치 가져오기
        weight=emotion[1]
        total_weight+=weight
        # 가중치 적용
        emotion_r=int(emotion_color[1:3],16)*weight
        emotion_g=int(emotion_color[3:5],16)*weight
        emotion_b=int(emotion_color[5:7],16)*weight
        # 가중 색상 저장
        weighted_color.append((emotion_r,emotion_g,emotion_b))

    # 가중 평균 계산
    emotion_r=0
    emotion_g=0
    emotion_b=0
    for color in weighted_color:
        emotion_r+=color[0]
        emotion_g+=color[1]
        emotion_b+=color[2]
    emotion_r=round(emotion_r/total_weight)
    emotion_g=round(emotion_g/total_weight)
    emotion_b=round(emotion_b/total_weight)


    # DB 연결
    db_config=DB_CONFIG
    connection=get_db_connection(db_config)
    with connection.cursor() as cursor:
        # 각 칵테일의 색상 가져오기
        cursor.execute("SELECT color, cocktailDataId FROM CocktailData")
        colors = cursor.fetchall()
        min_distance=1000000000
        for color in colors:
            cocktail_r=int(color[0][1:3],16)
            cocktail_g=int(color[0][3:5],16)
            cocktail_b=int(color[0][5:7],16)

            # 색상 거리 계산
            distance=((emotion_r-cocktail_r)**2+(emotion_g-cocktail_g)**2+(emotion_b-cocktail_b)**2)**0.5
            if distance<min_distance:
                min_distance=distance
                cocktail_id=color[1]

        # 추천 칵테일 정보 가져오기
        cursor.execute("SELECT name, filePath, ingredients, description FROM CocktailData WHERE cocktailDataId=%s", (cocktail_id,))
        cocktail = cursor.fetchone()

        cocktail_info={
            "name": cocktail[0],
            "filePath": cocktail[1],
            "description": cocktail[3]
        }
        return cocktail_info


