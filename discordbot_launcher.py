import os

os.chdir('c:\\musicbot')
os.system('ssh -T git@github.com')
os.system('git remote add origin git@github.com:user-vo2/discord-bot.git')
os.system('git pull origin master')
print('Update check finished. Launching bot...')
os.system('c:\\python38\\python -O c:\\musicbot\\musicbot.py')
exit(0)
