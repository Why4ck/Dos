import subprocess
from colorama import init, Fore, Style
init()

print(Fore.RED, 'Why4ck DOS tool installer', Style.RESET_ALL, sep='')
subprocess.run(['pip', 'install', '.'])
print(Fore.RED, 'Install complete', Style.RESET_ALL, sep='')
print(Fore.GREEN, 'In cmd use:\nwhy4ck dos --url SITE --session HOW MANY SESSIONS --concurrency REQUESTS PER REPORT --size HOW MANT KB SIZE 1 REQUETS\nExample: why4ck dos --url "http://localhost" --session 10 --concurrency 10 --size 5', Style.RESET_ALL, sep='')