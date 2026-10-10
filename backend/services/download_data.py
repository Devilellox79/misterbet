"""
MisterBet - Download Dati Storici
Questo script scarica i file CSV con i risultati e le quote storiche da football-data.co.uk
"""

import os
import requests
from pathlib import Path

# Configurazione
BASE_URL = "https://www.football-data.co.uk/mmz4281"
DATA_DIR = Path(__file__).parent.parent / "data"

# Lista dei campionati e dei file da scaricare
# Formato: {codice_campionato: nome_campionato}
LEAGUES = {
    # Top Europa
    "E0": "Premier League",
    "E1": "Championship",  # Serie B inglese
    "SP1": "LaLiga",
    "SP2": "LaLiga 2",
    "I1": "Serie A",
    "I2": "Serie B",
    "D1": "Bundesliga",
    "D2": "Bundesliga 2",
    "F1": "Ligue 1",
    "F2": "Ligue 2",
    
    # Altri campionati europei
    "N1": "Eredivisie",
    "P1": "Primeira Liga",
    "T1": "Super Lig",
    "G1": "Super League Greece",
    "SW1": "Super League Switzerland",
    
    # Coppe europee (se disponibili)
    # Nota: le coppe spesso non hanno dati completi su football-data.co.uk
}

# Anni da scaricare (stagioni complete)
# Formato: "2324" significa stagione 2023/2024
SEASONS = [
    "2324",  # 2023/2024
    "2223",  # 2022/2023
    "2122",  # 2021/2022
    "2021",  # 2020/2021
    "1920",  # 2019/2020
]


def download_file(url: str, save_path: Path) -> bool:
    """
    Scarica un file da un URL e lo salva nel percorso specificato.
    
    Args:
        url: L'URL del file da scaricare
        save_path: Il percorso dove salvare il file
    
    Returns:
        True se il download è riuscito, False altrimenti
    """
    try:
        print(f"📥 Scaricamento: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Errore se il download fallisce
        
        # Salva il file
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Salvato: {save_path.name}")
        return True
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore download {url}: {e}")
        return False


def download_all_data():
    """
    Scarica tutti i file CSV per tutti i campionati e le stagioni configurate.
    """
    print("🚀 Avvio download dati storici da football-data.co.uk")
    print("=" * 60)
    
    # Crea la cartella data se non esiste
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    total_files = 0
    successful_downloads = 0
    
    # Scarica i file per ogni campionato e stagione
    for league_code, league_name in LEAGUES.items():
        print(f"\n🏆 {league_name} ({league_code})")
        
        for season in SEASONS:
            # Costruisci l'URL
            # Esempio: https://www.football-data.co.uk/mmz4281/2324/E0.csv
            url = f"{BASE_URL}/{season}/{league_code}.csv"
            
            # Costruisci il percorso di salvataggio
            # Esempio: backend/data/E0_2324.csv
            filename = f"{league_code}_{season}.csv"
            save_path = DATA_DIR / filename
            
            total_files += 1
            
            # Scarica il file
            if download_file(url, save_path):
                successful_downloads += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Download completato!")
    print(f"   File totali tentati: {total_files}")
    print(f"   Download riusciti: {successful_downloads}")
    print(f"   Download falliti: {total_files - successful_downloads}")
    print(f"   Dati salvati in: {DATA_DIR}")


if __name__ == "__main__":
    download_all_data()