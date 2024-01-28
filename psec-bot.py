





###################################################################################
#                                                                                 #
#                                                                                 #
#                                                                                 #
#                           ██████╗ ███████╗███████╗ ██████╗                      #
#                           ██╔══██╗██╔════╝██╔════╝██╔════╝                      #
#                           ██████╔╝███████╗█████╗  ██║                           #
#                           ██╔═══╝ ╚════██║██╔══╝  ██║                           #
#                           ██║     ███████║███████╗╚██████╗                      #
#                           ╚═╝     ╚══════╝╚══════╝ ╚═════╝                      #
#                                                                                 #
#                                                                                 #                                                                                                                                      #
#                    by : Cucurathieu, Teoad, philzAlicia, CellBrioche            #
#                                                                                 #
#                                                                                 #
###################################################################################











from random import randint, random
from discord.ext import commands
from datetime import date
from math import sqrt
from PIL import Image
import asyncio
import discord
import sqlite3
import csv
import os




#--|--# get la clé (token) du bot discord
f = open("token_discord.token", "r")
token_discord = f.readline()
#--|--# param bot
intents = discord.Intents().all()
intents.members = True
bot = commands.Bot(command_prefix='!',intents=intents)



###########  USE BDD TEST  ##########
db_test = False
if db_test :
    db_used = "database_test.db"
else :
    db_used = "database.db"



#--|--# lists/variables
admin_id_user = [382877512302067712, 408755725796376579, 461802780277997579]
nom_rarete = ["commun", "peu courant", "rare", "épique", "héroïque"]
liste_comandes = ["!commandes", "!c", "!force_change_jour", "!ajout_carte"]
DATE_actuel = date.today()  #date du jour
cureurs = [] #liste des curseurs des joueurs lorsqu'ils affichent leur carte une par une


#--|--# fonctions
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
    

#fonction pour restrindre certaines commande uniquement au admins
def admin_restrict(ctx) :
    if ctx.message.author.id in admin_id_user :
        return True
    else :
        return False
    

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
        curseur.execute(f"SELECT id FROM Cartes ")
        result = curseur.fetchall()
        id_cartes = [result[k][0] for k in range(len(result))]
        #ensuite, on regarde tout les gens sur le serveur et si un joueur n'es pas dans la BDD, il y est ajouté avec ses stats à 0
        curseur.execute("INSERT INTO Joueur (id_discord_player, fragment, fragment_cumule, xp, curseur_carte) VALUES (?, ?, ?, ?, ?)", (id_user, 0, 0, 0, 0))
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


#--|--# bot events
@bot.event
async def on_ready():
    print("\n----------------\nle bot est radis\n----------------\n")


#à chaque fois qu'un joueur écrit un message, on va incrémenter ses fragments et xp
@bot.event
async def on_message(message):
    test_changement_de_jour()
    if test_joueur_ecrit_commande(message.content) == False and test_player_in_bdd(message.author.id):
        id_user = message.author.id
        baseDeDonnees = sqlite3.connect(f'./assets/database/{db_used}')
        curseur = baseDeDonnees.cursor()
        curseur.execute(f"SELECT * FROM Joueur WHERE id_discord_player == {id_user}")
        resultat = curseur.fetchone()
        player_stats = {"id_discord_player" : resultat[0], "fragment" : resultat[1], "fragment_cumule" : resultat[2], "xp" : resultat[3]}
        player_stats["xp"]+=1
        if player_stats["fragment_cumule"] < 50 : #si le joueur n'a pas ateint son nombre max de fragment obtenut par messge par jour, on lui ajoute un fragment
            player_stats["fragment"]+=1
            player_stats["fragment_cumule"]+=1
        curseur.execute(f"""UPDATE Joueur 
                        SET fragment = {player_stats['fragment']}, fragment_cumule = {player_stats['fragment_cumule']}, xp = {player_stats['xp']}
                        WHERE id_discord_player == {player_stats['id_discord_player']}""")
        baseDeDonnees.commit()
        baseDeDonnees.close()
    await bot.process_commands(message)


