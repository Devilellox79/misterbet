"""
MisterBet - Fetch Live Odds
Questo script scarica le partite e le quote di oggi dai 5 campionati principali
usando The Odds API e le salva in un file JSON per l'elaborazione.
"""

import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# Configurazione
API_KEY = os.getenv("ODDS_API_KEY")
BASE_URL = "https://api.the-odds-api.com/v4/sports"
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "matches_today.json"

# Campionati principali da monitorare (codici ufficiali di The Odds API)
LEAGUES = [
    "soccer_italy_serie_a",
    "soccer_epl",          # Premier League
    "soccer_spain_la_liga",
    "soccer_germany_bundesliga",
    "soccer_france_ligue_one"
]

def fetch_odds_for_league(league_key):
    """Scarica le quote per un singolo campionato."""
    url = f"{BASE_URL}/{league_key}/odds/"
    params = {
        "regions": "eu",           # Bookmaker europei
        "markets": "h2h",          # Mercato 1X2 (Head to Head)
        "oddsFormat": "decimal",   # Formato decimale (es. 1.85)
        "apiKey": API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Errore nel download per {league_key}: {e}")
        return []

def process_and_save_matches():
    """Elabora i dati grezzi e li salva in un formato pulito per MisterBet."""
    print("📡 Avvio download quote live da The Odds API...")
    print("=" * 60)
    
    if not API_KEY or API_KEY == "la_tua_chiave_api_reale_qui":
        print("❌ ERRORE: API Key non trovata nel file .env!")
        print("   Controlla di aver inserito la chiave corretta nel file .env")
        return
    
    all_matches = []
    
    for league in LEAGUES:
        print(f"  🔍 Controllo: {league}...")
        raw_data = fetch_odds_for_league(league)
        
        for event in raw_data:
            # Prendiamo il primo bookmaker disponibile (spesso è bet365 o simile)
            bookmakers = event.get("bookmakers", [])
            if not bookmakers:
                continue
                
            # Cerchiamo bet365, altrimenti prendiamo il primo disponibile
            target_bookie = next((b for b in bookmakers if b["key"] == "bet365"), bookmakers[0])
            
            # Estrai le quote 1X2
            markets = target_bookie.get("markets", [])
            h2h_market = next((m for m in markets if m["key"] == "h2h"), None)
            
            if not h2h_market or len(h2h_market["outcomes"]) < 3:
                continue
                
            outcomes = {out["name"]: out["price"] for out in h2h_market["outcomes"]}
            
            # Mappatura dei nomi delle squadre (a volte l'API usa nomi leggermente diversi)
            home_team = event["home_team"]
            away_team = event["away_team"]
            
            # Verifica che ci siano tutte e 3 le quote
            if home_team in outcomes and away_team in outcomes and "Draw" in outcomes:
                match_data = {
                    "league": league,
                    "home_team": home_team,
                    "away_team": away_team,
                    "commence_time": event["commence_time"],
                    "odds": {
                        "1": outcomes[home_team],
                        "X": outcomes["Draw"],
                        "2": outcomes[away_team]
                    }
                }
                all_matches.append(match_data)
                
        print(f"  ✅ Trovate {len([m for m in all_matches if m['league'] == league])} partite per {league}")
    
    # Salva i dati
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_matches, f, indent=4, ensure_ascii=False)
        
    print("=" * 60)
    print(f"💾 Salvate {len(all_matches)} partite totali in: {OUTPUT_FILE}")
    print("✅ Download quote live completato!")

if __name__ == "__main__":
    process_and_save_matches()