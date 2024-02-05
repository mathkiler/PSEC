from scripts.global_commandes.import_et_variable import *
from scripts.daily_quest.puissance_4.fonctions_puissance_4 import *


async def place_pion(interaction, ind_colone_pion) :
    
    ind_line_pion = get_line_by_column(interaction.user.id, ind_colone_pion)
    if type(ind_line_pion) == int :
        #on reset le dernier piont posé par l'ia. On met un try car au premoier coup, il n'y a pas d'e premier piont palcé par l'ia
        try :
            reset_last_ia_posed(interaction.user.id)
        except :
            pass
        replace_somthing(interaction.user.id, "r", (ind_line_pion, ind_colone_pion))
        list_plateau = get_etat_puissance_4(interaction.user.id)
        result_test_fin_jeu = fin_du_jeu(list_plateau)
        if result_test_fin_jeu[0] == "eguale" :
            await c_gagne(interaction, result_test_fin_jeu[0],  result_test_fin_jeu)
        elif result_test_fin_jeu[0] == "win" :
            await c_gagne(interaction, result_test_fin_jeu[0],  result_test_fin_jeu)
        else : #patie IA
            ia = IA_p4(interaction.user.id, interaction)
            colonne = ia.p4_IA_find_best_move()
            ind_line_pion = get_line_by_column(interaction.user.id, colonne)
            replace_somthing(interaction.user.id, "j_last_posed", (ind_line_pion, colonne))
            list_plateau = get_etat_puissance_4(interaction.user.id)
            result_test_fin_jeu = fin_du_jeu(list_plateau)
            print(result_test_fin_jeu)
            if result_test_fin_jeu[0] == "eguale" :
                await c_gagne(interaction, result_test_fin_jeu[0],  result_test_fin_jeu)
            elif result_test_fin_jeu[0] == "win" :
                baseDeDonnees = sqlite3.connect(f'./assets/database/{db_used}')
                curseur = baseDeDonnees.cursor()
                curseur.execute(f"""UPDATE Joueur
                                SET daily_quest_done = 1
                                WHERE id_discord_player == {interaction.user.id}""")
                baseDeDonnees.commit()
                baseDeDonnees.close()
                name_img = create_img_p4(interaction.user.id, result_test_fin_jeu)
                await affiche_image_discord(interaction, name_img)
                os.remove(f"./assets/img tamp/{name_img}.png")
                await interaction.followup.send("C'est perdu ! Pomme-bot a été bien trop forte pour cette fois ||gros nul||", ephemeral=True)

            else :            
                name_img = create_img_p4(interaction.user.id, ["rien", None, None])
                await affiche_image_discord(interaction, name_img)
                os.remove(f"./assets/img tamp/{name_img}.png")

    else :
        name_img = create_img_p4(interaction.user.id, ["rien", None, None])
        await affiche_image_discord(interaction, name_img)
        os.remove(f"./assets/img tamp/{name_img}.png")
        msg = await interaction.followup.send("La colonne est déjà complête", ephemeral = True)
        await asyncio.sleep(5)
        await msg.delete()
    



#si le joueur gagne, on bloc tout (il a fini sa daily quest) et on lui donne une récompence
async def c_gagne(interaction, win_or_eguale, result_win) :
    #on actualise le plateau pour voi comment ça c'est fini
    name_img = create_img_p4(interaction.user.id, result_win)
    await affiche_image_discord(interaction, name_img)
    os.remove(f"./assets/img tamp/{name_img}.png")
    baseDeDonnees = sqlite3.connect(f'./assets/database/{db_used}')
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"""UPDATE Joueur
                    SET daily_quest_done = 1
                    WHERE id_discord_player == {interaction.user.id}""")
    baseDeDonnees.commit()
    baseDeDonnees.close()
    #choix du gain
    #xp gagné -> toujours 100
    if win_or_eguale == "win" :
        gain = choice(["carte", "xp", "fragment_5", "fragment_10"])
    else :
        gain = choice(["half-xp", "fragment_3"])
    if gain == "carte" :
        embed_gain_result, file_gain_result = effet_carte_puissance_4(interaction.user.id)
    elif "xp" in gain :
        embed_gain_result, file_gain_result = effet_xp_puissance_4(interaction.user.id, gain)
    else :
        embed_gain_result, file_gain_result = effet_fragment_puissance_4(interaction.user.id, get_nb_fragment(gain))
    #Enfin, on affiche le résultat au joueur sur discord 
    #en premeir le gif en fonction du gain gagné
    if file_gain_result == None :
        await interaction.followup.send(embed=embed_gain_result, ephemeral=True)
    else : 
        await interaction.followup.send(embed=embed_gain_result, file=file_gain_result, ephemeral=True)
