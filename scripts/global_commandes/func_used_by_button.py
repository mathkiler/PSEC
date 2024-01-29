from scripts.global_commandes.import_et_variable import *
from scripts.global_commandes.fonctions import *



#--|--# toutes commandes seront accéssible via des boutons (créé dans les classes plus bas). Les fonctions suivantes sont les interactions avecles boutons
async def voir_stats(interaction, le_cacher) :
    id_user = interaction.user.id
    test_cration_bdd_user(id_user)
    baseDeDonnees = sqlite3.connect(f'./assets/database/{db_used}')
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
    
    #on range les carte possédé dans leur carégorie pour en même temps compter les doublons de chaques cartes
    carte_arange = {"commun" : {}, "peu courant" : {}, "rare" : {}, "épique" : {}, "héroïque" : {}}
    for carte in resultat_carte_possede :
        carte_arange[carte[1]][carte[0]] = carte[2]

    txt_print_cartes = ""
    for rarete in carte_arange :
        if len(carte_arange[rarete]) != 0 :
            txt_print_cartes+=rarete+" : \n"
            for carte in carte_arange[rarete] :
                txt_print_cartes+="     "+str(carte_arange[rarete][carte])+" posssédé : "+carte+"\n"
            txt_print_cartes+="\n\n"
    
    await interaction.response.send_message(f"""Stats du joueur <@{id_user}> : 
                
Nombre de fragment actuel : {resultat_user_stats[1]}
Nombre de fragment du jour : {resultat_user_stats[2]}/50
Exp : {resultat_user_stats[3]}
Nombre de carte obtenu (en comptant les doublons) : {nb_cartes_avec_doublon}
Nombre de carte obtenu (sans compter les doublons) : {nb_cartes_sans_doublon}

Cartes obtenu : 
```{txt_print_cartes}```""", ephemeral=le_cacher)


#fonction pour ouvrir un caisse
async def opening(interaction) :
    #on chope les info du joueur
    id_user = interaction.user.id
    test_cration_bdd_user(id_user)
    baseDeDonnees = sqlite3.connect(f'./assets/database/{db_used}')
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"SELECT * FROM Joueur WHERE id_discord_player == {id_user}")
    resultat_user_stats = curseur.fetchone()

    if resultat_user_stats[1] < 5 :
            await interaction.response.send_message(f"Fond insuffisant. Il vous manque {5-resultat_user_stats[1]} fragments", ephemeral=True)
    else :
        #on lit le taux de drop en fonction du niveau du joueur
        with open('./assets/proba/Probabilité drop par niveau.csv', newline='') as csvfile:
            data = list(csv.reader(csvfile, delimiter=","))[1:-1]
        lvl_column = [int(j.pop(-2)) for j in data]
        for lvl in lvl_column :
            if lvl >= resultat_user_stats[3] :
                break
        #operations qui permet d'avoir la liste des proba selon le niveau du joueur
        proba_box = [float((piece_of_data)[:-1].replace(",", ".")) for piece_of_data in data[lvl_column.index(lvl)][1:-1]]
        #partie qui va piocher la carte en fonction des proba du niveau du joueur
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
        curseur.execute(f"""UPDATE Joueur 
                    SET fragment = {resultat_user_stats[1]-5}
                    WHERE id_discord_player == {id_user}""")
        curseur.execute(f"""UPDATE carte_possede 
                    SET nombre_carte_possede = nombre_carte_possede + 1
                    WHERE id_discord_player == {id_user} AND id == {carte_tiree[0]}""")
        baseDeDonnees.commit()
        baseDeDonnees.close()
        #Enfin, on affiche le résultat au joueur sur discord
        img_path = f"./assets/animations/open-box.gif"
        file = discord.File(img_path)
        embed = discord.Embed()
        embed.set_image(url=f"attachment://open-box.gif")
        msg = await interaction.response.send_message(f"<@{id_user}>",embed=embed, file=file)
        await asyncio.sleep(5)
        # await msg.delete() ne fonctionne pas PROBLEME = Le gif du case oppening ne s'éfface pas
        img_path = f'./assets/cartes/{carte_tiree[1]}.png'
        file = discord.File(img_path)
        embed = discord.Embed(title = f"Vous avez tiré une carte {carte_tiree[2]} !")
        embed.set_image(url=f"attachment://{formatage_nom_carte(carte_tiree[1])}.png")
        await msg.edit(embed=embed, file=file)
        

