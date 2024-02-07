from scripts.global_commandes.import_et_variable import *
from scripts.global_commandes.fonctions import *
from scripts.global_commandes.bouton import *


#--|--# Commande discord (admin = !nom_commande only)
#commande e base pour afficher les options de l'utilisateur. Renvoi vers la class Voir_Commandes()
#( posibilité d'écrire !c ou !commandes)
@bot.command(name="commandes", description="permet d'afficher les commandes possibles")
async def commandes(interaction: discord.Interaction) :
    test_cration_bdd_user(interaction.user.id)
    test_changement_de_jour()
    await interaction.response.send_message("Commandes possibles", view=Voir_Commandes(), ephemeral=True)


@bot.command(name="proba", description="Afficher le tableau des probabilités utilisés pour le drop des cartes.")
async def proba(interaction: discord.Interaction) :
    test_cration_bdd_user(interaction.user.id)
    test_changement_de_jour()
    await interaction.response.send_message("Tableau des probabilités utilisées pour le drop des cartes.", file=discord.File(CURRENT_PATH+"/assets/proba/proba_drop.png"))





#--|--# Commandes admin only

#commande pour ajouter une carte (une par une)
@bot.command(name="ajout_carte", description="admin only : permet de rajouter des cartes. !ajout_carte nom rarete")
async def ajout_carte(
    interaction: discord.Interaction,
    nom: discord.Option(str),
    rarete: discord.Option(str, choices=['commun', 'peu courant', 'rare', 'épique', 'héroïque'])
    ) :
    if admin_restrict(interaction.user.id) :
        resultat = ajouter_une_carte(nom, rarete)
        if resultat == None :
            await interaction.response.send_message("Carte bien ajouté", ephemeral=True)
        else :
            await interaction.response.send_message(f"Une erreur est survenue : ```{resultat}```", ephemeral=True)



#commande pour forcer les effets pour passer d'un jour à un autre
@bot.command(name="force_change_jour", description="admin only : force les effets pour passer d'un jour à un autre")
async def force_change_jour(interaction: discord.Interaction) :
    if admin_restrict(interaction.user.id) :
        baseDeDonnees = sqlite3.connect(CURRENT_PATH+f'\\assets\\database\\{db_used}')
        curseur = baseDeDonnees.cursor()
        curseur.execute(f"""UPDATE Joueur 
                    SET fragment = fragment + 1, fragment_cumule = 0, xp = xp + 1, daily_quest_done = 0""")
        baseDeDonnees.commit()
        baseDeDonnees.close()
        await interaction.response.send_message("Bdd mise à jour.", ephemeral=True)



#commande qui montre les artistes
@bot.command(name="artistes", description="Affiche les artistes qui on participés pour les cartes")
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