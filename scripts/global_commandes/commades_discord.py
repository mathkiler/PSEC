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
    await interaction.response.send_message("Tableau des probabilités utilisées pour le drop des cartes.", file=discord.File("./assets/proba/proba_drop.png"), ephemeral=True)





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
        baseDeDonnees = sqlite3.connect(f'./assets/database/{db_used}')
        curseur = baseDeDonnees.cursor()
        curseur.execute(f"""UPDATE Joueur 
                    SET fragment = fragment + 1, fragment_cumule = 0, xp = xp + 1, daily_quest_done = 0""")
        baseDeDonnees.commit()
        baseDeDonnees.close()
        await interaction.response.send_message("Bdd mise à jour.", ephemeral=True)



@bot.command(name="reroll", description="Échanger tout son XP contre des fragments (2 pour 1). Disponnible qu'à partir du niveau 5")
async def reroll(interaction : discord.Interaction) :
    test_cration_bdd_user(interaction.user.id)
    test_changement_de_jour()
    baseDeDonnees = sqlite3.connect(f'./assets/database/{db_used}')
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
Vous êtes actuelement **niveau {lvl_column.index(lvl)}**.
/proba pour voir l'xp nécessaire poru monter de niveau""",
        ephemeral=True
        )
    