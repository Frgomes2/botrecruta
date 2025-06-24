import random
import requests
from twitchio.ext import commands
from datetime import datetime

class PokemonComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_connection = bot.db_connection  # Usa a conexão do bot principal

        self.mensagens_sucesso = [
            f"🎊 **Parabéns, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}**! Você tirou **{{}}%**, e a chance mínima era **{{}}%** ⚡",
            f"🎊 **Incrível, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}**! Você tirou **{{}}%**, e a chance mínima era **{{}}%** ⚡",
            f"🎊 **Show, {{}}!** Capturou um Pokémon **{{}}** de raridade **{{}}**! Você tirou **{{}}%**, e a chance mínima era **{{}}%** ⚡",
        ]

        self.mensagens_falha = [
            f"💔 **Que pena, {{}}!** Você falhou ao capturar o Pokémon **{{}}** de raridade **{{}}**. Precisava de **{{}}%**, mas tirou **{{}}%**.",
            f"💥 **Ah não, {{}}!** O Pokémon **{{}}** de raridade **{{}}** escapou. Chance mínima era **{{}}%**, você conseguiu só **{{}}%**.",
        ]

    def save_pokemon(self, user, pokemon_id, pokemon_name, pokemon_rarity, attack, types, cap_avatar):
        cursor = self.db_connection.cursor()
        cursor.execute("""
            INSERT INTO pokemons_capturados 
            (cap_id_twitch, cap_nome_usuario, cap_pokemon_id, cap_pokemon_nome, cap_raridade, cap_ataque, cap_tipos, cap_avatar)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (user.id, user.name, pokemon_id, pokemon_name, pokemon_rarity, attack, types, cap_avatar))
        self.db_connection.commit()
        cursor.close()

    def check_attempts(self, user):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT tentativas, ultima_tentativa FROM tentativas_captura WHERE id_twitch = %s", (user.id,))
        result = cursor.fetchone()
        today = datetime.today().date()

        if result:
            tentativas, ultima = result
            if ultima == today:
                return tentativas
            else:
                cursor.execute("UPDATE tentativas_captura SET tentativas = 0, ultima_tentativa = %s WHERE id_twitch = %s", (today, user.id))
                self.db_connection.commit()
                return 0
        else:
            cursor.execute("INSERT INTO tentativas_captura (id_twitch, nome_usuario, tentativas, ultima_tentativa) VALUES (%s, %s, 0, %s)", (user.id, user.name, today))
            self.db_connection.commit()
            return 0

    def update_attempts(self, user):
        cursor = self.db_connection.cursor()
        cursor.execute("UPDATE tentativas_captura SET tentativas = tentativas + 1 WHERE id_twitch = %s", (user.id,))
        self.db_connection.commit()
        cursor.close()

    def obter_dados_pokemon(self, nome_pokemon):
        url = f"https://pokeapi.co/api/v2/pokemon/{nome_pokemon}"
        r1 = requests.get(url)
        if r1.status_code != 200:
            return "Common", None

        dados = r1.json()
        imagem_url = dados["sprites"]["front_default"]

        species_url = dados["species"]["url"]
        r2 = requests.get(species_url)
        if r2.status_code != 200:
            return "Common", imagem_url

        capture_rate = r2.json().get("capture_rate", 255)
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

    @commands.command(name="capturarpokemon")
    async def capturar_pokemon(self, ctx):
        user = ctx.author
        tentativas = self.check_attempts(user)

        if tentativas >= 10:
            await ctx.send(f"🚫 {user.name}, você já usou todas as Pokébolas hoje. Volte amanhã! 🚫")
            return

        probabilidades = {
            'Common': 50,
            'Uncommon': 60,
            'Rare': 70,
            'Very Rare': 80,
            'Legendary': 90,
            'Mythical': 100
        }

        pokemon_id = random.randint(1, 1000)
        r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}")
        if r.status_code != 200:
            await ctx.send(f"⚠️ Algo deu errado ao buscar o Pokémon.")
            return

        data = r.json()
        name = data["name"]
        attack = data["stats"][1]["base_stat"]
        types = ", ".join([t["type"]["name"] for t in data["types"]])

        raridade, avatar = self.obter_dados_pokemon(name)
        chance_minima = probabilidades[raridade]
        roll = random.randint(1, 100)

        if roll >= chance_minima:
            msg = random.choice(self.mensagens_sucesso)
            await ctx.send(msg.format(user.name, name, raridade, roll, chance_minima))
            self.save_pokemon(user, pokemon_id, name, raridade, attack, types, avatar)
        else:
            msg = random.choice(self.mensagens_falha)
            await ctx.send(msg.format(user.name, name, raridade, chance_minima, roll))

        self.update_attempts(user)

    @commands.command(name="meuspokemon")
    async def meupokemon(self, ctx):
        link = f"http://localhost/streamhub/perfil?user={ctx.author.name}"
        await ctx.send(f"🌟 Seus Pokémon estão aqui, {ctx.author.name}: {link}")
