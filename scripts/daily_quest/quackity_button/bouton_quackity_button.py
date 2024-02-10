from scripts.daily_quest.quackity_button.func_used_by_button_quackity_button import response_choix_button_quackity
from scripts.global_commandes.fonctions import pluriel, select_interaction_argument, test_daily_quest_completed
from scripts.global_commandes.import_et_variable import *
from scripts.daily_quest.quackity_button.fonctions_quackity_button import get_number_chance_left


class Quackity_button(discord.ui.View):
    @discord.ui.button(label="Démarrer le jeu", style=discord.ButtonStyle.primary)
    async def demarer_button_callback(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        if test_daily_quest_completed(interaction.user.id) == False :
            nb_chance_left = get_number_chance_left(interaction.user.id)
            embed = discord.Embed(title=f"{nb_chance_left} chance{pluriel(nb_chance_left)} restante{pluriel(nb_chance_left)}")
            await interaction.response.send_message(embed=embed, view=Choix_quackity_button(), ephemeral=True)
        else :
            await interaction.response.send_message("Vous avez déjà effectué votre quête du jour. Revenez demain pour une nouvelle quête.", ephemeral=True)


#les 25 boutons possible 
class Choix_quackity_button(discord.ui.View):
    @discord.ui.button(label="O", style=discord.ButtonStyle.primary)
    async def button_callback_0(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 0)
    @discord.ui.button(label="O", style=discord.ButtonStyle.primary)
    async def button_callback_1(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 1)
    @discord.ui.button(label="O", style=discord.ButtonStyle.primary)
    async def button_callback_2(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 2)
    @discord.ui.button(label="O", style=discord.ButtonStyle.primary)
    async def button_callback_3(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 3)
    @discord.ui.button(label="O", style=discord.ButtonStyle.primary)
    async def button_callback_4(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 4)

    @discord.ui.button(label="O", row=1, style=discord.ButtonStyle.primary)
    async def button_callback_5(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 5)
    @discord.ui.button(label="O", row=1, style=discord.ButtonStyle.primary)
    async def button_callback_6(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 6)
    @discord.ui.button(label="O", row=1, style=discord.ButtonStyle.primary)
    async def button_callback_7(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 7)
    @discord.ui.button(label="O", row=1, style=discord.ButtonStyle.primary)
    async def button_callback_8(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 8)
    @discord.ui.button(label="O", row=1, style=discord.ButtonStyle.primary)
    async def button_callback_9(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 9)

    @discord.ui.button(label="O", row=2, style=discord.ButtonStyle.primary)
    async def button_callback_10(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 10)
    @discord.ui.button(label="O", row=2, style=discord.ButtonStyle.primary)
    async def button_callback_11(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 11)
    @discord.ui.button(label="O", row=2, style=discord.ButtonStyle.primary)
    async def button_callback_12(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 12)
    @discord.ui.button(label="O", row=2, style=discord.ButtonStyle.primary)
    async def button_callback_13(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 13)
    @discord.ui.button(label="O", row=2, style=discord.ButtonStyle.primary)
    async def button_callback_14(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 14)
        
    @discord.ui.button(label="O", row=3, style=discord.ButtonStyle.primary)
    async def button_callback_15(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 15)
    @discord.ui.button(label="O", row=3, style=discord.ButtonStyle.primary)
    async def button_callback_16(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 16)
    @discord.ui.button(label="O", row=3, style=discord.ButtonStyle.primary)
    async def button_callback_17(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 17)
    @discord.ui.button(label="O", row=3, style=discord.ButtonStyle.primary)
    async def button_callback_18(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 18)
    @discord.ui.button(label="O", row=3, style=discord.ButtonStyle.primary)
    async def button_callback_19(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 19)

    @discord.ui.button(label="O", row=4, style=discord.ButtonStyle.primary)
    async def button_callback_20(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 20)
    @discord.ui.button(label="O", row=4, style=discord.ButtonStyle.primary)
    async def button_callback_21(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 21)
    @discord.ui.button(label="O", row=4, style=discord.ButtonStyle.primary)
    async def button_callback_22(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 22)
    @discord.ui.button(label="O", row=4, style=discord.ButtonStyle.primary)
    async def button_callback_23(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 23)
    @discord.ui.button(label="O", row=4, style=discord.ButtonStyle.primary)
    async def button_callback_24(self, button, interaction):
        interaction = select_interaction_argument(interaction, button)
        await response_choix_button_quackity(interaction, 24)


async def message_lunch_quest_quackity_button(interaction) :
    embed = discord.Embed(title="""Daily quest : Boutons de Quackity

Règle : vous devrez choisir entre 25 boutons pour gagner une possible récompense.
Vous avez 3 chances possibles.
                          
Gain possible : 
 • XP
 • Fragments
 • carte
""")
    #enfin on répond à l'utilisateur par  bouton...
    await interaction.response.send_message(embed = embed, view=Quackity_button(), ephemeral=True)