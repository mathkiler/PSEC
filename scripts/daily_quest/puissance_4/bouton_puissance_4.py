from scripts.daily_quest.puissance_4.fonctions_puissance_4 import create_img_p4
from scripts.daily_quest.puissance_4.func_used_by_button_puissance_4 import place_pion
from scripts.global_commandes.fonctions import test_daily_quest_completed
from scripts.global_commandes.import_et_variable import *

#toujours : joueur 1 = player = rouge



class MsgPuissance_4(discord.ui.View):
    @discord.ui.button(label="Démarer le jeu", style=discord.ButtonStyle.primary)
    async def demarer_button_callback(self, button, interaction):
        if test_daily_quest_completed(interaction.user.id) == False :
            name_img = create_img_p4(interaction.user.id, ["rien", None, None])
            img_path = CURRENT_PATH+f"/assets/img tamp/{name_img}.png"
            file = discord.File(img_path)
            embed = discord.Embed(title="Puissance 4")
            embed.set_image(url=f"attachment://{name_img}.png")
            await interaction.response.send_message(embed=embed, view=Puissance_4(),file=file,  ephemeral=True)
            os.remove(CURRENT_PATH+f"/assets/img tamp/{name_img}.png")
        else :
            await interaction.response.send_message("Vous avez déjà effectué votre quête du jour. Revenez demain pour une nouvelle quête.", ephemeral=True)



class Puissance_4(discord.ui.View) :
    @discord.ui.button(label="1", style=discord.ButtonStyle.primary)
    async def colone1_callback(self, button, interaction):
        if test_daily_quest_completed(interaction.user.id) == False :
            await place_pion(interaction, 0)
        else :
            await interaction.response.send_message("Vous avez déjà effectué votre quête du jour. Revenez demain pour une nouvelle quête.", ephemeral=True)


    @discord.ui.button(label="2", style=discord.ButtonStyle.primary)
    async def colone2_callback(self, button, interaction):
        if test_daily_quest_completed(interaction.user.id) == False :
            await place_pion(interaction, 1)
        else :
            await interaction.response.send_message("Vous avez déjà effectué votre quête du jour. Revenez demain pour une nouvelle quête.", ephemeral=True)

    @discord.ui.button(label="3", style=discord.ButtonStyle.primary)
    async def colone3_callback(self, button, interaction):
        if test_daily_quest_completed(interaction.user.id) == False :
            await place_pion(interaction, 2)
        else :
            await interaction.response.send_message("Vous avez déjà effectué votre quête du jour. Revenez demain pour une nouvelle quête.", ephemeral=True)

    @discord.ui.button(label="4", style=discord.ButtonStyle.primary)
    async def colone4_callback(self, button, interaction):
        if test_daily_quest_completed(interaction.user.id) == False :
            await place_pion(interaction, 3)
        else :
            await interaction.response.send_message("Vous avez déjà effectué votre quête du jour. Revenez demain pour une nouvelle quête.", ephemeral=True)

    @discord.ui.button(label="5", style=discord.ButtonStyle.primary)
    async def colone5_callback(self, button, interaction):
        if test_daily_quest_completed(interaction.user.id) == False :
            await place_pion(interaction, 4)
        else :
            await interaction.response.send_message("Vous avez déjà effectué votre quête du jour. Revenez demain pour une nouvelle quête.", ephemeral=True)

    @discord.ui.button(label="6", style=discord.ButtonStyle.primary)
    async def colone6_callback(self, button, interaction):
        if test_daily_quest_completed(interaction.user.id) == False :
            await place_pion(interaction, 5)
        else :
            await interaction.response.send_message("Vous avez déjà effectué votre quête du jour. Revenez demain pour une nouvelle quête.", ephemeral=True)

    @discord.ui.button(label="7", style=discord.ButtonStyle.primary)
    async def colone7_callback(self, button, interaction):
        if test_daily_quest_completed(interaction.user.id) == False :
            await place_pion(interaction, 6)
        else :
            await interaction.response.send_message("Vous avez déjà effectué votre quête du jour. Revenez demain pour une nouvelle quête.", ephemeral=True)



async def message_lunch_quest_puissance_4(interaction) :
    embed = discord.Embed(title="Daily quest : Puissance 4", description="""
Vous devrez gagner au puissance 4 contre Pomme-bot (vous commencez et êtes toujours rouge)
**Règle** : Voir les règles dans la rubrique règle sur ce site [ici](https://fr.wikipedia.org/wiki/Puissance_4)

**Comment jouer** : Appuyer sur le bouton corespondant à la colonne voulue
                                                                    
**Gain possible** : 
 • XP
 • Fragments
 • carte
""")
    #enfin on répond à l'utilisateur par  bouton...
    await interaction.response.send_message(embed = embed, view=MsgPuissance_4(), ephemeral=True)