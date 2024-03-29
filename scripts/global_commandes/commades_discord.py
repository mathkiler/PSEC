from scripts.global_commandes.import_et_variable import *
from scripts.global_commandes.fonctions import *
from scripts.global_commandes.bouton import *


#--|--# Commande discord (admin = !nom_commande only)
#commande e base pour afficher les options de l'utilisateur. Renvoi vers la class Voir_Commandes()
#( posibilité d'écrire !c ou !commandes)
@bot.command(name="commandes", description="Affiche les commandes possibles.")
async def commandes(interaction: discord.Interaction) :
    test_cration_bdd_user(interaction.user.id)
    test_changement_de_jour()
    await interaction.response.send_message("Commandes possibles", view=Voir_Commandes(), ephemeral=True)


@bot.command(name="proba", description="Affiche le tableau des probabilités de drop des cartes.")
async def proba(interaction: discord.Interaction) :
    test_cration_bdd_user(interaction.user.id)
    test_changement_de_jour()
    await interaction.response.send_message("Tableau des probabilités utilisées pour le drop des cartes.", file=discord.File(CURRENT_PATH+"/assets/proba/proba_drop.png"), ephemeral=True)





#--|--# Commandes admin only

#commande pour ajouter une carte (une par une)
@bot.command(name="ajout_carte", description="Admin only : permet de rajouter des cartes.")
async def ajout_carte(
    interaction: discord.Interaction,
    nom: discord.Option(str), # type: ignore
    rarete: discord.Option(str, choices=['commun', 'peu courant', 'rare', 'épique', 'héroïque']) # type: ignore
    ) :
    if admin_restrict(interaction.user.id) :
        carte_in_folder = False
        for (repertoire, sousRepertoires, fichiers) in os.walk(CURRENT_PATH+"/assets/cartes"):
            for file in fichiers :
                if file == nom+".png" :
                    carte_in_folder = True
                    break
            break
        if carte_in_folder :
            resultat = ajouter_une_carte(nom, rarete)
            if resultat == None :
                await interaction.response.send_message("Carte bien ajoutée.", ephemeral=True)
            else :
                await interaction.response.send_message(f"Une erreur est survenue : ```{resultat}```", ephemeral=True)
        else :
            await interaction.response.send_message(f"L'image au nom de `{nom}` ne figure pas dans le dossier des images des cartes. Veuillez ajouter l'image avant d'ajouter la carte dans la bdd", ephemeral=True)


#commande pour forcer les effets pour passer d'un jour à un autre
@bot.command(name="force_change_jour", description="Admin only : force les effets pour passer d'un jour à un autre.")
async def force_change_jour(interaction: discord.Interaction) :
    if admin_restrict(interaction.user.id) :
        baseDeDonnees = sqlite3.connect(db_path)
        curseur = baseDeDonnees.cursor()
        curseur.execute(f"""UPDATE Joueur 
                    SET fragment = fragment + 1, fragment_cumule = 0, xp = xp + 1, daily_quest_done = 0""")
        baseDeDonnees.commit()
        baseDeDonnees.close()
        await interaction.response.send_message("Bdd mise à jour.", ephemeral=True)



#commande qui montre les artistes
@bot.command(name="artistes", description="Affiche les artistes qui ont participé pour les cartes.")
async def artistes(interaction : discord.Interaction) :
    with open(CURRENT_PATH+"/assets/artistes/artistes.txt") as f :
        txt_artistes = f.readlines()
    txt_to_print_discord = ""
    for artiste in txt_artistes :
        artiste = artiste.split("|")
        if len(artiste[1]) == 0 :
            txt_to_print_discord+=f"**{artiste[0]}**"
        else :
            nb_tiret = "".join(["-" for k in range(17-len(artiste[0]))])
            txt_to_print_discord+=f"**{artiste[0]}** {nb_tiret}> [{artiste[2]}]({artiste[1]})\n"
    embed = discord.Embed(title="Artistes : ", description=txt_to_print_discord)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.command(name="affiche_bdd", description="Admin only : affiche l'état actuel de la bdd en format txt.")
async def affiche_bdd(interaction : discord.Interaction) :
    if admin_restrict(interaction.user.id) :
        txt_all_tables = calc_txt_bdd()
        name_file = str(randint(100000, 999999))
        with open(CURRENT_PATH+f"/assets/img_tamp/{name_file}.txt", "w") as f :
            f.write(txt_all_tables)
        await interaction.response.send_message("voici les tables : ", file=discord.File(CURRENT_PATH+f"/assets/img_tamp/{name_file}.txt"), ephemeral=True)
        os.remove(CURRENT_PATH+f"/assets/img_tamp/{name_file}.txt")

