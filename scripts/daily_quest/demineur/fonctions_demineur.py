from scripts.global_commandes.fonctions import *
from scripts.global_commandes.import_et_variable import *


def get_info_demineur(id_user) :
    with open(CURRENT_PATH+f"/assets/daily_quest_save/{id_user}.txt", "r") as f :
        txt = f.readlines()
    y_ind_arrow = int(txt[0][:-1])
    x_ind_arrow = int(txt[1][:-1])-1
    list_demineur = txt[2][:-1].split(",")
    list_ind_bomb = txt[3][:-1].split(",")
    list_ind_bomb = [int(list_ind_bomb[k]) for k in range(len(list_ind_bomb))]
    return x_ind_arrow, y_ind_arrow, list_demineur, list_ind_bomb

def get_tentative_restante(id_user) :
    with open(CURRENT_PATH+f"/assets/daily_quest_save/{id_user}.txt", "r") as f :
        txt = f.readlines()
    return txt[4]

def get_info_case(id_user, coord_to_get) :
    coord_to_get = (coord_to_get[0])+get_taille_demineur()*coord_to_get[1]
    with open(CURRENT_PATH+f"/assets/daily_quest_save/{id_user}.txt", "r") as f :
        txt = f.readlines()
    list_demineur = txt[2][:-1].split(",")
    return list_demineur[coord_to_get]


def get_taille_demineur() :
    return 9

def get_nb_bombes() :
    return 10
    
#convert le txt qui est save pour chauque joueur en message affichable sur discord (avec les emotes et au bon endroit)
def convert_txt_to_discord_demineur(id_user) :
    x_ind_arrow, y_ind_arrow, list_demineur, _ = get_info_demineur(id_user)
    taille_demineur = get_taille_demineur()
    discord_txt = f""":black_medium_square::black_medium_square::one::two::three::four::five::six::seven::eight::nine:
:black_medium_square:{':black_medium_square:'*(x_ind_arrow+1)}:arrow_down:"""
    ind_demineur_lecture = 0
    for y in range(taille_demineur) :
        discord_txt+=f"\n{demineur_redirect_emote[str(y+1)]}"
        if y == y_ind_arrow :
            discord_txt+=":arrow_right:"
        else :
            discord_txt+=":black_medium_square:"
        for x in range(taille_demineur) :
            if x == x_ind_arrow and y == y_ind_arrow and list_demineur[ind_demineur_lecture] == "c" : #si c'est la case séléctionné par les flèches (uniquement si c'est une case non miné)
                discord_txt+=":green_circle:"
            else :
                discord_txt+=demineur_redirect_emote[list_demineur[ind_demineur_lecture]]
            ind_demineur_lecture+=1
    return discord_txt
        

#pour modifier la colone ou ligne des selects
def modif_ligne_colonne_selected(new_value, ligne_colonne, id_user) : #ligne_colonne = 0 -> ligne, ligne_colonne = 1 -> colonne
    with open(CURRENT_PATH+f"/assets/daily_quest_save/{id_user}.txt", "r") as f :
        txt = f.readlines()
    txt[ligne_colonne] = f"{new_value}\n"
    with open(CURRENT_PATH+f"/assets/daily_quest_save/{id_user}.txt", "w") as f :
        f.write("".join(txt))


#remplace l'etat d'une case par autre chose : new_emote dans le txt save
def replace_somthing_in_demineur(id_user, new_emote, coord_to_replace) : 
    with open(CURRENT_PATH+f"/assets/daily_quest_save/{id_user}.txt", "r") as f :
        txt = f.readlines()
    list_demineur = txt[2][:-1].split(",")
    list_demineur[(coord_to_replace[0]-1)+get_taille_demineur()*coord_to_replace[1]] = new_emote
    txt[2] = ",".join(list_demineur)
    txt[2]+="\n"
    with open(CURRENT_PATH+f"/assets/daily_quest_save/{id_user}.txt", "w") as f :
        txt = f.write("".join(txt))


