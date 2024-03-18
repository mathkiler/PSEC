from scripts.global_commandes.import_et_variable import *
#--|--# fonctions


#fonction pour restrindre certaines commande uniquement au admins
def admin_restrict(id_user) :
    if id_user in admin_id_user :
        return True
    else :
        return False
    
#fonction pour ajouter une carte. A renseigner : nom, rarete
def ajouter_une_carte(nom, rarete) :
    try :
        baseDeDonnees = sqlite3.connect(db_path)
        curseur = baseDeDonnees.cursor()
        curseur.execute("INSERT INTO Cartes (nom, rarete) VALUES (?, ?)", (f"{nom}", f"{rarete}"))
        baseDeDonnees.commit()
        baseDeDonnees.close()
        return None
    except Exception as e :
        return e


#fonction qui permet de voir si on a changé de jour. (elle sera présente devant chaque actions) (elle update tout les joueurs en fonction du nombre e jour passé)
#PROBLEME = Si le bot est inactif ou crash au moment de changer de jour jusqu'à la prochaine action, le changement ne prendra pas effet
def test_changement_de_jour() :
    global DATE_actuel, motus_msg_player
    jour_diff = int((date.today()-DATE_actuel).days)
    if int(jour_diff) > 0 :
        motus_msg_player = {} #on reset le motus 
        DATE_actuel = date.today()  #date du jour
        baseDeDonnees = sqlite3.connect(db_path)
        curseur = baseDeDonnees.cursor()
        curseur.execute(f"""UPDATE Joueur 
                    SET fragment = fragment + {jour_diff}, fragment_cumule = 0, xp = xp + {jour_diff}""")
        baseDeDonnees.commit()
        baseDeDonnees.close()


#fonction pour tester si un utilisateur est ans la BDD (test seulement)
def test_player_in_bdd(id_user) :
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    curseur.execute("SELECT id_discord_player FROM Joueur")
    result = curseur.fetchall()
    baseDeDonnees.close()
    members_in_dbb = [result[k][0] for k in range(len(result))]
    if id_user in members_in_dbb :
        return True
    else :
        return False


#fonction pour tester si un utilisatzur est dans la BDD. Si oui, on lui rajoute ddans la bdd les info nécessaire
def test_cration_bdd_user(id_user) :
    if test_player_in_bdd(id_user) == False:
        baseDeDonnees = sqlite3.connect(db_path)
        curseur = baseDeDonnees.cursor()
        curseur.execute(f"SELECT id FROM Cartes")
        result = curseur.fetchall()
        id_cartes = [result[k][0] for k in range(len(result))]
        #ensuite, on regarde tout les gens sur le serveur et si un joueur n'es pas dans la BDD, il y est ajouté avec ses stats à 0
        curseur.execute("INSERT INTO Joueur (id_discord_player, fragment, fragment_cumule, xp, curseur_carte, daily_quest_done) VALUES (?, ?, ?, ?, ?, ?)", (id_user, 0, 0, 0, 0, 0))
        for id in id_cartes :
            curseur.execute("INSERT INTO carte_possede (id_discord_player, id, nombre_carte_possede) VALUES (?, ?, ?)", (id_user, id, 0))    
        baseDeDonnees.commit()
        baseDeDonnees.close()


#fonction pour formater le nom de l'image en nom utilisate en tant qu'url pour afficher l'image ans un embed
def formatage_nom_carte(nom) :
    nom = nom.replace(" ", "_")
    nom = nom.replace("é", "e")
    nom = nom.replace("è", "e")
    nom = nom.replace("ê", "e")
    nom = nom.replace("à", "a")
    nom = nom.replace("'", "")
    return nom


#test si un joueur écrit une commande pour ne pa lui ajouter de fragment auquel cas
def test_joueur_ecrit_commande(msg) :
    for com in liste_comandes :
        if com in msg :
            return True
    return False



def get_fragments_by_user(id_user) :
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"SELECT fragment FROM joueur Where id_discord_player == {id_user}")
    result = curseur.fetchone()[0]
    return result