@bot.command(name="reroll", description="Échanger tout son XP contre des fragments (2 pour 1). Disponible qu'à partir du niveau 5")
async def reroll(interaction : discord.Interaction) :
    test_cration_bdd_user(interaction.user.id)
    test_changement_de_jour()
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"SELECT xp FROM Joueur WHERE id_discord_player == {interaction.user.id}")
    xp_user = curseur.fetchone()[0]
    _, lvl_column, lvl = get_data_lvl_from_csv(xp_user)
    if lvl_column.index(lvl) >= 5 :
        await interaction.response.send_message(
            f"Vous êtes sur le point d'échanger **{xp_user}** exp contre **{xp_user//2}** fragments. **Vous reviendrez donc au niveau 1**\nConfirmer l'action ?",
             view=Reroll(),
             ephemeral=True
             )
    else :
        await interaction.response.send_message(
f"""Vous devez être minimum **niveau 5** pour reroll.
Vous êtes actuellement **niveau {lvl_column.index(lvl)}**.
/proba pour voir l'xp nécessaire pour monter de niveau""",
        ephemeral=True
        )
    


@bot.command(name="backup_bdd", description="Admin only : Créer une backup de la bdd dans ./assets/database/backup/database_backup_xx_xx_xxxx.db")
async def affiche_bdd(interaction : discord.Interaction) :
    if admin_restrict(interaction.user.id) :
        dt_string = datetime.now().strftime("%d-%m-%Y_%Hh-%Mm-%Ss")
        shutil.copyfile(CURRENT_PATH+"/assets/database/database.db", CURRENT_PATH+f"/assets/database/backup_database/database_backup_{dt_string}.db")
        await interaction.response.send_message("Backup créée.", ephemeral=True)



@bot.command(name="help", description="Affiche le fonctionnement du jeu et de ses commandes.")
async def help(interaction: discord.Interaction) :
    test_cration_bdd_user(interaction.user.id)
    test_changement_de_jour()
    embed = discord.Embed(description="""
Le but est d'obtenir toutes les cartes. Pour ce faire il existe 2 possibilités : 
• Faire des cartes openning
• Obtenir une carte en récompense lors d'une daily quest

Pour faire des cartes openning, vous aurez besoin de fragments obtenable de différentes manières :
• être actif sur le serveur, notamment en écrivant un message (1 msg = 1 fragment avec 50 fragments max par jour pour éviter le spam)
• Obtenir des fragments en récompense lors d'une daily quest
• Chaque jour, vous obtenez 1 fragment gratuit, même si vous êtes afk
Chaque carte openning coûte 5 fragments.
                          
Chaque joueur possède un niveau (0-10). Plus votre lvl est haut, plus vous avez de chance d'obtenir des cartes plus rares (/proba pour voir les probabilités).
Vous pouvez gagner de l'exp pour augmenter de niveau de la même manière que pour les fragments (exp nécessaire pour lvl up visible dans /proba).
Si vous obtenez des doublons, vous pouvez les revendre contre de l'exp dans la rubrique **mes cartes** (commun = 2 exp, peu courant = 4 exp, rare = 6 exp ...)
Vous pouvez aussi faire un /reroll pour échanger toutes votre exp contre des fragments (2 exp = 1 fragment).

Une daily quest par jour sous forme de mini-jeu sera faisable pour obtenir une récompense dans la rubrique **daily quest** dans la commande /commandes
                          
Pour effectuer les commandes, il vous suffit d'écrire un /nom_de_la_commande et discord vous proposera les slash commande en ce nom **de pomme-bot**
Attention, les messages visibles que par vous ne seront affichés sur discord que 15 minutes (c'est discord qui veut ça).

Les commandes disponibles sont :
• /commandes → Menu principal sous forme de bouton
• /proba → affiche les probabilités utilisées lors des cartes oppening
• /artistes → affiche tous les artistes qui ont réalisé les fanarts et un lien vers leur réseau.
• /reroll → Permet d'échanger tout son exp contre des fragments (2 exp pour 1 fragment)
• /help → Affiche cette commande""") 
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.command(name="classement", description="Affiche les classements selon plusieurs catégories.")
async def classement(interaction: discord.Interaction) :
    test_cration_bdd_user(interaction.user.id)
    test_changement_de_jour()
    await interaction.response.defer(ephemeral=True)
    img_name = await calc_classement(interaction, "Collectionneur")
    embed = discord.Embed(title=f"Classement")
    embed.set_image(url=f"attachment://{img_name}.png")
    #enfin on répond à l'utilisateur par l'image, bouton...
    await interaction.followup.send(embed = embed, view=Mon_classement(), file=discord.File(CURRENT_PATH+f"/assets/img_tamp/{img_name}.png"))
    os.remove(CURRENT_PATH+f"/assets/img_tamp/{img_name}.png")

