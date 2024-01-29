#import des modules
from random import randint, random
from discord.ext import commands
from datetime import date
from math import sqrt
from PIL import Image
import asyncio
import discord
import sqlite3
import csv
import os



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
admin_id_user = [382877512302067712, 408755725796376579, 461802780277997579]
nom_rarete = ["commun", "peu courant", "rare", "épique", "héroïque"]
liste_comandes = ["!commandes", "!c", "!force_change_jour", "!ajout_carte"]
DATE_actuel = date.today()  #date du jour