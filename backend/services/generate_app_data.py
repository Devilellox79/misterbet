"""
MisterBet - Master Orchestrator
Questo script unisce tutto:
1. Carica e addestra il modello matematico sui dati storici
2. Legge le partite di oggi (matches_today.json)
3. Calcola le probabilità e il "Gap di Valore"
4. Assegna l'affidabilità del Cluster storico
5. Genera il file finale (app_data.json) pronto per il Frontend
"""

import json
import sys
from pathlib import Path

# Aggiunge la cartella 'models' al percorso di Python per poter importare il modello
sys.path.append(str(Path(__file__).parent.parent))
from models.dixon_coles import DixonColesModel

# Percorsi dei file
DATA_DIR = Path(__file__).parent.parent / "data"
MATCHES_FILE = DATA_DIR / "matches_today.json"
CLUSTERS_FILE = DATA_DIR / "clusters.json"
OUTPUT_FILE = DATA_DIR / "app_data.json"

# Definizione delle fasce di quota (deve corrispondere a cluster_analyzer.py)
QUOTA_BANDS = {
    "Favorita_Forte": (1.30, 1.60),
    "Favorita_Moderata": (1.60, 2.00),
    "Equilibrata": (2.00, 2.50),
    "Sfavorita": (2.50, 3.50),
}

def get_cluster_info(odds, clusters_data):
    """Determina la fascia di quota e restituisce le statistiche del cluster."""
    for band_name, stats in clusters_data.items():
        min_q, max_q = QUOTA_BANDS[band_name]
        if min_q <= odds < max_q:
            return {
                "band": band_name,
                "hit_rate": stats["hit_rate"],
                "total_matches": stats["total"]
            }
    return {"band": "Fuori Fascia", "hit_rate": 0, "total_matches": 0}

def generate_final_data():
    """Funzione principale che orchestra tutto il processo."""
    print(" Caricamento modello e dati storici...")
    
    # 1. Inizializza e addestra il modello
    model = DixonColesModel()
    matches_df = model.load_data(DATA_DIR)
    model.fit(matches_df)
    print("✅ Modello pronto.")
    
    # 2. Carica i cluster storici
    with open(CLUSTERS_FILE, 'r', encoding='utf-8') as f:
        clusters_data = json.load(f)
        
    # 3. Carica le partite di oggi
    if not MATCHES_FILE.exists():
        print("❌ ERRORE: File matches_today.json non trovato. Esegui prima fetch_live_odds.py")
        return
        
    with open(MATCHES_FILE, 'r', encoding='utf-8') as f:
        today_matches = json.load(f)
        
    print(f"📡 Elaborazione delle {len(today_matches)} partite di oggi...")
    print("=" * 60)
    
    processed_matches = []
    skipped_no_value = 0
    skipped_errors = 0
    
    # 4. Processa ogni partita
    for match in today_matches:
        try:
            home_team = match["home_team"]
            away_team = match["away_team"]
            
            # Calcola le probabilità con il modello
            probs = model.predict_match(home_team, away_team)
            
            # Trova il miglior "Gap di Valore" tra 1, X e 2
            max_gap = 0.0
            best_bet = None
            best_model_prob = 0.0
            best_book_odd = 0.0
            
            # Controlla segno 1
            gap_1 = probs["1X2"]["1"] - (1 / match["odds"]["1"])
            if gap_1 > max_gap:
                max_gap = gap_1
                best_bet = "1"
                best_model_prob = probs["1X2"]["1"]
                best_book_odd = match["odds"]["1"]
                
            # Controlla segno X
            gap_x = probs["1X2"]["X"] - (1 / match["odds"]["X"])
            if gap_x > max_gap:
                max_gap = gap_x
                best_bet = "X"
                best_model_prob = probs["1X2"]["X"]
                best_book_odd = match["odds"]["X"]
                
            # Controlla segno 2
            gap_2 = probs["1X2"]["2"] - (1 / match["odds"]["2"])
            if gap_2 > max_gap:
                max_gap = gap_2
                best_bet = "2"
                best_model_prob = probs["1X2"]["2"]
                best_book_odd = match["odds"]["2"]
                
            # Se c'è un valore positivo significativo (gap > 3%)
            if max_gap > 0.03:
                book_prob = 1 / best_book_odd
                cluster_info = get_cluster_info(best_book_odd, clusters_data)
                
                # Formatta la data in modo leggibile
                time_str = match["commence_time"].replace("T", " ").split(".")[0]
                
                processed_matches.append({
                    "league": match["league"].replace("soccer_", "").replace("_", " ").title(),
                    "home_team": home_team,
                    "away_team": away_team,
                    "time": time_str,
                    "best_bet": best_bet,
                    "model_prob": round(best_model_prob * 100, 1),
                    "bookmaker_prob": round(book_prob * 100, 1),
                    "value_gap": round(max_gap * 100, 1),
                    "bookmaker_odd": round(best_book_odd, 2),
                    "cluster": cluster_info
                })
            else:
                skipped_no_value += 1
                
        except Exception as e:
            # Se il nome della squadra non corrisponde al database storico, la saltiamo
            skipped_errors += 1
            
    # 5. Ordina le partite per "Value Gap" decrescente (le migliori opportunità per prime)
    processed_matches.sort(key=lambda x: x["value_gap"], reverse=True)
    
    # 6. Salva il file finale
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(processed_matches, f, indent=4, ensure_ascii=False)
        
    print("=" * 60)
    print(f"📊 Partite processate con successo: {len(processed_matches)}")
    print(f"️  Saltate (nessun valore > 3%): {skipped_no_value}")
    print(f"❌ Saltate (errore nomi squadre): {skipped_errors}")
    print(f" File pronto per il Frontend: {OUTPUT_FILE}")
    print("✅ MisterBet Backend è COMPLETO e pronto!")

if __name__ == "__main__":
    generate_final_data()