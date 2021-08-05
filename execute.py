import os

os.chdir('c:\\discordbot')
os.system('git pull origin master')
print('Update check finished. Launching bot...')
os.system('c:\\python38\\python -O c:\\discordbot\\musicbot.py')
exit(0)