#test s'il y a des bombes autour de la case testée
def test_bomb_around(ind_case, list_ind_bomb) :
    nb_bombe = 0
    for y in range(-1, 2) :
        for x in range(-1, 2) :
            x_usable = ind_case%get_taille_demineur()
            y_usable = ind_case//get_taille_demineur()
            if 0 <= x_usable+x < get_taille_demineur() and 0 <= y_usable+y < get_taille_demineur() :
                check_ind_case = ind_case+x+y*get_taille_demineur()
                if 0 <= check_ind_case < get_taille_demineur()**2 and check_ind_case in list_ind_bomb :
                        nb_bombe+=1
    return nb_bombe


#fonction récursive qui va au final retourner une liste des case à déminer si la case initiale est une case vide
def demine_case_vide(case_to_explore, already_explore, ind_case_to_reveal, list_ind_bomb) :
    if len(case_to_explore) == 0 :
        return case_to_explore, already_explore, ind_case_to_reveal, list_ind_bomb
    already_explore.append(case_to_explore[0])
    curent_case_explored = case_to_explore.pop(0)
    for y in range(-1, 2) :
        for x in range(-1, 2) :
            x_usable = curent_case_explored%get_taille_demineur()
            y_usable = curent_case_explored//get_taille_demineur()
            if 0 <= x_usable+x < get_taille_demineur() and 0 <= y_usable+y < get_taille_demineur() :
                ind_case = curent_case_explored+x+y*get_taille_demineur()
                nb_bombe = test_bomb_around(ind_case, list_ind_bomb)
                if ind_case not in already_explore and nb_bombe == 0 : #case vide et non exploré
                    case_to_explore.append(ind_case)
                    ind_case_to_reveal.append([ind_case, nb_bombe])
                    demine_case_vide(case_to_explore, already_explore, ind_case_to_reveal, list_ind_bomb)
                else :
                    ind_case_to_reveal.append([ind_case, nb_bombe])
    
    return case_to_explore, already_explore, ind_case_to_reveal, list_ind_bomb
                


#test si le démineur est terminé
def test_demineur_termine(id_user) :
    with open(CURRENT_PATH+f"/assets/daily_quest_save/{id_user}.txt", "r") as f :
        txt = f.readlines()
    list_demineur = txt[2][:-1].split(",")
    list_ind_bomb = txt[3][:-1].split(",")
    list_ind_bomb = [int(list_ind_bomb[k]) for k in range(len(list_ind_bomb))]
    ind_case = 0
    for case in list_demineur :
        if case in ["c", "d"] and ind_case not in list_ind_bomb:
            return False
        ind_case+=1
    return True




#renvoi l'embed et effectu l'effet lorsque le gain est carte
def effet_carte_demineur(id_user) :
    #on get l'xp que le joueur possède
    baseDeDonnees = sqlite3.connect(CURRENT_PATH+f'/assets/database/{db_used}')
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
    embed = discord.Embed(title = f"""Bravo vous avez terminé le démineur ! 

Vous avez obtenu une nouvelle carte {carte_tiree[2]} !""")
    embed.set_image(url=f"attachment://{formatage_nom_carte(carte_tiree[1])}.png")
    return embed, file


#renvoi l'embed et effectu l'effet lorsque le gain est xp
def effet_xp_demineur(id_user) :
    baseDeDonnees = sqlite3.connect(CURRENT_PATH+f'/assets/database/{db_used}')
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"""UPDATE Joueur 
                SET xp = xp + 100
                WHERE id_discord_player == {id_user}""")
    baseDeDonnees.commit()
    baseDeDonnees.close()
    
    embed = discord.Embed(title="""Bravo vous avez terminé le démineur ! 

Vous avez obtenu un gain de + 100 exp !""")
    return embed, None

#renvoi l'embed et effectu l'effet lorsque le gain est fragment
def effet_fragment_demineur(id_user, nb_fragment) :
    baseDeDonnees = sqlite3.connect(CURRENT_PATH+f'/assets/database/{db_used}')
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"""UPDATE Joueur 
                SET fragment = fragment + {nb_fragment}
                WHERE id_discord_player == {id_user}""")
    baseDeDonnees.commit()
    baseDeDonnees.close()    
    embed = discord.Embed(title=f"""Bravo vous avez terminé le démineur!  

Vous avez obtenu un gain de + {nb_fragment} fragment{pluriel(nb_fragment)} !""")
    return embed, None


def get_nb_fragment(txt_fragment) :
    if "10" in txt_fragment :
        return txt_fragment[-2:]
    else :
        return txt_fragment[-1:]