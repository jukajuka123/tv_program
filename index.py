import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from colorama import Fore, init
import os

def info(recenica):
    print("[INFO] "+recenica)


def movies123NapuniNizLinkova(NizLinkovaiImena):
    info("Pretrazujem 123Movies")
    Sredjena = ""
    for rijec in pretrazi.split():
        Sredjena = Sredjena + "+" + rijec
    Sredjena = Sredjena[1:]
    r = requests.get("https://ww8.123moviesfree.net/searching?q=" + Sredjena + "&limit=40&offset=0")
    podaci = json.loads(str(r.text))
    for film in podaci["data"]:
        NizLinkovaiImena.append({
            "naslov": f"{film["t"]} (123moviesfree.net)",
            "link": f"{film["s"]}"
        })

def movies123PokreniFilm(vrsta,broj):

    if(vrsta == "film"):
        LinkIzabranogFilma = "https://ww8.123moviesfree.net/movie/"+NizLinkovaiImena[broj]["link"]+"/"
    elif(vrsta == "serija"):
        LinkIzabranogFilma = "https://ww8.123moviesfree.net/season/"+NizLinkovaiImena[broj]["link"]+"/"

    # 1. Podešavanje opcija da browser bude nevidljiv
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ključna linija za "bez browsera"
    chrome_options.add_argument("--disable-gpu") 

    # 2. Pokretanje drajvera
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 3. Otvaranje linka
        driver.get(LinkIzabranogFilma)

        # 4. Izvršavanje JS koda direktno u konzoli stranice
        # Primer: Menjamo naslov stranice ili ispisujemo nešto
        script = "console.log(\"document.getElementById('play-now').click();\"); document.getElementById('play-now').click(); return document.title;"
        result = driver.execute_script(script)

        info("Pokrecem film")

        time.sleep(2)

        if (vrsta == "serija"):
            script = "return document.getElementById('eps-list').children.length;"
            result = driver.execute_script(script)
            for i in range(1,int(result)+1):
                print("epizoda " + str(i))
            epizoda = input("Unesite epizodu za otvoriti: ")
            script = f"console.log(\"document.getElementById('ep-{epizoda}').click();\"); document.getElementById('ep-{epizoda}').click(); return document.title;"
            result = driver.execute_script(script)
            info("Otvaram epizodu")
            
        elif(vrsta == "film"):
            script = "console.log(\"document.getElementById('playo-now').click();\"); document.getElementById('playo-now').click(); return document.title;"
            result = driver.execute_script(script)
            info("Pokrecem player")

        # 1. Dajemo sajtu 3 sekunde da JS odradi svoje i popuni src
        time.sleep(5) 

        # 2. JS koji traži src unutar elementa 'playit' ili u samom elementu
        script = """
            var el = document.getElementById('playit');
            if (!el) return "Element 'playit' nije nađen";
            
            // Ako je sam 'playit' iframe, uzmi njegov src
            if (el.tagName === 'IFRAME') return el.src;
            
            // Ako je 'playit' div, nađi iframe unutar njega
            var frame = el.querySelector('iframe');
            if (frame) return frame.src;
            
            return "Iframe nije nađen unutar playit elementa";
        """

        video_izvor = driver.execute_script(script)
        print(f"Pronađeni SRC: {video_izvor}")
        #odavde ide funkcija neka koja salje televizoru pomocu os.system() adb liniju za otvaranje linka
        LinkIdeTvu(video_izvor)

    finally:
        driver.quit()


def YFlixNapuniNizLinkova(NizLinkovaiImena):
    info("Pretrazujem YFlix")
    Sredjena = ""
    for rijec in pretrazi.split():
        Sredjena = Sredjena + "+" + rijec
    Sredjena = Sredjena[1:]
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ključna linija za "bez browsera"
    chrome_options.add_argument("--disable-gpu") 
    link = "https://yflix.to/browser?keyword="+Sredjena

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(link)

    time.sleep(5)

    script = """
        return Array.from(document.getElementsByClassName('title')).map(el => {
            return {
                'ime': el.innerText,
                'link': el.href
            };
        });
        """
    result = driver.execute_script(script)
    for film in result:
        NizLinkovaiImena.append({
            "naslov": str(film['ime']) + " (YFLIX - no ads)",
            "link": film['link']
        })

