import random
import time
from twitchio.ext import commands

class RoubarComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.inventário = {
            "Call of Juarez: Gunslinger": 'httppontocom',
            "Tomb Raider: Underworld": 'anduspark',
            "Star Wars: Bounty Hunter": 'waldir_br4z',
            "Quake II": 'davizinho08davi',
            "Neverwinter Nights: Enhanced": 'joseva48',
            "Cristal do Space Hulk: Deathwing - Enhanced Edition.": 'davizinho08davi'
        }
        self.cooldown_ultimo_uso = 0  # Timestamp da última execução do comando

    @commands.command(name='roubar')
    async def roubar(self, ctx):
        try:
            # Verifica se há prêmios distribuídos
            prêmios_distribuídos = [presente for presente, dono in self.inventário.items() if dono is not None]

            if not prêmios_distribuídos:
                await ctx.send("🎁 Ainda não há presentes distribuídos para roubar. Aguarde um pouco mais! 🎁")
                return

            # Escolhe um presente aleatório e transfere para outro usuário
            presente_para_roubar = random.choice(prêmios_distribuídos)
            antigo_dono = self.inventário[presente_para_roubar]

            # Lista de bots a serem excluídos
            bots_excluídos = ["streamelements", "nightbot", "creatisbot", "streamlabs", "botrecruta","frgomes2","kamayeru_","xspringflowerx","x2osso","soundalerts!"]

            # Obtém participantes do chat
            participantes = [user.name for user in ctx.channel.chatters if
                             user.name not in bots_excluídos and user.name != antigo_dono]

            if not participantes:
                await ctx.send("🚫 Não há participantes elegíveis no chat para transferir o prêmio! 🚫")
                return

            novo_dono = random.choice(participantes)
            self.inventário[presente_para_roubar] = novo_dono

            await ctx.send(
                f"💰 {ctx.author.name} roubou **{presente_para_roubar}** de {antigo_dono} e deu para {novo_dono}! 💰")

        except Exception as e:
            print(f"Erro ao executar o comando roubar: {e}")
            await ctx.send("Desculpe, ocorreu um erro ao processar seu pedido. Tente novamente mais tarde.")

    @commands.command(name='prêmios')
    async def prêmios(self, ctx):
        try:
            # Lista os prêmios e seus donos
            prêmios_distribuídos = [f"**{presente}**: {dono}" for presente, dono in self.inventário.items() if
                                    dono is not None]

            if prêmios_distribuídos:
                await ctx.send(f"🎁 **Prêmios atualmente distribuídos:** {', '.join(prêmios_distribuídos)}")
            else:
                await ctx.send("🎁 Não há prêmios distribuídos no momento!")
        except Exception as e:
            print(f"Erro ao executar o comando prêmios: {e}")
            await ctx.send("Desculpe, ocorreu um erro ao processar seu pedido. Tente novamente mais tarde.")

    @commands.command(name='encerrar_roubo')
    async def encerrar_roubo(self, ctx):
        try:
            # Verifica se há prêmios distribuídos
            prêmios_distribuídos = [presente for presente, dono in self.inventário.items() if dono is not None]

            if not prêmios_distribuídos:
                await ctx.send("🎁 Não há prêmios para encerrar. Nenhum prêmio foi roubado ainda! 🎁")
                return

            # Reseta os prêmios
            for presente in self.inventário:
                self.inventário[presente] = None

            await ctx.send("🎁 Todos os prêmios foram retirados e a distribuição foi encerrada! 🎁")
        except Exception as e:
            print(f"Erro ao executar o comando encerrar_roubo: {e}")
            await ctx.send("Desculpe, ocorreu um erro ao tentar encerrar a distribuição dos prêmios.")
