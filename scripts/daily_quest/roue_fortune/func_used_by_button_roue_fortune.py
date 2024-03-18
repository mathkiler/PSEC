from scripts.global_commandes.import_et_variable import *
from scripts.daily_quest.roue_fortune.fonctions_roue_fortune import *


async def tourne_roue(interaction) :
    #pourcentage de chance de chaques récompense en %
    #xp gagné -> toujours 100
    gain = choice(["carte", "rien", "xp", "fragment_1", "fragment_5", "fragment_10"])
    if gain == "carte" :
        embed_wheel_finish, file_wheel_finish = effet_carte_roue_fortune(interaction.user.id)
    elif gain == "rien" :
        embed_wheel_finish, file_wheel_finish = effet_rien_roue_fortune()
    elif gain == "xp" :
        embed_wheel_finish, file_wheel_finish = effet_xp_roue_fortune(interaction.user.id)
    else :
        embed_wheel_finish, file_wheel_finish = effet_fragment_roue_fortune(interaction.user.id, get_nb_fragment(gain))

    baseDeDonnees = sqlite3.connect(CURRENT_PATH+f'/assets/database/{db_used}')
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"""UPDATE Joueur
                    SET daily_quest_done = 1
                    WHERE id_discord_player == {interaction.user.id}""")
    baseDeDonnees.commit()
    baseDeDonnees.close()

    #Enfin, on affiche le résultat au joueur sur discord 
    #en premeir le gif en fonction du gain gagné
    img_path = CURRENT_PATH+f"/assets/animations/daily_quest/roue_fortune/anim_gif/{gain}.gif"
    file = discord.File(img_path)
    embed = discord.Embed()
    embed.set_image(url=f"attachment://{gain}.gif")
    await interaction.response.send_message(embed=embed, file=file, ephemeral=True)
    await asyncio.sleep(9)
    await interaction.edit_original_response(embed=embed_wheel_finish, file=file_wheel_finish)