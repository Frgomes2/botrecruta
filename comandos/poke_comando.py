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

        self.mensagens_sucesso = [
            f"🎊 **Parabéns, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}** Voce tirou **{{}}%** ,sendo que Porcentagem Mínima para Conseguir capturar é de **{{}}%**    🎊⚡",
            f"🎊 **Incrível, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}**  Voce tirou **{{}}%** ,sendo que Porcentagem Mínima para Conseguir capturar é de **{{}}%**     🎊⚡",
            f"🎊 **Show de bola, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}*  Voce tirou **{{}}%** ,sendo que Porcentagem Mínima para Conseguir capturar é de **{{}}%**     🎊⚡",
            f"🎊 **Uau, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}**  Voce tirou **{{}}%** ,sendo que Porcentagem Mínima para Conseguir capturar é de **{{}}%**     🎊⚡",
            f"🎊 **Sensacional, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}**   Voce tirou **{{}}%** ,sendo que Porcentagem Mínima para Conseguir capturar é de **{{}}%** 🎊⚡",
            f"🎊 **Você arrasou, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}**  Voce tirou **{{}}%** ,sendo que Porcentagem Mínima para Conseguir capturar é de **{{}}%** 🎊⚡",
            f"🎊 **Você é incrível, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}**  Voce tirou **{{}}%** ,sendo que Porcentagem Mínima para Conseguir capturar é de **{{}}%** 🎊⚡",
            f"🎊 **Demais, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}**  Voce tirou **{{}}%** ,sendo que Porcentagem Mínima para Conseguir capturar é de **{{}}%** 🎊⚡",
            f"🎊 **Mandou bem, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}**  Voce tirou **{{}}%** ,sendo que Porcentagem Mínima para Conseguir capturar é de **{{}}%** 🎊 ⚡",
            f"🎊 **Arrasou, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}**  Voce tirou **{{}}%** ,sendo que Porcentagem Mínima para Conseguir capturar é de **{{}}%** 🎊⚡",
            f"🎊 **Top demais, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}**  Voce tirou **{{}}%** ,sendo que Porcentagem Mínima para Conseguir capturar é de **{{}}%** 🎊⚡",
            f"🎊 **Fantástico, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}**  Voce tirou **{{}}%** ,sendo que Porcentagem Mínima para Conseguir capturar é de **{{}}%** 🎊⚡",
            f"🎊 **Você fez história, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}** 🎊⚡",
            f"🎊 **Impressionante, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}** 🎊⚡",
            f"🎊 **Incrível, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}**  Voce tirou **{{}}%** ,sendo que Porcentagem Mínima para Conseguir capturar é de **{{}}%** 🎊⚡",
            f"🎊 **Você é um mestre, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}**  Voce tirou **{{}}%** ,sendo que Porcentagem Mínima para Conseguir capturar é de **{{}}%** 🎊⚡",
            f"🎊 **Você brilhou, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}**  Voce tirou **{{}}%** ,sendo que Porcentagem Mínima para Conseguir capturar é de **{{}}%** 🎊⚡",
            f"🎊 **Que sorte, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}**  Voce tirou **{{}}%** ,sendo que Porcentagem Mínima para Conseguir capturar é de **{{}}%** 🎊⚡",
            f"🎊 **Incrível, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}** Voce tirou **{{}}%** ,sendo que Porcentagem Mínima para Conseguir capturar é de **{{}}%** 🎊⚡",
            f"🎊 **Você conseguiu, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}**  Voce tirou **{{}}%** ,sendo que Porcentagem Mínima para Conseguir capturar é de **{{}}%** 🎊⚡",
        ]

        self.mensagens_falha = [
            f"💔 **Que pena, {{}}!** A tentativa de capturar o Pokémon **{{}}** de raridade **{{}}** falhou! Você precisaria de {{}}% de chance, mas você obteve apenas {{}}%. Tente novamente! 💔",
            f"💥 **Que tristeza, {{}}!** Infelizmente, você falhou ao capturar o Pokémon **{{}}** de raridade **{{}}**. A chance era de {{}}%, mas você obteve apenas {{}}%. Vamos tentar de novo! 💥",
            f"😢 **Oh não, {{}}!** A captura do Pokémon **{{}}** de raridade **{{}}** falhou! Você precisava de {{}}% de chance, mas obteve apenas {{}}%. Mais sorte na próxima! 😢",
            f"😞 **Infelizmente, {{}}!** Você não conseguiu capturar o Pokémon **{{}}** de raridade **{{}}**. A chance necessária era de {{}}%, mas a sua foi apenas {{}}%. Vamos tentar de novo! 😞",
            f"😣 **Você tentou, {{}}!** Mas a captura do Pokémon **{{}}** de raridade **{{}}** falhou. Você precisava de {{}}% de chance, mas obteve apenas {{}}%. Mais sorte da próxima vez! 😣",
        ]

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

    def save_pokemon(self, user, pokemon_id, pokemon_name, pokemon_rarity, attack, types, cap_avatar):
        """Salva o Pokémon capturado na base de dados, incluindo a URL da imagem."""
        cursor = self.db_connection.cursor()
        query = """
        INSERT INTO pokemons_capturados (cap_id_twitch, cap_nome_usuario, cap_pokemon_id, cap_pokemon_nome, cap_raridade, cap_ataque, cap_tipos, cap_avatar)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (user.id, user.name, pokemon_id, pokemon_name, pokemon_rarity, attack, types, cap_avatar)
        cursor.execute(query, values)
        self.db_connection.commit()
        print(
            f"Pokémon {pokemon_name} de raridade {pokemon_rarity} com imagem {cap_avatar} foi salvo para o usuário {user.name}.")
        cursor.close()

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

    def update_attempts(self, user):
        """Atualiza o número de tentativas no banco de dados."""
        cursor = self.db_connection.cursor()
        cursor.execute("UPDATE tentativas_captura SET tentativas = tentativas + 1 WHERE id_twitch = %s", (user.id,))
        self.db_connection.commit()

    def obter_dados_pokemon(self, nome_pokemon):
        url = f"https://pokeapi.co/api/v2/pokemon/{nome_pokemon}"  # Obter dados do Pokémon
        resposta = requests.get(url)

        if resposta.status_code == 200:
            dados = resposta.json()

            # A PokeAPI fornece a URL da imagem
            imagem_url = dados["sprites"]["front_default"]  # A URL da imagem padrão do Pokémon

            # Obter a URL da espécie do Pokémon, onde está a capture_rate
            species_url = dados["species"]["url"]
            species_resposta = requests.get(species_url)

            if species_resposta.status_code == 200:
                species_dados = species_resposta.json()
                capture_rate = species_dados["capture_rate"]  # Capture rate está aqui

                # Usar o capture_rate para determinar a raridade
                if capture_rate <= 3:
                    raridade = "Mythical"
                elif capture_rate <= 10:
                    raridade = "Legendary"
                elif capture_rate <= 50:
                    raridade = "Very Rare"
                elif capture_rate <= 100:
                    raridade = "Rare"
                elif capture_rate <= 150:
                    raridade = "Uncommon"
                else:
                    raridade = "Common"

                return raridade, imagem_url
            else:
                return "Common", None  # Retorna "Common" se não conseguir obter os dados de espécies
        else:
            return "Common", None  # Retorna "Common" se a resposta do Pokémon não for bem-sucedida

    @commands.command(name="capturarpokemon")
    async def capturar_pokemon(self, ctx):
        """Comando para capturar Pokémon via pontos de canal."""
        user = ctx.author

        # Verificar o número de tentativas de captura no dia
        tentativas = self.check_attempts(user)
        if tentativas >= 10:
            await ctx.send(
                f"🚫 {user.name}, você já usou todas as suas Pokebolas! Tente novamente amanhã. 🚫")
            return

        # Definindo as raridades e as probabilidades
        probabilidades = {
            'Common': 50,
            'Uncommon': 60,
            'Rare': 70,
            'Very Rare': 80,
            'Legendary': 90,
            'Mythical': 100
        }



        # Fazendo a requisição para a PokeAPI
        pokemon_url = f"https://pokeapi.co/api/v2/pokemon/{random.randint(1, 1000)}"  # Ajuste para o número total de Pokémon
        response = requests.get(pokemon_url)
        if response.status_code == 200:
            pokemon_data = response.json()
            pokemon_name = pokemon_data["name"]
            pokemon_id = pokemon_data["id"]
            attack = pokemon_data["stats"][1]["base_stat"]  # Pegando o ataque do Pokémon
            types = ", ".join([type["type"]["name"] for type in pokemon_data["types"]])
            raridade, cap_avatar = self.obter_dados_pokemon(pokemon_data["name"])
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
            await ctx.send(sucesso_mensagem.format(user.name, pokemon_name, raridade,porcentagem,captura_probabilidade))

            # Salvar Pokémon capturado no banco de dados
            self.save_pokemon(user, pokemon_id, pokemon_name, raridade, attack, types,cap_avatar)
        else:
            # Falha na captura
            falha_mensagem = random.choice(self.mensagens_falha)
            await ctx.send(falha_mensagem.format(user.name, pokemon_name, raridade, captura_probabilidade, porcentagem))

        # Atualiza o número de tentativas do usuário
        self.update_attempts(user)

    @commands.command(name="meuspokemon")
    async def meupokemon(self, ctx):
        """Comando para mostrar um link para os Pokémon capturados pelo usuário."""
        # Criando o link para o perfil do usuário
        link = f"http://localhost/streamhub/perfil?user={ctx.author.name}"

        # Formatação da mensagem com link direto (sem Markdown)
        message = f"🌟 **Pokémon de {ctx.author.name}** 🌟\n\n" \
                  f"🔗 **Seus Pokémon capturados podem ser conferidos aqui**: {link}"

        # Enviando a mensagem com o link direto
        await ctx.send(message)


