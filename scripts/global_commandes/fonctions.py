from scripts.global_commandes.import_et_variable import *
#--|--# fonctions


#fonction pour restrindre certaines commande uniquement au admins
def admin_restrict(ctx) :
    if ctx.message.author.id in admin_id_user :
        return True
    else :
        return False
    
#fonction pour ajouter une carte. A renseigner : nom, rarete
def ajouter_une_carte(nom, rarete) :
    try :
        baseDeDonnees = sqlite3.connect(f'./assets/database/{db_used}')
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
    global DATE_actuel
    jour_diff = int((date.today()-DATE_actuel).days)
    if int(jour_diff) > 0 :
        DATE_actuel = date.today()  #date du jour
        baseDeDonnees = sqlite3.connect(f'./assets/database/{db_used}')
        curseur = baseDeDonnees.cursor()
        curseur.execute(f"""UPDATE Joueur 
                    SET fragment = fragment + {jour_diff}, fragment_cumule = 0, xp = xp + {jour_diff}""")
        baseDeDonnees.commit()
        baseDeDonnees.close()


#fonction pour tester si un utilisateur est ans la BDD (test seulement)
def test_player_in_bdd(id_user) :
    baseDeDonnees = sqlite3.connect(f'./assets/database/{db_used}')
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
        baseDeDonnees = sqlite3.connect(f'./assets/database/{db_used}')
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
    baseDeDonnees = sqlite3.connect(f'./assets/database/{db_used}')
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"SELECT fragment FROM joueur Where id_discord_player == {id_user}")
    result = curseur.fetchone()[0]
    return result

def get_data_lvl_from_csv(xp_user) :
    with open('./assets/proba/Probabilité drop par niveau.csv', newline='') as csvfile:
            data = list(csv.reader(csvfile, delimiter=","))[1:-1]
    lvl_column = [int(j.pop(-2)) for j in data]
    for lvl in lvl_column :
        if lvl >= xp_user :
            break
    return data, lvl_column, lvl

#return True if the user already did the daily quest
def test_daily_quest_completed(id_user) :
    baseDeDonnees = sqlite3.connect(f'./assets/database/{db_used}')
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

def get_daily_quest() :
    #get toutes les info
    baseDeDonnees = sqlite3.connect(f'./assets/database/{db_used}')
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"""SELECT * FROM daily_quest""")
    result_daily_quest = curseur.fetchall()
    
    #test si on dois rajouter une quest ou non
    #si aucune quête n'a encore été proposé
    if len(result_daily_quest) == 0 :
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
    baseDeDonnees.close()
    return name_quest


#fonction qui permet d'obtenir les infos synchronisé pour tout les joueurs. Si aucune info n'est recise, un simple None sera return.
#Si une info à synchroniser est requise, on ira voir dans la fonction en question dans le fichier des fonctions de la daily quest
def selecteur_info_daily_quest(name_quest) :
    if name_quest == daily_quest_list_name[0] : #roue de la fortune
        return "None"
    elif name_quest == daily_quest_list_name[1] :
        return "None"
    

def selecteur_txt_initialisation_daily_quest(name_quest) :
    if name_quest == daily_quest_list_name[0] : #roue de la fortune
        return ""
    elif name_quest == daily_quest_list_name[1] :
        return "3"
    
    return ""

#fonction pour initialiser le ficihier txt de la save de la daily quest si besoin pour quaques utilisateur
def reset_initialisation_daily_quest_save(name_quest) :
    baseDeDonnees = sqlite3.connect(f'./assets/database/{db_used}')
    curseur = baseDeDonnees.cursor()
    curseur.execute("SELECT id_discord_player FROM Joueur")
    result_id_players = curseur.fetchall()
    result_id_players = [result_id_players[k][0] for k in range(len(result_id_players))]
    for id_user in result_id_players :
        with open(f'./assets/daily_quest_save/{id_user}.txt', 'w') as f:
            f.write(selecteur_txt_initialisation_daily_quest(name_quest))


def pluriel(nb) :
    if nb == 1 :
        return ""
    else :
        return "s"