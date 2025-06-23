import random
from twitchio.ext import commands
from psycopg2.extras import DictCursor

class RoubarComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bots_excluidos = [
            "streamelements", "nightbot", "creatisbot", "streamlabs", 
            "botrecruta", "frgomes2", "kamayeru_", "xspringflowerx", 
            "x2osso", "soundalerts!"
        ]

    @commands.command(name='roubar')
    async def roubar(self, ctx):
        conn = self.bot.db_connection
        cursor = conn.cursor(cursor_factory=DictCursor)

        try:
            cursor.execute("SELECT * FROM inventario_roubo WHERE dono IS NOT NULL")
            premios = cursor.fetchall()

            if not premios:
                await ctx.send("🎁 Ainda não há prêmios distribuídos para roubar.")
                return

            premio = random.choice(premios)
            presente_nome = premio['presente']
            antigo_dono = premio['dono']

            participantes = [u.name for u in ctx.channel.chatters if u.name != antigo_dono and u.name not in self.bots_excluidos]
            if not participantes:
                await ctx.send("🚫 Ninguém no chat pra receber o roubo! 🚫")
                return

            novo_dono = random.choice(participantes)

            cursor.execute("UPDATE inventario_roubo SET dono = %s WHERE presente = %s", (novo_dono, presente_nome))
            conn.commit()

            await ctx.send(f"💰 {ctx.author.name} roubou **{presente_nome}** de {antigo_dono} e deu para {novo_dono}! 💰")

        except Exception as e:
            print(f"Erro ao roubar presente: {e}")
            await ctx.send("❌ Erro ao tentar roubar presente.")
        finally:
            cursor.close()

    @commands.command(name='prêmios')
    async def premios(self, ctx):
        conn = self.bot.db_connection
        cursor = conn.cursor(cursor_factory=DictCursor)

        try:
            cursor.execute("SELECT * FROM inventario_roubo WHERE dono IS NOT NULL")
            premios = cursor.fetchall()

            if not premios:
                await ctx.send("🎁 Nenhum prêmio foi distribuído ainda.")
                return

            lista = [f"**{p['presente']}**: {p['dono']}" for p in premios]
            await ctx.send("🎁 **Prêmios distribuídos:** " + ", ".join(lista))

        except Exception as e:
            print(f"Erro ao buscar prêmios: {e}")
            await ctx.send("❌ Erro ao consultar prêmios.")
        finally:
            cursor.close()

    @commands.command(name='encerrar_roubo')
    async def encerrar_roubo(self, ctx):
        conn = self.bot.db_connection
        cursor = conn.cursor()

        try:
            cursor.execute("UPDATE inventario_roubo SET dono = NULL")
            conn.commit()
            await ctx.send("🎁 Todos os prêmios foram retirados e a distribuição foi encerrada!")

        except Exception as e:
            print(f"Erro ao encerrar roubo: {e}")
            await ctx.send("❌ Erro ao encerrar a distribuição dos prêmios.")
        finally:
            cursor.close()
