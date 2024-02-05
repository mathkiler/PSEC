from scripts.global_commandes.import_et_variable import *
from scripts.global_commandes.fonctions import *
from scripts.global_commandes.bouton import *


#--|--# Commande discord (admin = !nom_commande only)
#commande e base pour afficher les options de l'utilisateur. Renvoi vers la class Voir_Commandes()
#( posibilité d'écrire !c ou !commandes)
@bot.command(name="commandes", aliases=['c'], help="permet d'afficher les commandes possible sous forme de boutons")
async def commandes(ctx) :
    test_cration_bdd_user(ctx.message.author.id)
    test_changement_de_jour()
    await ctx.reply("Commandes possibles", view=Voir_Commandes())


@bot.command(name="proba", help="permet d'afficher le tableau des probabilités utilisé pour le drop des cartes.")
async def proba(ctx) :
    test_cration_bdd_user(ctx.message.author.id)
    test_changement_de_jour()
    await ctx.reply("Tableau des probabilités utilisées pour le drop des cartes.", file=discord.File(CURRENT_PATH+"/assets/proba/proba_drop.png"))





#--|--# Commandes admin only

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
        baseDeDonnees = sqlite3.connect(CURRENT_PATH+f'/assets/database/{db_used}')
        curseur = baseDeDonnees.cursor()
        curseur.execute(f"""UPDATE Joueur 
                    SET fragment = fragment + 1, fragment_cumule = 0, xp = xp + 1""")
        baseDeDonnees.commit()
        baseDeDonnees.close()
