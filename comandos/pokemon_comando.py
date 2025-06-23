import random
import psycopg2.extras
from twitchio.ext import commands

class PokemonComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='pokemon')
    async def pokemon(self, ctx, *, alvo: str = None):
        try:
            alvo = alvo or ctx.author.name
            db_connection = self.bot.db_connection

            if db_connection is None:
                await ctx.send("Erro de conexão com o banco de dados. Tente novamente mais tarde.")
                return

            cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT * FROM pokemon 
                LEFT JOIN pokemon_has_tipo t ON idPokemon = t.pokemon_idPokemon 
                LEFT JOIN tipo_pokemon tp ON t.tipo_idTipo = tp.idTipo 
                ORDER BY RANDOM() LIMIT 1
            """)
            pokemon_info = cursor.fetchone()

            if pokemon_info:
                pokemon = pokemon_info['Nome_Especie']
                tipo = pokemon_info['tipo_primario']
                porcentagem = random.randint(0, 100)

                cursor.execute("""
                    SELECT mensagem 
                    FROM mensagens 
                    WHERE tipo_funcao = 'pokemon' 
                    AND min_porcentagem <= %s 
                    AND max_porcentagem >= %s
                    ORDER BY RANDOM() LIMIT 1
                """, (porcentagem, porcentagem))
                mensagem_info = cursor.fetchone()

                if mensagem_info:
                    mensagem = mensagem_info['mensagem'].format(
                        alvo=alvo,
                        pokemon=pokemon,
                        tipo=tipo,
                        porcentagem=porcentagem
                    )
                    await ctx.send(mensagem)
                else:
                    await ctx.send(f"{alvo}, não encontramos uma mensagem adequada para essa compatibilidade.")
            else:
                await ctx.send("Nenhum Pokémon foi encontrado para o comando.")

            cursor.close()

        except Exception as e:
            print(f"Erro ao executar o comando pokemon: {e}")
            await ctx.send("Ocorreu um erro ao processar o comando. Tente novamente mais tarde.")
