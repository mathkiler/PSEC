from scripts.global_commandes.import_et_variable import *
from scripts.global_commandes.fonctions import *


#--|--# import des daily quests
from scripts.daily_quest.roue_fortune.bouton_roue_fortune import message_lunch_quest_roue_fortune
from scripts.daily_quest.quackity_button.bouton_quackity_button import message_lunch_quest_quackity_button
from scripts.daily_quest.motus.bouton_motus import message_lunch_quest_motus
from scripts.daily_quest.demineur.bouton_demineur import message_lunch_quest_demineur
from scripts.daily_quest.puissance_4.bouton_puissance_4 import message_lunch_quest_puissance_4


#--|--# toutes commandes seront accéssible via des boutons (créé dans les classes plus bas). Les fonctions suivantes sont les interactions avecles boutons
async def voir_stats(interaction, le_cacher) :
    id_user = interaction.user.id
    test_cration_bdd_user(id_user)
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"SELECT * FROM Joueur WHERE id_discord_player == {id_user}")
    resultat_user_stats = curseur.fetchone()
    curseur.execute(f"SELECT nombre_carte_possede FROM carte_possede WHERE id_discord_player == {id_user} AND nombre_carte_possede != 0")
    nb_cartes_avec_doublon = curseur.fetchall()
    nb_cartes_avec_doublon = sum([nb_cartes_avec_doublon[k][0] for k in range(len(nb_cartes_avec_doublon))])
    curseur.execute(f"SELECT count(*) FROM carte_possede WHERE id_discord_player == {id_user} AND nombre_carte_possede != 0")
    nb_cartes_sans_doublon = curseur.fetchone()[0]
    curseur.execute(f"SELECT nom, rarete, nombre_carte_possede FROM cartes as c, joueur as j, carte_possede as cp WHERE c.id == cp.id and cp.id_discord_player == j.id_discord_player and j.id_discord_player == {id_user} AND nombre_carte_possede != 0")
    resultat_carte_possede = curseur.fetchall()
    baseDeDonnees.close()
    #calcule du lvl du joueur
    _, lvl_column , lvl = get_data_lvl_from_csv(resultat_user_stats[3]) # TODO: replace with getter and delete CSV reading
    # lvl = get_level_by_user(id_user)

    #on range les carte possédé dans leur carégorie pour en même temps compter les doublons de chaques cartes
    carte_arange = {"commun" : {}, "peu courant" : {}, "rare" : {}, "épique" : {}, "héroïque" : {}}
    for carte in resultat_carte_possede :
        if carte[1] == "peu courant" :
            carte_arange[carte[1]][carte[0][3:]] = carte[2]
        else :
            carte_arange[carte[1]][carte[0][2:]] = carte[2]

    txt_print_cartes = ""
    for rarete in carte_arange :
        if len(carte_arange[rarete]) != 0 :
            txt_print_cartes+=rarete+" : \n"
            for carte in carte_arange[rarete] :
                txt_print_cartes+="     "+str(carte_arange[rarete][carte])+" possédé : "+carte+"\n"
            txt_print_cartes+="\n\n"
    
    await interaction.response.send_message(f"""Stats du joueur <@{id_user}> : 
               
Nombre de fragments actuels : {resultat_user_stats[1]}
Nombre de fragments du jour : {resultat_user_stats[2]}/50
Exp : {resultat_user_stats[3]} (niv {lvl_column.index(lvl)})
Nombre de cartes obtenues (en comptant les doublons) : {nb_cartes_avec_doublon}
Nombre de cartes obtenues (sans compter les doublons) : {nb_cartes_sans_doublon}

Cartes obtenues :
```{txt_print_cartes}```""", ephemeral=le_cacher)


#fonction pour ouvrir un caisse
async def opening(interaction, nb_opening) :
    #on chope les info du joueur
    id_user = interaction.user.id
    test_cration_bdd_user(id_user)
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"SELECT * FROM Joueur WHERE id_discord_player == {id_user}")
    resultat_user_stats = curseur.fetchone()
    #on regarde s'il a assez de fragments pour faire l'opening en fonction du nombre de carte qu'il veux ouvrir
    if resultat_user_stats[1] < 5*nb_opening :
            await interaction.response.send_message(f"Fond insuffisant. Il vous manque {nb_opening*5-resultat_user_stats[1]} fragments.", ephemeral=True)
    else :
        #on lit le taux de drop en fonction du niveau du joueur
        carte_obtained = pioche_cartes(curseur, baseDeDonnees, id_user, nb_opening)
        
        #Enfin, on affiche le résultat au joueur sur discord
        img_path = CURRENT_PATH+f"/assets/animations/open-box.gif"
        file = discord.File(img_path)
        embed = discord.Embed()
        embed.set_image(url=f"attachment://open-box.gif")
        msg = await interaction.response.send_message(f"<@{id_user}>",embed=embed, file=file)
        await asyncio.sleep(5)
        #le premier message change le gif de la box en un carte. Le reste envera des nouveaux messages 
        for c in range(nb_opening) :
            img_path = CURRENT_PATH+f'/assets/cartes/{carte_obtained[c][1]}.png'
            file = discord.File(img_path)
            embed = discord.Embed(title = f"Vous avez tiré une carte {carte_obtained[c][2]} !")
            embed.set_image(url=f"attachment://{formatage_nom_carte(carte_obtained[c][1])}.png")
            if c == 0 :
                await msg.edit(embed=embed, file=file)
            else :
                await interaction.followup.send(f"<@{id_user}>", embed=embed, file=file)