def PokreniYFlixFilm(broj):
    LinkIzabranogFilma = NizLinkovaiImena[broj]["link"]
    LinkIdeTvu(LinkIzabranogFilma)


def solarmovieNapuniNizLinkova(NizLinkovaiImena):
    info("Pretrazujem SolarMovie")
    Sredjena = ""
    for rijec in pretrazi.split():
        Sredjena = Sredjena + "+" + rijec
    Sredjena = Sredjena[1:]
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ključna linija za "bez browsera"
    chrome_options.add_argument("--disable-gpu") 
    link = "https://www3.solarmovie.cr/search/"+Sredjena

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(link)

    script = """
    return (function() {
        const elements = document.querySelectorAll('.ml-item');
        return Array.from(elements).map(item => {
            const mask = item.querySelector('.ml-mask');
            const infoH2 = item.querySelector('.mli-info h2');
            return {
                'naslov': infoH2 ? infoH2.innerText.trim() : 'Nema naslova',
                'link': mask ? mask.href : 'Nema linka'
            };
        });
    })();
    """
    result = driver.execute_script(script)
    for film in result:
        NizLinkovaiImena.append({
            "naslov": str(film['naslov']) + " (SolarMovie - los za serije)",
            "link": film['link']
        })

def PokreniSolarMovie(broj):
    LinkIzabranogFilma = NizLinkovaiImena[broj]["link"]
    html_kod = requests.get(LinkIzabranogFilma+"watching").text

    soup = BeautifulSoup(html_kod, 'html.parser')

    iframe = soup.find('iframe', id='iframe-embed')

    if iframe and iframe.has_attr('src'):
        video_src = iframe['src']
        LinkIdeTvu(video_src)
    else:
        print("Iframe sa tim ID-jem nije pronađen u HTML kodu.")
    


def LinkIdeTvu(link):
    ip = input("Ip adresa tva: ")
    os.system("adb connect "+ip)
    info("Prihvatite povezivanje ako vec niste")
    os.system("adb shell am start -a android.intent.action.VIEW -d \""+link+"\" com.truefedex.tvbro")
    info("Link proslijedjen tvu!")




#Inputi i slicno
brojac = 0
NizLinkovaiImena = []
filmserija = input("Pretrazujemo film/serija/youtube: ")
if(filmserija == "youtube"):
    search = input("Search youtube: ")
    Sredjena = ""
    for rijec in search.split():
        Sredjena = Sredjena + "+" + rijec
    Sredjena = Sredjena[1:]
    LinkIdeTvu("https://www.youtube.com/results?search_query="+Sredjena)
    exit()


pretrazi = input("Ime filma/serije: ")
movies123NapuniNizLinkova(NizLinkovaiImena)
YFlixNapuniNizLinkova(NizLinkovaiImena)
solarmovieNapuniNizLinkova(NizLinkovaiImena)
init(autoreset=True)

for i in range(0, len(NizLinkovaiImena)):
    if("123movies" in NizLinkovaiImena[i]["naslov"]):
        print(Fore.BLUE + str(i) + ". " + NizLinkovaiImena[i]["naslov"])
    elif("YFLIX" in NizLinkovaiImena[i]["naslov"]):
        print(Fore.GREEN + str(i) + ". " + NizLinkovaiImena[i]["naslov"])
    elif("SolarMovie" in NizLinkovaiImena[i]["naslov"]):
        print(Fore.CYAN + str(i) + ". " + NizLinkovaiImena[i]["naslov"])

broj = int(input("Unesite broj filma: "))

if(filmserija == "Film" or filmserija == "film"):
    if("123movies" in NizLinkovaiImena[broj]["naslov"]):
        movies123PokreniFilm(filmserija, broj)
    elif("YFLIX" in NizLinkovaiImena[broj]["naslov"]):
        PokreniYFlixFilm(broj)
    elif("SolarMovie") in NizLinkovaiImena[broj]["naslov"]:
        PokreniSolarMovie(broj)

elif(filmserija == "Serija" or filmserija == "serija"):
    if("123movies" in NizLinkovaiImena[broj]["naslov"]):
        movies123PokreniFilm(filmserija, broj)
    elif("YFLIX" in NizLinkovaiImena[broj]["naslov"]):
        PokreniYFlixFilm(broj)

