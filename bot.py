# Importações
import os
import mysql.connector
from twitchio.ext import commands
from dotenv import load_dotenv
from comandos.presentes_comando import PresentesComando
from comandos.votacao_comando import VotacaoComando
from comandos.tinder_comando import TinderComando
from comandos.dado_comando import DadoComando
from comandos.streamer_comando import StreamerComando
from comandos.jogador_comando import JogadorComando
from comandos.personagem_comando import PersonagemComando
from comandos.poke_comando import PokemonComando
from comandos.roubar_comando import RoubarComando

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Obter as variáveis de ambiente
token = os.getenv("TWITCH_TOKEN")
client_id = os.getenv("TWITCH_CLIENT_ID")
bot_nick = os.getenv("TWITCH_BOT_NICK")
channel = os.getenv("TWITCH_CHANNEL")
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

# Verificar se as variáveis estão configuradas
if not token or not client_id or not bot_nick or not channel:
    raise ValueError("Faltando configurações no arquivo .env")

# Classe do bot
class MyBot(commands.Bot):

    def __init__(self):
        super().__init__(
            token=token,
            client_id=client_id,
            nick=bot_nick,
            prefix="!fr",
            initial_channels=[channel]
        )
        # Conectar ao banco de dados
        self.db_connection = self.connect_to_db()

    def connect_to_db(self):
        """Conectar ao banco de dados MySQL."""
        try:
            connection = mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name
            )
            print("Conexão com o banco de dados estabelecida com sucesso.")
            return connection
        except mysql.connector.Error as err:
            print(f"Erro ao conectar ao banco de dados: {err}")
            return None

    def close_db_connection(self):
        """Fecha a conexão com o banco de dados."""
        if self.db_connection:
            self.db_connection.close()
            print("Conexão com o banco de dados fechada.")

    async def event_ready(self):
        print(f'Bot conectado como {self.nick}')

    async def event_message(self, message):
        # Adiciona o processamento dos comandos recebidos
        await self.handle_commands(message)

    def run(self):
        """Inicia o bot e configura o fechamento da conexão ao final."""
        try:
            super().run()
        finally:
            self.close_db_connection()


# Criação da instância do bot
bot = MyBot()

# Registra os Cogs (comandos) no bot, passando a conexão como argumento
bot.add_cog(PresentesComando(bot))
bot.add_cog(VotacaoComando(bot))
bot.add_cog(TinderComando(bot))
bot.add_cog(DadoComando(bot))
bot.add_cog(StreamerComando(bot))
bot.add_cog(JogadorComando(bot))
bot.add_cog(PersonagemComando(bot))
bot.add_cog(PokemonComando(bot))
bot.add_cog(RoubarComando(bot))


# Rodar o bot
if __name__ == "__main__":
    bot.run()
