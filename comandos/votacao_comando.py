import mysql.connector
from twitchio.ext import commands

# Variáveis globais de votação
voting_ended = True
voting_name = ""
votacao_id = None

class VotacaoComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = None
        self.cursor = None
        self.conectar_db()

    # Conexão com o banco de dados
    def conectar_db(self):
        self.conn = mysql.connector.connect(
            host="localhost",  # Substitua pelo seu host
            user="root",       # Substitua pelo seu usuário
            password="",       # Substitua pela sua senha
            database="twitch"  # O nome do banco de dados
        )
        self.cursor = self.conn.cursor()

    # Função para salvar a votação no banco de dados
    def salvar_votacao(self, nome_votacao):
        global votacao_id
        query = "INSERT INTO votacoes (nome_votacao) VALUES (%s)"
        self.cursor.execute(query, (nome_votacao,))
        self.conn.commit()
        votacao_id = self.cursor.lastrowid  # Pega o ID da votação recém-criada

    # Função para registrar o voto no banco de dados
    def salvar_voto(self, usuario_nome, nota):
        query = "INSERT INTO votos (votacao_id, usuario_nome, nota) VALUES (%s, %s, %s)"
        self.cursor.execute(query, (votacao_id, usuario_nome, nota))
        self.conn.commit()

    # Função para calcular a média das notas de uma votação
    def calcular_media_votacao(self):
        query = "SELECT nota FROM votos WHERE votacao_id = %s"
        self.cursor.execute(query, (votacao_id,))
        notas = self.cursor.fetchall()

        if notas:
            media = sum(nota[0] for nota in notas) / len(notas)
            return media
        return 0

    # Função para fechar a conexão com o banco de dados
    def fechar_conexao(self):
        self.cursor.close()
        self.conn.close()

    # Comando 'start_votos' para iniciar a votação
    @commands.command(name='start_votos')
    async def start_votos(self, ctx, *, nome_votacao: str):
        global voting_ended, voting_name, votacao_id

        if not ctx.author.is_mod:
            await ctx.send("🚫 Você precisa ser moderador para usar esse comando. 🚫")
            return

        if not voting_ended:
            await ctx.send("❌ A votação atual ainda não foi encerrada. ❌")
            return

        voting_name = nome_votacao
        voting_ended = False  # Define que a votação está aberta
        self.salvar_votacao(voting_name)  # Salva a votação no banco de dados
        await ctx.send(f"🎉 A votação **{voting_name}** começou! Use !fr nota para votar. 🎉")

    # Comando 'nota' para registrar a nota
    @commands.command(name='nota')
    async def nota(self, ctx, voto: str):
        global voting_ended, voting_name

        if voting_ended:
            await ctx.send(f"❌ A votação **{voting_name}** já foi encerrada. Não é possível votar. ❌")
            return

        voto = voto.replace(',', '.')

        try:
            voto_float = float(voto)
            voto_float = round(voto_float, 2)

            if 0 <= voto_float <= 10:
                self.salvar_voto(ctx.author.name, voto_float)  # Salva o voto no banco de dados
                await ctx.send(f"🎉 {ctx.author.name} deu a nota {voto_float} para **{voting_name}** 🎉")
            else:
                await ctx.send(f"🚫 {ctx.author.name}, sua nota deve ser entre 0 e 10. 🚫")
        except ValueError:
            await ctx.send(f"🚫 {ctx.author.name}, sua nota não é válida. Use um número entre 0 e 10 (exemplo: 8.8). 🚫")

    # Comando para encerrar a votação
    @commands.command(name='encerrar_votacao')
    async def encerrar_votacao(self, ctx):
        global voting_ended, voting_name

        if not ctx.author.is_mod:
            await ctx.send("🚫 Você precisa ser moderador para usar esse comando. 🚫")
            return

        if voting_ended:
            await ctx.send(f"❌ A votação **{voting_name}** já foi encerrada. ❌")
            return

        media_votos = self.calcular_media_votacao()  # Calcula a média no banco de dados
        if media_votos:
            await ctx.send(f"🎉 A votação **{voting_name}** foi encerrada. A média das notas é: {media_votos:.2f} 🎉")
        else:
            await ctx.send(f"❌ Nenhum voto registrado para a votação **{voting_name}**. ❌")

        voting_ended = True  # Define que a votação foi encerrada

    @commands.command(name='melhor_nota')
    async def melhor_nota(self, ctx):
        if not ctx.author.is_mod:
            await ctx.send("🚫 Você precisa ser moderador para usar esse comando. 🚫")
            return

        # Buscar as votações que já ocorreram
        self.cursor.execute("SELECT * FROM votacoes")
        votacoes = self.cursor.fetchall()

        if not votacoes:
            await ctx.send("❌ Não há votações registradas no momento. ❌")
            return

        # Variável para armazenar as mensagens do ranking
        mensagens_ranking = []

        # Iterar pelas votações e exibir resultados
        for votacao in votacoes:
            id_votacao = votacao[0]  # ID da votação
            nome_votacao = votacao[1]  # Nome da votação

            # Obter os votos dessa votação
            self.cursor.execute("SELECT usuario_nome, nota FROM votos WHERE votacao_id = %s", (id_votacao,))
            votos = self.cursor.fetchall()

            if votos:
                # Calcular a média dos votos
                media_votacao = sum(voto[1] for voto in votos) / len(votos)

                # Ordenar os votos e selecionar os 3 primeiros
                ordenados = sorted(votos, key=lambda x: x[1], reverse=True)  # Ordena pela nota (índice 1)
                top_3 = ordenados[:3]

                # Formatar a mensagem para adicionar à lista de rankings
                ranking = "📊 Top 3 desenhos com maior pontuação: \r\n"
                for i, (nome, nota) in enumerate(top_3):
                    ranking += f"{i + 1}º lugar: **{nome}** com nota de {nota:.2f}\n"

                # Adicionar a mensagem à lista
                mensagens_ranking.append(ranking)
            else:
                mensagens_ranking.append(f"❌ Não há votos registrados para a votação **{nome_votacao}**. ❌")

        # Enviar todas as mensagens do ranking de uma vez (em um único envio)
        if mensagens_ranking:
            await ctx.send("\n\n".join(mensagens_ranking))

    # Função para adicionar o Cog no bot
def setup(bot):
    bot.add_cog(VotacaoComando(bot))
