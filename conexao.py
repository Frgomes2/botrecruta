import os
from urllib.parse import urlparse

# Detecta ambiente
env = os.getenv("ENV", "development")

# Importações condicionais conforme o ambiente
if env == "production":
    import psycopg2
else:
    import mysql.connector

def conectar_postgresql():
    print("🔍 DEBUG ENV:", env)

    if env == "production":
        # Conexão para o Railway com PostgreSQL
        url = os.getenv("DATABASE_URL")
        if not url:
            print("❌ DATABASE_URL não encontrada.")
            return None

        result = urlparse(url)
        print("🔍 DEBUG DB:")
        print("Host:", result.hostname)
        print("User:", result.username)
        print("DB:", result.path.lstrip('/'))
        print("Port:", result.port)

        try:
            conn = psycopg2.connect(
                dbname=result.path.lstrip('/'),
                user=result.username,
                password=result.password,
                host=result.hostname,
                port=result.port
            )
            print("✅ Conexão com o PostgreSQL (Railway) estabelecida.")
            return conn
        except Exception as e:
            print(f"❌ Erro ao conectar ao PostgreSQL: {e}")
            return None

    else:
        # Conexão local usando MySQL
        try:
            conn = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", ""),
                database=os.getenv("DB_NAME", "twitch")
            )
            print("✅ Conexão com o MySQL (local) estabelecida.")
            return conn
        except Exception as e:
            print(f"❌ Erro ao conectar ao MySQL local: {e}")
            return None
