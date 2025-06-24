import os
import psycopg2
from urllib.parse import urlparse

def conectar_postgresql():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL não encontrada.")

    result = urlparse(database_url)

    db_name = result.path.lstrip('/')
    db_user = result.username
    db_password = result.password
    db_host = result.hostname
    db_port = result.port or 5432

    print(f"🔍 DEBUG DB:\nHost: {db_host}\nUser: {db_user}\nDB: {db_name}\nPort: {db_port}")

    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            sslmode='require'  # Railway exige SSL em alguns casos
        )
        print("✅ Conexão com o banco de dados estabelecida.")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return None
