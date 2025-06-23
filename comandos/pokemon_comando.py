import random
from twitchio.ext import commands

class PokemonComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='pokemon')
    async def pokemon(self, ctx, *, alvo: str = None):
        try:
            # Define o alvo do comando (quem digitou ou quem foi mencionado)
            alvo = alvo or ctx.author.name

            # Conecta ao banco de dados
            db_connection = self.bot.db_connection
            if db_connection is None:
                await ctx.send("Erro de conexão com o banco de dados. Tente novamente mais tarde.")
                return

            # Escolhe um Pokémon aleatório do banco de dados
            cursor = db_connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM `pokemon` left join pokemon_has_tipo t on idPokemon = t.pokemon_idPokemon left join tipo_pokemon tp on t.tipo_idTipo = tp.idTipo ORDER BY RAND() LIMIT 1")
            pokemon_info = cursor.fetchone()

            if pokemon_info:
                pokemon = pokemon_info['Nome_Especie']
                tipo = pokemon_info['tipo_primario']
                porcentagem = random.randint(0, 100)

                # Consulta as mensagens da tabela de mensagens baseadas na função "pokemon" e na porcentagem
                cursor.execute("""
                    SELECT mensagem 
                    FROM mensagens 
                    WHERE tipo_funcao = 'pokemon' 
                    AND min_porcentagem <= %s 
                    AND max_porcentagem >= %s
                    ORDER BY RAND() LIMIT 1
                """, (porcentagem, porcentagem))
                mensagem_info = cursor.fetchone()

                if mensagem_info:
                    # Formatar a mensagem com os dados do Pokémon
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
                print("Nenhum Pokémon encontrado no banco de dados.")
                await ctx.send("Nenhum Pokémon foi encontrado para o comando.")

            cursor.close()

        except Exception as e:
            print(f"Erro ao executar o comando pokemon: {e}")
            await ctx.send("Ocorreu um erro ao processar o comando. Tente novamente mais tarde.")