@bot.command(name="album", description="Permet d'afficher son album directement")
async def album(
    interaction: discord.Interaction,
    afficher_en_public: discord.Option(str, choices=['Non', 'Oui'], description="Afficher son album à tous pour flex un MAX",)
    ) :
    if afficher_en_public == "Non" : 
        reponse = True
    else :
        reponse = False
    test_changement_de_jour()
    await mon_album(interaction, reponse)


@bot.command(name="stats", description="Permet d'afficher ses stats directement")
async def stats(
    interaction: discord.Interaction,
    afficher_en_public: discord.Option(str, choices=['Non', 'Oui'], description="Afficher ses stats à tous pour flex un MAX",)
    ) :
    if afficher_en_public == "Non" : 
        reponse = True
    else :
        reponse = False
    test_changement_de_jour()
    await voir_stats(interaction, reponse)




@bot.command(name="echange_demarre", description="Démarrer un échange de cartes avec quelqu'un.")
async def echange_demarre(
    interaction: discord.Interaction,
    pseudo: discord.Option(discord.User, description="Pseudo de la personne avec qui faire l'échange") # type: ignore
    ) :
    if pseudo == interaction.user :
        await interaction.response.send_message("Vous ne pouvez pas échanger de carte avec vous-même. ||nan mais quelle idée en même temps...||", ephemeral=True)
        return
    if test_player_in_bdd(pseudo.id) == False :
        await interaction.response.send_message("Le joueur sélectionné n'est pas encore dans le jeu. Il doit au moins faire une commande pour créer son compte.", ephemeral=True)
        return
    plateau_created = creation_plateau_echange(interaction.user.id, pseudo.id)
    if plateau_created == False :
        await interaction.response.send_message(f"Vous avez déjà un échange en cours. Vous ne pouvez faire qu'un seul échange à la fois. **/echange_annule** pour annuler l'échange en cours", ephemeral=True)
        return
    await interaction.response.send_message(f"Demande d'échange envoyée à **{pseudo.global_name}**", ephemeral=True)
    await pseudo.send(f"**{interaction.user.global_name}** souhaite faire un échange avec vous, acceptez-vous ?", view = Accepter_echange())


@bot.command(name="echange_annule", description="Annuler un échange avec quelqu'un")
async def echange_annule(
    interaction: discord.Interaction
    ) :
    result_exist, ind_plateau, lines = plateau_echange_exist(interaction.user.id)
    if result_exist == False :
        await interaction.response.send_message(f"Vous n'avez pas d'échange en cours. **/echange_demarre** pseudo pour en créer un", ephemeral=True)
        return
    user_envoyeur, _ = await get_other_user_echange(interaction.user.id, lines, ind_plateau)
    annulation_echange(interaction.user.id)
    await interaction.response.send_message(f"L'échange avec **{user_envoyeur.global_name}** a bien été annulé", ephemeral=True)
    await user_envoyeur.send(f"**{interaction.user.global_name}** a annulé l'échange")


@bot.command(name="echange_ajout_carte", description="Ajouter une carte à échanger")
async def echange_ajout_carte(
    interaction: discord.Interaction,
    carte: discord.Option(str,description="Nom de la carte à échanger"), #type: ignore 
    quantite: discord.Option(int, description="Quantité de carte") # type: ignore
    ) :
    result_exist, ind_plateau, lines = plateau_echange_exist(interaction.user.id)
    if result_exist == False :
        await interaction.response.send_message(f"Vous n'avez pas d'échange en cours. **/echange_demarre** pseudo pour en créer un", ephemeral=True)
        return
    if quantite <= 0 :
        await interaction.response.send_message(f"Merci de ne pas échanger une quantité nulle ou négative de carte", ephemeral=True)
        return
    for carte_relatif in list(nom_carte_relatif.values()) :
        if carte.lower() in carte_relatif :
            await analyse_select_card_echange(interaction, carte_relatif[-1].lower(), quantite, ind_plateau, lines)
            return
    await interaction.response.send_message(f"La carte **{fomatage_carte_into_printable(carte)}** n'existe pas. Voici le nom de toutes les cartes :\n{' / '.join(get_all_cards(False))}", ephemeral=True)
        



