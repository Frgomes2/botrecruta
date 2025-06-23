import random
import requests
from twitchio.ext import commands
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime

# Carregar as variáveis de ambiente
load_dotenv()

# Configurações do banco de dados
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")


class PokemonComando(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db_connection = self.connect_to_db()

        # Mensagens de sucesso
        self.mensagens_sucesso = [
            f"🎉✨ **Parabéns, {{}}!** Você capturou um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! 🎉✨🔥",
            f"🌟 **Incrível, {{}}!** Você acaba de capturar um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! 🌟🔥",
            f"🎉 **Boa, {{}}!** Você capturou um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! 🎉✨",
            f"🚀 **Parabéns, {{}}!** Você pegou um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! 🚀🔥",
            f"🔥 **Show de bola, {{}}!** Você conseguiu capturar um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! 🔥",
            f"🌈 **Você fez acontecer, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! 🌈✨",
            f"💥 **Incrível, {{}}!** Você capturou um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! 💥🔥",
            f"🌟 **Uau, {{}}!** Você conseguiu capturar um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! 🌟🎉",
            f"✨ **Sensacional, {{}}!** Você capturou um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! ✨🔥",
            f"🎊 **Arrasou, {{}}!** Você capturou um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! 🎊🌟",
            f"💎 **Você está demais, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! 💎🔥",
            f"🎉 **Agora sim, {{}}!** Você pegou um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! 🎉✨",
            f"🌟 **Isso é épico, {{}}!** Você capturou um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! 🌟🔥",
            f"💫 **Você é um mestre, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! 💫🎉",
            f"🚀 **Que sorte, {{}}!** Você conseguiu capturar um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! 🚀🌟",
            f"🔥 **Você é um verdadeiro treinador, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! 🔥💎",
            f"🌈 **Você fez história, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! 🌈✨",
            f"🎉 **Conquista total, {{}}!** Você capturou um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! 🎉🌟",
            f"⚡ **Impressionante, {{}}!** Você capturou um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! ⚡🔥",
            f"✨ **Incrível desempenho, {{}}!** Você pegou um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! ✨💎",
            f"🎊 **Você está on fire, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! 🎊⚡",
            f"💥 **Demais, {{}}!** Você capturou um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! 💥🎉",
            f"🔥 **Você não para, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! 🔥✨",
            f"🌟 **Fantástico, {{}}!** Você pegou um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! 🌟💥",
            f"💎 **Mestre dos Pokémons, {{}}!** Você capturou um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! 💎🌈",
            f"🎉 **Agora você é lendário, {{}}!** Você capturou um Pokémon **{{}}** de raridade **{{}}** com {{}}% de chance! 🎉🔥"
        ]

        # Mensagens de falha
        self.mensagens_falha = [
            f"💔 **Que pena, {{}}!** A tentativa de capturar o Pokémon **{{}}** de raridade **{{}}** falhou! Você precisaria de {{}}% de chance, mas você obteve apenas {{}}%. Tente novamente! 💔",
            f"💥 **Que tristeza, {{}}!** Infelizmente, você falhou ao capturar o Pokémon **{{}}** de raridade **{{}}**. A chance era de {{}}%, mas você obteve apenas {{}}%. Vamos tentar de novo! 💥",
            f"😢 **Oh não, {{}}!** A captura do Pokémon **{{}}** de raridade **{{}}** falhou! Você precisava de {{}}% de chance, mas obteve apenas {{}}%. Mais sorte na próxima! 😢",
            f"💔 **Falhou dessa vez, {{}}!** A captura do Pokémon **{{}}** de raridade **{{}}** não deu certo. Você obteve apenas {{}}% de chance, quando a mínima era {{}}%. Tente novamente! 💔",
            f"😞 **Infelizmente, {{}}!** Você não conseguiu capturar o Pokémon **{{}}** de raridade **{{}}**. A chance necessária era de {{}}%, mas a sua foi apenas {{}}%. Vamos tentar de novo! 😞",
            f"💨 **Não foi dessa vez, {{}}!** Você falhou ao capturar o Pokémon **{{}}** de raridade **{{}}**. A sua chance foi de {{}}%, mas a mínima era {{}}%. Não desista! 💨",
            f"💔 **Que pena, {{}}!** O Pokémon **{{}}** de raridade **{{}}** escapa mais uma vez. Sua chance foi de {{}}%, quando era necessário {{}}%. Vamos tentar de novo! 💔",
            f"⚡ **Quase lá, {{}}!** A captura do Pokémon **{{}}** de raridade **{{}}** não foi bem-sucedida. A sua chance foi de {{}}%, mas você precisava de {{}}%. Melhor sorte na próxima! ⚡",
            f"🌧️ **Infelizmente, {{}}!** A captura do Pokémon **{{}}** de raridade **{{}}** falhou. Você obteve apenas {{}}%, quando a chance necessária era {{}}%. Vamos tentar outra vez! 🌧️",
            f"💥 **Falhou, {{}}!** O Pokémon **{{}}** de raridade **{{}}** escapou. A sua chance foi de {{}}%, mas você precisava de {{}}%. Tente novamente e não desista! 💥",
            f"❌ **Que pena, {{}}!** Você não conseguiu capturar o Pokémon **{{}}** de raridade **{{}}**. Sua chance foi de {{}}%, mas a mínima necessária era {{}}%. Vamos tentar de novo! ❌",
            f"😣 **Você tentou, {{}}!** Mas a captura do Pokémon **{{}}** de raridade **{{}}** falhou. Você precisava de {{}}% de chance, mas obteve apenas {{}}%. Mais sorte da próxima vez! 😣",
            f"💔 **Ah, {{}}!** A tentativa de capturar o Pokémon **{{}}** de raridade **{{}}** não deu certo. Você obteve {{}}% de chance, mas precisava de {{}}%. Vamos tentar de novo! 💔",
            f"💨 **Tão perto, {{}}!** O Pokémon **{{}}** de raridade **{{}}** ainda escapa. A sua chance foi de {{}}%, enquanto a mínima era {{}}%. Continue tentando! 💨",
            f"🚫 **Que frustração, {{}}!** Você não conseguiu capturar o Pokémon **{{}}** de raridade **{{}}**. Sua chance foi de {{}}%, mas precisava de {{}}%. Vamos tentar novamente! 🚫",
            f"☔ **Que pena, {{}}!** A captura do Pokémon **{{}}** de raridade **{{}}** falhou. A sua chance foi de {{}}%, quando a mínima necessária era {{}}%. Não desista, tente mais tarde! ☔",
            f"💔 **Quase lá, {{}}!** Você falhou ao capturar o Pokémon **{{}}** de raridade **{{}}**. A sua chance foi de {{}}%, mas a mínima era {{}}%. Vai dar certo da próxima! 💔",
            f"😢 **Não foi dessa vez, {{}}!** Você tentou capturar o Pokémon **{{}}** de raridade **{{}}**, mas a chance mínima era {{}}%, e você obteve apenas {{}}%. Vamos tentar de novo! 😢",
            f"💥 **Tente de novo, {{}}!** A captura do Pokémon **{{}}** de raridade **{{}}** não deu certo. Sua chance foi de {{}}%, quando a mínima era {{}}%. Vamos continuar tentando! 💥",
            f"⚡ **Você está perto, {{}}!** Mas não conseguiu capturar o Pokémon **{{}}** de raridade **{{}}**. A chance mínima era {{}}%, e você obteve apenas {{}}%. Vamos tentar mais uma vez! ⚡",
            f"🌧️ **Não foi dessa vez, {{}}!** A captura do Pokémon **{{}}** de raridade **{{}}** falhou. Sua chance foi de {{}}%, mas você precisava de {{}}%. Continue tentando! 🌧️",
            f"💔 **Falhou, {{}}!** O Pokémon **{{}}** de raridade **{{}}** escapou mais uma vez. Você obteve {{}}%, mas a mínima era {{}}%. Tente de novo em breve! 💔",
            f"😞 **Que decepção, {{}}!** A captura do Pokémon **{{}}** de raridade **{{}}** falhou. Sua chance foi de {{}}%, enquanto você precisava de {{}}%. Vamos tentar novamente! 😞",
            f"⚡ **Isso foi por pouco, {{}}!** O Pokémon **{{}}** de raridade **{{}}** escapou. Sua chance foi de {{}}%, mas precisava de {{}}%. Não desista, vamos tentar de novo! ⚡"
        ]

    def check_attempts(self, user):
        """Verifica o número de tentativas de captura do usuário no dia de hoje."""
        cursor = self.db_connection.cursor()
        query = "SELECT tentativas, ultima_tentativa FROM tentativas_captura WHERE id_twitch = %s"
        cursor.execute(query, (user.id,))
        result = cursor.fetchone()

        today = datetime.today().date()

        if result:
            tentativas, ultima_tentativa = result
            if ultima_tentativa == today:
                return tentativas  # Já tem tentativas no dia, retorna o número
            else:
                # Se for um novo dia, resetamos as tentativas para 0
                cursor.execute(
                    "UPDATE tentativas_captura SET tentativas = 0, ultima_tentativa = %s WHERE id_twitch = %s",
                    (today, user.id))
                self.db_connection.commit()
                return 0  # Resetando tentativas
        else:
            # Se o usuário ainda não tiver tentativas registradas, criamos um registro
            cursor.execute(
                "INSERT INTO tentativas_captura (id_twitch, nome_usuario, tentativas, ultima_tentativa) VALUES (%s, %s, 0, %s)",
                (user.id, user.name, today))
            self.db_connection.commit()
            return 0  # Primeira tentativa no dia

    def save_pokemon(self, user, pokemon_id, pokemon_name, pokemon_rarity, attack, types):
        """Salva o Pokémon capturado na base de dados."""
        cursor = self.db_connection.cursor()
        query = """
        INSERT INTO pokemons_capturados (id_twitch, nome_usuario, pokemon_id, pokemon_nome, raridade, ataque, tipos)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (user.id, user.name, pokemon_id, pokemon_name, pokemon_rarity, attack, types)
        cursor.execute(query, values)
        self.db_connection.commit()
        print(f"Pokémon {pokemon_name} de raridade {pokemon_rarity} foi salvo para o usuário {user.name}.")
        cursor.close()

    def update_attempts(self, user):
        """Atualiza o número de tentativas no banco de dados."""
        cursor = self.db_connection.cursor()
        cursor.execute("UPDATE tentativas_captura SET tentativas = tentativas + 1 WHERE id_twitch = %s", (user.id,))
        self.db_connection.commit()

    # Função para obter dados de um Pokémon da PokeAPI
    def obter_dados_pokemon(nome_pokemon):
        url = f"https://pokeapi.co/api/v2/pokemon/{nome_pokemon}"
        resposta = requests.get(url)

        if resposta.status_code == 200:
            dados = resposta.json()

            # A PokeAPI fornece uma taxa de captura (capture_rate), que pode ser usada como indicativo da raridade
            taxa_captura = dados["capture_rate"]

            # Usando a taxa de captura para determinar a raridade
            if taxa_captura <= 50:
                raridade = "Common"
            elif taxa_captura <= 60:
                raridade = "Uncommon"
            elif taxa_captura <= 70:
                raridade = "Rare"
            elif taxa_captura <= 80:
                raridade = "Very Rare"
            elif taxa_captura <= 90:
                raridade = "Legendary"
            elif taxa_captura <= 110:
                raridade = "Mythical"
            else:
                raridade = "Common"

            return raridade
        else:
            return "Common"

    def connect_to_db(self):
        """Conectar ao banco de dados MySQL."""
        try:
            connection = mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name
            )
            print("Conexão com o banco de dados estabelecida com sucesso.")
            return connection
        except mysql.connector.Error as err:
            print(f"Erro ao conectar ao banco de dados: {err}")
            return None

    @commands.command(name="meuspokemon")
    async def meupokemon(self, ctx):
        """Comando para mostrar os Pokémon capturados pelo usuário com mais detalhes e emojis."""
        cursor = self.db_connection.cursor()
        cursor.execute(
            "SELECT pokemon_nome, raridade, ataque, tipos FROM pokemons_capturados WHERE nome_usuario = %s",
            (ctx.author.name,))
        pokemons = cursor.fetchall()

        if pokemons:
            message = "🌟 **Seus Pokémon capturados** 🌟\n\n"
            for pokemon in pokemons:
                pokemon_nome = pokemon[0]
                raridade = pokemon[1]
                ataque = pokemon[2]
                tipos = pokemon[3]

                # Emojis para raridade
                if raridade.lower() == "comum":
                    raridade_emoji = "🟢"
                elif raridade.lower() == "incomum":
                    raridade_emoji = "🔵"
                elif raridade.lower() == "raro":
                    raridade_emoji = "🟣"
                elif raridade.lower() == "muito raro":
                    raridade_emoji = "🟠"
                elif raridade.lower() == "lendário":
                    raridade_emoji = "⭐"
                else:
                    raridade_emoji = "💎"

                # Formatação das informações com emojis
                message += f"**{pokemon_nome}** {raridade_emoji}\n"
                message += f"💥 **Ataque**: {ataque}\n"
                message += f"🌱 **Tipos**: {tipos}\n"
                message += "--------------------------------\n"

            # Enviando a mensagem formatada
            await ctx.send(message)
        else:
            await ctx.send("⚠️ **Você ainda não capturou nenhum Pokémon!** Tente capturar alguns e volte aqui! ⚠️")

        @commands.command(name="capturarpokemon")
        async def capturar_pokemon(self, ctx):
            user = ctx.author

            # Verificar o número de tentativas de captura no dia
            tentativas = self.check_attempts(user)
            if tentativas >= 10:
                await ctx.send(
                    f"🚫 {user.name}, você já usou todas as suas 10 tentativas de captura por hoje! Tente novamente amanhã. 🚫")
                return

            probabilidades = {
                'Common': 50,
                'Uncommon': 60,
                'Rare': 70,
                'Very Rare': 80,
                'Legendary': 90,
                'Mythical': 100
            }

            # Fazendo a requisição para a PokeAPI
            pokemon_url = f"https://pokeapi.co/api/v2/pokemon/{random.randint(1, 898)}"  # Ajuste para o número total de Pokémon
            response = requests.get(pokemon_url)
            if response.status_code == 200:
                pokemon_data = response.json()
                pokemon_name = pokemon_data["name"]
                pokemon_id = pokemon_data["id"]
                attack = pokemon_data["stats"][1]["base_stat"]  # Pegando o ataque do Pokémon
                types = ", ".join([type["type"]["name"] for type in pokemon_data["types"]])
                captura_probabilidade = probabilidades[self.obter_dados_pokemon(pokemon_data["name"])]

            else:
                pokemon_name = "pokémon desconhecido"
                pokemon_id = 0
                attack = 0
                types = "desconhecido"

            # Geração de uma porcentagem aleatória para captura
            captura_probabilidade = probabilidades[raridade]
            porcentagem = random.randint(1, 100)

            # Comparando a porcentagem com a chance mínima
            if porcentagem >= captura_probabilidade:
                # Pokémon capturado com sucesso
                sucesso_mensagem = random.choice(self.mensagens_sucesso)
                await ctx.send(sucesso_mensagem.format(user.name, pokemon_name, raridade, porcentagem))

                # Salvar Pokémon capturado no banco de dados
                self.save_pokemon(user, pokemon_id, pokemon_name, raridade, attack, types)
            else:
                # Falha na captura
                falha_mensagem = random.choice(self.mensagens_falha)
                await ctx.send(
                    falha_mensagem.format(user.name, pokemon_name, raridade, captura_probabilidade, porcentagem))

            # Atualiza o número de tentativas do usuário
            self.update_attempts(user)