#fonction utilisé pour obtenir une liste de carte pioché (et leurs infos) en fonction du nombre de carte à piocher
def pioche_cartes(curseur, baseDeDonnees, id_user, nb_opening) :
    carte_obtained = []
    for c in range(nb_opening) :
        #partie qui va piocher la carte en fonction des proba du niveau du joueur
        random_number = randint(1,10000) #random factor into 1 and 10000
        tab_proba_by_level = PROBA[get_level_by_user(id_user)] #probabilioty list by level

        cumule_proba_value = 0
        niveau_rarete = -1
        for i in range(len(tab_proba_by_level)):
            cumule_proba_value+=tab_proba_by_level[i]
            if random_number <= cumule_proba_value :
                niveau_rarete = i
                break
        
        if niveau_rarete == -1 :
            raise Exception("Failed to catch card's quality")
                    
        #on affecte tout les changements à la BDD
        curseur.execute(f"SELECT id, nom, rarete FROM Cartes WHERE rarete == '{nom_rarete[niveau_rarete]}' ORDER BY RANDOM() LIMIT 1 ")
        carte_tiree = curseur.fetchone()
        curseur.execute(f"""UPDATE Joueur 
                    SET fragment = fragment - 5
                    WHERE id_discord_player == {id_user}""")
        baseDeDonnees.commit()
        curseur.execute(f"""UPDATE carte_possede 
                    SET nombre_carte_possede = nombre_carte_possede + 1
                    WHERE id_discord_player == {id_user} AND id == {carte_tiree[0]}""")
        baseDeDonnees.commit()
        carte_obtained.append(carte_tiree)
    baseDeDonnees.close()
    return carte_obtained
        

