from twitchio.ext import commands

class OutrosComandos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="outro_comando")
    async def outro_comando(self, ctx):
        await ctx.send("Este é o comando de outro comando!")