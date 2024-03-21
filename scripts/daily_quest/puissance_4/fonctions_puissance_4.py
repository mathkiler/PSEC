from scripts.global_commandes.fonctions import *
from scripts.global_commandes.import_et_variable import *


def get_etat_puissance_4(id_user) :
    with open(CURRENT_PATH+f"/assets/daily_quest_save/{id_user}.txt", "r") as f :
        etat_p4 = f.readline().split(",")
    return etat_p4


#obtenir la ligne en fonction de la ligne 
def get_line_by_column(id_user, ind_column) :
    etat_p4 = get_etat_puissance_4(id_user)
    for line in range(5, -1, -1) :
        if etat_p4[ind_column+line*7] == "v" :
            return line
    return None #si la colonne est pleine, on renvoi None


def replace_somthing(id_user, new_etat, coords) :
    etat_p4 = get_etat_puissance_4(id_user)
    etat_p4[coords[1]+coords[0]*7] = new_etat
    with open(CURRENT_PATH+f"/assets/daily_quest_save/{id_user}.txt", "w") as f :
        f.write(",".join(etat_p4))

def create_img_p4(id_user, result_win) :
    etat_p4 = get_etat_puissance_4(id_user)
    img_final = Image.new('RGBA', (50*7, 50*7))
    ind_pion = 0
    for nb in range(1,8) :
        img_pion = Image.open(CURRENT_PATH+f"/assets/puissance_4/nombres/{nb}.png")
        img_final.paste(img_pion, (50*(nb-1), 0))
    for y in range(6) : 
        for x in range(7) :
            img_pion = Image.open(CURRENT_PATH+f"/assets/puissance_4/{etat_p4[ind_pion]}.png")
            img_final.paste(img_pion, (50*x, 50*(y+1)))
            ind_pion+=1
    if result_win[0] not in ["eguale", "rien"] :
        img_bar_win = Image.open(CURRENT_PATH+f"/assets/puissance_4/win_bar/win_{result_win[1]}.png")
        img_final.paste(img_bar_win, (50*result_win[2][1], 50*(6-result_win[2][0])), img_bar_win)
    name_img = randint(100000, 999999)
    img_final.save(CURRENT_PATH+f"/assets/img_tamp/{name_img}.png")
    return name_img


def reset_last_ia_posed(id_user) :
    list_plateau = get_etat_puissance_4(id_user)
    list_plateau[list_plateau.index("j_last_posed")] = "j"
    with open(CURRENT_PATH+f"/assets/daily_quest_save/{id_user}.txt", "w") as f :
        f.write(",".join(list_plateau))


async def affiche_image_discord(interaction, name_img) :
    img_path = CURRENT_PATH+f"/assets/img_tamp/{name_img}.png"
    file = discord.File(img_path)
    embed = discord.Embed(title="Puissance 4")
    embed.set_image(url=f"attachment://{name_img}.png")
    await interaction.response.edit_message(embed=embed, file=file)


