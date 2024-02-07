from scripts.daily_quest.roue_fortune.func_used_by_button_roue_fortune import tourne_roue
from scripts.global_commandes.fonctions import select_interaction_argument, test_daily_quest_completed
from scripts.global_commandes.import_et_variable import *


class Roue_fortune(discord.ui.View):
    @discord.ui.button(label="Tourner la roue", style=discord.ButtonStyle.primary)
    async def demarer_button_callback(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        if test_daily_quest_completed(interaction.user.id) == False :
            await tourne_roue(interaction)
        else :
            await interaction.response.send_message("Vous avez déjà effectué votre quête du jour. Revenez demain pour une nouvelle quête.", ephemeral=True)


async def message_lunch_quest_roue_fortune(interaction) :
    embed = discord.Embed(title="""Daily quest : Roue de la fortune

Règle : Vous avez juste à cliquer sur le bouton et prier pour obtenir une bonne récompense.
                          
Gain possible : 
 • XP
 • Fragments
 • carte
 • rien
""")
    #enfin on répond à l'utilisateur par  bouton...
    await interaction.response.send_message(embed = embed, view=Roue_fortune(), ephemeral=True)