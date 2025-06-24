import os
import psycopg2
import urllib.parse as urlparse

def conectar_postgresql():
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise Exception("DATABASE_URL não está definida.")

        # Parseia a URL
        result = urlparse.urlparse(database_url)
        username = result.username
        password = result.password
        database = result.path.lstrip('/')
        hostname = result.hostname
        port = result.port

        # Conecta ao banco
        return psycopg2.connect(
            dbname=database,
            user=username,
            password=password,
            host=hostname,
            port=port
        )

    except Exception as e:
        print("Erro ao conectar no banco de dados:", e)
        return None
