from random import choice, randint
import sqlite3
import os

from scripts.global_commandes.import_et_variable import CURRENT_PATH

####
#Proba des cartes aléatoire
commun=40
peu_courant=25
rare=16
epique=11
heroique=8



baseDeDonnees = sqlite3.connect(CURRENT_PATH+'\\assets\\database\\database.db')
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
    curseur.execute("INSERT INTO Cartes (nom, rarete) VALUES (?, ?)", (f"{nom}", f"{rarete}")) # On ajoute un enregistrement




#chargement des cartes selon la proba de rareté (en %): C=54, PC=25, R=12, E=6, H=3
def chargement_cartes() :
    proba_rarete = ["commun" for k in range(commun)]
    proba_rarete.extend(["peu courant" for k in range(peu_courant)])
    proba_rarete.extend(["rare" for k in range(rare)])
    proba_rarete.extend(["épique" for k in range(epique)])
    proba_rarete.extend(["héroïque" for k in range(heroique)])
    for (repertoire, sousRepertoires, fichiers) in os.walk(CURRENT_PATH+"/cartes"):
        for nom in fichiers :
            if "nom" != ".inconnue.png" :
                inser_into_cartes(nom[:-4], choice(proba_rarete))

    




def creation_des_table() :
    creation_player_table()
    baseDeDonnees.commit()
    try : #on essai si la table cartes est déjà créé. Si oui, on set une variable pour ne pas charger les cartes une nouvelle fois
        creation_cartes_table()
        carte_already_load = False
    except :
        carte_already_load = True
    baseDeDonnees.commit()
    creation_carte_possede_table()
    baseDeDonnees.commit()
    creation_daily_quest_table()
    baseDeDonnees.commit()
    return carte_already_load


def creation_BDD() : 
    carte_already_load = creation_des_table()
    baseDeDonnees.commit()
    if carte_already_load == False:
        chargement_cartes()
        baseDeDonnees.commit()

creation_BDD()


baseDeDonnees.close()