#fonction pour créer l'album puis l'envoyer (à tout le monde ou non)
async def mon_album(interaction, le_montrer) :
    await interaction.response.defer(ephemeral=le_montrer)
    #première partie, on récupère le nom de toutes le cartes que le joueur possède
    id_user = interaction.user.id
    test_cration_bdd_user(id_user)
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"SELECT nom FROM cartes as c, joueur as j, carte_possede as cp WHERE c.id == cp.id and cp.id_discord_player == j.id_discord_player and j.id_discord_player == {id_user} AND nombre_carte_possede != 0")
    resultat_carte_possede = curseur.fetchall()
    baseDeDonnees.close()
    resultat_carte_possede = [resultat_carte_possede[k][0] for k in range(len(resultat_carte_possede))]
    sorted(resultat_carte_possede) #on réarange la liste des cartes obtenu au cas où elle est malangé bizarement
        #on calcule la position des images (on démare à -1 car on va compter la carte unknown (carte qui montre celles non obtenue))
    nombre_totale_carte = len(ALL_CARTES)
    width_carte = 321
    height_carte = 515
    nb_carte_square = int(sqrt(nombre_totale_carte))
    nb_carte_remain = nombre_totale_carte-(nb_carte_square**2)
    if nb_carte_remain == 0 :
        nb_carte_remain = 0
    else :
        nb_carte_remain = 1
    
    #enfin, on créer l'image
    album = Image.new('RGBA', (width_carte*nb_carte_square, height_carte*(nb_carte_square+nb_carte_remain)))
    count = 0
    for carte in ALL_CARTES :
        if carte in resultat_carte_possede :
            im_carte = Image.open(CURRENT_PATH+f"/assets/cartes/{carte}.png")
        else :
            im_carte = Image.open(CURRENT_PATH+f"/assets/cartes/.inconnue.png")
        album.paste(im_carte, ((count%nb_carte_square)*width_carte,  (count//nb_carte_square)*height_carte))
        count+=1
    name_album = randint(100000, 999999)
    album.save(CURRENT_PATH+f"/assets/img_tamp/{name_album}.png")
    await interaction.followup.send(f"Album de <@{id_user}> :", file=discord.File(CURRENT_PATH+f'/assets/img_tamp/{name_album}.png'), ephemeral=le_montrer)
    os.remove(CURRENT_PATH+f"/assets/img_tamp/{name_album}.png")


#fonction pour affihcer ses cartes une par une
async def initialisation_mes_cartes(interaction) :
    #on chope les info du joueur (id, nombre de cartes, quel carte il a...)
    id_user = interaction.user.id
    test_cration_bdd_user(id_user)
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"SELECT curseur_carte FROM Joueur WHERE id_discord_player == {id_user}")
    index_curseur = curseur.fetchone()[0]
    curseur.execute(f"SELECT nom, rarete, nombre_carte_possede FROM cartes as c, joueur as j, carte_possede as cp WHERE c.id == cp.id and cp.id_discord_player == j.id_discord_player and j.id_discord_player == {id_user} AND nombre_carte_possede != 0")
    derange_ordre_cartes = curseur.fetchall()


    rarete_list_name_file = ["C_", "PC_", "R_", "E_", "H_"]
    rarete_list_arrange = [[], [], [], [], []] #arrangé dans le sens "C_", "PC_", "R_", "E_", "H_"
    for carte in derange_ordre_cartes :
        for ind_rarete in range(len(rarete_list_name_file)) :
            if rarete_list_name_file[ind_rarete] in carte[0] :
                break
        rarete_list_arrange[ind_rarete].append(carte)
    resultat_carte_possede = rarete_list_arrange[0]
    for k in range(1,5) :
        resultat_carte_possede.extend(rarete_list_arrange[k])

    nb_cartes = len(resultat_carte_possede)
    baseDeDonnees.close()

    return resultat_carte_possede, index_curseur, nb_cartes
    

async def selecteur_button_mes_cartes(interaction : discord.Interaction, button) :
    #si le bouton est appuyé, on update la variable du curseur puis on affiche la nouvelle image
    #on chope les info du joueur (id, nombre de cartes, quel carte il a...)
    id_user = interaction.user.id
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"SELECT curseur_carte FROM Joueur WHERE id_discord_player == {id_user}")
    index_curseur = curseur.fetchone()[0]
    curseur.execute(f"SELECT nom, rarete, nombre_carte_possede FROM cartes as c, joueur as j, carte_possede as cp WHERE c.id == cp.id and cp.id_discord_player == j.id_discord_player and j.id_discord_player == {id_user} AND nombre_carte_possede != 0")
    resultat_carte_possede = curseur.fetchall()
    nb_cartes = len(resultat_carte_possede)
    #en fonction du bouton appuyé, on renvoi vers la bonne fonction pour bien changer le curseur
    if button == "five_prev" :
        index_curseur = mes_cartes_action_five_prev_buton(nb_cartes, index_curseur)
    elif button == "one_prev" :
        index_curseur = mes_cartes_action_one_prev_buton(nb_cartes, index_curseur)
    elif button == "one_next" :
        index_curseur = mes_cartes_action_one_next_buton(nb_cartes, index_curseur)
    elif button == "five_next" :
        index_curseur = mes_cartes_action_five_next_buton(nb_cartes, index_curseur)
    elif button == "stay_here" :
        pass
    #on update et affiche ce qu'il faut
    curseur.execute(f"""UPDATE Joueur 
        SET curseur_carte = {index_curseur}
        WHERE id_discord_player == {id_user}""")
    baseDeDonnees.commit()
    baseDeDonnees.close()
    #enfin on affect la nouvelle image à un nouveau embed pour l'affecter à l'embed principal de la fonction mes_cartes
    img_path = CURRENT_PATH+f"/assets/cartes/{resultat_carte_possede[index_curseur][0]}.png"
    new_file = discord.File(img_path)
    new_embed = discord.Embed(title=f"{index_curseur+1}/{nb_cartes}\nPossédée(s) : {resultat_carte_possede[index_curseur][2]}\nExp par doublon recylé ({resultat_carte_possede[index_curseur][1]}) : {(nom_rarete.index(resultat_carte_possede[index_curseur][1])+1)*2}")
    new_embed.set_image(url=f"attachment://{formatage_nom_carte(resultat_carte_possede[index_curseur][0])}.png")
    await interaction.response.edit_message(embed=new_embed, file=new_file) # attach the new image file with the embed


#fonction pour changer le curseur en fonction
def mes_cartes_action_five_prev_buton(nb_cartes, index_curseur): #ici, interaction mais référence à l'interaction avec le bouton "mes cartes" de début
    if index_curseur > 4 : 
        index_curseur-=5
    else :
        index_curseur = 0
    return index_curseur

def mes_cartes_action_one_prev_buton(nb_cartes, index_curseur): #ici, interaction mais référence à l'interaction avec le bouton "mes cartes" de début
    if index_curseur > 0 : 
        index_curseur-=1
    else :
        index_curseur = nb_cartes-1
    return index_curseur

def mes_cartes_action_one_next_buton(nb_cartes, index_curseur): #ici, interaction mais référence à l'interaction avec le bouton "mes cartes" de début
    if index_curseur < nb_cartes-1 : 
        index_curseur+=1
    else :
        index_curseur = 0 
    return index_curseur

def mes_cartes_action_five_next_buton(nb_cartes, index_curseur): #ici, interaction mais référence à l'interaction avec le bouton "mes cartes" de début
    if index_curseur < nb_cartes-6 : 
        index_curseur+=5
    else :
        index_curseur = nb_cartes-1
    return index_curseur


#fonction pour faire supprimer un doublon et obtenir de l'xp
async def mes_cartes_supprime_doublon(interaction, combien_doublon) :
    id_user = interaction.user.id
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"SELECT curseur_carte FROM Joueur WHERE id_discord_player == {id_user}")
    index_curseur = curseur.fetchone()[0]
    curseur.execute(f"SELECT cp.id, rarete, nombre_carte_possede, nom FROM cartes as c, joueur as j, carte_possede as cp WHERE c.id == cp.id and cp.id_discord_player == j.id_discord_player and j.id_discord_player == {id_user} AND nombre_carte_possede != 0")
    resultat_carte_possede = curseur.fetchall()
    carte_selected_info = resultat_carte_possede[index_curseur]
    if carte_selected_info[2] > 1 or combien_doublon == "ALL" :
        if combien_doublon == "UN" : 
            gain_xp = supprimer_UN_doublon(carte_selected_info)
            nb_carte_destroy = 1
        elif combien_doublon == "TOUS" :
            gain_xp = supprimer_TOUS_doublon(carte_selected_info)
            nb_carte_destroy = carte_selected_info[2]-1
        elif combien_doublon == "ALL" :
            gain_xp = supprimer_ALL_doublon(resultat_carte_possede, baseDeDonnees, curseur, id_user)
            nb_carte_destroy = carte_selected_info[2]-1
        curseur.execute(f"""UPDATE Joueur 
            SET xp = xp + {gain_xp}
            WHERE id_discord_player == {id_user}""")
        baseDeDonnees.commit()
        if combien_doublon != "ALL" :
            curseur.execute(f"""UPDATE carte_possede 
                SET nombre_carte_possede = nombre_carte_possede - {nb_carte_destroy}
                WHERE id_discord_player == {id_user} AND id == {carte_selected_info[0]}""")
            baseDeDonnees.commit()
        baseDeDonnees.close()
        await selecteur_button_mes_cartes(interaction, "stay_here")
        await interaction.followup.send(f"Vous avez obtenu **{gain_xp}** exp en recyclant vos doublons.", ephemeral=True)
    else :
        await interaction.response.send_message(f"Il ne vous reste plus aucun doublon de {carte_selected_info[3]}.", ephemeral=True)

