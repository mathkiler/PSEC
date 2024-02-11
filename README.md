**PSEC projet**

This Bot discord include card opening, daily quests...

![image](https://github.com/mathkiler/PSEC/assets/98045481/3b54b512-2097-4f66-9d05-5198a87ed1c5)

**Description**

This discord bot is made for QSMP-FR discord server.
It's all about card oppening. Oppening case be release with "fragment" that user earn by complete daily quest, on speak in discord.
Daily quest are mini-game where users can earn fragment/xp/card or nothing.



**Getting Started**
**Dependencies**

This bot can work properly on differents OS like Window or Linux but you'll need to have some prerequi : 

•at least Python 3.8

•download some python librarys. You can find them in "./for_linux/install-libs-linux.sh" if you are on linux, just run this script. If not, put the line in the .sh script in a terminal.
exmple to install lib : 

    pip install discord

**Installing**

You can download the program on github and run it in your own server.
Before run the code, you'll need to create a file .env (you can place this file anywhere but place .env next to psec-bot.py is better)
In this file you have to write token_discord=put_the_token_of_your_bot_here
exemple bellow
![image](https://github.com/mathkiler/PSEC/assets/98045481/b96f637b-41b4-4dfa-b9eb-8dcf68ab13ab)

**Executing program**

Before run the program you'll need to create the database. To do this, just execute the file create_db.py. /!\ Careful execute this file will overwrite the database if it already exist /!\

    python3 create_db.py
  
Then you can run the file psec-bot.py an enjoy the bot

    python3 psec-bot.py
    
