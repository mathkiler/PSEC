from random import choice, randint
import sqlite3
import os

from scripts.global_commandes.import_et_variable import CURRENT_PATH


baseDeDonnees = sqlite3.connect(CURRENT_PATH+'/assets/database/database.db')
curseur = baseDeDonnees.cursor()



id_user = 382877512302067712
curseur.execute(f"""UPDATE carte_possede
                SET nombre_carte_possede = nombre_carte_possede - 4
                WHERE id_discord_player={id_user} AND id = 2""")
baseDeDonnees.commit()
curseur.execute(f"""UPDATE carte_possede
                SET nombre_carte_possede = nombre_carte_possede - 2
                WHERE id_discord_player={id_user} AND id = 5""")
baseDeDonnees.commit()
curseur.execute(f"""UPDATE carte_possede
                SET nombre_carte_possede = nombre_carte_possede - 2
                WHERE id_discord_player={id_user} AND id = 28""")
baseDeDonnees.commit() 


baseDeDonnees.close()

os.system("del resolving_Teoad_Bug.py")