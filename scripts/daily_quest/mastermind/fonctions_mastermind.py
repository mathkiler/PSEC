from scripts.global_commandes.fonctions import *
from scripts.global_commandes.import_et_variable import *


def calc_state_mastermind(id_user) :
    with open(CURRENT_PATH+f"/assets/daily_quest_save/{id_user}.txt", "r") as f :
        lines = f.readlines()
        txt = lines[1:-1]
        current_choix_pion = lines[-1:][0]
    secret_comb = get_secret_combination(id_user)
    txt_to_display = ":one::two::three::four:\n"
    for line in txt :
        current_line = line.split("|")
        for c_line in current_line :
            txt_to_display+=c_line.replace("\n", "")
        txt_to_display+=":beginner:"
        result_verif = verif_combinaison(current_line, secret_comb)
        for bien_place in range(result_verif[0]) :
            txt_to_display+=":white_check_mark:"
        for mal_place in range(result_verif[1]) :
            txt_to_display+=":o:"
        txt_to_display+="\n"
    for state in current_choix_pion.split("|") :
        if state == "" :
            txt_to_display+=":white_square_button:"
        else :
            txt_to_display+=state
    txt_to_display+=":beginner:"
    print(txt_to_display)
    return txt_to_display





def verif_combinaison(comb_test, secret_comb) :
    result = [0,0] #[0] = pion bien placé, [1] = pion existant mais mal placé
    result_tamp = []
    for j in range(4):
        if comb_test[j] == secret_comb[j] :
            result[0] += 1
            result_tamp.append(j)

    for k in range(4):
        if k in result_tamp :
            pass
        else:
            if comb_test[k] in secret_comb:
                result[1]+=1    
    return result



def get_secret_combination(id_user) :
    with open(CURRENT_PATH+f"/assets/daily_quest_save/{id_user}.txt", "r") as f :
        txt = f.readlines() 
    return txt[0].split("|")

def get_current_combination(id_user) :
    with open(CURRENT_PATH+f"/assets/daily_quest_save/{id_user}.txt", "r") as f :
        txt = f.readlines() 
    return txt[-1].split("|")




#renvoi l'embed et effectu l'effet lorsque le gain est carte
def effet_carte_mastermind(id_user) :
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
def effet_xp_mastermind(id_user) :
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    #on cherche à avoir le niveau du joueur pour lui adapter son gain d'exp
    curseur.execute(f"SELECT * FROM Joueur WHERE id_discord_player == {id_user}")
    resultat_user_stats = curseur.fetchone()
    _, lvl_column , lvl = get_data_lvl_from_csv(resultat_user_stats[3]) 

    curseur.execute(f"""UPDATE Joueur 
                SET xp = xp + {(lvl_column.index(lvl)+1)*11}
                WHERE id_discord_player == {id_user}""")
    baseDeDonnees.commit()
    baseDeDonnees.close()
    
    embed = discord.Embed(title=f"""Bravo vous avez trouvé le bon bouton ! 

Vous avez obtenu un gain de + {(lvl_column.index(lvl)+1)*11} exp !""")
    return embed, None

#renvoi l'embed et effectu l'effet lorsque le gain est fragment
def effet_fragment_mastermind(id_user, nb_fragment) :
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"""UPDATE Joueur 
                SET fragment = fragment + {nb_fragment}
                WHERE id_discord_player == {id_user}""")
    baseDeDonnees.commit()
    baseDeDonnees.close()    
    embed = discord.Embed(title=f"""Bravo vous avez trouvé le bon bouton !  

Vous avez obtenu un gain de + {nb_fragment} fragments !""")
    return embed, None

