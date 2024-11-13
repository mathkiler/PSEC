#information d'utilisation de ce script : 
#ce script sert à cree les 3 messages utile pour envoyer et emttre à jour la bdd du lien entre les id discord et id web
#on envoi par default un "." qu'un modifira au besoin
#executer ce script plusieurs fois n'est pas utile mais n'est pas dengereux (le bot envera des message dans un channel privé)
















from dotenv import load_dotenv
import discord
import os

#on load toutes la variables du .env qui est privé
load_dotenv()
intents = discord.Intents().all()
intents.members = True
bot = discord.Bot(intents=intents)
CHANNEL_ID = 1304502350228230224


#--|--# bot events
@bot.event
async def on_ready():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is not None:
        # Envoyez le message dans le canal
        await channel.send(".")
        await channel.send(".")
        await channel.send(".")
    else:
        print(f"Impossible de trouver le canal avec l'ID {CHANNEL_ID}")
    os._exit(1)


if __name__ == "__main__" :
    bot.run(os.getenv('token_discord'))