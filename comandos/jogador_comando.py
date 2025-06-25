import random
import logging
from twitchio.ext import commands

class JogadorComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='jogador')
    async def jogador(self, ctx, *, alvo: str = None):
        try:
            alvo = (alvo or ctx.author.name).lstrip('@').strip()
            db = self.bot.db_connection

            if not db:
                await ctx.send("❌ Erro de conexão com o banco de dados. Tente novamente mais tarde.")
                return

            with db.cursor() as cursor:
                # Escolhe jogador aleatório
                cursor.execute("SELECT nome FROM jogadores ORDER BY RAND() LIMIT 1")
                row = cursor.fetchone()
                if not row:
                    await ctx.send("❌ Nenhum jogador foi encontrado no banco de dados.")
                    return

                jogador = row[0]
                porcentagem = random.randint(0, 100)

                # Busca mensagem compatível com a % sorteada
                cursor.execute("""
                    SELECT mensagem
                    FROM tb_mensagens 
                    WHERE tipo_funcao = 'jogador' 
                    AND min_porcentagem <= %s AND max_porcentagem >= %s
                    ORDER BY RAND() LIMIT 1
                """, (porcentagem, porcentagem))
                msg_row = cursor.fetchone()

                if msg_row:
                    mensagem = msg_row[0].format(alvo=alvo, jogador=jogador, porcentagem=porcentagem)
                    await ctx.send(mensagem)
                else:
                    await ctx.send(f"⚠️ {alvo}, não encontramos uma mensagem para {porcentagem}% de compatibilidade.")

        except Exception as e:
            logging.error(f"Erro ao executar o comando !jogador: {e}", exc_info=True)
            await ctx.send("❌ Ocorreu um erro ao processar o comando. Tente novamente mais tarde.")