#--|--# Commande discord (admin = !nom_commande only)
#commande e base pour afficher les options de l'utilisateur. Renvoi vers la class Voir_Commandes()
#( posibilité d'écrire !c ou !commandes)
@bot.command(name="c", help="permet d'afficher les commandes possible sous forme de boutons")
async def c(ctx) :
    test_cration_bdd_user(ctx.message.author.id)
    test_changement_de_jour()
    await ctx.reply("Commandes possibles", view=Voir_Commandes())
@bot.command(name="commandes", help="permet d'afficher les commandes possible sous forme de boutons")
async def commandes(ctx) :
    test_cration_bdd_user(ctx.message.author.id)
    test_changement_de_jour()
    await ctx.reply("Commandes possibles", view=Voir_Commandes())



#commande pour ajouter une carte (une par une)
@bot.command(name="ajout_carte", help="admin only : permet de rajouter des cartes. !ajout_carte nom rarete")
async def ajout_carte(ctx) :
    if admin_restrict(ctx) :
        #traitement du message pour envoyer les bon paramètre à la fonction ajouter_une_carte (à cause des " " qui peuvent être mis dans les nom et rareté)
        mess = ctx.message.content.lower().split(" ")
        mess.pop(0)
        if mess[-1] == "courant" :
            rarete = mess[-2]+" "+mess[-1]
            mess.pop(-1)
            mess.pop(-1)
        else :
            rarete = mess[-1]
            mess.pop(-1)
        resultat = ajouter_une_carte(" ".join(mess), rarete)
        if resultat == None :
            await ctx.send("Carte bien ajouté")
        else :
            await ctx.send(f"Une erreur est survenue : ```{resultat}```")



#commande pour forcer les effets pour passer d'un jour à un autre
@bot.command(name="force_change_jour", help="admin only : force les effets pour passer d'un jour à un autre")
async def force_change_jour(ctx) :
    if admin_restrict(ctx) :
        baseDeDonnees = sqlite3.connect(f'./assets/database/{db_used}')
        curseur = baseDeDonnees.cursor()
        curseur.execute(f"""UPDATE Joueur 
                    SET fragment = fragment + 1, fragment_cumule = 0, xp = xp + 1""")
        baseDeDonnees.commit()
        baseDeDonnees.close()


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
    if carte_selected_info[2] > 1 :
        if combien_doublon == "UN" : 
            gain_xp = supprimer_UN_doublon(carte_selected_info)
            nb_carte_destroy = 1
        elif combien_doublon == "TOUS" :
            gain_xp = supprimer_TOUS_doublon(carte_selected_info)
            nb_carte_destroy = carte_selected_info[2]-1
        curseur.execute(f"""UPDATE Joueur 
            SET xp = xp + {gain_xp}
            WHERE id_discord_player == {id_user}""")
        curseur.execute(f"""UPDATE carte_possede 
            SET nombre_carte_possede = nombre_carte_possede - {nb_carte_destroy}
            WHERE id_discord_player == {id_user} AND id == {carte_selected_info[0]}""")
        baseDeDonnees.commit()
        baseDeDonnees.close()
        await selecteur_button_mes_cartes(interaction, "stay_here")
    else :
        await interaction.response.send_message(f"Il ne vous reste plus aucun doublon de {carte_selected_info[3]}.", ephemeral=True)

def supprimer_UN_doublon(carte_selected_info) :
    return (nom_rarete.index(carte_selected_info[1])+1)*2

def supprimer_TOUS_doublon(carte_selected_info) :
    return ((nom_rarete.index(carte_selected_info[1])+1)*2)*(carte_selected_info[2]-1)


