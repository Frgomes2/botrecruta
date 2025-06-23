import os
import psycopg2
from twitchio.ext import commands

voting_ended = True
voting_name = ""
votacao_id = None

class VotacaoComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = None
        self.cursor = None
        self.conectar_db()

    def conectar_db(self):
        self.conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        self.cursor = self.conn.cursor()

    def salvar_votacao(self, nome_votacao):
        global votacao_id
        query = "INSERT INTO votacoes (nome_votacao) VALUES (%s) RETURNING id"
        self.cursor.execute(query, (nome_votacao,))
        votacao_id = self.cursor.fetchone()[0]
        self.conn.commit()

    def salvar_voto(self, usuario_nome, nota):
        query = "INSERT INTO votos (votacao_id, usuario_nome, nota) VALUES (%s, %s, %s)"
        self.cursor.execute(query, (votacao_id, usuario_nome, nota))
        self.conn.commit()

    def calcular_media_votacao(self):
        query = "SELECT nota FROM votos WHERE votacao_id = %s"
        self.cursor.execute(query, (votacao_id,))
        notas = self.cursor.fetchall()

        if notas:
            media = sum(nota[0] for nota in notas) / len(notas)
            return media
        return 0

    def fechar_conexao(self):
        self.cursor.close()
        self.conn.close()

    @commands.command(name='start_votos')
    async def start_votos(self, ctx, *, nome_votacao: str):
        global voting_ended, voting_name, votacao_id

        if not ctx.author.is_mod:
            await ctx.send("🚫 Você precisa ser moderador para usar esse comando.")
            return

        if not voting_ended:
            await ctx.send("❌ A votação atual ainda não foi encerrada.")
            return

        voting_name = nome_votacao
        voting_ended = False
        self.salvar_votacao(voting_name)
        await ctx.send(f"🎉 A votação **{voting_name}** começou! Use !fr nota para votar.")

    @commands.command(name='nota')
    async def nota(self, ctx, voto: str):
        global voting_ended, voting_name

        if voting_ended:
            await ctx.send(f"❌ A votação **{voting_name}** já foi encerrada.")
            return

        voto = voto.replace(',', '.')
        try:
            voto_float = float(voto)
            voto_float = round(voto_float, 2)

            if 0 <= voto_float <= 10:
                self.salvar_voto(ctx.author.name, voto_float)
                await ctx.send(f"🎉 {ctx.author.name} deu a nota {voto_float} para **{voting_name}** 🎉")
            else:
                await ctx.send(f"🚫 {ctx.author.name}, a nota deve ser entre 0 e 10.")
        except ValueError:
            await ctx.send(f"🚫 {ctx.author.name}, nota inválida. Use número com ponto (ex: 9.5).")

    @commands.command(name='encerrar_votacao')
    async def encerrar_votacao(self, ctx):
        global voting_ended, voting_name

        if not ctx.author.is_mod:
            await ctx.send("🚫 Você precisa ser moderador para usar esse comando.")
            return

        if voting_ended:
            await ctx.send(f"❌ A votação **{voting_name}** já foi encerrada.")
            return

        media_votos = self.calcular_media_votacao()
        if media_votos:
            await ctx.send(f"🎉 A votação **{voting_name}** foi encerrada. Média: {media_votos:.2f}")
        else:
            await ctx.send(f"❌ Nenhum voto registrado para **{voting_name}**.")
        voting_ended = True

    @commands.command(name='melhor_nota')
    async def melhor_nota(self, ctx):
        if not ctx.author.is_mod:
            await ctx.send("🚫 Você precisa ser moderador para usar esse comando.")
            return

        self.cursor.execute("SELECT * FROM votacoes")
        votacoes = self.cursor.fetchall()

        if not votacoes:
            await ctx.send("❌ Não há votações registradas.")
            return

        mensagens_ranking = []

        for votacao in votacoes:
            id_votacao = votacao[0]
            nome_votacao = votacao[1]

            self.cursor.execute("SELECT usuario_nome, nota FROM votos WHERE votacao_id = %s", (id_votacao,))
            votos = self.cursor.fetchall()

            if votos:
                media_votacao = sum(v[1] for v in votos) / len(votos)
                ordenados = sorted(votos, key=lambda x: x[1], reverse=True)
                top_3 = ordenados[:3]

                ranking = f"📊 Top 3 da votação **{nome_votacao}**:\n"
                for i, (nome, nota) in enumerate(top_3):
                    ranking += f"{i + 1}º: {nome} — {nota:.2f}\n"

                mensagens_ranking.append(ranking)
            else:
                mensagens_ranking.append(f"❌ Sem votos para **{nome_votacao}**.")

        await ctx.send("\n\n".join(mensagens_ranking))

def setup(bot):
    bot.add_cog(VotacaoComando(bot))
