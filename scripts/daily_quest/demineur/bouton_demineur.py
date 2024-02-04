from scripts.daily_quest.demineur.fonctions_demineur import convert_txt_to_discord_demineur, get_nb_bombes, get_taille_demineur, modif_ligne_colonne_selected
from scripts.daily_quest.demineur.func_used_by_button_demineur import *
from scripts.global_commandes.fonctions import pluriel, test_daily_quest_completed
from scripts.global_commandes.import_et_variable import *


#explication des etat possibles sauvegardé :
#c = case non miné
#b = bombe
#d = drapeau
#1-2-3-4-5-6-7-8-9 = nombre
#0 = rien

#L'etat d'un démineur est sauvegarddé pour chaque joueur dans ./assets/daily_quest_save/{id_discor_player}.txt


#class pour afficher le message d'explication au début
class MsgDemineur(discord.ui.View):
    @discord.ui.button(label="Démarer le jeu", style=discord.ButtonStyle.primary)
    async def demarer_button_callback(self, button, interaction):
        if test_daily_quest_completed(interaction.user.id) == False :
            discord_txt = convert_txt_to_discord_demineur(interaction.user.id)
            tentative_restante = get_tentative_restante(interaction.user.id)
            embed = discord.Embed(title=f"Nombre de bombes : {get_nb_bombes()}\ntentative{pluriel(int(tentative_restante))} restante{pluriel(int(tentative_restante))} : {tentative_restante}", description=discord_txt)
            await interaction.response.send_message(embed=embed, view=Demineur(), ephemeral=True)
        else :
            await interaction.response.send_message("Vous avez déjà effectué votre quête du jour. Revenez demain pour une nouvelle quête.", ephemeral=True)


#class du jeu
class Demineur(discord.ui.View):
    #select pour choisir la colonne
    @discord.ui.select( placeholder = "flèche en haut (colonne)", min_values = 1, max_values = 1,
        options = [ 
            discord.SelectOption(
                label=f"{k}",
            ) for k in range(1, get_taille_demineur()+1)
        ]
    )
    async def select_colonne_callback(self, select, interaction): # the function called when the user is done selecting options
        if test_daily_quest_completed(interaction.user.id) == False :
            modif_ligne_colonne_selected(int(select.values[0]), 1, interaction.user.id)
            discord_txt = convert_txt_to_discord_demineur(interaction.user.id)
            tentative_restante = get_tentative_restante(interaction.user.id)
            embed = discord.Embed(title=f"Nombre de bombes : {get_nb_bombes()}\ntentative{pluriel(int(tentative_restante))} restante{pluriel(int(tentative_restante))} : {tentative_restante}", description=discord_txt)
            await interaction.response.edit_message(embed=embed)
        else :
            await interaction.response.send_message("Vous avez déjà effectué votre quête du jour. Revenez demain pour une nouvelle quête.", ephemeral=True)


    @discord.ui.select( placeholder = "flèche de gauche (ligne)", min_values = 1, max_values = 1,
        options = [
            discord.SelectOption(
                label=f"{k}",
            ) for k in range(1, get_taille_demineur()+1)
        ]
    )
    async def select_ligne_callback(self, select, interaction): # the function called when the user is done selecting options
        if test_daily_quest_completed(interaction.user.id) == False :
            modif_ligne_colonne_selected(int(select.values[0])-1, 0, interaction.user.id)
            discord_txt = convert_txt_to_discord_demineur(interaction.user.id)
            tentative_restante = get_tentative_restante(interaction.user.id)
            embed = discord.Embed(title=f"Nombre de bombes : {get_nb_bombes()}\ntentative{pluriel(int(tentative_restante))} restante{pluriel(int(tentative_restante))} : {tentative_restante}", description=discord_txt)
            await interaction.response.edit_message(embed=embed)
        else :
            await interaction.response.send_message("Vous avez déjà effectué votre quête du jour. Revenez demain pour une nouvelle quête.", ephemeral=True)




    @discord.ui.button(label="déminer", style=discord.ButtonStyle.primary)
    async def deminer_callback(self, button, interaction):
        if test_daily_quest_completed(interaction.user.id) == False :
            await demine_case(interaction)
        else :
            await interaction.response.send_message("Vous avez déjà effectué votre quête du jour. Revenez demain pour une nouvelle quête.", ephemeral=True)



    @discord.ui.button(label="drapeau", style=discord.ButtonStyle.primary)
    async def drapeau_callback(self, button, interaction):
        if test_daily_quest_completed(interaction.user.id) == False :
            await add_flag(interaction)
        else :
            await interaction.response.send_message("Vous avez déjà effectué votre quête du jour. Revenez demain pour une nouvelle quête.", ephemeral=True)


async def message_lunch_quest_demineur(interaction) :
    embed = discord.Embed(title="""Daily quest : Demineur""", description="""

**Règle** : voir ce site pour les règles bien expliqués **[ici]**(https://demineur.nhtdev.com/fr/rules) 

**Comment jouer** :selectionner la ligne et la colonne grâce au 2 selecteurs présent
Puis appuyer sur le bouton "déminer" ou "drapeau" pour effectuer les bonnes actions.
(Pour drapeau, appuyer en place un. Réappuyer pour l'enlenver)
                          
**légende** :
 • :white_medium_square: = case non exploré
 • :bomb: = bombe
 • :triangular_flag_on_post: = drapeau
 •     = case vide (pas d'emoji)
 • :one: :two: :three: :four: :five: :six: :seven: :eight: = nombre de bombe dans les cases adjacente   
 • :arrow_down: = colonne séléctionné
 • :arrow_right: = ligne séléctionné
 • :green_circle: = case selectioné (s'affiche uniquement si c'est une case non minée)
                                     
**Gain possible** : 
 • XP
 • Fragments
 • carte
""")
    #enfin on répond à l'utilisateur par  bouton...
    await interaction.response.send_message(embed = embed, view=MsgDemineur(), ephemeral=True)