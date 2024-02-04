#import des modules
from random import randint, random, choice
from discord.ext import commands
from datetime import date
from math import sqrt
from PIL import Image
import asyncio
import discord
import sqlite3
import csv
import os



#--|--# import des daily quests
#roue de la fortune




#--|--# param bot
intents = discord.Intents().all()
intents.members = True
bot = commands.Bot(command_prefix='!',intents=intents)


###########  USE BDD TEST  ##########
db_test = False
if db_test :
    db_used = "database_test.db"
else :
    db_used = "database.db"


#--|--# lists/variables
admin_id_user = [382877512302067712, 408755725796376579, 461802780277997579, 581776637042098188]
nom_rarete = ["commun", "peu courant", "rare", "épique", "héroïque"]
liste_comandes = ["!commandes", "!c", "!force_change_jour", "!ajout_carte"]
DATE_actuel = date.today()  #date du jour
daily_quest_list_name = ["roue de la fortune", "bouton de quackity", "motus", "demineur"]#liste contenant les nom des events.
motus_msg_player = {} #dictionnaire utile pour le jeu motus. En clé, l'id discord. En value, (le message qui contient le jeu, nombre d'essai restant, mot donnés )
demineur_redirect_emote = {
    "c" : ":white_medium_square:",
    "b" : ":firecracker:",
    "d" : ":triangular_flag_on_post:",
    "1" : ":one:",
    "2" : ":two:",
    "3" : ":three:",
    "4" : ":four:",
    "5" : ":five:",
    "6" : ":six:",
    "7" : ":seven:",
    "8" : ":eight:",
    "9" : ":nine:",
    "0" : ":black_medium_square:"
}