from discord.ui.item import Item
from scripts.daily_quest.mastermind.func_used_by_button_mastermind import *
from scripts.global_commandes.fonctions import pluriel, select_interaction_argument, test_daily_quest_completed, check_current_daily_quest
from scripts.global_commandes.import_et_variable import *
from scripts.daily_quest.mastermind.fonctions_mastermind import calc_state_mastermind


class Mastermind(discord.ui.View):
    @discord.ui.button(label="Démarrer le jeu", style=discord.ButtonStyle.primary)
    async def demarer_button_callback(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        if test_daily_quest_completed(interaction.user.id) == False :
            if check_current_daily_quest("mastermind") : 
                current_state_master = calc_state_mastermind(interaction.user.id)
                embed = discord.Embed(description=current_state_master)
                await interaction.response.send_message(embed=embed, view=Choix_mastermind(), ephemeral=True)
            else :
                await interaction.response.send_message("Vous essayez de faire une daily quest fermée.")
        else :
            await interaction.response.send_message("Vous avez déjà effectué votre quête du jour. Revenez demain pour une nouvelle quête.", ephemeral=True)


class Choix_mastermind(discord.ui.View) :
    @discord.ui.select(
        placeholder = "Pion 1",
        min_values = 1, 
        max_values = 1, 
        options = [ 
            discord.SelectOption(label = "blanc", emoji="⚪"),
            discord.SelectOption(label = "noir", emoji="⚫"),
            discord.SelectOption(label = "rouge", emoji="🔴"),
            discord.SelectOption(label = "bleu", emoji="🔵"),
            discord.SelectOption(label = "marron", emoji="🟤"),
            discord.SelectOption(label = "violet", emoji="🟣"),
            discord.SelectOption(label = "vert", emoji="🟢"),
            discord.SelectOption(label = "jaune", emoji="🟡"),
            discord.SelectOption(label = "orange", emoji="🟠")
        ]
    )
    async def select_callback1(self, select, interaction): # the function called when the user is done selecting options
        await update_choix_pion(interaction, 0, select.values[0])
    @discord.ui.select(
        placeholder = "Pion 2",
        min_values = 1, 
        max_values = 1, 
        options = [ 
            discord.SelectOption(label = "blanc", emoji="⚪"),
            discord.SelectOption(label = "noir", emoji="⚫"),
            discord.SelectOption(label = "rouge", emoji="🔴"),
            discord.SelectOption(label = "bleu", emoji="🔵"),
            discord.SelectOption(label = "marron", emoji="🟤"),
            discord.SelectOption(label = "violet", emoji="🟣"),
            discord.SelectOption(label = "vert", emoji="🟢"),
            discord.SelectOption(label = "jaune", emoji="🟡"),
            discord.SelectOption(label = "orange", emoji="🟠")
        ]
    )
    async def select_callback2(self, select, interaction): # the function called when the user is done selecting options
        await update_choix_pion(interaction, 1, select.values[0])
    @discord.ui.select(
        placeholder = "Pion 3",
        min_values = 1, 
        max_values = 1, 
        options = [ 
            discord.SelectOption(label = "blanc", emoji="⚪"),
            discord.SelectOption(label = "noir", emoji="⚫"),
            discord.SelectOption(label = "rouge", emoji="🔴"),
            discord.SelectOption(label = "bleu", emoji="🔵"),
            discord.SelectOption(label = "marron", emoji="🟤"),
            discord.SelectOption(label = "violet", emoji="🟣"),
            discord.SelectOption(label = "vert", emoji="🟢"),
            discord.SelectOption(label = "jaune", emoji="🟡"),
            discord.SelectOption(label = "orange", emoji="🟠")
        ]
    )
    async def select_callback3(self, select, interaction): # the function called when the user is done selecting options
        await update_choix_pion(interaction, 2, select.values[0])
    @discord.ui.select(
        placeholder = "Pion 4",
        min_values = 1, 
        max_values = 1, 
        options = [ 
            discord.SelectOption(label = "blanc", emoji="⚪"),
            discord.SelectOption(label = "noir", emoji="⚫"),
            discord.SelectOption(label = "rouge", emoji="🔴"),
            discord.SelectOption(label = "bleu", emoji="🔵"),
            discord.SelectOption(label = "marron", emoji="🟤"),
            discord.SelectOption(label = "violet", emoji="🟣"),
            discord.SelectOption(label = "vert", emoji="🟢"),
            discord.SelectOption(label = "jaune", emoji="🟡"),
            discord.SelectOption(label = "orange", emoji="🟠")
        ]
    )
    async def select_callback4(self, select, interaction): # the function called when the user is done selecting options
        await update_choix_pion(interaction, 3, select.values[0])
    
    @discord.ui.button(label="Soumettre", style=discord.ButtonStyle.primary)
    async def soumettre_button_callback(self, button, interaction):
        test_changement_de_jour()
        interaction = select_interaction_argument(interaction, button)
        await action_master(interaction)

async def message_lunch_quest_mastermind(interaction) :
    embed = discord.Embed(title="Daily quest : Mastermind"
, description="""Règle : vous devrez trouver une combinaison secrète formée de 4 couleurs **différentes**.
À chaque essai, vous devez proposer une combinaison. Vous avez 10 propositions possibles.
À chaque proposition soumise à Pomme-Bot, vous aurez un retour pour chaque pion de 3 types possibles.
1-un pion est bien placé = un rond vert.
2-un pion est mal placé = un rond rouge.
3-un pion n'est pas dans la combinaison secrète = un rond blanc
                          
Attention, il n'y a pas d'indication sur quel pion est mal/bien placé ou quel pion n'existe pas. C'est à vous de déduire ces informations.
La combinaison est à gauche,
et les informations relatives aux combinaisons sont à droite.


                          
Gain possible : 
 • XP
 • Fragments
 • carte
""")
    #enfin on répond à l'utilisateur par  bouton...
    await interaction.response.send_message(embed = embed, view=Mastermind(), ephemeral=True)