@bot.command(name="echange_retire_carte", description="Retirer une carte à échanger qui est déjà dans l'échange")
async def echange_retire_carte(
    interaction: discord.Interaction,
    carte: discord.Option(str,description="Nom de la carte à échanger") #type: ignore 
    ) :
    result_exist, ind_plateau, lines = plateau_echange_exist(interaction.user.id)
    if result_exist == False :
        await interaction.response.send_message(f"Vous n'avez pas d'échange en cours. **/echange_demarre** pseudo pour en créer un", ephemeral=True)
        return
    for carte_relatif in list(nom_carte_relatif.values()) :
        if carte.lower() in carte_relatif :
            result_exist, lines = suppression_carte(interaction.user.id, ind_plateau, lines, carte_relatif[-1].lower())
            if result_exist == False :
                await interaction.response.send_message(f"La carte **{fomatage_carte_into_printable(carte)}** n'est pas présente dans l'échange", ephemeral=True)
                return
            else :
                user_envoyeur, _ = await get_other_user_echange(interaction.user.id, lines, ind_plateau)
                with open(CURRENT_PATH+f"/assets/plateau_echange/plateaux.txt", "w") as file_plateau:
                    file_plateau.write("".join(lines))
                await display_current_plateau(interaction, user_envoyeur, {"info" : "suppr", "carte" : fomatage_carte_into_printable(carte)}, ind_plateau, lines)
                return
    await interaction.response.send_message(f"La carte **{fomatage_carte_into_printable(carte)}** n'existe pas. Voici le nom de toutes les cartes :\n{' / '.join(get_all_cards(False))}", ephemeral=True)


@bot.command(name="echange_en_cours", description="Affiche l'échange en cours si vous en avez un")
async def echange_en_cours(interaction: discord.Interaction) :
    result_exist, ind_plateau, lines = plateau_echange_exist(interaction.user.id)
    if result_exist == False :
        await interaction.response.send_message(f"Vous n'avez pas d'échange en cours. **/echange_demarre** pseudo pour en créer un", ephemeral=True)
        return
    user_envoyeur, _ = await get_other_user_echange(interaction.user.id, lines, ind_plateau)
    await display_current_plateau(interaction, user_envoyeur, {"info" : "affiche_current_plateau"}, ind_plateau, lines)


@bot.command(name="echange_help", description="Affiche comment fonctionne le systeme d'échange e cartes entre joueur")
async def echange_en_cours(interaction: discord.Interaction) :
    embed = discord.Embed(title="Aide system d'echange", description="""
Grâce à ce système, vous pourrez échanger n'importe laquelle de vos cartes contre n'importe quelle carte d'une personne.
Toutes les commandes de ce système commencent par un **/echange_**
Vous ne pouvez avoir **qu'un seul** échange en même temps.
Vous pouvez échanger le nombre de cartes différentes que vous souhaitez et leur quantité que vous souhaitez.
Attention, il n'y a aucune restriction quant à l'échange. Si vous acceptez d'échanger une pomme héroïque contre un avion commun, c'est votre unique choix.

**Commandes disponibles dans l'ordre d'utilisation : **

• /echange_demarre pseudo ⇒ permet de proposer de démarrer un échange avec quelqu'un (cette commande ne pourra être effectuée que sur le serveur).
• /echange_annule ⇒ permet d'annuler l'échange en cours.
• /echange_en_cours ⇒ permet d'afficher l'échange en cours
• /echange_ajout_carte carte quantité ⇒ permet d'ajouter une carte sur le plateau d'échange en spécifiant sa quantité
• /echange_retire_carte carte ⇒ permet de retirer une carte que vous avez préalablement placée sur le plateau avec la commande /echange_ajout_carte
                          
Pour effectuer l'échange, il vous suffit d'appuyer sur le bouton `Effectuer l'échange` lorsque vous voyez le plateau (/echange_en_cours par exemple) ce qui enverra une demande à l'autre joueur. S'il l'accepte, la transaction est immédiatement effectuée.""")
    await interaction.response.send_message(embed=embed, ephemeral=True)
