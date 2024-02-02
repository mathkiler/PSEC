from time import time

temps = time()
yes = False
w = "zythums"
with open("liste_de_mot_fr.txt") as file:
    line = file.readline() 
    while line :
         if line == w :    
            yes = True
            break
         line = file.readline()

print(f"Le mot « {w} »", "est" if yes else "n'est pas", "un mot français.")

print("temps pour tester si un mot est dans le dico : ", time()-temps)