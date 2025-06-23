import random
from twitchio.ext import commands

class TinderComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='tinder')
    async def tinder(self, ctx):
        try:
            # Exibe a lista de chatters para depuração
            print(f"Chatters no canal {ctx.channel.name}: {ctx.channel.chatters}")

            # Conecta ao banco de dados
            db_connection = self.bot.db_connection
            if db_connection is None:
                await ctx.send("Erro de conexão com o banco de dados. Tente novamente mais tarde.")
                return

            # Escolhe um streamer aleatório do banco de dados
            cursor = db_connection.cursor(dictionary=True)

            # Lista de bots a serem desconsiderados
            bots_excluidos = ["streamelements", "nightbot",  "creatisbot", "streamlabs", "botrecruta"]

            # Verifica se o comando está sendo executado em um canal válido
            if not ctx.channel.chatters:
                await ctx.send("🚫 Não há participantes no chat para gerar o match! Aguarde até que outros entrem. 🚫")
                return

            # Obtém os usuários ativos no chat, excluindo o autor do comando e os bots desconsiderados
            participantes = [user.name for user in ctx.channel.chatters if user.name != ctx.author.name and user.name not in bots_excluidos]

            if not participantes:
                await ctx.send("🚫 Não há outros usuários no chat para gerar o match! Aguarde até que outros entrem. 🚫")
                return

            # Escolhe um parceiro aleatório da lista de participantes
            parceiro = random.choice(participantes)

            # Gera uma porcentagem aleatória de 0 a 100
            porcentagem = random.randint(0, 100)


            # Consulta as mensagens da tabela de mensagens baseadas na função "streamer" e na porcentagem
            if porcentagem >= 50:
                # Mensagens tristes
                cursor.execute( "SELECT mensagem  FROM mensagens WHERE tipo_funcao = 'match' AND max_porcentagem = 100    ORDER BY RAND() LIMIT 1")
            else:
                # Mensagens tristes
                cursor.execute("SELECT mensagem  FROM mensagens WHERE tipo_funcao = 'match' AND max_porcentagem = 50    ORDER BY RAND() LIMIT 1")


            mensagem_info = cursor.fetchone()
            mensagem = mensagem_info['mensagem'].format(user1=ctx.author.name, user2=parceiro, porcentagem=porcentagem)
            await ctx.send(mensagem)


        except Exception as e:
            print(f"Erro ao executar o comando tinder: {e}")  # Exibe o erro
            await ctx.send("Desculpe, ocorreu um erro ao processar seu pedido. Tente novamente mais tarde.")
