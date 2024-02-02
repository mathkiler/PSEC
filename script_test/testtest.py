from time import time

temps = time()
yes = False
w = "zythums"
with open("liste_de_mot_fr.txt") as file:
    for m in file.readlines() :    
        if m == w :
            yes = True
            break

print(f"Le mot « {w} »", "est" if yes else "n'est pas", "un mot français.")

print("temps pour tester si un mot est dans le dico : ", time()-temps)