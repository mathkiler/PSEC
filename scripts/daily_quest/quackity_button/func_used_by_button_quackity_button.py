from scripts.global_commandes.import_et_variable import *
from scripts.daily_quest.quackity_button.fonctions_quackity_button import *


#effet si on appui sur un bouton 
async def response_choix_button_quackity(interaction, ind_button) :
    if test_daily_quest_completed(interaction.user.id) :
        await interaction.response.send_message("Vous avez déjà effectué votre quête du jour. Revenez demain pour une nouvelle quête.", ephemeral=True)
        return
    if check_current_daily_quest("bouton de quackity") == False:
        await interaction.response.send_message("Vous essayez de faire une daily quest fermée.")
        return
    nb_chance_left = get_number_chance_left(interaction.user.id)
    tirage = randint(0,24-(3-nb_chance_left))
    if tirage != 0 :
        if nb_chance_left == 1 :
            baseDeDonnees = sqlite3.connect(db_path)
            curseur = baseDeDonnees.cursor()
            curseur.execute(f"""UPDATE Joueur
                            SET daily_quest_done = 1
                            WHERE id_discord_player == {interaction.user.id}""")
            baseDeDonnees.commit()
            baseDeDonnees.close()
            new_embed = discord.Embed(title="0 chance restante")
            await interaction.response.edit_message(embed=new_embed)
            await interaction.followup.send("C'est perdu ! Vous ferez peut-être mieux la prochaine fois.", ephemeral= True)
        else :
            with open(CURRENT_PATH+f"/assets/daily_quest_save/{interaction.user.id}.txt", "w") as f :
                f.write(str(nb_chance_left-1))
            new_embed = discord.Embed(title=f"{nb_chance_left-1} chance{pluriel(nb_chance_left-1)} restante{pluriel(nb_chance_left-1)}")
            await interaction.response.edit_message(embed=new_embed)
            await interaction.followup.send(f"Loupé, il vous reste encore {nb_chance_left-1} chance{pluriel(nb_chance_left-1)}.", ephemeral=True)
    else :
        #choix du gain
        #xp gagné -> toujours 100
        gain = choice(["carte", "xp", "fragment_10", "fragment_15"])
        if gain == "carte" :
            embed_gain_result, file_gain_result = effet_carte_quackity_button(interaction.user.id)
        elif gain == "xp" :
            embed_gain_result, file_gain_result = effet_xp_quackity_button(interaction.user.id)
        else :
            embed_gain_result, file_gain_result = effet_fragment_quackity_button(interaction.user.id, gain[-2:])

        baseDeDonnees = sqlite3.connect(db_path)
        curseur = baseDeDonnees.cursor()
        curseur.execute(f"""UPDATE Joueur
                        SET daily_quest_done = 1
                        WHERE id_discord_player == {interaction.user.id}""")
        baseDeDonnees.commit()
        baseDeDonnees.close()

        #Enfin, on affiche le résultat au joueur sur discord 
        #en premeir le gif en fonction du gain gagné
        if file_gain_result == None :
            await interaction.response.send_message(embed=embed_gain_result, ephemeral=True)
        else : 
            await interaction.response.send_message(embed=embed_gain_result, file=file_gain_result, ephemeral=True)
