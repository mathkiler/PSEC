





###################################################################################
#                                                                                 #
#                                                                                 #
#                                                                                 #
#                           ██████╗ ███████╗███████╗ ██████╗                      #
#                           ██╔══██╗██╔════╝██╔════╝██╔════╝                      #
#                           ██████╔╝███████╗█████╗  ██║                           #
#                           ██╔═══╝ ╚════██║██╔══╝  ██║                           #
#                           ██║     ███████║███████╗╚██████╗                      #
#                           ╚═╝     ╚══════╝╚══════╝ ╚═════╝                      #
#                                                                                 #
#                                                                                 #                                                                                                                                      #
#                    by : Cucurathieu, Teoad, philzAlicia, CellBrioche,           #
#                                         ento                                    #
#                                                                                 #
###################################################################################




#import des autres fichiers python
from import_et_variable import * 
from fonctions import *
from bot_event import *
from commades_discord import *
from dotenv import load_dotenv

#on load toutes la variables du .env qui est privé
load_dotenv()



if __name__ == "__main__" :
    bot.run(os.getenv('token_discord'))