def supprimer_UN_doublon(carte_selected_info) :
    return (nom_rarete.index(carte_selected_info[1])+1)*2

def supprimer_TOUS_doublon(carte_selected_info) :
    return ((nom_rarete.index(carte_selected_info[1])+1)*2)*(carte_selected_info[2]-1)

def supprimer_ALL_doublon(resultat_carte_possede, baseDeDonnees, curseur, id_user) :
    gain_xp = 0
    for carte in resultat_carte_possede :
        if carte[2] > 1 :
            gain_xp+=((nom_rarete.index(carte[1])+1)*2)*(carte[2]-1)
            curseur.execute(f"""UPDATE carte_possede 
                    SET nombre_carte_possede = 1
                    WHERE id_discord_player == {id_user} AND id == {carte[0]}""")
            baseDeDonnees.commit()
    return gain_xp



#fonction pour selectionner le message d'arrivé dans la quest (la plus part du temps les règles). On passe part un selecteur dans une fonction car on veux garder l'information de l'interaction
async def selecteur_lunch_quest(name_quest, interaction) :
    if name_quest == "roue de la fortune" :
        await message_lunch_quest_roue_fortune(interaction)
    elif name_quest == "bouton de quackity" :
        await message_lunch_quest_quackity_button(interaction)
    elif name_quest == "motus" :
        await message_lunch_quest_motus(interaction)
    elif name_quest == "demineur" :
        await message_lunch_quest_demineur(interaction)
    elif name_quest == "puissance 4" :
        await message_lunch_quest_puissance_4(interaction)



#fonction pour faire prendre effet au reroll
async def effet_reroll(interaction) :
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"SELECT xp FROM Joueur WHERE id_discord_player == {interaction.user.id}")
    xp_user = curseur.fetchone()[0]
    curseur.execute(f"""UPDATE Joueur 
            SET xp = 0, fragment = fragment + {xp_user//2}
            WHERE id_discord_player == {interaction.user.id}""")
    baseDeDonnees.commit()
    baseDeDonnees.close()
    await interaction.response.send_message(f"Vous avez obtenu {xp_user//2} fragments.", ephemeral=True)




