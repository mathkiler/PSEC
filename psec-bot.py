





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

from scripts.global_commandes.bot_event import *
from scripts.global_commandes.commades_discord import *
from dotenv import load_dotenv

#on load toutes la variables du .env qui est privé
load_dotenv()



if __name__ == "__main__" :
    bot.run(os.getenv('token_discord'))