#import des modules
from random import randint, random, choice
# from discord.ext import commands
from datetime import date, datetime
from math import sqrt, inf
from PIL import Image
import numpy as np
import asyncio
import discord
import sqlite3
import shutil
import csv
import os


#--|--# import des daily quests
#roue de la fortune




#--|--# param bot
intents = discord.Intents().all()
intents.members = True
bot = discord.Bot(intents=intents)

###########  USE BDD TEST  ##########
db_test = False
if db_test :
    db_used = "database_test.db"
else :
    db_used = "database.db"


#--|--# lists/variables
CURRENT_PATH = os.getcwd()
db_path = CURRENT_PATH+f'/assets/database/{db_used}'
admin_id_user = [382877512302067712, 408755725796376579, 461802780277997579, 581776637042098188]
bot_id =[1066399413062357062, 1112502285503824003]
nom_rarete = ["commun", "peu courant", "rare", "épique", "héroïque"]
liste_comandes = ["/commandes", "/proba" "/force_change_jour", "/ajout_carte", "/affiche_bdd", "/reroll", "/artistes"]
DATE_actuel = date.today()  #date du jour
daily_quest_list_name = ["roue de la fortune", "bouton de quackity", "motus", "demineur", "puissance 4"]#liste contenant les nom des events.
motus_msg_player = {} #dictionnaire utile pour le jeu motus. En clé, l'id discord. En value, (le message qui contient le jeu, nombre d'essai restant, mot donnés )
demineur_redirect_emote = { #dict des emotes poru le démineur
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
nombre_demineur = [str(k+1) for k in range(9)]
alphabet_demnineur = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
INFINI = inf


nom_carte_relatif = {
    "C_Cucurucho" : ["cucurucho"],
    "C_avion" : ["avion", "l'avion"],
    "C_Bagi" : ["bagi"],
    "C_Cellbit" : ["cellbit", "celbit"],
    "C_club" : ["le club", "club"],
    "C_El_Quackity" : ["el quackity", "elquackity", "el quakity", "elquakity"],
    "C_Foolish" : ["foolish", "folish"],
    "C_gare" : ["gare", "la gare"],
    "C_Ironmouse" : ["ironmouse"],
    "C_Jaiden" : ["jaiden", "jeiden"],
    "C_Philza" : ["philza", "philsa"],
    "C_Roier" : ["roier"],
    "C_Slimecicle" : ["slimecicle", "slime"],
    "C_wall" : ["wall", "the wall", "mur", "le mur"],
    "C_Mike" : ["mike"],
    "E_Tototte" : ["tototte", "totote", "tottote", "tottotto"],
    "E_Cafard_Cucaracha" : ["cafard", "cucarachas", "cucaracha", "la cucarachas", "cafard cucaracha"],
    "E_Lobo_Nocturno" : ["lobo nocturno", "lovo nocturno", "lobo nocturo", "lovo nocturo"],
    "E_Ramon" : ["ramon", "remon"],
    "E_Richalyson" : ["richarlyson", "richalyson"],
    "H_Gegg" : ["gegg", "geg"],
    "H_Pomme" : ["pomme", "pome"],
    "H_Kameto" : ["kameto", "kamel"],
    "PC_Evil_cucurucho" : ["evil cucurucho"],
    "PC_antoineD" : ["antoined", "antoine", "antoine daniel", "daniel"],
    "PC_Aypierre" : ["aypierre", "aypiere"],
    "PC_Baghera " : ["baghera", "bagera", "baghera jones", "bagera jones"],
    "PC_Dapper" : ["dapper", "dapeur", "dappeur", "daper"],
    "PC_Etoiles" : ["etoiles", "etoile", "etoil", "étoiles", "étoile", "étoil"],
    "PC_Furest_Camp" : ["furest camp"],
    "PC_Musee" : ["musée", "muse", "musee", "muséé"],
    "PC_Pactw" : ["pac", "pact", "pactw", "pak", "pakt", "paktw"],
    "PC_Tubbo" : ["tubbo", "tebbo", "tubo", "tebo"],
    "R_BadBoyHalo" : ["bebou", "badboyhalo", "bad boy halo", "bad", "badboy", "bad boy"],
    "R_CellBrioche" : ["brioche", "cellbrioche", "cell brioche", "cellbitbrioche", "cellbit brioche"],
    "R_CucurAthieu" : ["mathieu", "cucurathieu", "rat", "rathieu"],
    "R_FitMC" : ["fit", "fitmc"],
    "R_le_code" : ["code", "le code"],
    "R_PhilzAlicia" : ["alicia", "philzalicia", "philz alicia"],
    "R_Quackity" : ["quackity", "quakity"],
    "R_Tallulah" : ["tallulah", "talulah", "talullah", "tallullah", "tallula", "talula", "talulla", "tallulla", "tahllula", "tahlula", "tahlulla", "tahllulla"],
    "R_Teoad" : ["teo", "téo", "teoad", "teod"]
}
ALL_CARTES = [
    'C_avion','C_Bagi','C_Cellbit','C_club','C_Cucurucho','C_El_Quackity','C_Foolish','C_gare','C_Ironmouse','C_Jaiden','C_Mike','C_Philza','C_Roier','C_Slimecicle','C_wall',
    'PC_Aypierre','PC_Baghera ','PC_Dapper','PC_Etoiles','PC_Evil_cucurucho','PC_Furest_Camp','PC_Musee','PC_Pactw','PC_Tubbo','PC_antoineD',
    'R_BadBoyHalo','R_CellBrioche','R_CucurAthieu','R_FitMC','R_le_code','R_PhilzAlicia','R_Quackity','R_Tallulah','R_Teoad',
    'E_Cafard_Cucaracha','E_Lobo_Nocturno','E_Ramon','E_Richarlyson','E_Tototte',
    'H_Gegg','H_Kameto','H_Pomme'
] #nom de tte les cartes dans le bon ordre 