#fonction pour créer l'album puis l'envoyer (à tout le monde ou non)
async def mon_album(interaction, le_montrer) :
    #première partie, on récupère le nom de toutes le cartes que le joueur possède
    id_user = interaction.user.id
    test_cration_bdd_user(id_user)
    baseDeDonnees = sqlite3.connect(f'./assets/database/{db_used}')
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"SELECT nom FROM cartes as c, joueur as j, carte_possede as cp WHERE c.id == cp.id and cp.id_discord_player == j.id_discord_player and j.id_discord_player == {id_user} AND nombre_carte_possede != 0")
    resultat_carte_possede = curseur.fetchall()
    baseDeDonnees.close()
    resultat_carte_possede = [resultat_carte_possede[k][0] for k in range(len(resultat_carte_possede))]
        #on calcule la position des images (on démare à -1 car on va compter la carte unknown (carte qui montre celles non obtenue))
    nombre_totale_carte = -1
    ordre_cartes = []
    for (repertoire, sousRepertoires, fichiers) in os.walk("./assets/cartes"):
        for f in fichiers :
            ordre_cartes.append(f[:-4])
            nombre_totale_carte+=1
    ordre_cartes.pop(0) # pour enlever la carte unknown
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
    for carte in ordre_cartes :
        if carte in resultat_carte_possede :
            im_carte = Image.open(f"./assets/cartes/{carte}.png")
        else :
            im_carte = Image.open(f"./assets/cartes/.inconnue.png")
        album.paste(im_carte, ((count%nb_carte_square)*width_carte,  (count//nb_carte_square)*height_carte))
        count+=1
    name_album = randint(10000, 99999)
    album.save(f"./assets/album tamp/{name_album}.png")
    await interaction.response.send_message(f"Album de <@{id_user}> :", file=discord.File(f'./assets/album tamp/{name_album}.png'), ephemeral=le_montrer)
    os.remove(f"./assets/album tamp/{name_album}.png")


#fonction pour affihcer ses cartes une par une
async def initialisation_mes_cartes(interaction) :
    #on chope les info du joueur (id, nombre de cartes, quel carte il a...)
    id_user = interaction.user.id
    test_cration_bdd_user(id_user)
    baseDeDonnees = sqlite3.connect(f'./assets/database/{db_used}')
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"SELECT curseur_carte FROM Joueur WHERE id_discord_player == {id_user}")
    index_curseur = curseur.fetchone()[0]
    curseur.execute(f"SELECT nom, rarete, nombre_carte_possede FROM cartes as c, joueur as j, carte_possede as cp WHERE c.id == cp.id and cp.id_discord_player == j.id_discord_player and j.id_discord_player == {id_user} AND nombre_carte_possede != 0")
    resultat_carte_possede = curseur.fetchall()
    nb_cartes = len(resultat_carte_possede)
    baseDeDonnees.close()

    return resultat_carte_possede, index_curseur, nb_cartes
    

async def selecteur_button_mes_cartes(interaction : discord.Interaction, button) :
    #si le bouton est appuyé, on update la variable du curseur puis on affiche la nouvelle image
    #on chope les info du joueur (id, nombre de cartes, quel carte il a...)
    id_user = interaction.user.id
    baseDeDonnees = sqlite3.connect(f'./assets/database/{db_used}')
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
    img_path = f"./assets/cartes/{resultat_carte_possede[index_curseur][0]}.png"
    new_file = discord.File(img_path)
    new_embed = discord.Embed(title=f"{index_curseur+1}/{nb_cartes}\nPossédée(s) : {resultat_carte_possede[index_curseur][2]}\nExp par doublon vendu ({resultat_carte_possede[index_curseur][1]}) : {(nom_rarete.index(resultat_carte_possede[index_curseur][1])+1)*2}")
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
    baseDeDonnees = sqlite3.connect(f'./assets/database/{db_used}')
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
        await interaction.followup.send(f"Vous avez obtenue **{gain_xp}** exp en vendant vos doublons", ephemeral=True)
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