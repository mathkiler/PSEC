from scripts.daily_quest.motus.fonctions_motus import genere_FIRST_image_motus, genere_image_motus, get_mot_mystere
from scripts.global_commandes.fonctions import pluriel, select_interaction_argument, test_daily_quest_completed, test_message_mp, check_current_daily_quest
from scripts.global_commandes.import_et_variable import *


class Motus(discord.ui.View):
    @discord.ui.button(label="Démarrer le jeu", style=discord.ButtonStyle.primary)
    async def demarer_button_callback(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        if test_daily_quest_completed(interaction.user.id) == False :
            if check_current_daily_quest("motus") :
                if str(interaction.user.id) in motus_msg_player and test_message_mp(interaction.channel): #true si il a déjà démarer le jeu
                    mot_mystere = get_mot_mystere()
                    nb_chance_left = motus_msg_player[f"{interaction.user.id}"]["nb_chance_left"]
                    embed = discord.Embed(title=f"""Tentative{pluriel(nb_chance_left)} restante{pluriel(nb_chance_left)} : {nb_chance_left}
    mot en {len(mot_mystere)} lettres""")
                    name_img = genere_image_motus(mot_mystere, motus_msg_player[f"{interaction.user.id}"]["mot_donnes"])
                    embed.set_image(url=f"attachment://{name_img}.png")
                    await interaction.response.send_message(embed=embed, file=discord.File(CURRENT_PATH+f'/assets/img_tamp/{name_img}.png'), ephemeral=True)
                    motus_msg_player[str(interaction.user.id)]["interaction"] = interaction
                    os.remove(CURRENT_PATH+f"/assets/img_tamp/{name_img}.png")
                elif test_message_mp(interaction.channel): #premier message affichant le motus
                    nb_chance_left = 6
                    mot_mystere = get_mot_mystere()
                    embed = discord.Embed(title=f"""Tentative{pluriel(nb_chance_left)} restante{pluriel(nb_chance_left)} : {nb_chance_left}
    mot en {len(mot_mystere)} lettres""")
                    name_img = genere_FIRST_image_motus(mot_mystere)
                    embed.set_image(url=f"attachment://{name_img}.png")
                    await interaction.response.send_message(embed=embed, file=discord.File(CURRENT_PATH+f'/assets/img_tamp/{name_img}.png'))
                    os.remove(CURRENT_PATH+f"/assets/img_tamp/{name_img}.png")
                    motus_msg_player[str(interaction.user.id)] = {"nb_chance_left" : 6, "mot_donnes" : []}
                else :
                    await interaction.response.send_message("Cette quête ne peut s'effectuer **qu'en** MP avec pomme-bot.", ephemeral=True)
            else :
                await interaction.response.send_message("Vous essayez de faire une daily quest fermée.")
        else :
            await interaction.response.send_message("Vous avez déjà effectué votre quête du jour. Revenez demain pour une nouvelle quête.", ephemeral=True)




async def message_lunch_quest_motus(interaction) :
    embed = discord.Embed(title="""Daily quest : Motus""", description="""
**Règle :** le but est de retrouver des mots (qui ont tous un lien avec QSMP)
La 1ʳᵉ lettre du mot mystère est affichée. Le but est de trouver le mot en un minimum de coups sans dépasser 6 tentatives ou la partie est perdue.
À chaque tentative, les lettres bien placées sont en rouge et celles mal placées en jaune. Les mots mal orthographiés ou absents du dictionnaire ne seront pas testés.

**Comment jouer :** écrivez simplement un mot dans le chat.
                          
:warning:**Attention**:warning: : Le jeu est faisable **uniquement en MP avec pomme-bot** 
           
**Gain possible :** 
 • XP
 • Fragments
 • carte
""")
    #enfin on répond à l'utilisateur par  bouton...
    await interaction.response.send_message(embed = embed, view=Motus(), ephemeral=True)