#-------------------partie sur l'IA----------------------#
class IA_p4 :
    def __init__(self, id_user, interaction) :
        self.id_user = id_user
        self.interaction = interaction
        self.matrice = None #matrice qui sera initialisé comme l'état actuel du jeu en liste de liste
        self.profondeur = 2 #profondeur de l'ia de recherche
        self.PIECE_1 = 1
        self.PIECE_2 = 2

    def p4_IA_find_best_move(self) :
        self.merge_plateau_to_matrice()
        _, colonne = self.minimax(
                self.matrice, self.profondeur, True)
        return colonne


    def merge_plateau_to_matrice(self) :
        plateau_list = get_etat_puissance_4(self.id_user)
        ind_case = 0
        self.matrice = np.zeros((6, 7))
        dict_redirect_usable_value = {"v" : 0, "j" : 1, "r" : 2}
        for y in range(6) :
            for x in range(7) :
                self.matrice[5-y][x] = dict_redirect_usable_value[plateau_list[ind_case]]
                ind_case+=1



    def minimax(self, board, depth, maximizingPlayer):  # utilisation du pseudo code wikipedia
        terminal_status = self.is_terminal(board)
        colonnesDisponibles = self.getColonnesDisponibles(board)
        if(depth == 0 or terminal_status):
            if(terminal_status):
                if(self.winning_moves(board, self.PIECE_1)):  # l'IA à gagné
                    return 100000000, None
                if(self.winning_moves(board, self.PIECE_2)):  # Le joueur humain adversaire à gagné
                    return -10000000, None
                else:  # Le jeux est fini sans gagnant car tableau rempli
                    return 0, None

            else:
                return self.valeurDecision(board, self.PIECE_1), None

        if(maximizingPlayer):
            try :
                colonneDecision = choice(colonnesDisponibles)
            except :
                return -10000000, None
            valeur = -INFINI
            for colonne in colonnesDisponibles:
                temporary_board = board.copy()
                rangee = self.getNextOpenRow(temporary_board, colonne)
                # simulation du coup pour la colonne donnée
                self.insererPiece(temporary_board, rangee, colonne, self.PIECE_1)
                nouvelle_valeur = self.minimax(
                    temporary_board, depth-1, False)[0]  # car minimax retourne un tuple
                if(nouvelle_valeur > valeur):
                    valeur = nouvelle_valeur
                    colonneDecision = colonne
            return valeur, colonneDecision

        else:
            try :
                colonneDecision = choice(colonnesDisponibles)
            except :
                return -10000000, None
            valeur = INFINI
            for colonne in colonnesDisponibles:
                temporary_board = board.copy()
                rangee = self.getNextOpenRow(temporary_board, colonne)
                self.insererPiece(temporary_board, rangee, colonne, self.PIECE_2)
                nouvelle_valeur = self.minimax(
                    temporary_board, depth-1, True)[0]  # car minimax retourne un tuple
                if(nouvelle_valeur < valeur):
                    valeur = nouvelle_valeur
                    colonneDecision = colonne
            return valeur, colonneDecision


    # Place une piece dans une coordonnée du tableau
    def insererPiece(self, board, row, colonne, piece):
        board[row][colonne] = piece

    # Retourne la range disponible pour une colonne donnee
    def getNextOpenRow(self, board, colonne):
        for r in range(6):
            if board[r][colonne] == 0:
                return r

    # Donne une valeur plus ou moins grande, dependant des placements avantageux des pieces placées
    def valeurDecision(self, board, piece):

        valeur = 0
        
        # preferer les cases au centre du tableau
        center_array = [int(j) for j in list(board[:, 7//2])]
        center_count = center_array.count(piece)
        valeur += center_count * 2

        # Horizontal
        for i in range(6):

            # Get les rangés du tableau de jeux dans un array plus facile de manipuler
            row_array = [int(j) for j in list(board[i, :])]
            for colonne in range(4):
                tranche = row_array[colonne:colonne+4]  # De row[0] à row[4]
                valeur += self.evalCombinaison(tranche, piece)

        # Vertical
        for i in range(7):

            col_array = [int(j) for j in list(board[:, i])]
            for rangE in range(3):
                tranche = col_array[rangE:rangE+4]
                valeur += self.evalCombinaison(tranche, piece)

        # Diagonal upwords
        for colonne in range(4):
            for rangE in range(3):
                diag_array = [board[rangE+i, colonne+i] for i in range(4)]
            valeur += self.evalCombinaison(diag_array, piece)

        # Diagonal downwords
        for colonne in range(4):
            for rangE in range(3):
                diag_array = [board[rangE+3-i, colonne+i] for i in range(4)]
            valeur += self.evalCombinaison(diag_array, piece)

        return valeur


    # Système d'évaluation d'espaces de 4 pièces appellés "tranche"
    def evalCombinaison(self, tranche, piece):
        # initialisation de la variable retourné "valeur"
        valeur = 0

        # initialisation piece_ennemis
        if(piece == 1):
            piece_ennemis = 2
        elif(piece == 2):
            piece_ennemis = 1

        # use case: puissance 4
        if (tranche.count(piece) == 4):
            valeur += 1000
        # use case: puissance 3 avec 1 case vide
        if(tranche.count(piece) == 3 and tranche.count(0) == 1):
            valeur += 80
        # use case: puissance 2 avec 2 case vides
        if(tranche.count(piece) == 2 and tranche.count(0) == 2):
            valeur += 8
        # use case: puissance 4 potentiel pour le joueur adverse
        if(tranche.count(piece_ennemis) == 3 and tranche.count(0) == 1):
            valeur -= 1000

        return valeur


    # Retourne une liste des rangés disponibles
    def getColonnesDisponibles(self, board):
        listeDisponibilite = []
        for colonne in range(7):
            if(self.isDisponible(board, colonne) == True):
                listeDisponibilite.append(colonne)
        return listeDisponibilite




    # Retourne True si la situation de jeu est "terminal"
    def is_terminal(self, board):
        return (self.winning_moves(board, self.PIECE_1) or self.winning_moves(board, self.PIECE_2) and self.isBoardFull(board))



    # Test l'ensemble des positionnements gagnant pour une piece(joueur) donne
    def winning_moves(self, board, piece):
        # Horizontal
        for c in range(4):
            for r in range(6):
                if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                    return True

        # Vertical
        for c in range(7):
            for r in range(3):
                if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                    return True

        # Diagonal upwords
        for c in range(4):
            for r in range(3):
                if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                    return True

        # Diagonal downwords
        for c in range(4):
            for r in range(3, 6):
                if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                    return True

        return False


    # Verifie si le plateau est plein
    def isBoardFull(self, board):
        boolean = True
        for i in range(7):
            boolean = self.isDisponible(board, i)
        return boolean

    # Test la disponibilite d'une coordonnee(rangée, colonne) du tableau
    def isDisponible(self, board, colonne):
        return board[5][colonne] == 0





def fin_du_jeu(board):
    board_test = np.zeros((6, 7))
    dict_redirect_usable_value = {"v" : 0, "j" : 1, "j_last_posed" : 1, "r" : 2}
    ind_case = 0
    for y in range(6) :
        for x in range(7) :
            board_test[5-y][x] = dict_redirect_usable_value[board[ind_case]]
            ind_case+=1
    result_p1 = cacl_move_gagant(board_test, 1)
    if result_p1[0] : return ["win", result_p1[1], result_p1[2]]
    result_p2 = cacl_move_gagant(board_test, 2)
    if result_p1[0] : return ["win", result_p2[1], result_p2[2]]
    elif plateau_complet(board_test) : return ["eguale", None, None]
    return ["rien", None, None]

def plateau_complet(board) :
    for line in board :
        if 0 in line : return False
    return True


# Test l'ensemble des positionnements gagnant pour une piece(joueur) donne
def cacl_move_gagant(board, piece):
    # Horizontal
    for c in range(4):
        for r in range(6):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece and piece != 0:
                return [True, "h", (r, c)]

    # Vertical
    for c in range(7):
        for r in range(3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece and piece != 0:
                return [True, "v", (r+3, c)]

    # Diagonal upwords
    for c in range(4):
        for r in range(3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece and piece != 0:
                return [True, "d_rightUp", (r+3, c)]

    # Diagonal downwords
    for c in range(4):
        for r in range(3, 6):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece and piece != 0:
                return [True, "d_leftUp", (r, c)]

    return [False, None, None]






#renvoi l'embed et effectu l'effet lorsque le gain est carte
def effet_carte_puissance_4(id_user) :
    #on get l'xp que le joueur possède
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"SELECT xp FROM Joueur WHERE id_discord_player == {id_user}")
    resultat_user_stats = curseur.fetchone()[0]
    #on lit le taux de drop en fonction du niveau du joueur
    data, lvl_column, lvl = get_data_lvl_from_csv(resultat_user_stats)
    #operations qui permet d'avoir la liste des proba selon le niveau du joueur
    proba_box = [float((piece_of_data)[:-1].replace(",", ".")) for piece_of_data in data[lvl_column.index(lvl)][1:-1]]
    #pioche d'une carte
    random_number = random()*100
    cumule_proba = 0
    for prob in proba_box :
        if prob+cumule_proba >= random_number :
            break
        cumule_proba+=prob
    index_box = proba_box.index(prob)
    #on affecte tout les changements à la BDD
    curseur.execute(f"SELECT id, nom, rarete FROM Cartes WHERE rarete == '{nom_rarete[index_box]}' ORDER BY RANDOM() LIMIT 1 ")
    carte_tiree = curseur.fetchone()
    curseur.execute(f"""UPDATE carte_possede 
                SET nombre_carte_possede = nombre_carte_possede + 1
                WHERE id_discord_player == {id_user} AND id == {carte_tiree[0]}""")
    baseDeDonnees.commit()
    baseDeDonnees.close()
    #Enfin, on affiche le résultat au joueur sur discord
    img_path = CURRENT_PATH+f'/assets/cartes/{carte_tiree[1]}.png'
    file = discord.File(img_path)
    embed = discord.Embed(title = f"""Bravo, vous avez gagné contre Pomme-bot ! 

Vous avez obtenu une nouvelle carte {carte_tiree[2]} !""")
    embed.set_image(url=f"attachment://{formatage_nom_carte(carte_tiree[1])}.png")
    return embed, file


#renvoi l'embed et effectu l'effet lorsque le gain est xp
def effet_xp_puissance_4(id_user, gain) :
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    #on cherche à avoir le niveau du joueur pour lui adapter son gain d'exp
    curseur.execute(f"SELECT * FROM Joueur WHERE id_discord_player == {id_user}")
    resultat_user_stats = curseur.fetchone()
    _, lvl_column , lvl = get_data_lvl_from_csv(resultat_user_stats[3]) 
    if gain == "xp" :
        xp = lvl_column.index(lvl)*11
        msgWinOrNot = "Bravo, vous avez gagné contre Pomme-bot !"
    else :
        msgWinOrNot = "Égalité, voici un lot de consolation"
        xp = lvl_column.index(lvl)*6
    curseur.execute(f"""UPDATE Joueur 
                SET xp = xp + {xp}
                WHERE id_discord_player == {id_user}""")
    baseDeDonnees.commit()
    baseDeDonnees.close()
    
    embed = discord.Embed(title=f"""{msgWinOrNot} 

Vous avez obtenu un gain de + {xp} exp !""")
    return embed, None

#renvoi l'embed et effectu l'effet lorsque le gain est fragment
def effet_fragment_puissance_4(id_user, nb_fragment) :
    if nb_fragment == "3" :
        msg_to_print = "Égalité, voici un lot de consolation"
    else :
        msg_to_print = "Bravo, vous avez gagné contre Pomme-bot !"
    baseDeDonnees = sqlite3.connect(db_path)
    curseur = baseDeDonnees.cursor()
    curseur.execute(f"""UPDATE Joueur 
                SET fragment = fragment + {nb_fragment}
                WHERE id_discord_player == {id_user}""")
    baseDeDonnees.commit()
    baseDeDonnees.close()    
    embed = discord.Embed(title=f"""{msg_to_print}

Vous avez obtenu un gain de + {nb_fragment} fragment{pluriel(nb_fragment)} !""")
    return embed, None


def get_nb_fragment(txt_fragment) :
    if "10" in txt_fragment :
        return txt_fragment[-2:]
    else :
        return txt_fragment[-1:]