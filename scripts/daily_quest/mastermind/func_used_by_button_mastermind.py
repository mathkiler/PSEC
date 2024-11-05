from scripts.global_commandes.import_et_variable import *
from scripts.daily_quest.mastermind.fonctions_mastermind import *



async def update_choix_pion(interaction, ind_pion, couleur) :
    color_emoji_name = {
        "blanc" : ":white_circle:",
        "noir" : ":black_circle:",
        "rouge" : ":red_circle:",
        "bleu" : ":blue_circle:",
        "marron" : ":brown_circle:",
        "violet" : ":purple_circle:",
        "vert" : ":green_circle:",
        "jaune" : ":yellow_circle:",
        "orange" : ":orange_circle:"
    }
    with open(CURRENT_PATH+f"/assets/daily_quest_save/{interaction.user.id}.txt", "r") as f :
        txt = f.readlines()
        print(txt)
    last = txt[-1].split("|")
    last[ind_pion] = color_emoji_name[couleur]
    txt[-1] = "|".join(last)
    with open(CURRENT_PATH+f"/assets/daily_quest_save/{interaction.user.id}.txt", "w") as f :
        f.write("".join(txt))
    current_stat = calc_state_mastermind(interaction.user.id)
    embed = discord.Embed(description=current_stat)
    await interaction.response.edit_message(embed=embed)


async def action_master(interaction) :

    secret_comb = get_secret_combination(interaction.user.id)
    comb_test = get_current_combination(interaction.user.id)
    if "" in comb_test :
        print("c'est mal fait")
        return
    if verif_combinaison(comb_test, secret_comb)[0] == 4 :
        await c_gagne(interaction)
    else :
        with open(CURRENT_PATH+f"/assets/daily_quest_save/{interaction.user.id}.txt", "a") as f :
            f.write("\n|||")
    current_stat = calc_state_mastermind(interaction.user.id)
    embed = discord.Embed(description=current_stat)
    await interaction.response.edit_message(embed=embed)


#si le joueur gagne, on bloc tout (il a fini sa daily quest) et on lui donne une récompence
async def c_gagne(interaction) :
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"""UPDATE Joueur
                    SET daily_quest_done = 1
                    WHERE id_discord_player == {interaction.user.id}""")
    baseDeDonnees.commit()
    baseDeDonnees.close()

    #choix du gain
    #xp gagné -> toujours 100
    gain = choice(["carte", "xp", "fragment_10", "fragment_15"])
    if gain == "carte" :
        embed_gain_result, file_gain_result = effet_carte_mastermind(interaction.user.id)
    elif gain == "xp" :
        embed_gain_result, file_gain_result = effet_xp_mastermind(interaction.user.id)
    else :
        embed_gain_result, file_gain_result = effet_fragment_mastermind(interaction.user.id, gain[-2:])
    #Enfin, on affiche le résultat au joueur sur discord 
    #en premeir le gif en fonction du gain gagné
    if file_gain_result == None :
        await interaction.followup.send(embed=embed_gain_result)
    else : 
        await interaction.followup.send(embed=embed_gain_result, file=file_gain_result)