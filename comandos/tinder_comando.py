import random
import logging
from twitchio.ext import commands

class TinderComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='tinder')
    async def tinder(self, ctx):
        try:
            db = self.bot.db_connection
            if not db:
                await ctx.send("❌ Erro de conexão com o banco de dados. Tente novamente mais tarde.")
                return

            bots_excluidos = {"streamelements", "nightbot", "creatisbot", "streamlabs", "botrecruta"}
            participantes = [
                user.name for user in getattr(ctx.channel, "chatters", [])
                if user.name.lower() != ctx.author.name.lower() and user.name.lower() not in bots_excluidos
            ]

            if not participantes:
                await ctx.send("🚫 Não há outros usuários no chat para dar match! Aguarde mais gente. 🚫")
                return

            parceiro = random.choice(participantes)
            porcentagem = random.randint(0, 100)

            with db.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT mensagem 
                    FROM tb_mensagens 
                    WHERE tipo_funcao = 'match' 
                    AND min_porcentagem <= %s AND max_porcentagem >= %s 
                    ORDER BY RAND() LIMIT 1
                """, (porcentagem, porcentagem))
                msg_row = cursor.fetchone()

            if msg_row and isinstance(msg_row["mensagem"], str):
                mensagem = msg_row["mensagem"].format(
                    user1=ctx.author.name,
                    user2=parceiro,
                    porcentagem=porcentagem
                )
            else:
                mensagem = f"💞 {ctx.author.name} e {parceiro} deram match com {porcentagem}% de compatibilidade! Mas ninguém soube o que dizer... 🫣"

            await ctx.send(mensagem)

        except Exception as e:
            logging.error(f"Erro ao executar o comando !tinder: {e}", exc_info=True)
            await ctx.send("❌ Ocorreu um erro ao processar o comando. Tente novamente mais tarde.")
