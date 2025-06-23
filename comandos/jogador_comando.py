import random
from twitchio.ext import commands
import logging

class JogadorComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='jogador')
    async def jogador(self, ctx, *, alvo: str = None):
        try:
            alvo = alvo or ctx.author.name
            db_connection = self.bot.db_connection

            if db_connection is None:
                await ctx.send("❌ Erro de conexão com o banco de dados. Tente novamente mais tarde.")
                return

            with db_connection.cursor() as cursor:
                cursor.execute("SELECT nome FROM jogadores ORDER BY RANDOM() LIMIT 1")
                jogador_info = cursor.fetchone()

                if not jogador_info:
                    await ctx.send("❌ Nenhum jogador foi encontrado para o comando.")
                    return

                jogador = jogador_info[0]
                porcentagem = random.randint(0, 100)

                cursor.execute("""
                    SELECT mensagem 
                    FROM mensagens 
                    WHERE tipo_funcao = 'jogador' 
                    AND min_porcentagem <= %s 
                    AND max_porcentagem >= %s 
                    ORDER BY RANDOM() LIMIT 1
                """, (porcentagem, porcentagem))

                mensagem_info = cursor.fetchone()

                if mensagem_info:
                    mensagem = mensagem_info[0].format(alvo=alvo, jogador=jogador, porcentagem=porcentagem)
                    await ctx.send(mensagem)
                else:
                    await ctx.send(f"⚠️ {alvo}, não encontramos uma mensagem adequada para essa compatibilidade.")

        except Exception as e:
            logging.error(f"Erro ao executar o comando jogador: {e}")
            await ctx.send("❌ Ocorreu um erro ao processar o comando. Tente novamente mais tarde.")