#--|--# création des boutons d'interraction
#bouton des commandes possible des utilisateurs via la commande !commandes
class Voir_Commandes(discord.ui.View):
    @discord.ui.button(label="Voir ses stats", style=discord.ButtonStyle.primary)
    async def stats_private_button_callback(self, button, interaction):
        test_changement_de_jour()
        await voir_stats(interaction, True)

    @discord.ui.button(label="Montrer ses stats à tout le monde pour flex", style=discord.ButtonStyle.green)
    async def stats_public_button_callback(self, button, interaction):
        test_changement_de_jour()
        await voir_stats(interaction, False)
        
    @discord.ui.button(label="Opening d'une carte", row=1, style=discord.ButtonStyle.primary)
    async def opening_button_callback(self, button, interaction):
        test_changement_de_jour()
        await interaction.response.send_message("Démarer l'opening ?", view=Start_opening(), ephemeral=True)

    @discord.ui.button(label="Mes cartes", row=2, style=discord.ButtonStyle.primary)
    async def mes_cartes_button_callback(self, button, interaction):
        test_changement_de_jour()
        resultat_carte_possede, index_curseur, nb_cartes = await initialisation_mes_cartes(interaction)
        #si le joueur n'a pas de carte on le lui dis gentilment
        if nb_cartes <= 0 :
            await interaction.response.send_message("Vous n'avez pas de carte !", ephemeral=True)
        else :
            #on affiche l'image 
            img_path = f"./assets/cartes/{resultat_carte_possede[index_curseur][0]}.png"
            file = discord.File(img_path)
            embed = discord.Embed(title=f"{index_curseur+1}/{nb_cartes}\nPossédée(s) : {resultat_carte_possede[index_curseur][2]}\nExp par doublon vendu ({resultat_carte_possede[index_curseur][1]}) : {(nom_rarete.index(resultat_carte_possede[index_curseur][1])+1)*2}")
            embed.set_image(url=f"attachment://{formatage_nom_carte(resultat_carte_possede[index_curseur][0])}.png")
            #enfin on répond à l'utilisateur par l'image, bouton...
            await interaction.response.send_message(embed = embed, view=Mes_cartes(), file=file, ephemeral=True)


    @discord.ui.button(label="Mon album", row=3, style=discord.ButtonStyle.primary)
    async def album_private_button_callback(self, button, interaction):
        test_changement_de_jour()
        await mon_album(interaction, True)

    @discord.ui.button(label="Montrer mon album à tout le monde", row=3, style=discord.ButtonStyle.green)
    async def album_public_button_callback(self, button, interaction):
        test_changement_de_jour()
        await mon_album(interaction, False)


#bouton/message oui ou non pour la validation lors du choix d'ouvrir un case opening
class Start_opening(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    @discord.ui.button(label="Confirmer", style=discord.ButtonStyle.primary)
    async def oui_button_callback(self, button, interaction):
        test_changement_de_jour()
        await opening(interaction)

    @discord.ui.button(label="Annuler", style=discord.ButtonStyle.red)
    async def non_button_callback(self, button, interaction):
        test_changement_de_jour()
        await interaction.response.send_message("Action annulé", ephemeral=True)


#bouton/message pour afficher mes cartes
class Mes_cartes(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View

    @discord.ui.button(label="-5", style=discord.ButtonStyle.secondary)
    async def five_prev_button_callback(self, button, interaction):
        test_changement_de_jour()
        await selecteur_button_mes_cartes(interaction, "five_prev")

    @discord.ui.button(label="Prev", style=discord.ButtonStyle.secondary)
    async def left_button_callback(self, button, interaction):
        test_changement_de_jour()
        await selecteur_button_mes_cartes(interaction, "one_prev")

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def one_next_button_callback(self, button, interaction):
        test_changement_de_jour()
        await selecteur_button_mes_cartes(interaction, "one_next")

    @discord.ui.button(label="+5", style=discord.ButtonStyle.secondary)
    async def five_next_button_callback(self, button, interaction):
        test_changement_de_jour()
        await selecteur_button_mes_cartes(interaction, "five_next")

    @discord.ui.button(label="Recycler UN doublon", row=1, style=discord.ButtonStyle.red)
    async def supr_one_doublon_button_callback(self, button, interaction):
        test_changement_de_jour()
        await mes_cartes_supprime_doublon(interaction, "UN")

    @discord.ui.button(label="Recycler TOUT les doublons", row=1, style=discord.ButtonStyle.red)
    async def supr_all_doublon_button_callback(self, button, interaction):
        test_changement_de_jour()
        await mes_cartes_supprime_doublon(interaction, "TOUS")



if __name__ == "__main__" :
    bot.run(token_discord)