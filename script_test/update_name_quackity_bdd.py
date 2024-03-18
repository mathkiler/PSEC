import sqlite3
import os

CURRENT_PATH = os.getcwd()[:-12]
db_path = CURRENT_PATH+f'/assets/database/database.db'


baseDeDonnees = sqlite3.connect(db_path)
curseur = baseDeDonnees.cursor()




    
curseur.execute(f"""UPDATE Cartes 
      SET nom = C_El_Quackity
      WHERE id == 4""")


curseur.execute(f"""UPDATE Cartes 
      SET nom = R_Quackity
      WHERE id == 7""")





baseDeDonnees.commit()
baseDeDonnees.close()