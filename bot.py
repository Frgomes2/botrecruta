import os
from urllib.parse import urlparse
import psycopg2
from twitchio.ext import commands
from dotenv import load_dotenv

# Importa seus comandos
from comandos.presentes_comando import PresentesComando
from comandos.votacao_comando import VotacaoComando
from comandos.tinder_comando import TinderComando
from comandos.dado_comando import DadoComando
from comandos.streamer_comando import StreamerComando
from comandos.jogador_comando import JogadorComando
from comandos.personagem_comando import PersonagemComando
from comandos.poke_comando import PokemonComando
from comandos.roubar_comando import RoubarComando

# Carrega variáveis do .env (caso em local)
load_dotenv()

# Twitch configs
token = os.getenv("TWITCH_TOKEN")
client_id = os.getenv("TWITCH_CLIENT_ID")
bot_nick = os.getenv("TWITCH_BOT_NICK")
channel = os.getenv("TWITCH_CHANNEL")

# Banco de dados - via DATABASE_URL
database_url = os.getenv("DATABASE_URL")
if database_url:
    result = urlparse(database_url)
    db_name = result.path.lstrip('/')
    db_user = result.username
    db_password = result.password
    db_host = result.hostname
    db_port = result.port
else:
    raise ValueError("DATABASE_URL não encontrada")

# Verifica se configs estão completas
variaveis_faltando = []
for nome, valor in {
    "TWITCH_TOKEN": token,
    "TWITCH_CLIENT_ID": client_id,
    "TWITCH_BOT_NICK": bot_nick,
    "TWITCH_CHANNEL": channel
}.items():
    if not valor:
        variaveis_faltando.append(nome)

if variaveis_faltando:
    raise ValueError(f"Faltam as seguintes variáveis no .env ou no Railway: {', '.join(variaveis_faltando)}")

# Classe principal do Bot
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=token,
            client_id=client_id,
            nick=bot_nick,
            prefix="!fr",
            initial_channels=[channel]
        )
        self.db_connection = self.connect_to_db()

    def connect_to_db(self):
        try:
            conn = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port
            )
            print("✅ Conexão com o banco de dados estabelecida.")
            return conn
        except psycopg2.Error as err:
            print(f"❌ Erro ao conectar ao banco de dados: {err}")
            return None

    def close_db_connection(self):
        if self.db_connection:
            self.db_connection.close()
            print("🔌 Conexão com o banco de dados fechada.")

    async def event_ready(self):
        print(f"🤖 Bot conectado como {self.nick}")

    async def event_message(self, message):
        await self.handle_commands(message)

    def run(self):
        try:
            super().run()
        finally:
            self.close_db_connection()

# Instancia o bot
bot = MyBot()

# Adiciona todos os comandos (Cogs)
bot.add_cog(PresentesComando(bot))
bot.add_cog(VotacaoComando(bot))
bot.add_cog(TinderComando(bot))
bot.add_cog(DadoComando(bot))
bot.add_cog(StreamerComando(bot))
bot.add_cog(JogadorComando(bot))
bot.add_cog(PersonagemComando(bot))
bot.add_cog(PokemonComando(bot))
bot.add_cog(RoubarComando(bot))

# Executa
if __name__ == "__main__":
    bot.run()
