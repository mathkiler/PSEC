from scripts.global_commandes.fonctions import *
from scripts.global_commandes.import_et_variable import *






#renvoi l'embed lorsque le gain est rien
def effet_rien_roue_fortune() :
    
    img_path = CURRENT_PATH+f"/assets/animations/daily_quest/roue_fortune/fin_animation_png/rien.png"
    file = discord.File(img_path)
    embed = discord.Embed(title="""Résultat : 
                         
PERDU !

Tu n'as rien gagné et pourtant tu n'avais qu'une chance sur 6 de perdre...""")
    embed.set_image(url=f"attachment://rien.png")
    return embed, file


#renvoi l'embed et effectu l'effet lorsque le gain est carte
def effet_carte_roue_fortune(id_user) :
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
    embed = discord.Embed(title = f"""Résultat : 

Vous avez obtenu une nouvelle carte {carte_tiree[2]} !""")
    embed.set_image(url=f"attachment://carte.png")
    embed.set_image(url=f"attachment://{formatage_nom_carte(carte_tiree[1])}.png")
    return embed, file


#renvoi l'embed et effectu l'effet lorsque le gain est xp
def effet_xp_roue_fortune(id_user) :
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    #on cherche à avoir le niveau du joueur pour lui adapter son gain d'exp
    curseur.execute(f"SELECT * FROM Joueur WHERE id_discord_player == {id_user}")
    resultat_user_stats = curseur.fetchone()
    _, lvl_column , lvl = get_data_lvl_from_csv(resultat_user_stats[3]) 

    curseur.execute(f"""UPDATE Joueur 
                SET xp = xp + {lvl_column.index(lvl)*11}
                WHERE id_discord_player == {id_user}""")
    baseDeDonnees.commit()
    baseDeDonnees.close()
    
    img_path = CURRENT_PATH+f"/assets/animations/daily_quest/roue_fortune/fin_animation_png/xp.png"
    file = discord.File(img_path)
    embed = discord.Embed(title=f"""Résultat : 
                         
Vous avez obtenu un gain de + {lvl_column.index(lvl)*11} exp !""")
    embed.set_image(url=f"attachment://xp.png")
    return embed, file

#renvoi l'embed et effectu l'effet lorsque le gain est fragment
def effet_fragment_roue_fortune(id_user, nb_fragment) :
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"""UPDATE Joueur 
                SET fragment = fragment + {nb_fragment}
                WHERE id_discord_player == {id_user}""")
    baseDeDonnees.commit()
    baseDeDonnees.close()
    img_path = CURRENT_PATH+f"/assets/animations/daily_quest/roue_fortune/fin_animation_png/fragment_{nb_fragment}.png"
    file = discord.File(img_path)
    embed = discord.Embed(title=f"""Résultat : 
                         
Vous avez obtenu un gain de + {nb_fragment} fragment{pluriel(nb_fragment)} !""")
    embed.set_image(url=f"attachment://fragment_{nb_fragment}.png")
    return embed, file


def get_nb_fragment(txt_fragment) :
    if "10" in txt_fragment :
        return txt_fragment[-2:]
    else :
        return txt_fragment[-1:]