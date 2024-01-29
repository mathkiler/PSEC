from random import choice, randint
import sqlite3
import os

####
#Proba des cartes aléatoire
commun=40
peu_courant=25
rare=16
epique=11
heroique=8


baseDeDonnees = sqlite3.connect('./assets/database/database.db')
curseur = baseDeDonnees.cursor()


# # ---createur de la bdd joueur


def creation_player_table() :
    curseur.execute("""CREATE TABLE Joueur 
                    (id_discord_player INTEGER NOT NULL UNIQUE PRIMARY KEY,
                    fragment INTEGER,
                    fragment_cumule INTEGER,
                    xp INTEGER,
                    curseur_carte INTEGER
                    )""")
                        #id_discord_player = id discord du joueur. Avec son id on peux obtenir toutes les info de ce joueur (psuedo, roles...)
                        # fragment = fragment en temps réel du joueur
                        #fragment_cumule = fragement du joueur cumulé dans la journé pour savoir quand il dépasse le max (50) valeur reset à 00h00 tout les jours
                        #curseur_carte = utile pour savoir quel carte le joueur regarde lors u visionnage es ses cartes une par une
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













def inser_into_cartes(nom, rarete) :
    curseur.execute("INSERT INTO Cartes (nom, rarete) VALUES (?, ?)", (f"{nom}", f"{rarete}")) # On ajoute un enregistrement


def inser_into_carte_possede(id_discord_player, id) :
    curseur.execute("INSERT INTO carte_possede (id_discord_player, id) VALUES (?, ?)", (f"{id_discord_player}", f"{id}"))



#chargement des cartes selon la proba de rareté (en %): C=54, PC=25, R=12, E=6, H=3
def chargement_cartes() :
    proba_rarete = ["commun" for k in range(commun)]
    proba_rarete.extend(["peu courant" for k in range(peu_courant)])
    proba_rarete.extend(["rare" for k in range(rare)])
    proba_rarete.extend(["épique" for k in range(epique)])
    proba_rarete.extend(["héroïque" for k in range(heroique)])
    for (repertoire, sousRepertoires, fichiers) in os.walk("./assets/cartes"):
        for nom in fichiers :
            if "nom" != ".inconnue.png" :
                inser_into_cartes(nom[:-4], choice(proba_rarete))


def aff_table_cartes() :
    id_user = 461802780277997579
    for k in range(3,7) :
        curseur.execute(f"""UPDATE carte_possede 
                    SET nombre_carte_possede = {randint(3,10)}
                    WHERE id_discord_player == {id_user} AND id == {k}""")
        baseDeDonnees.commit()
    curseur.execute(f"SELECT cp.id, rarete, nombre_carte_possede, nom FROM cartes as c, joueur as j, carte_possede as cp WHERE c.id == cp.id and cp.id_discord_player == j.id_discord_player and j.id_discord_player == {id_user} AND nombre_carte_possede != 0")
    resultat_carte_possede = curseur.fetchall()
    print(resultat_carte_possede)    

    

# curseur.execute(f"""UPDATE carte_possede 
#             SET nombre_carte_possede = 5
#             WHERE id_discord_player == {461802780277997579} AND id == 14""")
# baseDeDonnees.commit()


# curseur.execute("DELETE FROM Cartes WHERE nom ='.inconnue' ")
# baseDeDonnees.commit()
    




# curseur.execute(f"SELECT id_discord_player FROM Joueur")
# result = curseur.fetchall()
# for member in result :
#     for nb_carte in range(randint(5, 50)) :
#         inser_into_carte_possede(member[0], randint(1,26))



def creation_des_table() :
    creation_player_table()
    baseDeDonnees.commit()
    creation_cartes_table()
    baseDeDonnees.commit()
    creation_carte_possede_table()
    baseDeDonnees.commit()


def creation_BDD() : 
    creation_des_table()
    baseDeDonnees.commit()
    chargement_cartes()
    baseDeDonnees.commit()

# creation_BDD()

aff_table_cartes()


baseDeDonnees.close()