def get_data_lvl_from_csv(xp_user) :
    with open(CURRENT_PATH+'/assets/proba/Probabilité drop par niveau.csv', newline='') as csvfile:
            data = list(csv.reader(csvfile, delimiter=","))[1:-1]
    lvl_column = [int(j.pop(-2)) for j in data]
    for lvl in lvl_column :
        if lvl >= xp_user :
            break
    return data, lvl_column, lvl

#return True if the user already did the daily quest
def test_daily_quest_completed(id_user) :
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"SELECT daily_quest_done FROM Joueur WHERE id_discord_player == {id_user}")
    daily_quest_done = curseur.fetchone()[0]
    if daily_quest_done == 0 : 
        return False
    else :
        return True



def reset_daily_quest_all_users(baseDeDonnees, curseur) :
    curseur.execute("""UPDATE Joueur
                    SET daily_quest_done = 0""")
    baseDeDonnees.commit()

def get_daily_quest(id_user) :
    global motus_msg_player
    #get toutes les info
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"""SELECT * FROM daily_quest""")
    result_daily_quest = curseur.fetchall()
    
    #test si on dois rajouter une quest ou non
    #si aucune quête n'a encore été proposé
    if len(result_daily_quest) == 0 :
        motus_msg_player = []
        reset_daily_quest_all_users(baseDeDonnees, curseur)
        name_quest = choice(daily_quest_list_name)
        info_quest = selecteur_info_daily_quest(name_quest) #daily_quest_dict_info renvoi le return de la fonction lié à l'event pour les info pour syncrhoniser tout les joueurs
        curseur.execute("INSERT INTO daily_quest (nom_event, jour_event, info_quest) VALUES (?, ?, ?)", (name_quest, str(date.today()), info_quest))
        baseDeDonnees.commit()
        reset_initialisation_daily_quest_save(name_quest)
        baseDeDonnees.close()
        return name_quest
    #on prend la dernière quête 
    jour_diff = int((date.today()-date.fromisoformat(result_daily_quest[-1][1])).days)
    #tet si on a fait le tour des quest pour faire un roulement des quêtes
    if jour_diff >= 1 :
        motus_msg_player = []
        reset_daily_quest_all_users(baseDeDonnees, curseur)
        #on choisi une quest au hazard selon 2 options : 1=le roulement complet des quest a été fini, on reboot et propose une quest au hazard. 2=Le roulement n'est pas fini. On choisi donc une quest dans les quest restantes non proposé
        if len(result_daily_quest) >= len(daily_quest_list_name) :
            curseur.execute("DELETE FROM daily_quest")
            baseDeDonnees.commit()
            name_quest = choice(daily_quest_list_name)
        else :
            #boucle pour choisir une quest qui n'a pas encore été proposé. On est assuré que ça ne boucle pas à l'infini car on passe par le if plus haut si le nombre maximum de quest a été proposé
            name_quest = choice(daily_quest_list_name)
            while name_quest in [result_daily_quest[k][0] for k in range(len(result_daily_quest))] :
                name_quest = choice(daily_quest_list_name)
        #enfin, on ajoute la nouvelle quest à la bdd
        info_quest = selecteur_info_daily_quest(name_quest) #daily_quest_dict_info renvoi le return de la fonction lié à l'event pour les info pour syncrhoniser tout les joueurs
        curseur.execute("INSERT INTO daily_quest (nom_event, jour_event, info_quest) VALUES (?, ?, ?)", (name_quest, str(date.today()), info_quest))
        baseDeDonnees.commit()
        reset_initialisation_daily_quest_save(name_quest)
    #la quest du jour est encore d'actualité (on a pas encore changé de jour)
    else :
        name_quest = result_daily_quest[-1][0]
        create_daily_quest_save_if_not_exist(name_quest, id_user)
    baseDeDonnees.close()
    return name_quest


#fonction qui permet d'obtenir les infos synchronisé pour tout les joueurs. Si aucune info n'est recise, un simple None sera return.
#Si une info à synchroniser est requise, on ira voir dans la fonction en question dans le fichier des fonctions de la daily quest
def selecteur_info_daily_quest(name_quest) :
    if name_quest == daily_quest_list_name[2] :
        with open(CURRENT_PATH+"/assets/motus/mot_possible_motus.txt", "r") as f :
            mot_mystere = choice(f.readlines()).replace("\n", "")
        return mot_mystere
    return "None"

