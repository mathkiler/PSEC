import sqlite3
import os

CURRENT_PATH = os.getcwd()[:-12]
db_path = CURRENT_PATH+f'/assets/database/database.db'

baseDeDonnees = sqlite3.connect(db_path)
curseur = baseDeDonnees.cursor()

#brioche
curseur.execute(f"""UPDATE Joueur 
      SET fragment = fragment + {20}
      WHERE id_discord_player == {581776637042098188}""")

#dava
curseur.execute(f"""UPDATE Joueur 
      SET fragment = fragment + {10}
      WHERE id_discord_player == {187985316093755392}""")

baseDeDonnees.commit()
baseDeDonnees.close()