async def calc_classement(interaction, type_classement) :
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    if type_classement == "Collectionneur" :
        curseur.execute(f"SELECT count(nom), j.id_discord_player FROM cartes as c, joueur as j, carte_possede as cp WHERE c.id == cp.id and cp.id_discord_player == j.id_discord_player AND nombre_carte_possede != 0 GROUP BY cp.id_discord_player ORDER BY count(nom) DESC")
        resultat_carte_possede = curseur.fetchall()
        info_classement = {
            "name_categorie" : type_classement,
            "description" : "Le plus de cartes possédées (sans doublons)",
            "info_display" : "cartes : ",
            "classement" : ordre_classement_and_equality(interaction, resultat_carte_possede)
        }
    elif type_classement == "Grip sou" :
        curseur.execute(f"SELECT fragment, id_discord_player FROM Joueur order by fragment DESC")
        resultat_carte_possede = curseur.fetchall()
        info_classement = {
            "name_categorie" : type_classement,
            "description" : "Le plus de fragments",
            "info_display" : "fragments : ",
            "classement" : ordre_classement_and_equality(interaction, resultat_carte_possede)
        }

    elif type_classement == "Farmer" :
        curseur.execute(f"SELECT xp, id_discord_player FROM Joueur order by xp DESC")
        resultat_carte_possede = curseur.fetchall()
        info_classement = {
            "name_categorie" : type_classement,
            "description" : "Le plus de XP",
            "info_display" : "XP : ",
            "classement" : ordre_classement_and_equality(interaction, resultat_carte_possede)
        }
    elif type_classement == "Super fan" :
        curseur.execute(f"SELECT max(nombre_carte_possede), id_discord_player, c.nom FROM carte_possede as cp, Cartes as c WHERE cp.id == c.id GROUP BY id_discord_player ORDER BY max(nombre_carte_possede) DESC")
        resultat_carte_possede = curseur.fetchall()
        for k in range(len(resultat_carte_possede)) :
            resultat_carte_possede[k] = [resultat_carte_possede[k][0], resultat_carte_possede[k][1], resultat_carte_possede[k][2]] #on trensforme le tuple en liste
            if resultat_carte_possede[k][2][:resultat_carte_possede[k][2].index("_")] == "PC" :
                resultat_carte_possede[k][2] = resultat_carte_possede[k][2][3:]
            else :
                resultat_carte_possede[k][2] = resultat_carte_possede[k][2][2:]
        info_classement = {
            "name_categorie" : type_classement,
            "description" : "Le plus de fois la même carte",
            "info_display" : "Nombre : ",
            "classement" : ordre_classement_and_equality(interaction, resultat_carte_possede)
        }
    

    img_ranked = Image.open(CURRENT_PATH+f"/assets/classement/classement_template.png")
    I1 = ImageDraw.Draw(img_ranked)
 
    # Adding text for title categorie (Collectionneur ici)
    title_font = ImageFont.truetype(CURRENT_PATH+f"/assets/fonts/arial.ttf", 40)
    bbox = title_font.getbbox(info_classement["name_categorie"])
    I1.text((500-bbox[2]//2, 490-bbox[3]//2), info_classement["name_categorie"], font=title_font, stroke_width=1, fill =(0, 0, 0))
    
    #adding description
    title_font = ImageFont.truetype(CURRENT_PATH+f"/assets/fonts/arial.ttf", 15)
    bbox = title_font.getbbox(info_classement["description"])
    I1.text((500-bbox[2]//2, 520-bbox[3]//2), info_classement["description"], font=title_font, fill =(0, 0, 0))
    
    #rank current player
    if info_classement["classement"]["self_player"]["in_podium"] == False :
        title_font = ImageFont.truetype(CURRENT_PATH+f"/assets/fonts/arial.ttf", 25)
        msg = info_classement["classement"]["self_player"]["info_self_player"][-1]+info_classement["classement"]["self_player"]["info_self_player"][1]
        bbox = title_font.getbbox(msg)
        I1.text((500-bbox[2]//2, 580-bbox[3]//2), msg, font=title_font, fill=(0, 0, 0))
        if len(info_classement["classement"]["self_player"]["info_self_player"]) >= 4 :
            msg = info_classement["info_display"]+str(info_classement["classement"]["self_player"]["info_self_player"][0])+" ("+info_classement["classement"]["self_player"]["info_self_player"][2]+")"
        else :
            msg = info_classement["info_display"]+str(info_classement["classement"]["self_player"]["info_self_player"][0])
        bbox = title_font.getbbox(msg)
        I1.text((500-bbox[2]//2, 610-bbox[3]//2), msg, font=title_font, fill =(0, 0, 0))
    title_font = ImageFont.truetype(CURRENT_PATH+f"/assets/fonts/arial.ttf", 25)
    #adding pp and rank and info 
    coords_classement_pp = [(450, 35, -1/2), (184, 140, -1), (700, 165, 0)]
    title_font = ImageFont.truetype(CURRENT_PATH+f"/assets/fonts/arial.ttf", 20)
    for ind_podium in range(3) :
        ind_player_pixel = 0
        if len(info_classement["classement"][str(ind_podium)]) > 1 :
             coords_classement_pp = [(450, 35, -1/2), (244, 140, -1), (646, 165, 0)]
        start_display_pp = coords_classement_pp[ind_podium][0]+int(120*coords_classement_pp[ind_podium][2]*(len(info_classement["classement"][str(ind_podium)])-1)) #var pour savoir où commencer en pixel
        for user_rank in info_classement["classement"][str(ind_podium)] :
            User = await bot.fetch_user(user_rank[1])
            update_get_pp_by_id_user(user_rank[1], str(User.avatar))
            pp_user = Image.open(CURRENT_PATH+f"/assets/storage_pp_users/{user_rank[1]}.png")
            pp_user.thumbnail((100, 100))
            Image.Image.paste(img_ranked, pp_user, (start_display_pp+ind_player_pixel, coords_classement_pp[ind_podium][1]))
            pp_user.close()
            msg = info_classement["info_display"]+str(user_rank[0])
            bbox = title_font.getbbox(msg)
            try :
                msg+="\n("+user_rank[2]+")"
            except :
                pass
            I1.text(((start_display_pp+ind_player_pixel+50)-bbox[2]//2, (coords_classement_pp[ind_podium][1]+115)-bbox[3]//2), msg, font=title_font, fill =(0, 0, 0))
            user_name = User.display_name    
            bbox = title_font.getbbox(user_name)
            I1.text(((start_display_pp+ind_player_pixel+50)-bbox[2]//2, (coords_classement_pp[ind_podium][1]-20)-bbox[3]//2), user_name, font=title_font, fill =(0, 0, 0))
            ind_player_pixel+=120
        

    #save image
    random_name = randint(1000000, 9999999)
    img_ranked.save(CURRENT_PATH+f"/assets/img_tamp/{random_name}.png")
    img_ranked.close()
    return random_name
    
    



async def get_other_user_echange(id_user, lines, ind_plateau) :
    info_plateau = lines[ind_plateau].split("|")
    if int(info_plateau[0]) == id_user :
        placement_ind_user = 0
        id_user_envoyeur = int(info_plateau[1])
    else :
        id_user_envoyeur = int(info_plateau[0])
        placement_ind_user = 1
    user_envoyeur = await bot.fetch_user(id_user_envoyeur)
    return user_envoyeur, placement_ind_user


#func du bouton pour annuler l'échange
async def action_echange_annule(interaction) :
    _, ind_plateau, lines = plateau_echange_exist(interaction.user.id)
    annulation_echange(interaction.user.id)
    user_envoyeur, _ = await get_other_user_echange(interaction.user.id, lines, ind_plateau)
    await interaction.response.send_message(f"Échange avec **{user_envoyeur.global_name}** annulé")
    await user_envoyeur.send(f"**{interaction.user.global_name}** a refusé l'échange")


async def action_echange_confirme_demarage(interaction) :
    _, ind_plateau, lines = plateau_echange_exist(interaction.user.id)
    user_envoyeur, _ = await get_other_user_echange(interaction.user.id, lines, ind_plateau)
    await interaction.response.send_message(f"Échange avec **{user_envoyeur.global_name}** démarré.\n Faites un **/echange_ajout_carte** pour ajouter des cartes à échanger\n Faites un **/echange_retire_carte** pour retirer des cartes\nEnfin, appuyez sur `Effectuer l'échange` pour demander à l'autre d'effectuer l'échange", ephemeral=True)
    await user_envoyeur.send(f"Échange avec **{interaction.user.global_name}** démarré.\n Faites un **/echange_ajout_carte** pour ajouter des cartes à échanger\n Faites un **/echange_retire_carte** pour retirer des cartes\nEnfin, appuyez sur `Effectuer l'échange` pour demander à l'autre d'effectuer l'échange")


async def analyse_select_card_echange(interaction, carte, quantite, ind_plateau, lines) :
    id_user = interaction.user.id
    test_cration_bdd_user(id_user)
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"SELECT nom, nombre_carte_possede FROM cartes as c, joueur as j, carte_possede as cp WHERE c.id == cp.id and cp.id_discord_player == j.id_discord_player and j.id_discord_player == {id_user} AND nombre_carte_possede != 0")
    resultat_carte_possede = curseur.fetchall()
    baseDeDonnees.close()
    #on vire la saut de ligne \n avant pour éviter les bugs
    lines[ind_plateau] = lines[ind_plateau].replace("\n", "")
    for test_carte in resultat_carte_possede :
        if test_carte[0].lower() == carte : 
            if test_carte[1] >= quantite : #affectation de l'ajout de la carte
                info_plateau = lines[ind_plateau].split("|")
                user_envoyeur, placement_ind_user = await get_other_user_echange(id_user, lines, ind_plateau)
                new_cards_player = ""
                card_changed = False
                for card_player in info_plateau[placement_ind_user+2].split("-") :
                    info_card = card_player.split("#")
                    if carte == info_card[0] : #si la carte éxite déjà dans l'échange
                        card_changed = True
                        info_card[1] = str(quantite)
                    new_cards_player+="-"+"#".join(info_card)
                info_plateau[placement_ind_user+2] = new_cards_player[1:]
                if card_changed == False : #si c'est une nouvelle carte
                    if len(info_plateau[placement_ind_user+2]) == 0 :
                        prefix = ""
                    else :
                        prefix = "-"
                    info_plateau[placement_ind_user+2]+=prefix+carte+"#"+str(quantite)
                info_plateau = "|".join(info_plateau)
                if ind_plateau+1 == len(lines) :
                    lines[ind_plateau] = info_plateau
                else :
                    lines[ind_plateau] = info_plateau+"\n"
                with open(CURRENT_PATH+f"/assets/plateau_echange/plateaux.txt", "w") as file_plateau:
                    file_plateau.write("".join(lines))
                await display_current_plateau(interaction, user_envoyeur, {"info" : "ajout", "carte" : fomatage_carte_into_printable(carte), "quantite" : quantite}, ind_plateau, lines)
                return
            else : 
                await interaction.response.send_message(f"Vous n'avez pas la quantité nécessaire de cartes **{fomatage_carte_into_printable(carte)}**. Vous en avez **{test_carte[1]}**, mais voulez en échanger **{quantite}**", ephemeral=True)
            return
    await interaction.response.send_message(f"Vous ne possédez pas la carte **{fomatage_carte_into_printable(carte)}**", ephemeral=True)
    
    



async def display_current_plateau(interaction, user_envoyeur, info_changement, ind_plateau, lines) :
    lines[ind_plateau] = lines[ind_plateau].replace("\n", "")
    info_plateau = lines[ind_plateau].split("|")
    current_user_tested = await bot.fetch_user(int(info_plateau[0]))
    txt_echange = f"**{current_user_tested.global_name}** échange :"
    if info_plateau[2] != "" :
        for card_player in info_plateau[2].split("-") :
            info_card = card_player.split("#")
            txt_echange+=f"\n{fomatage_carte_into_printable(info_card[0])} | quantité(s) : {info_card[1]}"
    txt_echange+="\n\n        :arrows_clockwise:\n"
    current_user_tested = await bot.fetch_user(int(info_plateau[1]))
    txt_echange+= f"\n**{current_user_tested.global_name}** échange :"
    if info_plateau[3] != "" :
        for card_player in info_plateau[3].split("-") :
            info_card = card_player.split("#")
            txt_echange+=f"\n{fomatage_carte_into_printable(info_card[0])} | quantité(s) : {info_card[1]}"
    embed = discord.Embed(title=f"Plateau d'échange", description=txt_echange)
    
    if info_changement["info"] == "ajout" :
        await interaction.response.send_message(embed=embed, ephemeral=True, view=Affect_echange())
        await user_envoyeur.send(f"**{interaction.user.global_name}** ajoute la carte **{info_changement['carte']}** en **{info_changement['quantite']}** exemplaire{pluriel(int(info_changement['quantite']))}. Voici le nouvel échange :", embed=embed, view=Affect_echange())
    elif info_changement["info"] == "suppr" :
        await interaction.response.send_message(embed=embed, ephemeral=True, view=Affect_echange())
        await user_envoyeur.send(f"**{interaction.user.global_name}** supprime la carte **{info_changement['carte']}** de l'échange. Voici le nouvel échange :", embed=embed, view=Affect_echange())
    elif info_changement["info"] == "affect_echange" :
        await interaction.response.send_message("La demande d'échange a été envoyée. En attente d'une réponse", ephemeral=True)
        await user_envoyeur.send(f"{interaction.user.global_name} souhaite procéder à l'échange ci-dessous :", embed=embed, view=Acceptation_affect_echange())
    elif info_changement["info"] == "annule_demande_affectation" :
        await interaction.response.send_message("Vous avez bien refusé la demande d'échange. Voici le plateau d'échange en cours : ", embed=embed, view=Affect_echange(), ephemeral=True)
        await user_envoyeur.send(f"{interaction.user.global_name} a refusé votre proposition d'échange. Voici le plateau d'échange en cours : ", embed=embed, view=Affect_echange())
    elif info_changement["info"] == "affiche_current_plateau" :
        await interaction.response.send_message("Voici le plateau d'échange en cours : ", embed=embed, view=Affect_echange(), ephemeral=True)
    elif info_changement["info"] == "problem_transacion" :
        await interaction.response.send_message("Il y a eu un problème lors de la transaction : une ou plusieurs cartes ont voulu être échangés alors que son possesseur n'en avait pas assez. Voici le plateau d'échange réajusté : ", embed=embed, view=Affect_echange(), ephemeral=True)
        await user_envoyeur.send(f"Il y a eu un problème lors de la transaction : une ou plusieurs cartes ont voulu être échangés alors que son possesseur n'en avait pas assez. Voici le plateau d'échange réajusté : ", embed=embed, view=Affect_echange())


async def action_echange_affect(interaction) :
    _, ind_plateau, lines = plateau_echange_exist(interaction.user.id)
    user_envoyeur, _ = await get_other_user_echange(interaction.user.id, lines, ind_plateau)
    await display_current_plateau(interaction, user_envoyeur, {"info" : "affect_echange"}, ind_plateau, lines)
    

#class bouton pour lancer la demande d'échange
class Affect_echange(discord.ui.View): 
    @discord.ui.button(label="Effectuer l'échange", style=discord.ButtonStyle.primary)
    async def Confirmer_button_callback(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await action_echange_affect(interaction)



async def echange_annule_affectation(interaction) :
    _, ind_plateau, lines = plateau_echange_exist(interaction.user.id)
    user_envoyeur, _ = await get_other_user_echange(interaction.user.id, lines, ind_plateau)
    await display_current_plateau(interaction, user_envoyeur, {"info" : "annule_demande_affectation"}, ind_plateau, lines)


async def echange_confirme_affectation(interaction) :
    _, ind_plateau, lines = plateau_echange_exist(interaction.user.id)
    lines[ind_plateau] = lines[ind_plateau].replace("\n", "")
    info_plateau = lines[ind_plateau].split("|")
    user_envoyeur, _ = await get_other_user_echange(interaction.user.id, lines, ind_plateau)
    all_info_echange = [
        {
            "id_user" : int(info_plateau[k]),
            "cartes" : [card.split("#")[0] for card in info_plateau[k+2].split("-")],
            "quantite" : [card.split("#")[-1] for card in info_plateau[k+2].split("-")]
        } for k in range(2)
    ]

    all_cartes_lower = [c.lower() for c in ALL_CARTES]
    ind_player=0
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    for player in all_info_echange :
        for ind_carte in range(len(player["cartes"])) :
            if player["cartes"][0] != "" :
                nom_carte_with_prefix = ALL_CARTES[all_cartes_lower.index(player["cartes"][ind_carte])]
                curseur.execute(f"SELECT id FROM Cartes WHERE nom == '{nom_carte_with_prefix}'" )
                id_carte_tested = curseur.fetchone()[0]
                curseur.execute(f"SELECT nombre_carte_possede FROM carte_possede WHERE id == {id_carte_tested} AND id_discord_player == {player['id_user']}" )
                nb_carte_possede_current = curseur.fetchone()[0]
                if nb_carte_possede_current < int(player["quantite"][ind_carte]) : #si le nombre de carte possédé ne correspond pas réelement à son nombre de carte,, on réajuste et le dis
                    baseDeDonnees.close()
                    await echange_reajustement_quantite(interaction, user_envoyeur, lines, ind_plateau, info_plateau, all_cartes_lower)
                    return

                curseur.execute(f"""UPDATE carte_possede 
                    SET nombre_carte_possede = nombre_carte_possede - {int(player["quantite"][ind_carte])}
                    WHERE id_discord_player == {player["id_user"]} AND id == {id_carte_tested}""")
                
                curseur.execute(f"""UPDATE carte_possede 
                    SET nombre_carte_possede = nombre_carte_possede + {int(player["quantite"][ind_carte])}
                    WHERE id_discord_player == {all_info_echange[ind_player-1]["id_user"]} AND id == {id_carte_tested}""")
        ind_player+=1
    baseDeDonnees.commit()
    baseDeDonnees.close()
    annulation_echange(interaction.user.id)
    await interaction.response.send_message("Vous avez accepté l'échange. Transaction effectuée", ephemeral=True)
    await user_envoyeur.send(f"**{interaction.user.global_name}** a accepté l'échange. Transaction effectuée")


async def echange_reajustement_quantite(interaction, user_envoyeur, lines, ind_plateau, info_plateau, all_cartes_lower) :
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    for ind_carte_player in range(2, 4) :
        info_cartes = info_plateau[ind_carte_player].split("-")
        for ind_carte in range(len(info_cartes)) :
            current_card = info_cartes[ind_carte].split("#")
            nom_carte_with_prefix = ALL_CARTES[all_cartes_lower.index(current_card[0])]
            curseur.execute(f"SELECT nombre_carte_possede FROM carte_possede as cp, cartes as c WHERE id_discord_player = {int(info_plateau[ind_carte_player-2])} AND cp.id == c.id AND nom == '{nom_carte_with_prefix}'" )
            nb_carte_possede_current = curseur.fetchone()[0]
            if nb_carte_possede_current <= int(current_card[1]) :
                current_card[1] = str(nb_carte_possede_current)
            info_cartes[ind_carte] = "#".join(current_card)
        info_plateau[ind_carte_player] = "-".join(info_cartes)
    lines[ind_plateau] = "|".join(info_plateau)
    with open(CURRENT_PATH+f"/assets/plateau_echange/plateaux.txt", "w") as file_plateau:
        file_plateau.write("".join(lines))
    await display_current_plateau(interaction, user_envoyeur, {"info" : "problem_transacion"}, ind_plateau, lines)
    





#class bouton pour accépter ou non laffectation de l'échange
class Acceptation_affect_echange(discord.ui.View): 
    @discord.ui.button(label="Confirmer", style=discord.ButtonStyle.green)
    async def Confirmer_button_callback(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await echange_confirme_affectation(interaction)


    @discord.ui.button(label="Refuser", style=discord.ButtonStyle.red)
    async def Annuler_button_callback(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await echange_annule_affectation(interaction)