def selecteur_txt_initialisation_daily_quest(name_quest) :
    if name_quest == daily_quest_list_name[1] :
        return "3"
    elif name_quest == daily_quest_list_name[3] : #initialisation du plateau démineur
        plateau_save = ["0\n", "1\n"]
        plateau_save.extend(["c\n" if k == 9*9-1 else "c," for k in range(9*9)])
        ind_list_bomb = []
        for k in range(10) : #nombre de bombes
            placement = randint(0,9*9-1)
            while placement in ind_list_bomb :
                placement = randint(0,9*9-1)
            ind_list_bomb.append(f"{placement},")
        ind_list_bomb[-1] = ind_list_bomb[-1][:-1]+"\n"
        plateau_save.extend(ind_list_bomb)
        plateau_save.append("3")
        return "".join(plateau_save)
    elif name_quest == daily_quest_list_name[4] :
        save_to_paste = ""
        for k in range(6*7) :
            save_to_paste+="v,"
        return save_to_paste[:-1] #[:-1] pour enlever la dernière virgule ","

    return ""

#fonction pour initialiser le ficihier txt de la save de la daily quest si besoin pour quaques utilisateur
def reset_initialisation_daily_quest_save(name_quest) :
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    curseur.execute("SELECT id_discord_player FROM Joueur")
    result_id_players = curseur.fetchall()
    result_id_players = [result_id_players[k][0] for k in range(len(result_id_players))]
    for id_user in result_id_players :
        with open(CURRENT_PATH+f'/assets/daily_quest_save/{id_user}.txt', 'w') as f:
            f.write(selecteur_txt_initialisation_daily_quest(name_quest))

#fonction pour initialiser le ficihier txt de la save de la daily quest si besoin pour quaques utilisateur
def create_daily_quest_save_if_not_exist(name_quest, id_user) :
    if os.path.exists(CURRENT_PATH+f"/assets/daily_quest_save/{id_user}.txt") == False:
        with open(CURRENT_PATH+f'/assets/daily_quest_save/{id_user}.txt', 'w') as f:
            f.write(selecteur_txt_initialisation_daily_quest(name_quest))



def pluriel(nb) :
    if nb == 1 :
        return ""
    else :
        return "s"
    

def select_interaction_argument(interaction1, interaction2) :
    if str(type(interaction1)) == "<class 'discord.interactions.Interaction'>" :
        return interaction1
    else :
        return interaction2

