import random
import logging
from twitchio.ext import commands

class PersonagemComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='personagem')
    async def personagem(self, ctx, *, alvo: str = None):
        try:
            alvo = (alvo or ctx.author.name).lstrip('@').strip()
            db = self.bot.db_connection

            if not db:
                await ctx.send("❌ Erro de conexão com o banco de dados. Tente novamente mais tarde.")
                return

            with db.cursor() as cursor:
                # Seleciona personagem aleatório
                cursor.execute("SELECT nome, descricao FROM personagens ORDER BY RAND() LIMIT 1")
                row = cursor.fetchone()
                if not row:
                    await ctx.send("❌ Nenhum personagem foi encontrado no banco de dados.")
                    return

                personagem, descricao = row
                porcentagem = random.randint(0, 100)

                # Seleciona mensagem correspondente à porcentagem
                cursor.execute("""
                    SELECT mensagem 
                    FROM tb_mensagens 
                    WHERE tipo_funcao = 'personagem' 
                    AND min_porcentagem <= %s 
                    AND max_porcentagem >= %s
                    ORDER BY RAND() LIMIT 1
                """, (porcentagem, porcentagem))
                msg_row = cursor.fetchone()

                if msg_row and isinstance(msg_row[0], str):
                    mensagem = msg_row[0].format(
                        alvo=alvo,
                        personagem=personagem,
                        descricao=descricao,
                        porcentagem=porcentagem
                    )
                    await ctx.send(mensagem)
                else:
                    await ctx.send(f"⚠️ {alvo}, não encontramos uma mensagem para {porcentagem}% de compatibilidade.")

        except Exception as e:
            logging.error(f"Erro ao executar o comando !personagem: {e}", exc_info=True)
            await ctx.send("❌ Ocorreu um erro ao processar o comando. Tente novamente mais tarde.")
