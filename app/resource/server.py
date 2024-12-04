import pymysql

DB_CONFIG = {
    'host': 'localhost',
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


file_server_url="https://lpilogue-cocktail.s3.us-east-2.amazonaws.com/"