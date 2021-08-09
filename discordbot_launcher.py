import os

os.chdir('c:\\musicbot')
os.system('ssh -T git@github.com')
os.system('git pull origin main')
print('Update check finished. Launching bot...')
os.system('c:\\python38\\python -O c:\\musicbot\\musicbot.py')
exit(0)
