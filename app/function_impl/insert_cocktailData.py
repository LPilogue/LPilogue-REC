from sqlalchemy import create_engine
import pandas as pd
import os

from app.resource.server import file_server_url, get_db_connection, DB_CONFIG


def insert_cocktail():
    file_path = "C:/Users/wlswn/Downloads/cocktail_colored.csv"
    df = pd.read_csv(file_path)
    print(df.head())
    # 데이터베이스 연결 설정
    db_config=DB_CONFIG
    # SQLAlchemy 엔진 생성
    engine = create_engine(
        f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")
    # 테이블로 데이터 삽입
    table_name = 'Cocktail'
    df.to_sql(table_name, con=engine, if_exists='append', index=False)
    print("Data inserted successfully.")
    # 파일 경로 업데이트

    connection=get_db_connection(db_config)
    with connection.cursor() as cursor:
            # 칵테일 이름 가져오기
            cursor.execute("SELECT id, name FROM Cocktail")
            cocktails = cursor.fetchall()  # [(id, name), ...]

            # 각 칵테일의 파일 경로 생성 및 업데이트
            for cocktail_id, name in cocktails:
                # 칵테일 이름으로 파일 경로 생성
                file_path = os.path.join(file_server_url, f"{name.replace(' ', '_')}.png")

                # 파일 경로 업데이트
                update_query = "UPDATE Cocktail SET imagePath = %s WHERE id = %s"
                cursor.execute(update_query, (file_path, cocktail_id))

            # 변경사항 커밋
            connection.commit()
            print("File paths updated successfully!")

