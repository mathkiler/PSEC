#import des modules
from random import randint, random, choice
# from discord.ext import commands
from datetime import date, datetime
from math import sqrt, inf
from PIL import Image, ImageFont, ImageDraw
import numpy as np
import requests
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
    "C_Cucurucho" : ["cucurucho", "c_cucurucho"],
    "C_avion" : ["avion", "l'avion", "c_avion"],
    "C_Bagi" : ["bagi", "C_Bagi"],
    "C_Cellbit" : ["cellbit", "celbit", "c_cellbit"],
    "C_club" : ["le club", "club", "c_club"],
    "C_El_Quackity" : ["el quackity", "elquackity", "el quakity", "elquakity", "c_el_quackity"],
    "C_Foolish" : ["foolish", "folish", "c_foolish"],
    "C_gare" : ["gare", "la gare", "c_gare"],
    "C_Ironmouse" : ["ironmouse", "c_ironmouse"],
    "C_Jaiden" : ["jaiden", "jeiden", "c_jaiden"],
    "C_Philza" : ["philza", "philsa", "c_philza"],
    "C_Roier" : ["roier", "C_Roier"],
    "C_Slimecicle" : ["slimecicle", "slime", "c_slimecicle"],
    "C_wall" : ["wall", "the wall", "mur", "le mur", "c_wall"],
    "C_Mike" : ["mike", "C_Mike"],
    "E_Tototte" : ["tototte", "totote", "tottote", "tottotto", "e_tototte"],
    "E_Cafard_Cucaracha" : ["cafard", "cucarachas", "cucaracha", "la cucarachas", "cafard cucaracha", "r_cafard_cucaracha"],
    "E_Lobo_Nocturno" : ["lobo nocturno", "lovo nocturno", "lobo nocturo", "lovo nocturo", "r_lobo_nocturno"],
    "E_Ramon" : ["ramon", "remon", "e_ramon"],
    "E_Richarlyson" : ["richarlyson", "richalyson", "r_richarlyson"],
    "H_Gegg" : ["gegg", "geg", "h_gegg"],
    "H_Pomme" : ["pomme", "pome", "h_pomme"],
    "H_Kameto" : ["kameto", "kamel", "h_kameto"],
    "PC_Evil_cucurucho" : ["evil cucurucho", "pc_evil_cucurucho"],
    "PC_antoineD" : ["antoined", "antoine", "antoine daniel", "daniel", "pc_antoined"],
    "PC_Aypierre" : ["aypierre", "aypiere", "PC_Aypierre"],
    "PC_Baghera" : ["baghera", "bagera", "baghera jones", "bagera jones", "pc_Baghera"],
    "PC_Dapper" : ["dapper", "dapeur", "dappeur", "daper", "pc_dapper"],
    "PC_Etoiles" : ["etoiles", "etoile", "etoil", "étoiles", "étoile", "étoil", "pc_etoiles"],
    "PC_Furest_Camp" : ["furest camp", "pc_furest_camp"],
    "PC_Musee" : ["musée", "muse", "musee", "muséé", "pc_musee"],
    "PC_Pactw" : ["pac", "pact", "pactw", "pak", "pakt", "paktw", "pc_pactw"],
    "PC_Tubbo" : ["tubbo", "tebbo", "tubo", "tebo", "pc_tubbo"],
    "R_BadBoyHalo" : ["bebou", "badboyhalo", "bad boy halo", "bad", "badboy", "bad boy", "r_badboyhalo"],
    "R_CellBrioche" : ["brioche", "cellbrioche", "cell brioche", "cellbitbrioche", "cellbit brioche", "r_cellbrioche"],
    "R_CucurAthieu" : ["mathieu", "cucurathieu", "rat", "rathieu", "r_cucurathieu"],
    "R_FitMC" : ["fit", "fitmc", "r_fitmc"],
    "R_le_code" : ["code", "le code", "r_le_code"],
    "R_PhilzAlicia" : ["alicia", "philzalicia", "philz alicia", "r_philzalicia"],
    "R_Quackity" : ["quackity", "quakity", "r_quackity"],
    "R_Tallulah" : ["tallulah", "talulah", "talullah", "tallullah", "tallula", "talula", "talulla", "tallulla", "tahllula", "tahlula", "tahlulla", "tahllulla", "r_tallulah"],
    "R_Teoad" : ["teo", "téo", "teoad", "teod", "r_teoad"]
}
ALL_CARTES = [
    'C_avion','C_Bagi','C_Cellbit','C_club','C_Cucurucho','C_El_Quackity','C_Foolish','C_gare','C_Ironmouse','C_Jaiden','C_Mike','C_Philza','C_Roier','C_Slimecicle','C_wall',
    'PC_Aypierre','PC_Baghera ','PC_Dapper','PC_Etoiles','PC_Evil_cucurucho','PC_Furest_Camp','PC_Musee','PC_Pactw','PC_Tubbo','PC_antoineD',
    'R_BadBoyHalo','R_CellBrioche','R_CucurAthieu','R_FitMC','R_le_code','R_PhilzAlicia','R_Quackity','R_Tallulah','R_Teoad',
    'E_Cafard_Cucaracha','E_Lobo_Nocturno','E_Ramon','E_Richarlyson','E_Tototte',
    'H_Gegg','H_Kameto','H_Pomme'
] #nom de tte les cartes dans le bon ordre 

PROBA = [[9000,800,100,80,20], #niv0
[8150,1500,200,100,50], #niv1
[7000,2500,300,120,80], #niv2
[5000,3500,1000,400,100], #niv3
[3000,4000,2350,500,150], #niv4
[1500,3200,4000,1000,300], #niv5
[800,2000,5000,1700,500], #niv6
[600,1900,4400,2400,700], #niv7
[500,1800,3400,3300,1000], #niv8
[400,1500,2500,4100,1500], #niv9
[300,700,2000,5000,2000]] #niv10

XP_LEVELS = [50,100,200,300,500,700,1000,1300,1800,2500,4000]