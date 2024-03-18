from scripts.global_commandes.fonctions import *
from scripts.global_commandes.import_et_variable import *


def get_number_chance_left(id_user) :
    with open(CURRENT_PATH+f"/assets/daily_quest_save/{id_user}.txt", "r") as f :
        txt = f.readlines()
    if len(txt) == 1 :
        txt = txt[0]
    else :
        txt = txt[0][:1]
    try :
        return int(txt[0])
    except Exception as e:
        print("il y a eu un problème lors de la lecture de fichier de save", e)




#renvoi l'embed et effectu l'effet lorsque le gain est carte
def effet_carte_quackity_button(id_user) :
    #on get l'xp que le joueur possède
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"SELECT xp FROM Joueur WHERE id_discord_player == {id_user}")
    resultat_user_stats = curseur.fetchone()[0]
    #on lit le taux de drop en fonction du niveau du joueur
    data, lvl_column, lvl = get_data_lvl_from_csv(resultat_user_stats)
    #operations qui permet d'avoir la liste des proba selon le niveau du joueur
    proba_box = [float((piece_of_data)[:-1].replace(",", ".")) for piece_of_data in data[lvl_column.index(lvl)][1:-1]]
    #pioche d'une carte
    random_number = random()*100
    cumule_proba = 0
    for prob in proba_box :
        if prob+cumule_proba >= random_number :
            break
        cumule_proba+=prob
    index_box = proba_box.index(prob)
    #on affecte tout les changements à la BDD
    curseur.execute(f"SELECT id, nom, rarete FROM Cartes WHERE rarete == '{nom_rarete[index_box]}' ORDER BY RANDOM() LIMIT 1 ")
    carte_tiree = curseur.fetchone()
    curseur.execute(f"""UPDATE carte_possede 
                SET nombre_carte_possede = nombre_carte_possede + 1
                WHERE id_discord_player == {id_user} AND id == {carte_tiree[0]}""")
    baseDeDonnees.commit()
    baseDeDonnees.close()
    #Enfin, on affiche le résultat au joueur sur discord
    img_path = CURRENT_PATH+f'/assets/cartes/{carte_tiree[1]}.png'
    file = discord.File(img_path)
    embed = discord.Embed(title = f"""Bravo, vous avez trouvé le bon bouton ! 

Vous avez obtenu une nouvelle carte {carte_tiree[2]} !""")
    embed.set_image(url=f"attachment://{formatage_nom_carte(carte_tiree[1])}.png")
    return embed, file


#renvoi l'embed et effectu l'effet lorsque le gain est xp
def effet_xp_quackity_button(id_user) :
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"""UPDATE Joueur 
                SET xp = xp + 100
                WHERE id_discord_player == {id_user}""")
    baseDeDonnees.commit()
    baseDeDonnees.close()
    
    embed = discord.Embed(title="""Bravo vous avez trouvé le bon bouton ! 

Vous avez obtenu un gain de + 100 exp !""")
    return embed, None

#renvoi l'embed et effectu l'effet lorsque le gain est fragment
def effet_fragment_quackity_button(id_user, nb_fragment) :
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"""UPDATE Joueur 
                SET fragment = fragment + {nb_fragment}
                WHERE id_discord_player == {id_user}""")
    baseDeDonnees.commit()
    baseDeDonnees.close()    
    embed = discord.Embed(title=f"""Bravo vous avez trouvé le bon bouton !  

Vous avez obtenu un gain de + {nb_fragment} fragment{pluriel(nb_fragment)} !""")
    return embed, None


def get_nb_fragment(txt_fragment) :
    if "10" in txt_fragment :
        return txt_fragment[-2:]
    else :
        return txt_fragment[-1:]