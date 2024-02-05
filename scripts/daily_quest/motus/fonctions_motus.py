from scripts.daily_quest.motus.func_used_by_button_motus import gagne_motus
from scripts.global_commandes.fonctions import *
from scripts.global_commandes.import_et_variable import *





def get_mot_mystere() :
    baseDeDonnees = sqlite3.connect(CURRENT_PATH+f'/assets/database/{db_used}')
    curseur = baseDeDonnees.cursor()
    curseur.execute("SELECT info_quest FROM daily_quest")
    result = curseur.fetchall()[-1][0]
    baseDeDonnees.close()
    return result


def genere_image_motus(mot_mystere, mots_donnes) :
        #enfin, on créer l'image
    
    img_final_motus = Image.new('RGBA', (75*len(mot_mystere), 75*len(mots_donnes)))

    count_mot = 0
    for mot in mots_donnes :
        ind_lettre = 0
        letters_in_mot = []
        ordonancement_lettre = ["lettre_normal" for k in range(len(mot))] #liste de si les lettres sont bien placé, mal placé, ou rien
        #test si les lettres sont parfaitement bien placés uniquement
        for lettre in mot :
            if lettre == mot_mystere[ind_lettre] :            
                ordonancement_lettre[ind_lettre] = "lettre_bonne"
            else :
                letters_in_mot.append(mot_mystere[ind_lettre])
            ind_lettre+=1
        ind_lettre = 0
        #test si les lettres sont juste mal placé
        for lettre in mot :
            if lettre in letters_in_mot and ordonancement_lettre[ind_lettre] == "lettre_normal" :            
                letters_in_mot.pop(letters_in_mot.index(lettre))
                ordonancement_lettre[ind_lettre] = "lettre_mal_place"
            ind_lettre+=1
        ind_lettre = 0
        #enfin on affiche les lettres sur l'image
        for lettre in mot :
            img_back_letter = Image.open(CURRENT_PATH+f"/assets/motus/image_lettre/{ordonancement_lettre[ind_lettre]}.png")
            img_final_motus.paste(img_back_letter, (75*ind_lettre, 75*count_mot))
            let = Image.open(CURRENT_PATH+f"/assets/motus/image_lettre/lettre/{lettre}.png")
            img_final_motus.paste(let, (75*ind_lettre, 75*count_mot), let)
            ind_lettre+=1
        count_mot+=1   
    name_img = randint(100000, 999999)
    img_final_motus.save(CURRENT_PATH+f"/assets/img tamp/{name_img}.png")
    return name_img



def genere_FIRST_image_motus(mot_mystere) :
    img_final_motus = Image.new('RGBA', (75*len(mot_mystere), 75))
    img_back_letter = Image.open(CURRENT_PATH+f"/assets/motus/image_lettre/lettre_bonne.png")
    img_final_motus.paste(img_back_letter, (0, 0))
    let = Image.open(CURRENT_PATH+f"/assets/motus/image_lettre/lettre/{mot_mystere[0]}.png")
    img_final_motus.paste(let, (0, 0), let)
    for k in range(len(mot_mystere)-1) :
        img_back_letter = Image.open(CURRENT_PATH+f"/assets/motus/image_lettre/lettre_normal.png")
        img_final_motus.paste(img_back_letter, (75*(k+1), 0))
        let = Image.open(CURRENT_PATH+f"/assets/motus/image_lettre/lettre/.point.png")
        img_final_motus.paste(let, (75*(k+1), 0), let)
    name_img = randint(100000, 999999)
    img_final_motus.save(CURRENT_PATH+f"/assets/img tamp/{name_img}.png")
    return name_img




async def user_test_mot_motus(id_user, mot_user) :
    mot_user = formatage_mot_user_motus(mot_user)
    mot_mystere = get_mot_mystere()
    if len(mot_user) > len(mot_mystere) :
        msg = await motus_msg_player[id_user]["interaction"].followup.send(f"**{mot_user}** est trop long ({len(mot_user)} lettres au lieu de {len(mot_mystere)} lettres)", ephemeral = True)
        await asyncio.sleep(5)
        await msg.delete()
    elif len(mot_user) < len(mot_mystere) :
        msg = await motus_msg_player[id_user]["interaction"].followup.send(f"**{mot_user}** est trop court ({len(mot_user)} lettres au lieu de {len(mot_mystere)} lettres)", ephemeral = True)
        await asyncio.sleep(5)
        await msg.delete()
    elif mot_user in motus_msg_player[id_user]["mot_donnes"] :
        msg = await motus_msg_player[id_user]["interaction"].followup.send(f"**{mot_user}** a déjà été proposé.", ephemeral = True)
        await asyncio.sleep(5)
        await msg.delete()
    else :
        mot_in_dico = False
        with open(CURRENT_PATH+f"/assets/motus/liste_de_mot_fr_dico.txt") as file:
            line = file.readline() 
            while line :
                if line.replace("\n", "") == mot_user :    
                    mot_in_dico = True
                    break
                line = file.readline()
        if mot_in_dico == False :
            msg = await motus_msg_player[id_user]["interaction"].followup.send(f"**{mot_user}** n'est pas dans mon dictionnaire", ephemeral = True)
            await asyncio.sleep(5)
            await msg.delete()
        else :
            
            motus_msg_player[id_user]["nb_chance_left"]-=1
            nb_chance_left = motus_msg_player[id_user]["nb_chance_left"]
            embed = discord.Embed(title=f"""Tentative{pluriel(nb_chance_left)} restante{pluriel(nb_chance_left)} : {nb_chance_left}
    mot en {len(mot_mystere)} lettres""")
            motus_msg_player[id_user]["mot_donnes"].append(mot_user)
            name_img = genere_image_motus(mot_mystere, motus_msg_player[id_user]["mot_donnes"])
            embed.set_image(url=f"attachment://{name_img}.png")
            await motus_msg_player[id_user]["message_motus"].edit(embed=embed, file=discord.File(CURRENT_PATH+f'/assets/img tamp/{name_img}.png'))
            os.remove(CURRENT_PATH+f"/assets/img tamp/{name_img}.png")
            #test si c'est la fin du jeu
            if mot_user == mot_mystere :
                await gagne_motus(motus_msg_player[id_user]["interaction"])
                motus_msg_player.pop(id_user)
            #le user perd le jeu aucune tentative restante
            elif motus_msg_player[id_user]["nb_chance_left"] == 0 :
                await motus_msg_player[id_user]["interaction"].followup.send(f"Perdu ! Le mot était **{mot_mystere}**", ephemeral = True)
                motus_msg_player.pop(id_user)
                baseDeDonnees = sqlite3.connect(CURRENT_PATH+f'/assets/database/{db_used}')
                curseur = baseDeDonnees.cursor()
                curseur.execute(f"""UPDATE Joueur
                                SET daily_quest_done = 1
                                WHERE id_discord_player == {id_user}""")
                baseDeDonnees.commit()
                baseDeDonnees.close()



    

def formatage_mot_user_motus(nom) :
    nom = nom.replace("é", "e")
    nom = nom.replace("à", "a")
    nom = nom.replace("è", "e")
    nom = nom.replace("ù", "u")
    nom = nom.replace("à", "a")
    nom = nom.replace("â", "a")
    nom = nom.replace("ê", "e")
    nom = nom.replace("î", "i")
    nom = nom.replace("ô", "o")
    nom = nom.replace("û", "u")
    nom = nom.replace("ç", "c")
    return nom