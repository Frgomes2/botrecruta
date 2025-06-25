import logging
import random
from typing import Optional, Tuple, List
from twitchio.ext import commands
from twitchio import PartialUser

# Configuração de logging mais robusta
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('dado_bot.log')
    ]
)

# Lista de bots/bloqueados padrão
DEFAULT_BLOCKED_USERS = {"botrecruta", "nightbot", "streamelements", "streamlabs"}

class DadoComando(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot   
        self._setup_database()

    def _setup_database(self) -> None:
        try:
            with self.bot.db_connection.cursor() as cursor:
                cursor.execute(""" 
                    CREATE TABLE IF NOT EXISTS tb_usuarios_twitch (
                        id_twitch VARCHAR(255) PRIMARY KEY,
                        nome_usuario VARCHAR(255) NOT NULL,
                        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_nome_usuario 
                    ON tb_usuarios_twitch (nome_usuario);
                """)

                cursor.execute(""" 
                    CREATE TABLE IF NOT EXISTS tb_placar_dado (
                        jogador_id VARCHAR(255) NOT NULL,
                        adversario_id VARCHAR(255) NOT NULL,
                        vitorias INT DEFAULT 0 CHECK (vitorias >= 0),
                        PRIMARY KEY (jogador_id, adversario_id),
                        FOREIGN KEY (jogador_id) REFERENCES tb_usuarios_twitch(id_twitch) ON DELETE CASCADE,
                        FOREIGN KEY (adversario_id) REFERENCES tb_usuarios_twitch(id_twitch) ON DELETE CASCADE
                    );
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tb_estatisticas_dado (
                        usuario_id VARCHAR(255) PRIMARY KEY,
                        total_jogos INT DEFAULT 0,
                        total_vitorias INT DEFAULT 0,
                        FOREIGN KEY (usuario_id) REFERENCES tb_usuarios_twitch(id_twitch) ON DELETE CASCADE
                    );
                """)

            self.bot.db_connection.commit()
            logging.info("Tabelas criadas/verificadas com sucesso")
        except Exception as err:
            logging.error(f"Erro ao configurar banco de dados: {err}", exc_info=True)
            raise

    @commands.command(name='ranking_dado')
    async def ranking_dado(self, ctx: commands.Context) -> None:
        """Mostra o ranking dos 5 melhores jogadores."""
        try:
            with self.bot.db_connection.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT u.nome_usuario, SUM(p.vitorias) AS vitorias
                    FROM tb_placar_dado p
                    JOIN tb_usuarios_twitch u ON p.jogador_id = u.id_twitch
                    GROUP BY u.nome_usuario
                    ORDER BY vitorias DESC
                    LIMIT 5
                """)
                resultados = cursor.fetchall()

            if not resultados:
                await ctx.send("🚫 Não há jogadores registrados no ranking ainda.")
                return

            ranking = ["🏆 **Ranking de Vitórias no Dado** 🏆"]
            for i, row in enumerate(resultados, 1):
                ranking.append(f"{i}. {row['nome_usuario']} - {row['vitorias']} vitórias")
            
            await ctx.send("\n".join(ranking))

        except Exception as e:
            logging.error(f"Erro ao buscar ranking: {e}", exc_info=True)
            await ctx.send("❌ Ocorreu um erro ao buscar o ranking. Tente novamente mais tarde.")

    @commands.command(name='placar_dado')
    async def placar_dado(self, ctx: commands.Context, nome_usuario: Optional[str] = None) -> None:
        """Mostra o placar de um usuário específico."""
        if not nome_usuario:
            await ctx.send("ℹ️ Uso correto: !placar_dado @nome_do_usuario")
            return

        nome_usuario = nome_usuario.lstrip('@').strip().lower()
        
        try:
            id_usuario = await self._get_user_id(nome_usuario)
            if not id_usuario:
                await ctx.send(f"🚫 Usuário '{nome_usuario}' não encontrado.")
                return

            with self.bot.db_connection.cursor() as cursor:
                # Vitórias como jogador principal
                cursor.execute("""
                    SELECT COALESCE(SUM(vitorias), 0) 
                    FROM tb_placar_dado 
                    WHERE jogador_id = %s
                """, (id_usuario,))
                vitorias = cursor.fetchone()[0]

                # Derrotas (quando outros venceram contra este usuário)
                cursor.execute("""
                    SELECT COALESCE(SUM(vitorias), 0) 
                    FROM tb_placar_dado 
                    WHERE adversario_id = %s
                """, (id_usuario,))
                derrotas = cursor.fetchone()[0]

                # Estatísticas gerais
                cursor.execute("""
                    SELECT total_jogos, total_vitorias 
                    FROM tb_estatisticas_dado 
                    WHERE usuario_id = %s
                """, (id_usuario,))
                stats = cursor.fetchone()
                
                win_rate = (stats[1] / stats[0] * 100) if stats and stats[0] > 0 else 0

            response = [
                f"📊 **Estatísticas de {nome_usuario}**",
                f"Vitórias: {vitorias}",
                f"Derrotas: {derrotas}",
                f"Total de jogos: {stats[0] if stats else 0}",
                f"Taxa de vitórias: {win_rate:.1f}%"
            ]
            
            await ctx.send(" | ".join(response))

        except Exception as e:
            logging.error(f"Erro ao buscar placar para {nome_usuario}: {e}", exc_info=True)
            await ctx.send("❌ Ocorreu um erro ao buscar o placar.")

    @commands.command(name='dado', aliases=['rolardado'])
    async def dado(self, ctx: commands.Context, oponente: str = None) -> None:
        """Rola um dado contra outro usuário ou um oponente aleatório."""
        try:
            # Determinar oponente
            parceiro, mensagem_intro = await self._determinar_oponente(ctx, oponente)
            if not parceiro:
                return

            # Validar oponente
            if not await self._validar_oponente(ctx, parceiro):
                return

            # Obter IDs dos jogadores
            id_autor, id_parceiro = await self._get_player_ids(ctx, parceiro)
            if not id_autor or not id_parceiro:
                await ctx.send("❌ Não foi possível identificar os jogadores.")
                return

            # Atualizar informações dos usuários
            await self._update_user(id_autor, ctx.author.name)
            await self._update_user(id_parceiro, parceiro)

            # Rolar os dados
            numero_1, numero_2 = random.randint(1, 6), random.randint(1, 6)
            
            # Determinar vencedor
            vencedor_id, perdedor_id, vencedor_nome, resultado = self._determinar_vencedor(
                ctx.author.name, id_autor, 
                parceiro, id_parceiro, 
                numero_1, numero_2
            )

            if resultado == "empate":
                await ctx.send(f"{ctx.author.name} tirou {numero_1} e {parceiro} tirou {numero_2}. Foi um empate! 🔥")
                return

            # Atualizar placar e estatísticas
            await self._atualizar_placar(vencedor_id, perdedor_id)
            await self._atualizar_estatisticas(id_autor, id_parceiro, vencedor_id == id_autor)

            # Obter placar atualizado
            v1, v2 = await self._get_placar(id_autor, id_parceiro)

            # Enviar mensagem de resultado
            mensagem = (
                f"{mensagem_intro}"
                f"{ctx.author.name} tirou {numero_1}! 🎲\n"
                f"{parceiro} tirou {numero_2}! 🎲\n"
                f"Ganhador: {vencedor_nome} 🎉\n"
                f"Placar: {ctx.author.name} {v1} x {v2} {parceiro}"
            )

            await ctx.send(mensagem)

        except Exception as e:
            logging.error(f"Erro no comando !dado: {e}", exc_info=True)
            await ctx.send("❌ Ocorreu um erro ao processar o comando. Tente novamente.")

    async def _determinar_oponente(self, ctx: commands.Context, oponente: Optional[str]) -> Tuple[Optional[str], str]:
        """Determina o oponente com base no input ou escolhe aleatoriamente."""
        if oponente:
            return oponente.lstrip('@').lower(), ""
        
        with self.bot.db_connection.cursor() as cursor:
            cursor.execute("""
                SELECT nome_usuario FROM tb_usuarios_twitch
                WHERE LOWER(nome_usuario) != %s
                ORDER BY RANDOM()
                LIMIT 1
            """, (ctx.author.name.lower(),))
            resultado = cursor.fetchone()

        if not resultado:
            await ctx.send("🚫 Nenhum oponente registrado ainda.")
            return None, ""

        parceiro = resultado[0].lower()
        return parceiro, f"🎯 "

    async def _validar_oponente(self, ctx: commands.Context, parceiro: str) -> bool:
        """Valida se o oponente é permitido."""
        blocked = DEFAULT_BLOCKED_USERS | {ctx.author.name.lower()}
        
        if parceiro in blocked:
            await ctx.send(f"🚫 Você não pode jogar contra @{parceiro}.")
            return False
        
        return True

    async def _get_player_ids(self, ctx: commands.Context, parceiro: str) -> Tuple[Optional[str], Optional[str]]:
        """Obtém os IDs dos jogadores."""
        try:
            users: List[PartialUser] = await self.bot.fetch_users([ctx.author.name, parceiro])
            id_autor = next((u.id for u in users if u.name.lower() == ctx.author.name.lower()), None)
            id_parceiro = next((u.id for u in users if u.name.lower() == parceiro.lower()), None)
            return id_autor, id_parceiro
        except Exception as e:
            logging.error(f"Erro ao buscar IDs: {e}")
            return None, None

    def _determinar_vencedor(self, nome_autor: str, id_autor: str, 
                           nome_parceiro: str, id_parceiro: str,
                           num1: int, num2: int) -> Tuple[str, str, str, str]:
        """Determina o vencedor com base nos números sorteados."""
        if num1 > num2:
            return id_autor, id_parceiro, nome_autor, "vitoria"
        elif num2 > num1:
            return id_parceiro, id_autor, nome_parceiro, "vitoria"
        return None, None, None, "empate"

    async def _atualizar_placar(self, vencedor_id: str, perdedor_id: str) -> None:
        """Atualiza o placar no banco de dados."""
        with self.bot.db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO tb_placar_dado (jogador_id, adversario_id, vitorias)
                VALUES (%s, %s, 1)
                ON CONFLICT (jogador_id, adversario_id) DO UPDATE
                SET vitorias = tb_placar_dado.vitorias + 1
            """, (vencedor_id, perdedor_id))
        self.bot.db_connection.commit()

    async def _atualizar_estatisticas(self, id_autor: str, id_parceiro: str, autor_ganhou: bool) -> None:
        """Atualiza as estatísticas gerais dos jogadores."""
        with self.bot.db_connection.cursor() as cursor:
            # Atualizar estatísticas do autor
            cursor.execute("""
                INSERT INTO tb_estatisticas_dado (usuario_id, total_jogos, total_vitorias)
                VALUES (%s, 1, %s)
                ON CONFLICT (usuario_id) DO UPDATE
                SET 
                total_jogos = tb_estatisticas_dado.total_jogos + 1,
                total_vitorias = tb_estatisticas_dado.total_vitorias + EXCLUDED.total_vitorias
            """, (id_autor, 1 if autor_ganhou else 0))

            cursor.execute("""
                INSERT INTO tb_estatisticas_dado (usuario_id, total_jogos, total_vitorias)
                VALUES (%s, 1, %s)
                ON CONFLICT (usuario_id) DO UPDATE
                SET 
                total_jogos = tb_estatisticas_dado.total_jogos + 1,
                total_vitorias = tb_estatisticas_dado.total_vitorias + EXCLUDED.total_vitorias
            """, (id_parceiro, 0 if autor_ganhou else 1))
            
        self.bot.db_connection.commit()

    async def _get_placar(self, id_autor: str, id_parceiro: str) -> Tuple[int, int]:
        """Obtém o placar entre dois jogadores."""
        with self.bot.db_connection.cursor() as cursor:
            cursor.execute("""
                SELECT COALESCE(SUM(vitorias), 0)
                FROM tb_placar_dado
                WHERE jogador_id = %s AND adversario_id = %s
            """, (id_autor, id_parceiro))
            v1 = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COALESCE(SUM(vitorias), 0)
                FROM tb_placar_dado
                WHERE jogador_id = %s AND adversario_id = %s
            """, (id_parceiro, id_autor))
            v2 = cursor.fetchone()[0]

        return v1, v2

    async def _get_user_id(self, nome_usuario: str) -> Optional[str]:
        """Obtém o ID de um usuário pelo nome."""
        try:
            users = await self.bot.fetch_users([nome_usuario])
            return users[0].id if users else None
        except Exception as e:
            logging.error(f"Erro ao buscar ID do usuário {nome_usuario}: {e}")
            return None

    async def _update_user(self, id_twitch: str, nome_usuario: str) -> None:
        """Atualiza ou insere um usuário no banco de dados."""
        try:
            with self.bot.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO tb_usuarios_twitch (id_twitch, nome_usuario)
                    VALUES (%s, %s)
                    ON CONFLICT (id_twitch) DO UPDATE
                    SET nome_usuario = EXCLUDED.nome_usuario
                """, (id_twitch, nome_usuario))
        except Exception as e:
            logging.error(f"Erro ao atualizar usuário {nome_usuario}: {e}")
