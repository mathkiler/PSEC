from scripts.global_commandes.import_et_variable import *
from scripts.global_commandes.fonctions import *
from scripts.global_commandes.func_used_by_button import *


#--|--# création des boutons d'interraction
#bouton des commandes possible des utilisateurs via la commande !commandes
class Voir_Commandes(discord.ui.View):
    @discord.ui.button(label="Voir ses stats", style=discord.ButtonStyle.primary)
    async def stats_private_button_callback(self, interaction, button):
        test_changement_de_jour()
        await voir_stats(interaction, True)

    @discord.ui.button(label="Montrer ses stats à tout le monde pour flex", style=discord.ButtonStyle.green)
    async def stats_public_button_callback(self, interaction, button):
        test_changement_de_jour()
        await voir_stats(interaction, False)
        
    @discord.ui.button(label="Opening de carte", row=1, style=discord.ButtonStyle.primary)
    async def opening_button_callback(self, button, interaction):
        test_changement_de_jour()
        #on va chercher le nombre de fragment de l'utilisateur pour lui montrer avant son opening
        fragments = get_fragments_by_user(interaction.user.id)
        await interaction.response.send_message(f"vous avez **{fragments}** fragrment(s)\nDémarer l'opening ?", view=Start_opening(), ephemeral=True)

    @discord.ui.button(label="Mes cartes", row=2, style=discord.ButtonStyle.primary)
    async def mes_cartes_button_callback(self, button, interaction):
        test_changement_de_jour()
        resultat_carte_possede, index_curseur, nb_cartes = await initialisation_mes_cartes(interaction)
        #si le joueur n'a pas de carte on le lui dis gentilment
        if nb_cartes <= 0 :
            await interaction.response.send_message("Vous n'avez pas de carte !", ephemeral=True)
        else :
            #on affiche l'image 
            img_path = CURRENT_PATH+f"/assets/cartes/{resultat_carte_possede[index_curseur][0]}.png"
            file = discord.File(img_path)
            embed = discord.Embed(title=f"{index_curseur+1}/{nb_cartes}\nPossédée(s) : {resultat_carte_possede[index_curseur][2]}\nExp par doublon vendu ({resultat_carte_possede[index_curseur][1]}) : {(nom_rarete.index(resultat_carte_possede[index_curseur][1])+1)*2}")
            embed.set_image(url=f"attachment://{formatage_nom_carte(resultat_carte_possede[index_curseur][0])}.png")
            #enfin on répond à l'utilisateur par l'image, bouton...
            await interaction.response.send_message(embed = embed, view=Mes_cartes(), file=file, ephemeral=True)


    @discord.ui.button(label="Mon album", row=3, style=discord.ButtonStyle.primary)
    async def album_private_button_callback(self, button, interaction):
        test_changement_de_jour()
        await mon_album(interaction, True)

    @discord.ui.button(label="Montrer mon album à tout le monde", row=3, style=discord.ButtonStyle.green)
    async def album_public_button_callback(self, button, interaction):
        test_changement_de_jour()
        await mon_album(interaction, False)


    @discord.ui.button(label="Quete quotidienne", row=4, style=discord.ButtonStyle.primary)
    async def daily_quest_button_callback(self, button, interaction):
        test_changement_de_jour()
        test_cration_bdd_user(interaction.user.id)
        name_quest = get_daily_quest()
        if test_daily_quest_completed(interaction.user.id) :
            await interaction.response.send_message("Vous avez déjà effectué votre quête du jour. Revenez demain pour une nouvelle quête.", ephemeral=True)
        else :
            await selecteur_lunch_quest(name_quest, interaction)


#bouton/message pour choisir combien de carte l'utilisateur veux ouvrir d'un coup. Ou s'il veux finalemnt annuler l'action (ce ui au passage ne change rien du tout)
class Start_opening(discord.ui.View): 
    @discord.ui.button(label="Ouvrir 1 carte", style=discord.ButtonStyle.primary)
    async def ouvrir_1_button_callback(self, button, interaction):
        test_changement_de_jour()
        await opening(interaction, 1)

    @discord.ui.button(label="Ouvrir 5 carte", style=discord.ButtonStyle.primary)
    async def ouvrir_5_button_callback(self, button, interaction):
        test_changement_de_jour()
        await opening(interaction, 5)

    @discord.ui.button(label="Ouvrir 10 carte", style=discord.ButtonStyle.primary)
    async def ouvrir_10_button_callback(self, button, interaction):
        test_changement_de_jour()
        await opening(interaction, 10)

    @discord.ui.button(label="Annuler", style=discord.ButtonStyle.red)
    async def non_button_callback(self, button, interaction):
        test_changement_de_jour()
        await interaction.response.send_message("Action annulé", ephemeral=True)


#bouton/message pour afficher mes cartes
class Mes_cartes(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View

    @discord.ui.button(label="-5", style=discord.ButtonStyle.secondary)
    async def five_prev_button_callback(self, button, interaction):
        test_changement_de_jour()
        await selecteur_button_mes_cartes(interaction, "five_prev")

    @discord.ui.button(label="Prev", style=discord.ButtonStyle.secondary)
    async def left_button_callback(self, button, interaction):
        test_changement_de_jour()
        await selecteur_button_mes_cartes(interaction, "one_prev")

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def one_next_button_callback(self, button, interaction):
        test_changement_de_jour()
        await selecteur_button_mes_cartes(interaction, "one_next")

    @discord.ui.button(label="+5", style=discord.ButtonStyle.secondary)
    async def five_next_button_callback(self, button, interaction):
        test_changement_de_jour()
        await selecteur_button_mes_cartes(interaction, "five_next")

    @discord.ui.button(label="Recycler UN doublon", row=1, style=discord.ButtonStyle.red)
    async def supr_un_doublon_button_callback(self, button, interaction):
        test_changement_de_jour()
        await mes_cartes_supprime_doublon(interaction, "UN")

    @discord.ui.button(label="Recycler TOUT les doublons de cette carte", row=1, style=discord.ButtonStyle.red)
    async def supr_tout_doublon_button_callback(self, button, interaction):
        test_changement_de_jour()
        await mes_cartes_supprime_doublon(interaction, "TOUS")

    @discord.ui.button(label="Recycler TOUT les doublons de  l'album", row=2, style=discord.ButtonStyle.red)
    async def supr_all_doublon_button_callback(self, button, interaction):
        test_changement_de_jour()
        await mes_cartes_supprime_doublon(interaction, "ALL")