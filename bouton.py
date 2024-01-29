from import_et_variable import *
from fonctions import *
from func_used_by_button import *


#--|--# création des boutons d'interraction
#bouton des commandes possible des utilisateurs via la commande !commandes
class Voir_Commandes(discord.ui.View):
    @discord.ui.button(label="Voir ses stats", style=discord.ButtonStyle.primary)
    async def stats_private_button_callback(self, button, interaction):
        test_changement_de_jour()
        await voir_stats(interaction, True)

    @discord.ui.button(label="Montrer ses stats à tout le monde pour flex", style=discord.ButtonStyle.green)
    async def stats_public_button_callback(self, button, interaction):
        test_changement_de_jour()
        await voir_stats(interaction, False)
        
    @discord.ui.button(label="Opening d'une carte", row=1, style=discord.ButtonStyle.primary)
    async def opening_button_callback(self, button, interaction):
        test_changement_de_jour()
        await interaction.response.send_message("Démarer l'opening ?", view=Start_opening(), ephemeral=True)

    @discord.ui.button(label="Mes cartes", row=2, style=discord.ButtonStyle.primary)
    async def mes_cartes_button_callback(self, button, interaction):
        test_changement_de_jour()
        resultat_carte_possede, index_curseur, nb_cartes = await initialisation_mes_cartes(interaction)
        #si le joueur n'a pas de carte on le lui dis gentilment
        if nb_cartes <= 0 :
            await interaction.response.send_message("Vous n'avez pas de carte !", ephemeral=True)
        else :
            #on affiche l'image 
            img_path = f"./assets/cartes/{resultat_carte_possede[index_curseur][0]}.png"
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


#bouton/message oui ou non pour la validation lors du choix d'ouvrir un case opening
class Start_opening(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    @discord.ui.button(label="Confirmer", style=discord.ButtonStyle.primary)
    async def oui_button_callback(self, button, interaction):
        test_changement_de_jour()
        await opening(interaction)

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
    async def supr_one_doublon_button_callback(self, button, interaction):
        test_changement_de_jour()
        await mes_cartes_supprime_doublon(interaction, "UN")

    @discord.ui.button(label="Recycler TOUT les doublons", row=1, style=discord.ButtonStyle.red)
    async def supr_all_doublon_button_callback(self, button, interaction):
        test_changement_de_jour()
        await mes_cartes_supprime_doublon(interaction, "TOUS")