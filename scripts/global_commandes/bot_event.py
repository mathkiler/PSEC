from scripts.daily_quest.motus.fonctions_motus import user_test_mot_motus
from scripts.global_commandes.import_et_variable import *
from scripts.global_commandes.fonctions import *



#--|--# bot events
@bot.event
async def on_ready():
    print("\n----------------\nle bot est radis\n----------------\n")


#à chaque fois qu'un joueur écrit un message, on va incrémenter ses fragments et xp
@bot.event
async def on_message(message):
    test_changement_de_jour()
    if test_joueur_ecrit_commande(message.content) == False and test_player_in_bdd(message.author.id):
        if str(message.author.id) in motus_msg_player and " " not in message.content :
            try : #si on est en MP discord, on ne peux pas supprimer le message de l'utilisteur
                await message.delete()
            except :
                pass
            try : #si le timeout du premier message est dépassé
                await user_test_mot_motus(str(message.author.id), message.content.lower())
            except :
                try : #si l'utilisateur à bloqué ses DM...
                    await message.author.send("Un prolème est survenue, probablement que le time out du message est dépassé.\nRecomencez l'intecation depuis !commande pour recommencer.")
                except :
                    await message.channel.send("Un prolème est survenue, probablement que le time out du message est dépassé.\nRecomencez l'intecation depuis !commande pour recommencer.")
        else :
            id_user = message.author.id
            baseDeDonnees = sqlite3.connect(CURRENT_PATH+f'\\assets\\database\\{db_used}')
            curseur = baseDeDonnees.cursor()
            curseur.execute(f"SELECT * FROM Joueur WHERE id_discord_player == {id_user}")
            resultat = curseur.fetchone()
            player_stats = {"id_discord_player" : resultat[0], "fragment" : resultat[1], "fragment_cumule" : resultat[2], "xp" : resultat[3]}
            if player_stats["fragment_cumule"] < 50 : #si le joueur n'a pas ateint son nombre max de fragment obtenut par messge par jour, on lui ajoute un fragment
                player_stats["fragment"]+=1
                player_stats["fragment_cumule"]+=1
                player_stats["xp"]+=1
                curseur.execute(f"""UPDATE Joueur 
                                SET fragment = {player_stats['fragment']}, fragment_cumule = {player_stats['fragment_cumule']}, xp = {player_stats['xp']}
                                WHERE id_discord_player == {player_stats['id_discord_player']}""")
                baseDeDonnees.commit()
            baseDeDonnees.close()