import os
import psycopg2
from twitchio.ext import commands
from dotenv import load_dotenv

# Importação dos comandos
from comandos.presentes_comando import PresentesComando
from comandos.votacao_comando import VotacaoComando
from comandos.tinder_comando import TinderComando
from comandos.dado_comando import DadoComando
from comandos.streamer_comando import StreamerComando
from comandos.jogador_comando import JogadorComando
from comandos.personagem_comando import PersonagemComando
from comandos.poke_comando import PokemonComando
from comandos.roubar_comando import RoubarComando

# Carregar as variáveis do .env
load_dotenv()

# Twitch configs
token = os.getenv("TWITCH_TOKEN")
client_id = os.getenv("TWITCH_CLIENT_ID")
bot_nick = os.getenv("TWITCH_BOT_NICK")
channel = os.getenv("TWITCH_CHANNEL")

# PostgreSQL configs
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
db_port = os.getenv("DB_PORT", "5432")  # valor padrão

# Verifica todas as variáveis essenciais
variaveis_faltando = []
if not token: variaveis_faltando.append("TWITCH_TOKEN")
if not client_id: variaveis_faltando.append("TWITCH_CLIENT_ID")
if not bot_nick: variaveis_faltando.append("TWITCH_BOT_NICK")
if not channel: variaveis_faltando.append("TWITCH_CHANNEL")
if not db_host: variaveis_faltando.append("DB_HOST")
if not db_user: variaveis_faltando.append("DB_USER")
if not db_password: variaveis_faltando.append("DB_PASSWORD")
if not db_name: variaveis_faltando.append("DB_NAME")
if not db_port: variaveis_faltando.append("DB_PORT")

if variaveis_faltando:
    raise ValueError(f"Faltam as seguintes variáveis no .env ou no Railway: {', '.join(variaveis_faltando)}")

# Bot class
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
        print(f'🤖 Bot conectado como {self.nick}')

    async def event_message(self, message):
        await self.handle_commands(message)

    def run(self):
        try:
            super().run()
        finally:
            self.close_db_connection()

# Instancia e registra os comandos
bot = MyBot()

bot.add_cog(PresentesComando(bot))
bot.add_cog(VotacaoComando(bot))
bot.add_cog(TinderComando(bot))
bot.add_cog(DadoComando(bot))
bot.add_cog(StreamerComando(bot))
bot.add_cog(JogadorComando(bot))
bot.add_cog(PersonagemComando(bot))
bot.add_cog(PokemonComando(bot))
bot.add_cog(RoubarComando(bot))

# Inicia o bot
if __name__ == "__main__":
    bot.run()
