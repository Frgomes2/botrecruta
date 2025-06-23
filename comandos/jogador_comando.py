import random
from twitchio.ext import commands

class JogadorComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='jogador')
    async def jogador(self, ctx, *, alvo: str = None):
        try:
            # Define o alvo do comando (quem digitou ou quem foi mencionado)
            alvo = alvo or ctx.author.name

            # Conecta ao banco de dados
            db_connection = self.bot.db_connection
            if db_connection is None:
                await ctx.send("Erro de conexão com o banco de dados. Tente novamente mais tarde.")
                return

            # Escolhe um jogador aleatório do banco de dados
            cursor = db_connection.cursor(dictionary=True)
            cursor.execute("SELECT nome FROM jogadores ORDER BY RAND() LIMIT 1")
            jogador_info = cursor.fetchone()

            if jogador_info:
                jogador = jogador_info['nome']
                porcentagem = random.randint(0, 100)  # Gera uma porcentagem aleatória

                # Consulta as mensagens da tabela de mensagens baseadas na função "jogador" e na porcentagem
                if porcentagem >= 50:
                    cursor.execute(""" 
                        SELECT mensagem 
                        FROM mensagens 
                        WHERE tipo_funcao = 'jogador' 
                        AND min_porcentagem <= %s 
                        AND max_porcentagem >= %s 
                        ORDER BY RAND() LIMIT 1
                    """, (porcentagem, porcentagem))
                else:
                    cursor.execute(""" 
                        SELECT mensagem 
                        FROM mensagens 
                        WHERE tipo_funcao = 'jogador' 
                        AND min_porcentagem <= %s 
                        AND max_porcentagem >= %s 
                        ORDER BY RAND() LIMIT 1
                    """, (0, 50))  # Seleciona mensagens para porcentagens <= 50%

                mensagem_info = cursor.fetchone()

                if mensagem_info:
                    mensagem = mensagem_info['mensagem'].format(alvo=alvo, jogador=jogador, porcentagem=porcentagem)
                    await ctx.send(mensagem)
                else:
                    await ctx.send(f"{alvo}, não encontramos uma mensagem adequada para essa compatibilidade.")
            else:
                print("Nenhum jogador encontrado no banco de dados.")
                await ctx.send("Nenhum jogador foi encontrado para o comando.")

            cursor.close()

        except Exception as e:
            print(f"Erro ao executar o comando jogador: {e}")
            await ctx.send("Ocorreu um erro ao processar o comando. Tente novamente mais tarde.")
