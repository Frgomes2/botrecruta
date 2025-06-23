import random
from twitchio.ext import commands

class StreamerComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='streamer')
    async def streamer(self, ctx, *, alvo: str = None):
        try:
            # Define o alvo do comando (quem digitou ou quem foi mencionado)
            alvo = alvo or ctx.author.name

            # Conecta ao banco de dados
            db_connection = self.bot.db_connection
            if db_connection is None:
                await ctx.send("Erro de conexão com o banco de dados. Tente novamente mais tarde.")
                return

            # Escolhe um streamer aleatório do banco de dados
            cursor = db_connection.cursor(dictionary=True)
            cursor.execute("SELECT nome FROM streamers ORDER BY RAND() LIMIT 1")
            streamer_info = cursor.fetchone()

            if streamer_info:
                streamer = streamer_info['nome']
                porcentagem = random.randint(0, 100)  # Gera uma porcentagem aleatória
                print(f"Porcentagem gerada: {porcentagem}")  # Depuração

                # Consulta as mensagens da tabela de mensagens baseadas na função "streamer" e na porcentagem
                if porcentagem >= 50:
                    # Mensagens tristes
                    cursor.execute("SELECT mensagem  FROM mensagens WHERE tipo_funcao = 'streamer' AND max_porcentagem = 100    ORDER BY RAND() LIMIT 1")
                else:
                    # Mensagens tristes
                    cursor.execute("SELECT mensagem  FROM mensagens WHERE tipo_funcao = 'streamer' AND max_porcentagem = 50    ORDER BY RAND() LIMIT 1")


                mensagem_info = cursor.fetchone()

                if mensagem_info:
                    mensagem = mensagem_info['mensagem'].format(alvo=alvo, streamer=streamer, porcentagem=porcentagem)
                    await ctx.send(mensagem)
                else:
                    print("Nenhuma mensagem encontrada para essa porcentagem.")  # Depuração
                    await ctx.send(f"{alvo}, não encontramos uma mensagem adequada para essa compatibilidade.")
            else:
                print("Nenhum streamer encontrado no banco de dados.")
                await ctx.send("Nenhum streamer foi encontrado para o comando.")

            cursor.close()

        except Exception as e:
            print(f"Erro ao executar o comando streamer: {e}")
            await ctx.send("Ocorreu um erro ao processar o comando. Tente novamente mais tarde.")
