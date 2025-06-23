import psycopg2
from twitchio.ext import commands

voting_ended = True
voting_name = ""
votacao_id = None

class VotacaoComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def salvar_votacao(self, nome_votacao):
        global votacao_id
        with self.bot.db_connection.cursor() as cursor:
            cursor.execute("INSERT INTO votacoes (nome_votacao) VALUES (%s) RETURNING id", (nome_votacao,))
            votacao_id = cursor.fetchone()[0]
        self.bot.db_connection.commit()

    def salvar_voto(self, usuario_nome, nota):
        with self.bot.db_connection.cursor() as cursor:
            cursor.execute("INSERT INTO votos (votacao_id, usuario_nome, nota) VALUES (%s, %s, %s)",
                           (votacao_id, usuario_nome, nota))
        self.bot.db_connection.commit()

    def calcular_media_votacao(self):
        with self.bot.db_connection.cursor() as cursor:
            cursor.execute("SELECT nota FROM votos WHERE votacao_id = %s", (votacao_id,))
            notas = cursor.fetchall()

        return sum(n[0] for n in notas) / len(notas) if notas else 0

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
            voto_float = round(float(voto), 2)
            if 0 <= voto_float <= 10:
                self.salvar_voto(ctx.author.name, voto_float)
                await ctx.send(f"🎉 {ctx.author.name} deu a nota {voto_float} para **{voting_name}** 🎉")
            else:
                await ctx.send("🚫 Nota deve ser entre 0 e 10.")
        except ValueError:
            await ctx.send("🚫 Nota inválida. Use número com ponto (ex: 8.5).")

    @commands.command(name='encerrar_votacao')
    async def encerrar_votacao(self, ctx):
        global voting_ended, voting_name

        if not ctx.author.is_mod:
            await ctx.send("🚫 Você precisa ser moderador para encerrar votações.")
            return

        if voting_ended:
            await ctx.send(f"❌ A votação **{voting_name}** já foi encerrada.")
            return

        media = self.calcular_media_votacao()
        await ctx.send(f"🎉 A votação **{voting_name}** foi encerrada. Média: {media:.2f}" if media else "❌ Nenhum voto registrado.")
        voting_ended = True

    @commands.command(name='melhor_nota')
    async def melhor_nota(self, ctx):
        if not ctx.author.is_mod:
            await ctx.send("🚫 Você precisa ser moderador para consultar o ranking.")
            return

        with self.bot.db_connection.cursor() as cursor:
            cursor.execute("SELECT * FROM votacoes")
            votacoes = cursor.fetchall()

        if not votacoes:
            await ctx.send("❌ Não há votações registradas.")
            return

        mensagens = []
        for votacao in votacoes:
            id_votacao, nome_votacao = votacao
            with self.bot.db_connection.cursor() as cursor:
                cursor.execute("SELECT usuario_nome, nota FROM votos WHERE votacao_id = %s", (id_votacao,))
                votos = cursor.fetchall()

            if votos:
                media = sum(v[1] for v in votos) / len(votos)
                top = sorted(votos, key=lambda x: x[1], reverse=True)[:3]
                rank = f"📊 **{nome_votacao}** (Média: {media:.2f}):\n"
                rank += "\n".join(f"{i+1}º: {nome} — {nota:.2f}" for i, (nome, nota) in enumerate(top))
                mensagens.append(rank)
            else:
                mensagens.append(f"❌ Sem votos para **{nome_votacao}**.")

        await ctx.send("\n\n".join(mensagens))

def setup(bot):
    bot.add_cog(VotacaoComando(bot))
