import random
from twitchio.ext import commands

class PersonagemComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='personagem')
    async def personagem(self, ctx, *, alvo: str = None):
        try:
            alvo = alvo or ctx.author.name

            db_connection = self.bot.db_connection
            if db_connection is None:
                await ctx.send("Erro de conexão com o banco de dados. Tente novamente mais tarde.")
                return

            cursor = db_connection.cursor()
            cursor.execute("SELECT nome, descricao FROM personagens ORDER BY RANDOM() LIMIT 1")
            personagem_info = cursor.fetchone()

            if personagem_info:
                personagem, descricao = personagem_info
                porcentagem = random.randint(0, 100)

                cursor.execute("""
                    SELECT mensagem 
                    FROM mensagens 
                    WHERE tipo_funcao = 'personagem' 
                    AND min_porcentagem <= %s 
                    AND max_porcentagem >= %s
                    ORDER BY RANDOM() LIMIT 1
                """, (porcentagem, porcentagem))
                mensagem_info = cursor.fetchone()

                if mensagem_info:
                    mensagem = mensagem_info[0].format(
                        alvo=alvo,
                        personagem=personagem,
                        descricao=descricao,
                        porcentagem=porcentagem
                    )
                    await ctx.send(mensagem)
                else:
                    await ctx.send(f"{alvo}, não encontramos uma mensagem adequada para essa compatibilidade.")
            else:
                await ctx.send("Nenhum personagem foi encontrado para o comando.")

            cursor.close()

        except Exception as e:
            print(f"Erro ao executar o comando personagem: {e}")
            await ctx.send("Ocorreu um erro ao processar o comando. Tente novamente mais tarde.")
