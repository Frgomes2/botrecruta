import logging
import random
from twitchio.ext import commands

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DadoComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.criar_tabelas()

    def criar_tabelas(self):
        try:
            with self.bot.db_connection.cursor() as cursor:
                cursor.execute(""" 
                    CREATE TABLE IF NOT EXISTS tb_usuarios_twtich (
                        id_twitch VARCHAR(255) PRIMARY KEY,
                        nome_usuario VARCHAR(255),
                        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cursor.execute(""" 
                    CREATE TABLE IF NOT EXISTS tb_placar_dado (
                        jogador_id VARCHAR(255),
                        adversario_id VARCHAR(255),
                        vitorias INT DEFAULT 0,
                        PRIMARY KEY (jogador_id, adversario_id)
                    )
                """)
            self.bot.db_connection.commit()
        except Exception as err:
            logging.error(f"Erro ao criar tabelas: {err}")

    @commands.command(name='ranking_dado')
    async def ranking_dado(self, ctx):
        try:
            with self.bot.db_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT u.nome_usuario, SUM(p.vitorias) AS vitorias
                    FROM tb_placar_dado p
                    JOIN tb_usuarios_twtich u ON p.jogador_id = u.id_twitch
                    GROUP BY u.nome_usuario
                    ORDER BY vitorias DESC
                    LIMIT 3
                """)
                resultados = cursor.fetchall()

            if not resultados:
                await ctx.send("🚫 Não há jogadores registrados no ranking ainda.")
                return

            ranking = "🏆 **Ranking de Vitórias no Dado** 🏆\n"
            for i, (nome, vitorias) in enumerate(resultados, 1):
                ranking += f"{i}. {nome} - {vitorias} vitórias\n"

            await ctx.send(ranking)

        except Exception as e:
            logging.error(f"Erro ao buscar ranking: {e}")
            await ctx.send("❌ Ocorreu um erro ao buscar o ranking.")

    @commands.command(name='placar_dado')
    async def placar_dado(self, ctx, nome_usuario=None):
        if not nome_usuario:
            await ctx.send("🚫 Use `!placar_dado nome` para consultar o placar.")
            return

        nome_usuario = nome_usuario.lstrip('@').lower()

        try:
            id_usuario = await self.obter_user_id(nome_usuario)
            if not id_usuario:
                await ctx.send(f"🚫 Usuário {nome_usuario} não encontrado.")
                return

            with self.bot.db_connection.cursor() as cursor:
                cursor.execute("SELECT SUM(vitorias) FROM tb_placar_dado WHERE jogador_id = %s", (id_usuario,))
                vitorias = cursor.fetchone()[0] or 0

                cursor.execute("SELECT SUM(vitorias) FROM tb_placar_dado WHERE adversario_id = %s", (id_usuario,))
                derrotas = cursor.fetchone()[0] or 0

            await ctx.send(f"📊 Placar de {nome_usuario}: {vitorias} vitórias e {derrotas} derrotas.")

        except Exception as e:
            logging.error(f"Erro ao buscar placar: {e}")
            await ctx.send("❌ Ocorreu um erro ao buscar o placar.")

    @commands.command(name='dado')
    async def dado(self, ctx, *args):
        bots_excluidos = ["streamelements", "nightbot", "creatisbot", "streamlabs", "botrecruta"]
        participantes = [user.name for user in ctx.channel.chatters if user.name != ctx.author.name and user.name not in bots_excluidos]

        if not participantes:
            await ctx.send("🚫 Não há usuários no chat para jogar.")
            return

        parceiro = args[0].lstrip('@').lower() if args else random.choice(participantes)
        if parceiro not in participantes:
            await ctx.send(f"🚫 {parceiro} não está no chat.")
            return

        numero_1 = random.randint(1, 6)
        numero_2 = random.randint(1, 6)

        id_autor = await self.obter_user_id(ctx.author.name)
        id_parceiro = await self.obter_user_id(parceiro)

        if not id_autor or not id_parceiro:
            await ctx.send("❌ Não foi possível identificar os jogadores.")
            return

        await self.atualizar_usuario(id_autor, ctx.author.name)
        await self.atualizar_usuario(id_parceiro, parceiro)

        if numero_1 > numero_2:
            vencedor_id, perdedor_id, vencedor_nome = id_autor, id_parceiro, ctx.author.name
        elif numero_2 > numero_1:
            vencedor_id, perdedor_id, vencedor_nome = id_parceiro, id_autor, parceiro
        else:
            await ctx.send(f"{ctx.author.name} tirou {numero_1} e {parceiro} tirou {numero_2}. Foi um empate! 🔥")
            return

        with self.bot.db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO tb_placar_dado (jogador_id, adversario_id, vitorias)
                VALUES (%s, %s, 1)
                ON CONFLICT (jogador_id, adversario_id)
                DO UPDATE SET vitorias = tb_placar_dado.vitorias + 1
            """, (vencedor_id, perdedor_id))

            cursor.execute("SELECT vitorias FROM tb_placar_dado WHERE jogador_id = %s AND adversario_id = %s", (id_autor, id_parceiro))
            v1 = cursor.fetchone()[0] or 0

            cursor.execute("SELECT vitorias FROM tb_placar_dado WHERE jogador_id = %s AND adversario_id = %s", (id_parceiro, id_autor))
            v2 = cursor.fetchone()[0] or 0

        self.bot.db_connection.commit()

        mensagem = (
            f"{ctx.author.name} tirou {numero_1}! 🎲 {parceiro} tirou {numero_2}! 🎲\n"
            f"Ganhador: {vencedor_nome} 🎉\n"
            f"Placar: {ctx.author.name} {v1} x {v2} {parceiro}"
        )
        await ctx.send(mensagem)

    async def obter_user_id(self, nome_usuario):
        try:
            usuario = await self.bot.fetch_users([nome_usuario])
            return usuario[0].id if usuario else None
        except Exception as e:
            logging.error(f"Erro ao buscar ID do usuário {nome_usuario}: {e}")
            return None

    async def atualizar_usuario(self, id_twitch, nome_usuario):
        try:
            with self.bot.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO tb_usuarios_twtich (id_twitch, nome_usuario)
                    VALUES (%s, %s)
                    ON CONFLICT (id_twitch)
                    DO UPDATE SET nome_usuario = EXCLUDED.nome_usuario
                """, (id_twitch, nome_usuario))
            self.bot.db_connection.commit()
        except Exception as e:
            logging.error(f"Erro ao atualizar usuário: {e}")
