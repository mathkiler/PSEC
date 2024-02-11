from scripts.daily_quest.demineur.fonctions_demineur import *
from scripts.global_commandes.import_et_variable import *



#class du jeu
class Demineur(discord.ui.View):
    @discord.ui.button(label="Déminer", style=discord.ButtonStyle.primary)
    async def deminer_callback(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        if test_daily_quest_completed(interaction.user.id) == False :
            if check_current_daily_quest("demineur") :
                await demine_case(interaction)
            else :
                await interaction.response.send_message("Vous essayez de faire une daily quest fermée.")
        else :
            await interaction.response.send_message("Vous avez déjà effectué votre quête du jour. Revenez demain pour une nouvelle quête.")



    @discord.ui.button(label="Drapeau", style=discord.ButtonStyle.primary)
    async def drapeau_callback(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        if test_daily_quest_completed(interaction.user.id) == False :
            if check_current_daily_quest("demineur") :
                await add_flag(interaction)
                await interaction.response.send_message("Vous essayez de faire une daily quest fermée.")
        else :
            await interaction.response.send_message("Vous avez déjà effectué votre quête du jour. Revenez demain pour une nouvelle quête.")





#ajout un drapeau (ou l'enlève s'il y en a un)
async def add_flag(interaction) :
    x_ind_arrow, y_ind_arrow, _, _ = get_info_demineur(interaction.user.id)
    case_to_compare = get_info_case(interaction.user.id, (x_ind_arrow, y_ind_arrow))
    if case_to_compare == "c" :
        replace_somthing_in_demineur(interaction.user.id, "d", (x_ind_arrow+1, y_ind_arrow))
    elif case_to_compare == "d" :
        replace_somthing_in_demineur(interaction.user.id, "c", (x_ind_arrow+1, y_ind_arrow))    
    #si il clic sur une case autre que d ou c, on réaffiche quand même le plateau pour ne pas avoir un "echec de l'interaction"
    discord_txt = convert_txt_to_discord_demineur(interaction.user.id)
    tentative_restante = get_tentative_restante(interaction.user.id)
    embed = discord.Embed(title=f"Nombre de bombes : {get_nb_bombes()}\nTentative{pluriel(int(tentative_restante))} restante{pluriel(int(tentative_restante))} : {tentative_restante}", description=discord_txt)
    await interaction.response.edit_message(embed=embed)




async def demine_case(interaction) :
    x_ind_arrow, y_ind_arrow, _, list_ind_bomb = get_info_demineur(interaction.user.id)
    case_to_compare = get_info_case(interaction.user.id, (x_ind_arrow, y_ind_arrow))
    ind_case = x_ind_arrow+get_taille_demineur()*y_ind_arrow
    taille_demineur = get_taille_demineur()
    if ind_case in list_ind_bomb and case_to_compare != "d": #si il clic sur une bombe (le nul)
        tentative_restante = int(get_tentative_restante(interaction.user.id))-1
        for bomb in list_ind_bomb :
            replace_somthing_in_demineur(interaction.user.id, "b", (bomb%taille_demineur+1, bomb//taille_demineur))
        if tentative_restante == 0 : #et c'est perdu complêtement
            baseDeDonnees = sqlite3.connect(CURRENT_PATH+f'\\assets\\database\\{db_used}')
            curseur = baseDeDonnees.cursor()
            curseur.execute(f"""UPDATE Joueur
                            SET daily_quest_done = 1
                            WHERE id_discord_player == {interaction.user.id}""")
            baseDeDonnees.commit()
            baseDeDonnees.close()
            
            discord_txt = convert_txt_to_discord_demineur(interaction.user.id)
            embed = discord.Embed(title=f"Nombre de bombes : {get_nb_bombes()}\nTentative restante : 0", description=discord_txt)
            await interaction.response.edit_message(embed=embed)
            await interaction.followup.send(f"Perdu ! Réfléchit mieux la prochaine fois :upside_down:")
        else : #il perd juste une chance sur x
            discord_txt = convert_txt_to_discord_demineur(interaction.user.id)
            embed = discord.Embed(title=f"Nombre de bombes : {get_nb_bombes()}\nTentative restante : {tentative_restante}", description=discord_txt)
            await interaction.response.edit_message(embed=embed)
            await interaction.original_response()
            await interaction.followup.send(f"**Perdu !** Encore **{tentative_restante}** tentative{pluriel(tentative_restante)}.")
            #recalcule d'un nouveau plateau démineur
            plateau_save = ["0\n", "1\n"]
            plateau_save.extend(["c\n" if k == get_taille_demineur()*get_taille_demineur()-1 else "c," for k in range(get_taille_demineur()*get_taille_demineur())])
            ind_list_bomb = []
            for k in range(get_nb_bombes()) : #nombre de bombes
                placement = randint(0,get_taille_demineur()*get_taille_demineur()-1)
                while placement in ind_list_bomb :
                    placement = randint(0,get_taille_demineur()*get_taille_demineur()-1)
                ind_list_bomb.append(f"{placement},")
            ind_list_bomb[-1] = ind_list_bomb[-1][:-1]+"\n"
            plateau_save.extend(ind_list_bomb)
            plateau_save.append(str(tentative_restante))
            plateau_save = "".join(plateau_save)
            #on réécrit le nouveau plateau ans la save
            with open(CURRENT_PATH+f"/assets/daily_quest_save/{interaction.user.id}.txt", "w") as f :
                f.write(plateau_save)
            discord_txt = convert_txt_to_discord_demineur(interaction.user.id)
            embed = discord.Embed(title=f"Nombre de bombes : {get_nb_bombes()}\nTentative{pluriel(tentative_restante)} restante{pluriel(tentative_restante)} : {tentative_restante}", description=discord_txt)
            #await message.edit(embed=embed)
            await interaction.followup.send(embed=embed, view=Demineur())
    elif case_to_compare == "c" : #il appui sur une case non minée
        nb_bombe = test_bomb_around(ind_case, list_ind_bomb)
        if nb_bombe != 0 : #une case avec un nombre
            replace_somthing_in_demineur(interaction.user.id, str(nb_bombe), (x_ind_arrow+1, y_ind_arrow))
            discord_txt = convert_txt_to_discord_demineur(interaction.user.id)
            tentative_restante = get_tentative_restante(interaction.user.id)
            embed = discord.Embed(title=f"Nombre de bombes : {get_nb_bombes()}\nTentative{pluriel(int(tentative_restante))} restante{pluriel(int(tentative_restante))} : {tentative_restante}", description=discord_txt)
            await interaction.response.edit_message(embed=embed)
        else : #une case vide qui implique d'enlever les autres cases vides autour en casquade (c'est un peux le bordel pour le faire mais avec de la recursivité ça passe)
            case_to_explore = [ind_case] #case qu'on dois explorer
            already_explore = [] #case déja exploré
            ind_case_to_reveal = [[ind_case, 0]] #case à rélévé à la fin de l'analyse
            _, _, ind_case_to_reveal_doublon, _ = demine_case_vide(case_to_explore, already_explore, ind_case_to_reveal, list_ind_bomb)
            #traitement bien chiant pour enlever les doublons car ces des listes de lites. bref ça enlève les doublons
            list_t = [ind_case_to_reveal_doublon[k][0] for k in range(len(ind_case_to_reveal_doublon))]
            list_test = []
            for k in range(len(list_t)) :
                if list_t[k] not in list_test :
                    list_test.append(list_t[k])
            ind_case_to_reveal = []
            for k in range(len(ind_case_to_reveal_doublon)) :
                if ind_case_to_reveal_doublon[k][0] in list_test :
                    ind_case_to_reveal.append([ind_case_to_reveal_doublon[k][0], ind_case_to_reveal_doublon[k][1]])
                    list_test.pop(list_test.index(ind_case_to_reveal_doublon[k][0]))
            for case in ind_case_to_reveal :
                replace_somthing_in_demineur(interaction.user.id, str(case[1]), (case[0]%taille_demineur+1, case[0]//taille_demineur))

            discord_txt = convert_txt_to_discord_demineur(interaction.user.id)
            tentative_restante = get_tentative_restante(interaction.user.id)
            embed = discord.Embed(title=f"Nombre de bombes : {get_nb_bombes()}\nTentative{pluriel(int(tentative_restante))} restante{pluriel(int(tentative_restante))} : {tentative_restante}", description=discord_txt)
            await interaction.response.edit_message(embed=embed)
        if test_demineur_termine(interaction.user.id) : #si le joueur gagne = il ne reste sur le plateau que lescases non miné (ou drapeaué) 
            await c_gagne(interaction)


    else :
        discord_txt = convert_txt_to_discord_demineur(interaction.user.id)
        tentative_restante = get_tentative_restante(interaction.user.id)
        embed = discord.Embed(title=f"Nombre de bombes : {get_nb_bombes()}\nTentative{pluriel(int(tentative_restante))} restante{pluriel(int(tentative_restante))} : {tentative_restante}", description=discord_txt)
        await interaction.response.edit_message(embed=embed)


#si le joueur gagne, on bloc tout (il a fini sa daily quest) et on lui donne une récompence
async def c_gagne(interaction) :
    taille_demineur = get_taille_demineur()
    _, _, _, list_ind_bomb = get_info_demineur(interaction.user.id)
    for bomb in list_ind_bomb :
        replace_somthing_in_demineur(interaction.user.id, "b", (bomb%taille_demineur+1, bomb//taille_demineur))
    baseDeDonnees = sqlite3.connect(CURRENT_PATH+f'\\assets\\database\\{db_used}')
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"""UPDATE Joueur
                    SET daily_quest_done = 1
                    WHERE id_discord_player == {interaction.user.id}""")
    baseDeDonnees.commit()
    baseDeDonnees.close()
    discord_txt = convert_txt_to_discord_demineur(interaction.user.id)
    embed = discord.Embed(title=f"Nombre de bombes : {get_nb_bombes()}\nTentative restante : 0", description=discord_txt)
    message = await interaction.original_response()
    await message.edit(embed=embed)
    #choix du gain
    #xp gagné -> toujours 100
    gain = choice(["carte", "xp", "fragment_5", "fragment_10"])
    if gain == "carte" :
        embed_gain_result, file_gain_result = effet_carte_demineur(interaction.user.id)
    elif gain == "xp" :
        embed_gain_result, file_gain_result = effet_xp_demineur(interaction.user.id)
    else :
        embed_gain_result, file_gain_result = effet_fragment_demineur(interaction.user.id, get_nb_fragment(gain))
    #Enfin, on affiche le résultat au joueur sur discord 
    #en premeir le gif en fonction du gain gagné
    if file_gain_result == None :
        await interaction.followup.send(embed=embed_gain_result)
    else : 
        await interaction.followup.send(embed=embed_gain_result, file=file_gain_result)




async def demineur_move_selecteur(message) :
    if message.content in alphabet_demnineur :
        message_for_demineur = True
        move_select_info = {"content_msg" : alphabet_demnineur.index(message.content)+1, "type selecteur" : "column"}
    elif message.content in nombre_demineur :
        message_for_demineur = True
        move_select_info = {"content_msg" : message.content, "type selecteur" : "line"}
    elif message.content in [alphabet_demnineur[k]+nombre_demineur[i] for k in range(9) for i in range(9)] :
        message_for_demineur = True
        move_select_info = {"content_msg" : [message.content[1], alphabet_demnineur.index(message.content[0])+1], "type selecteur" : "both"}
    elif message.content in [nombre_demineur[k]+alphabet_demnineur[i] for k in range(9) for i in range(9)] :
        message_for_demineur = True
        move_select_info = {"content_msg" : [message.content[0], alphabet_demnineur.index(message.content[1])+1], "type selecteur" : "both"}
    else :
        message_for_demineur = False
    if message_for_demineur :
        modif_ligne_colonne_selected(move_select_info, message.author.id)
        discord_txt = convert_txt_to_discord_demineur(message.author.id)
        tentative_restante = get_tentative_restante(message.author.id)
        embed = discord.Embed(title=f"Nombre de bombes : {get_nb_bombes()}\nTentative{pluriel(int(tentative_restante))} restante{pluriel(int(tentative_restante))} : {tentative_restante}", description=discord_txt)
        await message.author.send(embed=embed, view=Demineur())
