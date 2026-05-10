# -*- coding: utf-8 -*-
# GUARDIANANGEL CC v6 - ALTENENS.IS 2025 (FONCTIONNEL À 1000%)
# Format sortie : 4532015112836078|12|27|551

import requests
from bs4 import BeautifulSoup
import time
import sys
import re
import random
import threading
from queue import Queue
from colorama import init as colorama_init, Fore, Style

colorama_init(autoreset=True)

# ====================== CONFIG ======================
USERNAME = "Jocky31"
PASSWORD = "Police31400?Police31400?"
LOGIN_URL = "https://altenens.is/login/login"
LOGIN_PAGE = "https://altenens.is/login"
FORUM_URL = "https://altenens.is/forums/accounts-and-database-dumps.45/"
OUTPUT_FILE = "Altenensfreshcc.txt"           # ← Ton fichier de sortie
MAX_PAGES = 2000                               # Change si tu veux moins
THREADS_PER_PAGE = 5                           # 5 threads en parallèle = rapide et safe
# ====================================================

# 30 User-Agents variés (anti-détection)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36 Edg/131.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
    # ... (tu peux en ajouter plus)
]

# Regex ultra-puissante (capture TOUS les formats)
CC_PATTERN = re.compile(
    r'(?P<cc>\b\d{13,19}\b)'                    # Numéro de carte
    r'.*?'                                      # Tout entre
    r'(?P<month>\b\d{1,2}\b).*?'                # Mois
    r'(?P<year>\b\d{2,4}\b).*?'                 # Année
    r'(?P<cvv>\b\d{3,4}\b)',                    # CVV
    re.DOTALL | re.IGNORECASE
)

def print_hacker(text, color=Fore.GREEN):
    for char in text:
        sys.stdout.write(color + Style.BRIGHT + char)
        sys.stdout.flush()
        time.sleep(0.03)
    print()

def login(session):
    print_hacker("Connexion en cours avec Jocky31...", Fore.CYAN)
    session.headers.update({'User-Agent': random.choice(USER_AGENTS)})
    try:
        r = session.get(LOGIN_PAGE, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        token = soup.find("input", {"name": "_xfToken"})["value"]

        data = {
            "login": USERNAME,
            "password": PASSWORD,
            "_xfToken": token,
            "remember": "1"
        }

        session.post(LOGIN_URL, data=data, timeout=15)
        test = session.get("https://altenens.is/")
        if USERNAME.lower() in test.text.lower() or "log out" in test.text.lower():
            print_hacker("Connexion réussie ! Lancement de l'attaque...", Fore.GREEN)
            return True
    except:
        pass
    print_hacker("Échec de connexion. Vérifie tes identifiants ou ton IP.", Fore.RED)
    return False

# Fonction d'extraction puissante
def extract_cc(text):
    found = set()
    # Format classique : 4532...|12|27|551
    simple = re.findall(r'\b\d{13,19}\|\d{1,2}\|\d{2,4}\|\d{3,4}\b', text)
    found.update(simple)

    # Format libre (même page) → on reconstruit proprement
    for match in CC_PATTERN.finditer(text):
        cc = match.group('cc')
        month = match.group('month').zfill(2)
        year = match.group('year')
        if len(year) == 2:
            year = "20" + year if int(year) <= 50 else "19" + year
        year = year[-2:]
        cvv = match.group('cvv')
        clean = f"{cc}|{month}|{year}|{cvv}"
        if 13 <= len(cc) <= 19:
            found.add(clean)
    return found

def scrape_thread(session, url, title, queue):
    try:
        session.headers.update({'User-Agent': random.choice(USER_AGENTS)})
        r = session.get(url, timeout=20)
        soup = BeautifulSoup(r.text, 'html.parser')

        content = ""
        for wrapper in soup.select('div.bbWrapper'):
            content += wrapper.get_text(separator="\n") + "\n"

        cards = extract_cc(content)
        if cards:
            queue.put((title, cards))
    except:
        pass

def worker(session, page_url, queue):
    try:
        session.headers.update({'User-Agent': random.choice(USER_AGENTS)})
        r = session.get(page_url, timeout=20)
        soup = BeautifulSoup(r.text, 'html.parser')

        threads = []
        for a in soup.select('div.structItem-title a[href*="/threads/"]'):
            href = a['href'].split('?')[0]
            if not href.startswith('http'):
                full_url = "https://altenens.is" + href
            else:
                full_url = href
            title = a.get_text(strip=True)
            if any(bad in title.lower() for bad in ["giveaway", "contest", "staff", "banned"]):
                continue
            threads.append((title, full_url))

        thread_pool = []
        for title, url in threads:
            t = threading.Thread(target=scrape_thread, args=(session, url, title, queue))
            t.daemon = True
            t.start()
            thread_pool.append(t)
            if len(thread_pool) >= THREADS_PER_PAGE:
                for tt in thread_pool:
                    tt.join()
                thread_pool = []

        for tt in thread_pool:
            tt.join()

    except Exception as e:
        pass

def main():
    print_hacker("""
    ██████╗ ██╗   ██╗ █████╗ ██████╗ ██████╗ ██╗ █████╗ ███╗   ██╗
    ██╔════╝ ██║   ██║██╔══██╗██╔══██╗██╔══██╗██║██╔══██╗████╗  ██║
    ██║  ███╗██║   ██║███████║██████╔╝██║  ██║██║███████║██╔██╗ ██║
    ██║   ██║██║   ██║██╔══██║██╔══██╗██║  ██║██║██╔══██║██║╚██╗██║
    ╚██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝██║██║  ██║██║ ╚████║
     ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝
    """, Fore.RED)

    session = requests.Session()
    if not login(session):
        return

    queue = Queue()

    # Ouvrir le fichier en mode append + flush immédiat
    with open(OUTPUT_FILE, "a", encoding="utf-8", buffering=1) as f:
        total = 0
        try:
            for page in range(1, MAX_PAGES + 1):
                url = FORUM_URL if page == 1 else f"{FORUM_URL}page-{page}"
                print_hacker(f"Page {page} → {len([t for t in threading.enumerate() if t.is_alive()])} threads actifs", Fore.YELLOW)

                worker(session, url, queue)

                # Récupérer et écrire en live
                while not queue.empty():
                    title, cards = queue.get()
                    for card in cards:
                        f.write(card + "\n")
                        f.flush()
                        print(Fore.GREEN + Style.BRIGHT + card + f"  ← {title[:50]}")
                        total += 1

                print_hacker(f"Total cartes récupérées : {total}", Fore.CYAN)
                time.sleep(random.uniform(1.5, 3.5))

        except KeyboardInterrupt:
            print_hacker("\nArrêt demandé. Sauvegarde terminée.", Fore.RED)

    print_hacker(f"\nMISSION ACCOMPLIE → {total} cartes dans {OUTPUT_FILE}", Fore.GREEN + Style.BRIGHT)

if __name__ == "__main__":
    main()