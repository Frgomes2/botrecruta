import random
from twitchio.ext import commands

class PresentesComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.presentes = list(range(1, 101))
        self.presentes[0] = "Call of Juarez: Gunslinger"
        self.presentes[1] = "Tomb Raider: Underworld"
        self.presentes[2] = "Star Wars: Bounty Hunter"
        self.presentes[3] = "Quake II"
        self.presentes[4] = "Space Hulk: Deathwing - Enhanced Edition."
        self.presentes[5] = "Neverwinter Nights: Enhanced"


        for i in range(12, len(self.presentes)):
            self.presentes[i] = "Carvão"
        random.shuffle(self.presentes)

        self.presentes_retirados = set()
        self.presentes_ativos = False
        self.presentes_escolhidos = {}
        self.historico_presentes_lista = []  # Nome do atributo atualizado

        self.frases_carvao = [
            " mas adivinha? Só ganhou **Carvão**! 🔥 Parece que o Papai Noel te sacaneou esse ano!",
            " mas ganhou apenas **Carvão**? Haha, acho que o bom velhinho tá de má vontade hoje! 🔥",
            " mas o que veio foi só **Carvão**! O Natal é assim: às vezes a gente se ilude! 🔥",
            " mas no final só veio **Carvão**! Acho que o bom velhinho tem um senso de humor peculiar, né? 🔥",
            " Ah, você ganhou sacos de **Carvão**! Não é o presente dos sonhos, mas pelo menos vai esquentar sua noite! 🔥"
        ]

    @commands.command(name='ativar_presentes')
    async def ativar_presentes(self, ctx):
        if not (ctx.author.is_mod or ctx.author.name == 'SeuNomeDeBot'):
            await ctx.send("🚫 Você precisa ser moderador ou o dono do canal para usar esse comando. 🚫")
            return
        self.presentes_ativos = True
        await ctx.send("🎉 A brincadeira de **Presentes** foi ativada! 🎁 Agora você pode escolher um número de 1 a 100 e retirar seu presente com o comando `!fr presente [número]`! 🎉")

    @commands.command(name='presente')
    async def escolher_presente(self, ctx, numero: int):
        if not self.presentes_ativos:
            await ctx.send("🎁 A brincadeira de **Presentes** não está ativa no momento. Tente novamente mais tarde!")
            return
        if numero < 1 or numero > 100:
            await ctx.send("🚫 Por favor, escolha um número entre 1 e 100. 🚫")
            return
        if numero in self.presentes_retirados:
            await ctx.send(f"🚫 O presente número {numero} já foi retirado. Escolha outro número. 🚫")
            return
        if ctx.author.name in self.presentes_escolhidos and self.presentes_escolhidos[ctx.author.name] >= 5:
            await ctx.send(f"🚫 {ctx.author.name}, você já escolheu 5 presentes! Não é possível escolher mais presentes. 🚫")
            return

        self.presentes_retirados.add(numero)
        if ctx.author.name in self.presentes_escolhidos:
            self.presentes_escolhidos[ctx.author.name] += 1
        else:
            self.presentes_escolhidos[ctx.author.name] = 1

        presente_escolhido = self.presentes[numero - 1]
        if presente_escolhido == "Carvão":
            frase_carvao = random.choice(self.frases_carvao)
            await ctx.send(f"🎁 Você escolheu o presente número {numero}, {frase_carvao}")
        else:
            await ctx.send(f"🎁 Você escolheu o presente número {numero}, que é... **{presente_escolhido}**! 🎉")

        # Registrar o presente no histórico
        self.historico_presentes_lista.append({
            "usuario": ctx.author.name,
            "numero": numero,
            "presente": presente_escolhido
        })

    @commands.command(name='historico_presentes')
    async def historico_presentes(self, ctx):
        if not ctx.author.is_mod:
            await ctx.send("🚫 Apenas moderadores podem visualizar o histórico de presentes.")
            return
        if not self.historico_presentes_lista:
            await ctx.send("📜 Nenhum presente foi retirado ainda.")
            return
        historico = [f"{h['usuario']} escolheu {h['numero']} e ganhou {h['presente']}" for h in self.historico_presentes_lista]
        await ctx.send("📜 Histórico de Presentes: " + " | ".join(historico))
