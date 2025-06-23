import random
from twitchio.ext import commands
from psycopg2.extras import DictCursor

class PresentesComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.presentes = ["Carvão"] * 100
        self.presentes[0] = "Call of Juarez: Gunslinger"
        self.presentes[1] = "Tomb Raider: Underworld"
        self.presentes[2] = "Star Wars: Bounty Hunter"
        self.presentes[3] = "Quake II"
        self.presentes[4] = "Space Hulk: Deathwing - Enhanced Edition"
        self.presentes[5] = "Neverwinter Nights: Enhanced"

        random.shuffle(self.presentes)
        self.presentes_ativos = False

        self.frases_carvao = [
            " mas adivinha? Só ganhou **Carvão**! 🔥",
            " mas ganhou apenas **Carvão**? Haha, Papai Noel te sacaneou! 🔥",
            " mas o que veio foi só **Carvão**! Que zica! 🔥"
        ]

    @commands.command(name='ativar_presentes')
    async def ativar_presentes(self, ctx):
        if not (ctx.author.is_mod or ctx.author.name == 'SeuNomeDeBot'):
            await ctx.send("🚫 Você precisa ser moderador ou o dono do canal para ativar.")
            return
        self.presentes_ativos = True
        await ctx.send("🎉 A brincadeira de **Presentes** foi ativada! Use `!fr presente [número]` para participar!")

    @commands.command(name='presente')
    async def escolher_presente(self, ctx, numero: int):
        if not self.presentes_ativos:
            await ctx.send("🎁 A brincadeira de **Presentes** não está ativa no momento.")
            return
        if numero < 1 or numero > 100:
            await ctx.send("🚫 Escolha um número entre 1 e 100.")
            return

        conn = self.bot.db_connection
        cursor = conn.cursor(cursor_factory=DictCursor)

        # Já foi retirado?
        cursor.execute("SELECT 1 FROM presentes_retirados WHERE numero = %s", (numero,))
        if cursor.fetchone():
            await ctx.send(f"🚫 O presente número {numero} já foi retirado.")
            return

        # Limite de 5 por usuário
        cursor.execute("SELECT total_escolhidos FROM presentes_escolhidos WHERE usuario = %s", (ctx.author.name,))
        resultado = cursor.fetchone()
        total = resultado['total_escolhidos'] if resultado else 0
        if total >= 5:
            await ctx.send(f"🚫 {ctx.author.name}, você já retirou 5 presentes.")
            return

        presente_escolhido = self.presentes[numero - 1]

        # Salvar retirada
        cursor.execute("""
            INSERT INTO presentes_retirados (numero, presente, usuario) VALUES (%s, %s, %s)
        """, (numero, presente_escolhido, ctx.author.name))

        # Atualizar ou inserir contagem
        if resultado:
            cursor.execute("""
                UPDATE presentes_escolhidos SET total_escolhidos = total_escolhidos + 1 WHERE usuario = %s
            """, (ctx.author.name,))
        else:
            cursor.execute("""
                INSERT INTO presentes_escolhidos (usuario, total_escolhidos) VALUES (%s, 1)
            """, (ctx.author.name,))

        conn.commit()
        cursor.close()

        if presente_escolhido == "Carvão":
            frase = random.choice(self.frases_carvao)
            await ctx.send(f"🎁 Você escolheu o presente número {numero},{frase}")
        else:
            await ctx.send(f"🎁 Você escolheu o presente número {numero}, que é... **{presente_escolhido}**! 🎉")

    @commands.command(name='historico_presentes')
    async def historico_presentes(self, ctx):
        if not ctx.author.is_mod:
            await ctx.send("🚫 Apenas moderadores podem ver o histórico.")
            return

        conn = self.bot.db_connection
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute("""
            SELECT usuario, numero, presente FROM presentes_retirados ORDER BY data DESC LIMIT 10
        """)
        registros = cursor.fetchall()
        cursor.close()

        if not registros:
            await ctx.send("📜 Nenhum presente foi retirado ainda.")
            return

        texto = "📜 Últimos Presentes: " + " | ".join([f"{r['usuario']} escolheu {r['numero']} ({r['presente']})" for r in registros])
        await ctx.send(texto)
