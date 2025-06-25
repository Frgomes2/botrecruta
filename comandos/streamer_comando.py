import random
from twitchio.ext import commands

class StreamerComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='streamer')
    async def streamer(self, ctx, *, alvo: str = None):
        try:
            alvo = alvo or ctx.author.name
            db_connection = self.bot.db_connection

            if db_connection is None:
                await ctx.send("❌ Erro de conexão com o banco de dados. Tente novamente mais tarde.")
                return

            cursor = db_connection.cursor(dictionary=True)
            cursor.execute("SELECT nome FROM streamers ORDER BY RANDOM() LIMIT 1")
            streamer_info = cursor.fetchone()

            if not streamer_info:
                await ctx.send("🎥 Nenhum streamer foi encontrado para o comando.")
                return

            streamer = streamer_info['nome']
            porcentagem = random.randint(0, 100)

            cursor.execute("""
                SELECT mensagem  
                FROM tb_mensagens 
                WHERE tipo_funcao = 'streamer' 
                AND min_porcentagem <= %s 
                AND max_porcentagem >= %s 
                ORDER BY RANDOM() LIMIT 1
            """, (porcentagem, porcentagem))
            mensagem_info = cursor.fetchone()

            if mensagem_info:
                mensagem = mensagem_info['mensagem'].format(
                    alvo=alvo,
                    streamer=streamer,
                    porcentagem=porcentagem
                )
                await ctx.send(mensagem)
            else:
                await ctx.send(f"{alvo}, não encontramos uma mensagem adequada para essa compatibilidade.")

        except Exception as e:
            print(f"Erro ao executar o comando streamer: {e}")
            await ctx.send("❌ Ocorreu um erro ao processar o comando. Tente novamente mais tarde.")

        finally:
            if cursor:
                cursor.close()
