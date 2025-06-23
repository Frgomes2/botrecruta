import random
from twitchio.ext import commands

class TinderComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='tinder')
    async def tinder(self, ctx):
        cursor = None
        try:
            db_connection = self.bot.db_connection
            if db_connection is None:
                await ctx.send("❌ Erro de conexão com o banco de dados. Tente novamente mais tarde.")
                return

            bots_excluidos = ["streamelements", "nightbot", "creatisbot", "streamlabs", "botrecruta"]
            participantes = [user.name for user in ctx.channel.chatters if user.name != ctx.author.name and user.name not in bots_excluidos]

            if not participantes:
                await ctx.send("🚫 Não há outros usuários no chat para gerar o match! Aguarde até que outros entrem. 🚫")
                return

            parceiro = random.choice(participantes)
            porcentagem = random.randint(0, 100)

            cursor = db_connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT mensagem 
                FROM mensagens 
                WHERE tipo_funcao = 'match' 
                AND min_porcentagem <= %s 
                AND max_porcentagem >= %s 
                ORDER BY RANDOM() LIMIT 1
            """, (porcentagem, porcentagem))
            mensagem_info = cursor.fetchone()

            if mensagem_info:
                mensagem = mensagem_info['mensagem'].format(
                    user1=ctx.author.name,
                    user2=parceiro,
                    porcentagem=porcentagem
                )
                await ctx.send(mensagem)
            else:
                await ctx.send(f"{ctx.author.name} e {parceiro} deram match com {porcentagem}%, mas nenhuma mensagem foi encontrada.")

        except Exception as e:
            print(f"Erro ao executar o comando tinder: {e}")
            await ctx.send("❌ Ocorreu um erro ao processar o comando. Tente novamente mais tarde.")

        finally:
            if cursor:
                cursor.close()
