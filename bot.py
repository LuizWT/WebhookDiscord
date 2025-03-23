import discord
from dotenv import load_dotenv
from discord.ext import commands
import os

intents = discord.Intents.all()


load_dotenv()

token = os.environ.get("DISCORD_TOKEN")
if not token:
    raise ValueError("DISCORD_TOKEN não configurado nas variáveis de ambiente!")


bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}!')

@bot.event
async def on_message(message: discord.Message):

    if message.author.bot:
        return

    channel = message.channel

    webhooks = await channel.webhooks()
    webhook = None
    for wh in webhooks:
        if wh.name == "RelayWebhook":
            webhook = wh
            break

    if webhook is None:
        webhook = await channel.create_webhook(name="RelayWebhook")

    username = message.author.display_name

    avatar_url = message.author.avatar.url if message.author.avatar else message.author.default_avatar.url
    content = message.content

    files = []
    for attachment in message.attachments:
        file = await attachment.to_file()
        files.append(file)

    try:
        await message.delete()
    except discord.Forbidden:
        print("Sem permissão para deletar a mensagem.")
        return
    except discord.HTTPException as e:
        print(f"Falha ao deletar a mensagem: {e}")
        return

    try:
        await webhook.send(content=content, username=username, avatar_url=avatar_url, files=files)
    except Exception as e:
        print(f"Erro ao enviar mensagem via webhook: {e}")

    await bot.process_commands(message)

bot.run(token)
