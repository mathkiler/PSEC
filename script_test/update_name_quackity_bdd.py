import sqlite3

from scripts.global_commandes.import_et_variable import db_path


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