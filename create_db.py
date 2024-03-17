from random import choice, randint
import sqlite3
import os

from scripts.global_commandes.import_et_variable import CURRENT_PATH

link_carte_to_rarete = {
    "C_Cucurucho" : "commun",
    "C_avion" : "commun",
    "C_Bagi" : "commun",
    "C_Cellbit" : "commun",
    "C_club" : "commun",
    "C_El_Quakity" : "commun",
    "C_Foolish" : "commun",
    "C_gare" : "commun",
    "C_Ironmouse" : "commun",
    "C_Jaiden" : "commun",
    "C_Philza" : "commun",
    "C_Roier" : "commun",
    "C_Slimecicle" : "commun",
    "C_wall" : "commun",
    "C_Mike" : "commun",
    "E_Tototte" : "épique",
    "E_Cafard_Cucaracha" : "épique",
    "E_Lobo_Nocturno" : "épique",
    "E_Ramon" : "épique",
    "E_Richalyson" : "épique",
    "H_Gegg" : "héroïque",
    "H_Pomme" : "héroïque",
    "H_Kameto" : "héroïque",
    "PC_Evil_cucurucho" : "peu courant",
    "PC_antoineD" : "peu courant",
    "PC_Aypierre" : "peu courant",
    "PC_Baghera " : "peu courant",
    "PC_Dapper" : "peu courant",
    "PC_Etoiles" : "peu courant",
    "PC_Furest_Camp" : "peu courant",
    "PC_Musee" : "peu courant",
    "PC_Pactw" : "peu courant",
    "PC_Tubbo" : "peu courant",
    "R_BadBoyHalo" : "rare",
    "R_CellBrioche" : "rare",
    "R_CucurAthieu" : "rare",
    "R_FitMC" : "rare",
    "R_le_code" : "rare",
    "R_PhilzAlicia" : "rare",
    "R_Quakity" : "rare",
    "R_Tallulah" : "rare",
    "R_Teoad" : "rare"
}

try :
    os.remove(CURRENT_PATH+"\\assets\\database\\database.db")
    os.remove(CURRENT_PATH+"/assets/database/database.db")
except :
    pass



baseDeDonnees = sqlite3.connect(CURRENT_PATH+'/assets/database/database.db')
curseur = baseDeDonnees.cursor()


# # ---createur de la bdd joueur


def creation_player_table() :
    curseur.execute("""CREATE TABLE Joueur 
                    (id_discord_player INTEGER NOT NULL UNIQUE PRIMARY KEY,
                    fragment INTEGER,
                    fragment_cumule INTEGER,
                    xp INTEGER,
                    curseur_carte INTEGER,
                    daily_quest_done INTEGER
                    )""")
                        #id_discord_player = id discord du joueur. Avec son id on peux obtenir toutes les info de ce joueur (psuedo, roles...)
                        # fragment = fragment en temps réel du joueur
                        #fragment_cumule = fragement du joueur cumulé dans la journé pour savoir quand il dépasse le max (50) valeur reset à 00h00 tout les jours
                        #curseur_carte = utile pour savoir quel carte le joueur regarde lors u visionnage es ses cartes une par une
                        #daily_quest_done = 0 = False, le joueur n'as pas encore fini la quest. 1
    baseDeDonnees.commit() 
# creation_player_table()

# ---createur de la bdd cartes
def creation_cartes_table() :
    curseur.execute("""CREATE TABLE Cartes 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL UNIQUE,
                    rarete TEXT CHECK(rarete == 'commun' OR rarete == 'peu courant' OR rarete == 'rare' OR rarete == 'épique' OR rarete == 'héroïque'))""") # Création de la base de données
    baseDeDonnees.commit() # On envoie la requête SQL
# creation_cartes_table()


def creation_carte_possede_table() :
    curseur.execute("""CREATE TABLE carte_possede (
                    id_discord_player INTEGER NOT NULL,
                    id INTEGER NOT NULL,
                    nombre_carte_possede INTEGER NOT NULL,
                    FOREIGN KEY (id_discord_player) REFERENCES Joueur (id_discord_player),
                    FOREIGN KEY (id) REFERENCES Cartes (id)
    );""")
    baseDeDonnees.commit() 
# creation_carte_possede_table()
    
def creation_daily_quest_table() :
    curseur.execute("""CREATE TABLE daily_quest (
                    nom_event TEXT NOT NULL PRIMARY KEY,
                    jour_event TEXT NOT NULL,
                    info_quest TEXT
    );""")
    baseDeDonnees.commit() 
# creation_daily_quest_table()













def inser_into_cartes(nom, rarete) :
    curseur.execute("INSERT INTO Cartes (nom, rarete) VALUES (?, ?)", (nom, rarete)) # On ajoute un enregistrement




#chargement des cartes selon la proba de rareté (en %): C=54, PC=25, R=12, E=6, H=3
def chargement_cartes() :
    
    for (repertoire, sousRepertoires, fichiers) in os.walk(CURRENT_PATH+"/assets/cartes"):
        for nom in fichiers :
            if nom != ".inconnue.png" :
                inser_into_cartes(nom[:-4], link_carte_to_rarete[nom[:-4]])
        break

    




def creation_des_table() :
    creation_player_table()
    baseDeDonnees.commit()

    creation_cartes_table()
    baseDeDonnees.commit()


    creation_carte_possede_table()
    baseDeDonnees.commit()

    creation_daily_quest_table()
    baseDeDonnees.commit()



def creation_BDD() : 
    creation_des_table()
    baseDeDonnees.commit()
    chargement_cartes()
    baseDeDonnees.commit()

creation_BDD()


baseDeDonnees.close()
