import os
from dotenv import load_dotenv

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

def carregar_configuracoes():
    return {
        'TOKEN': os.getenv('TOKEN'),
        'CLIENT_ID': os.getenv('CLIENT_ID'),
        'BOT_NICK': os.getenv('BOT_NICK'),
        'CHANNEL': os.getenv('CHANNEL'),
    }
