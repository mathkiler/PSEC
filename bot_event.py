from import_et_variable import *
from fonctions import *



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