from scripts.global_commandes.fonctions import formatage_nom_carte, get_data_lvl_from_csv, pluriel
from scripts.global_commandes.import_et_variable import *



#effet si on appui sur un bouton 
async def gagne_motus(interaction) :
    gain = choice(["carte", "xp", "fragment_5", "fragment_10"])
    if gain == "carte" :
        embed_gain_result, file_gain_result = effet_carte_motus(interaction.user.id)
    elif gain == "xp" :
        embed_gain_result, file_gain_result = effet_xp_motus(interaction.user.id)
    else :
        embed_gain_result, file_gain_result = effet_fragment_motus(interaction.user.id, get_nb_fragment(gain))

    baseDeDonnees = sqlite3.connect(CURRENT_PATH+f'/assets/database/{db_used}')
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"""UPDATE Joueur
                    SET daily_quest_done = 1
                    WHERE id_discord_player == {interaction.user.id}""")
    baseDeDonnees.commit()
    baseDeDonnees.close()

    #Enfin, on affiche le résultat au joueur sur discord 
    #en premeir le gif en fonction du gain gagné
    if file_gain_result == None :
        await interaction.followup.send(embed=embed_gain_result, ephemeral=True)
    else : 
        await interaction.followup.send(embed=embed_gain_result, file=file_gain_result, ephemeral=True)



#renvoi l'embed et effectu l'effet lorsque le gain est carte
def effet_carte_motus(id_user) :
    #on get l'xp que le joueur possède
    baseDeDonnees = sqlite3.connect(CURRENT_PATH+f'/assets/database/{db_used}')
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"SELECT xp FROM Joueur WHERE id_discord_player == {id_user}")
    resultat_user_stats = curseur.fetchone()[0]
    #on lit le taux de drop en fonction du niveau du joueur
    data, lvl_column, lvl = get_data_lvl_from_csv(resultat_user_stats)
    #operations qui permet d'avoir la liste des proba selon le niveau du joueur
    proba_box = [float((piece_of_data)[:-1].replace(",", ".")) for piece_of_data in data[lvl_column.index(lvl)][1:-1]]
    #pioche d'une carte
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
    curseur.execute(f"""UPDATE carte_possede 
                SET nombre_carte_possede = nombre_carte_possede + 1
                WHERE id_discord_player == {id_user} AND id == {carte_tiree[0]}""")
    baseDeDonnees.commit()
    baseDeDonnees.close()
    #Enfin, on affiche le résultat au joueur sur discord
    img_path = CURRENT_PATH+f'/assets/cartes/{carte_tiree[1]}.png'
    file = discord.File(img_path)
    embed = discord.Embed(title = f"""Bravo vous avez trouvé le bon mot ! 

Vous avez obtenu une nouvelle carte {carte_tiree[2]} !""")
    embed.set_image(url=f"attachment://{formatage_nom_carte(carte_tiree[1])}.png")
    return embed, file


#renvoi l'embed et effectu l'effet lorsque le gain est xp
def effet_xp_motus(id_user) :
    baseDeDonnees = sqlite3.connect(CURRENT_PATH+f'/assets/database/{db_used}')
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"""UPDATE Joueur 
                SET xp = xp + 100
                WHERE id_discord_player == {id_user}""")
    baseDeDonnees.commit()
    baseDeDonnees.close()
    
    embed = discord.Embed(title="""Bravo vous avez trouvé le bon mot ! 

Vous avez obtenu un gain de + 100 exp !""")
    return embed, None

#renvoi l'embed et effectu l'effet lorsque le gain est fragment
def effet_fragment_motus(id_user, nb_fragment) :
    baseDeDonnees = sqlite3.connect(CURRENT_PATH+f'/assets/database/{db_used}')
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"""UPDATE Joueur 
                SET fragment = fragment + {nb_fragment}
                WHERE id_discord_player == {id_user}""")
    baseDeDonnees.commit()
    baseDeDonnees.close()    
    embed = discord.Embed(title=f"""Bravo vous avez trouvé le bon mot !  

Vous avez obtenu un gain de + {nb_fragment} fragment{pluriel(nb_fragment)} !""")
    return embed, None


def get_nb_fragment(txt_fragment) :
    if "10" in txt_fragment :
        return txt_fragment[-2:]
    else :
        return txt_fragment[-1:]