def calc_txt_bdd() :
    baseDeDonnees = sqlite3.connect(CURRENT_PATH+f"/assets/database/{db_used}")
    curseur = baseDeDonnees.cursor()
    txt_all_tables = ""
    try :
        curseur.execute("SELECT * FROM Joueur")
        result_table = curseur.fetchall()
    except :
        result_table = []
    if len(result_table) != 0 : #Si la table est vide
        
        max_len_pseudo = max([len(bot.get_user(result_table[k][0]).name) for k in range(len(result_table))])
        txt_all_tables+=f"""TABLE Joueur :

|-{"".join(["-" for k in range(max_len_pseudo//2-3)])}pseudo{"".join(["-" for k in range(max_len_pseudo//2-3)])}-|-fragment-|-fragment cumule-|---xp---|-curseur-|-daily quest done-|\n"""
        for user in result_table :
            txt_all_tables+=f'| {bot.get_user(user[0]).name}{get_nb_espace(bot.get_user(user[0]).name, max_len_pseudo)} |  {user[1]}{get_nb_espace(user[1], 8)}|  {user[2]}{get_nb_espace(user[2], 15)}|  {user[3]}{get_nb_espace(user[3], 6)}|  {user[4]}{get_nb_espace(user[4], 7)}|  {user[5]}{get_nb_espace(user[5], 16)}|\n'
    else :
        txt_all_tables+=f"""TABLE Joueur :

|----pseudo----|-fragment-|-fragment cumule-|---xp---|-curseur-|-daily quest done-|\n"""

    try :
        curseur.execute("SELECT * FROM Cartes")
        result_table = curseur.fetchall()
    except :
        result_table = []
    if len(result_table) != 0 : #Si la table est vide
            
        max_len = max([len(str(result_table[k][1])) for k in range(len(result_table))])
        txt_all_tables+=f"""\n\n\nTABLE Cartes :
                                                                                                                                    
|-id carte-|-{"".join(["-" for k in range(max_len//2-4)])}nom carte{"".join(["-" for k in range(max_len//2-4)])}-|-----rareté-----|\n"""
        for user in result_table :
            txt_all_tables+=f'|  {user[0]}{get_nb_espace(user[0], 7)} |  {user[1]}{get_nb_espace(user[1], max_len)}|  {user[2]}{get_nb_espace(user[2], 14)}|\n'
    else :
        txt_all_tables+=f"""\n\n\nTABLE Cartes :
                                                                                                                                    
|-id carte-|---nom carte---|-----rareté-----|\n"""


    try :
        curseur.execute("SELECT * FROM carte_possede")
        result_table = curseur.fetchall()
    except :
        result_table = []
    if len(result_table) != 0 : #Si la table est vide
                
        max_len_pseudo = max([len(bot.get_user(result_table[k][0]).name) for k in range(len(result_table))])
        txt_all_tables+=f"""\n\n\nTABLE Carte possède :
                                                                                                                                    
|-{"".join(["-" for k in range(max_len_pseudo//2-3)])}pseudo{"".join(["-" for k in range(max_len_pseudo//2-3)])}--|-id carte-|-nombre carte possédé-|\n"""
        for user in result_table :
            txt_all_tables+=f'|  {bot.get_user(user[0]).name}{get_nb_espace(bot.get_user(user[0]).name, max_len_pseudo)} |  {user[1]}{get_nb_espace(user[1], 8)}|  {user[2]}{get_nb_espace(user[2], 20)}|\n'
    else :
        txt_all_tables+=f"""\n\n\nTABLE Carte possède :
                                                                                                                                    
|-----pseudo-----|-id carte-|-nombre carte possédé-|\n"""

    try :
        curseur.execute("SELECT * FROM daily_quest")
        result_table = curseur.fetchall()
    except :
        result_table = []
    if len(result_table) != 0 : #Si la table est vide
                
        max_len_nom_event = max([len(str(result_table[k][0])) for k in range(len(result_table))])
        max_len_info_quest = max([len(str(result_table[k][2])) for k in range(len(result_table))])
        if max_len_info_quest <= 10 :
            max_len_info_quest = 10
        txt_all_tables+=f"""\n\n\nTABLE daily quest :
                                                                                                                                    
|-{"".join(["-" for k in range(max_len_nom_event//2-4)])}nom event{"".join(["-" for k in range(max_len_nom_event//2-3)])}-|--jour event--|-{"".join(["-" for k in range(max_len_info_quest//2-5)])}info quest{"".join(["-" for k in range(max_len_info_quest//2-5)])}-|\n"""
        for user in result_table :
            txt_all_tables+=f'|  {user[0]}{get_nb_espace(user[0], max_len_nom_event)} |  {user[1]}{get_nb_espace(user[1], 12)}|  {user[2]}{get_nb_espace(user[2], max_len_info_quest)}|\n'
    else :
        txt_all_tables+=f"""\n\n\nTABLE daily quest :
                                                                                                                                    
|----nom event----|--jour event--|----info quest----|\n"""
    baseDeDonnees.close()
    return txt_all_tables

def get_nb_espace(thing_to_print, nb_left) :
    return "".join([" " for k in range(nb_left-len(str(thing_to_print)))])



#test si le message est écrit en MP
def test_message_mp(channel) :
    if "Direct Message with" in str(channel) or "discord.channel.PartialMessageable" in str(channel) :
        return True
    return False



#the if the current game is realy the game that user click on
def check_current_daily_quest(daily_quest_to_test) :
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"""SELECT * FROM daily_quest""")
    current_daily_quest = curseur.fetchall()[-1][0]
    if daily_quest_to_test == current_daily_quest :
        return True
    return False