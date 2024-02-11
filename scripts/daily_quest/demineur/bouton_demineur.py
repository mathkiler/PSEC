from scripts.daily_quest.demineur.fonctions_demineur import *
from scripts.daily_quest.demineur.func_used_by_button_demineur import *
from scripts.global_commandes.fonctions import pluriel, test_daily_quest_completed, select_interaction_argument, test_message_mp, check_current_daily_quest
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
    @discord.ui.button(label="Démarrer le jeu", style=discord.ButtonStyle.primary)
    async def demarer_button_callback(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        if test_daily_quest_completed(interaction.user.id) == False :
            if check_current_daily_quest("demineur") :
                if test_message_mp(interaction.channel) :
                    discord_txt = convert_txt_to_discord_demineur(interaction.user.id)
                    tentative_restante = get_tentative_restante(interaction.user.id)
                    embed = discord.Embed(title=f"Nombre de bombes : {get_nb_bombes()}\nTentative{pluriel(int(tentative_restante))} restante{pluriel(int(tentative_restante))} : {tentative_restante}", description=discord_txt)
                    await interaction.response.send_message(embed=embed, view=Demineur())
                else :
                    await interaction.response.send_message("Cette quête ne peut s'effectuer **qu'en** MP avec pomme-bot", ephemeral=True)
            else :
                await interaction.response.send_message("Vous essayez de faire une daily quest fermée.", ephemeral=True)
        else :
            await interaction.response.send_message("Vous avez déjà effectué votre quête du jour. Revenez demain pour une nouvelle quête.", ephemeral=True)




async def message_lunch_quest_demineur(interaction) :
    embed = discord.Embed(title="""Daily quest : Demineur""", description="""
**Règle** : voir ce site pour les règles bien expliquées [ici](https://demineur.nhtdev.com/fr/rules) 

**Comment jouer** :sélectionner la ligne et la colonne en écrivant dans le chat la ligne, la colonne ou les 2, par exemple `e4`, `c`, `4`ou `1a`
Puis appuyer sur le bouton "déminer" ou "drapeau" pour effectuer les bonnes actions.
(Pour Drapeau, appuyer en place un. Réappuyer pour l'enlever)

:warning:**Attention**:warning: : Le jeu est faisable **uniquement en MP avec pomme-bot** 

**légende** :
 • :white_medium_square: = case non explorée
 • :bomb: = bombe
 • :triangular_flag_on_post: = drapeau
 •     = case vide (pas d'emoji)
 • :one: :two: :three: :four: :five: :six: :seven: :eight: = nombre de bombes dans les cases adjacentes   
 • :arrow_down: = colonne sélectionnée
 • :arrow_right: = ligne sélectionnée
 • :green_circle: = case sélectionnée (s'affiche uniquement si c'est une case non minée)
                                     
**Gain possible** : 
 • XP
 • Fragments
 • carte
""")
    #enfin on répond à l'utilisateur par  bouton...
    await interaction.response.send_message(embed = embed, view=MsgDemineur(), ephemeral=True)





