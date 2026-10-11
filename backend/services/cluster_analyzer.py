"""
MisterBet - Cluster Analyzer (Comparazioni Affini)
Questo script analizza lo storico delle partite per calcolare l'affidabilità 
delle diverse fasce di quota (Quota Bands).
Genera un file JSON che verrà usato dall'app per mostrare i semafori.

Versione corretta:
- Rimossa fascia Outsider (non rilevante per le favorite)
- Gestione migliorata degli errori CSV
"""

import pandas as pd
import json
from pathlib import Path

# Configurazione
DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_FILE = DATA_DIR / "clusters.json"

# Definizione delle 4 Fasce di Quota (Bands)
# Rimossa "Outsider" perché non ha senso nel contesto delle favorite
QUOTA_BANDS = {
    "Favorita_Forte": (1.30, 1.60),
    "Favorita_Moderata": (1.60, 2.00),
    "Equilibrata": (2.00, 2.50),
    "Sfavorita": (2.50, 3.50),
}

def get_band(quota):
    """Determina a quale fascia appartiene una quota."""
    for band_name, (min_q, max_q) in QUOTA_BANDS.items():
        if min_q <= quota < max_q:
            return band_name
    return None

def analyze_historical_data():
    """Analizza i CSV storici e calcola le percentuali di successo per fascia."""
    print("🧠 Avvio analisi storica per Comparazioni Affini...")
    print("=" * 60)
    
    # Inizializza il dizionario per i risultati
    cluster_stats = {band: {"total": 0, "wins": 0, "hit_rate": 0.0} for band in QUOTA_BANDS.keys()}
    
    total_matches_analyzed = 0
    files_with_errors = 0
    
    # Leggi tutti i CSV
    for csv_file in DATA_DIR.glob("*.csv"):
        try:
            # on_bad_lines='skip' salta le righe malformate senza bloccare la lettura
            df = pd.read_csv(csv_file, on_bad_lines='skip')
            
            # Verifica colonne necessarie (Bet365 odds sono standard)
            required_cols = ['FTR', 'B365H', 'B365D', 'B365A']
            if not all(col in df.columns for col in required_cols):
                continue
            
            for index, row in df.iterrows():
                # Prendi le quote di chiusura (Bet365)
                odds_h = row['B365H']
                odds_d = row['B365D']
                odds_a = row['B365A']
                
                # Salta se mancano le quote
                if pd.isna(odds_h) or pd.isna(odds_d) or pd.isna(odds_a):
                    continue
                
                # Trova la quota più bassa (la favorita del bookmaker)
                min_odd = min(odds_h, odds_d, odds_a)
                
                # Determina la fascia
                band = get_band(min_odd)
                if band is None:
                    continue
                
                # Determina il risultato reale (H=Home, D=Draw, A=Away)
                result = row['FTR']
                
                # Verifica se la favorita ha vinto
                favorite_won = False
                if min_odd == odds_h and result == 'H':
                    favorite_won = True
                elif min_odd == odds_d and result == 'D':
                    favorite_won = True
                elif min_odd == odds_a and result == 'A':
                    favorite_won = True
                
                # Aggiorna le statistiche
                cluster_stats[band]["total"] += 1
                if favorite_won:
                    cluster_stats[band]["wins"] += 1
                    
                total_matches_analyzed += 1
                
        except Exception as e:
            print(f"  ️ Errore lettura {csv_file.name}: {e}")
            files_with_errors += 1
            
    # Calcola le percentuali (Hit Rate)
    print("\n📊 Risultati Analisi Comparazioni Affini:")
    print("-" * 60)
    
    for band, stats in cluster_stats.items():
        if stats["total"] > 0:
            stats["hit_rate"] = round((stats["wins"] / stats["total"]) * 100, 2)
            print(f"  {band:<20} | Partite: {stats['total']:<6} | Successi: {stats['hit_rate']}%")
        else:
            print(f"  {band:<20} | Nessun dato disponibile")
            
    print("-" * 60)
    print(f"Totale partite analizzate: {total_matches_analyzed}")
    print(f"File con errori (righe saltate): {files_with_errors}")
    
    # Salva i risultati in un file JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(cluster_stats, f, indent=4)
        
    print(f"\n💾 Report salvato in: {OUTPUT_FILE}")
    print("✅ Analisi completata! Il motore delle Comparazioni Affini è pronto.")

if __name__ == "__main__":
    analyze_historical_data()