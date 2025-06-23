import logging
import random
import mysql.connector
from twitchio.ext import commands

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DadoComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_connection = None
        self.db_cursor = None

        try:
            self.db_connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="twitch"
            )
            self.db_cursor = self.db_connection.cursor()
            # Criando as tabelas de placar e usuários, se não existirem
            self.db_cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS usuarios (
                    id_twitch VARCHAR(255) PRIMARY KEY,
                    nome_usuario VARCHAR(255),
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.db_cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS placar (
                    jogador_id VARCHAR(255),
                    adversario_id VARCHAR(255),
                    vitorias INT DEFAULT 0,
                    PRIMARY KEY (jogador_id, adversario_id)
                )
            """)
            self.db_connection.commit()
        except mysql.connector.Error as err:
            logging.error(f"Erro ao conectar no banco de dados: {err}")
            self.db_connection = None
            self.db_cursor = None

    @commands.command(name='ranking_dado')
    async def ranking_dado(self, ctx):
        try:
            # Consultar o ranking de vitórias no banco de dados
            self.db_cursor.execute("""
                SELECT u.nome_usuario, SUM(p.vitorias) AS vitorias
                FROM placar p
                JOIN usuarios u ON p.jogador_id = u.id_twitch OR p.adversario_id = u.id_twitch
                GROUP BY u.nome_usuario
                ORDER BY vitorias DESC
                LIMIT 3
            """)

            resultados = self.db_cursor.fetchall()

            if not resultados:
                await ctx.send("🚫 Não há jogadores registrados no ranking de dados ainda. Faça algumas partidas! 🚫")
                return

            # Formatando o ranking para exibição
            ranking = "🏆 **Ranking de Vitórias no Dado** 🏆\n"
            for i, (nome_usuario, vitorias) in enumerate(resultados, start=1):
                ranking += f"{i}. {nome_usuario} - {vitorias} vitórias\n"

            # Enviar o ranking
            await ctx.send(ranking)

        except Exception as e:
            logging.error(f"Erro ao tentar buscar o ranking de vitórias: {e}")
            await ctx.send("❌ Ocorreu um erro ao tentar buscar o ranking. Tente novamente mais tarde.")

    @commands.command(name='placar_dado')
    async def placar_dado(self, ctx, nome_usuario=None):
        if not nome_usuario:
            await ctx.send(
                "🚫 Por favor, forneça um nome de usuário para consultar o placar. Exemplo: `!placar_dado frgomes2` 🚫")
            return

        # Limpeza do nome de usuário para evitar erro na busca
        nome_usuario = nome_usuario.lstrip('@').lower()

        try:
            # Buscar o ID do usuário no banco de dados
            id_usuario = await self.obter_user_id(nome_usuario)
            if not id_usuario:
                logging.error(f"ID não encontrado para o usuário {nome_usuario}")
                await ctx.send(f"🚫 Usuário {nome_usuario} não encontrado. Verifique o nome e tente novamente. 🚫")
                return

            # Consultar vitórias do usuário
            query_vitorias = """
                SELECT COALESCE(SUM(vitorias), 0) 
                FROM placar 
                WHERE jogador_id = $1
            """
            logging.debug(f"Consultando vitórias para o ID {id_usuario}")
            resultado_vitorias = await self.db_cursor.fetchval(query_vitorias, id_usuario)
            vitorias = resultado_vitorias if resultado_vitorias else 0

            # Consultar derrotas do usuário
            query_derrotas = """
                SELECT COALESCE(SUM(derrotas), 0) 
                FROM placar 
                WHERE adversario_id = $1
            """
            logging.debug(f"Consultando derrotas para o ID {id_usuario}")
            resultado_derrotas = await self.db_cursor.fetchval(query_derrotas, id_usuario)
            derrotas = resultado_derrotas if resultado_derrotas else 0

            # Exibir o placar
            await ctx.send(f"📊 Placar de {nome_usuario}: {vitorias} vitórias e {derrotas} derrotas.")

        except Exception as e:
            logging.error(f"Erro ao tentar buscar o placar de {nome_usuario}: {e}", exc_info=True)
            await ctx.send("❌ Ocorreu um erro ao tentar buscar o placar. Tente novamente mais tarde.")

    async def obter_user_id(self, nome_usuario):
        """Busca o ID do usuário na Twitch utilizando a API."""
        try:
            usuario = await self.bot.fetch_users([nome_usuario])
            if usuario:
                return usuario[0].id  # Retorna o ID do primeiro usuário encontrado
            else:
                logging.error(f"Usuário {nome_usuario} não encontrado.")
                return None
        except Exception as e:
            logging.error(f"Erro ao obter ID do usuário {nome_usuario}: {e}")
            return None

    async def atualizar_usuario(self, id_twitch, nome_usuario):
        """Atualiza o nome do usuário na tabela de usuários com base no ID."""
        try:
            self.db_cursor.execute("""
                INSERT INTO usuarios (id_twitch, nome_usuario)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE nome_usuario = VALUES(nome_usuario)
            """, (id_twitch, nome_usuario))
            self.db_connection.commit()
            logging.info(f"Usuário {nome_usuario} (ID: {id_twitch}) atualizado no banco de dados.")
        except Exception as e:
            logging.error(f"Erro ao atualizar o usuário {nome_usuario} no banco de dados: {e}")

    @commands.command(name='dado')
    async def dado(self, ctx, *args):
        if not ctx.author:
            return  # Ignora mensagens sem autor válido

        # Valida conexão com o banco
        if self.db_connection is None or self.db_cursor is None:
            await ctx.send("❌ Ocorreu um erro com a conexão ao banco de dados. Tente novamente mais tarde.")
            return

        try:
            bots_excluidos = ["streamelements", "nightbot", "creatisbot", "streamlabs","botrecruta"]
            participantes = [user.name for user in ctx.channel.chatters if
                             user.name != ctx.author.name and user.name not in bots_excluidos]

            # Valida se há participantes disponíveis
            if len(participantes) == 0:
                await ctx.send("🚫 Não há outros usuários no chat para rolar o dado! Aguarde até que outros entrem. 🚫")
                return

            # Escolhe parceiro ou valida entrada do argumento
            if args:
                nome = args[0].lstrip('@').lower()
                if nome in [p.lower() for p in participantes]:
                    parceiro = nome
                else:
                    await ctx.send(f"🚫 Usuário {nome} não está no chat ou é um bot! Tente novamente. 🚫")
                    return
            else:
                parceiro = random.choice(participantes)

            # Gera os números aleatórios para a rolagem
            numero_1 = random.randint(1, 6)
            numero_2 = random.randint(1, 6)

            # Atualiza dados do autor
            id_autor = await self.obter_user_id(ctx.author.name)
            if not id_autor:
                logging.error(f"ID do autor ({ctx.author.name}) não encontrado.")
                await ctx.send("❌ Não foi possível obter seu ID. Tente novamente mais tarde.")
                return
            await self.atualizar_usuario(id_autor, ctx.author.name)

            # Atualiza dados do parceiro
            id_parceiro = await self.obter_user_id(parceiro)
            if not id_parceiro:
                logging.error(f"ID do parceiro ({parceiro}) não encontrado.")
                await ctx.send("❌ Não foi possível obter o ID do parceiro. Tente novamente mais tarde.")
                return
            await self.atualizar_usuario(id_parceiro, parceiro)

            # Determina o vencedor
            if numero_1 > numero_2:
                vencedor_id, perdedor_id, vencedor_nome = id_autor, id_parceiro, ctx.author.name
            elif numero_2 > numero_1:
                vencedor_id, perdedor_id, vencedor_nome = id_parceiro, id_autor, parceiro
            else:
                mensagem = f"{ctx.author.name} rolou o dado e tirou {numero_1}! 🎲 {parceiro} tirou {numero_2}! Foi um empate! 🔥"
                await ctx.send(mensagem)
                return

            # Atualiza placar no banco de dados
            self.db_cursor.execute("""
                INSERT INTO placar (jogador_id, adversario_id, vitorias)
                VALUES (%s, %s, 1)
                ON DUPLICATE KEY UPDATE vitorias = vitorias + 1
            """, (vencedor_id, perdedor_id))
            self.db_connection.commit()

            # Consulta placar atualizado
            self.db_cursor.execute("SELECT vitorias FROM placar WHERE jogador_id = %s AND adversario_id = %s",
                                   (id_autor, id_parceiro))
            vitorias_usuario = self.db_cursor.fetchone()
            vitorias_usuario = vitorias_usuario[0] if vitorias_usuario else 0

            self.db_cursor.execute("SELECT vitorias FROM placar WHERE jogador_id = %s AND adversario_id = %s",
                                   (id_parceiro, id_autor))
            vitorias_adversario = self.db_cursor.fetchone()
            vitorias_adversario = vitorias_adversario[0] if vitorias_adversario else 0

            # Monta uma única mensagem consolidada
            mensagem = (
                f"{ctx.author.name} rolou o dado e tirou {numero_1}! 🎲 "
                f"{parceiro} tirou {numero_2}! 🎲\n"
                f"Ganhador: {vencedor_nome} 🎉\n"
                f"Placar: {ctx.author.name} {vitorias_usuario} x {vitorias_adversario} {parceiro}"
            )
            await ctx.send(mensagem)

        except Exception as e:
            logging.error(f"Erro inesperado: {e}")
            await ctx.send("❌ Ocorreu um erro ao processar o comando. Tente novamente.")
