"""
MisterBet - Modello Independent Poisson
Questo modello calcola le probabilità dei risultati delle partite di calcio
usando la distribuzione di Poisson con parametri di attacco e difesa
calcolati dalle medie storiche dei gol.

Approccio: Independent Poisson Model (semplice, stabile, efficace)
- Attacco squadra = gol fatti in casa / media gol casa del campionato
- Difesa squadra = gol subiti in trasferta / media gol trasferta del campionato
- Vantaggio casa = log(media gol casa / media gol trasferta)
"""

import pandas as pd
import numpy as np
from scipy.stats import poisson
from pathlib import Path
from typing import Dict


class DixonColesModel:
    """
    Modello Independent Poisson per prevedere i risultati delle partite di calcio.
    """
    
    def __init__(self):
        """
        Inizializza il modello con parametri vuoti.
        """
        self.teams = []  # Lista delle squadre
        self.attack_params = {}  # Parametri di attacco per ogni squadra (in scala logaritmica)
        self.defense_params = {}  # Parametri di difesa per ogni squadra (in scala logaritmica)
        self.home_advantage = 0.0  # Vantaggio casa (in scala logaritmica)
        self.rho = 0.0  # Non usato in questo modello (mantenuto per compatibilità)
        self.is_fitted = False  # Flag per sapere se il modello è stato addestrato
    
    def load_data(self, data_dir: Path) -> pd.DataFrame:
        """
        Carica tutti i file CSV dalla cartella data e li unisce in un unico DataFrame.
        Filtra solo i campionati principali per ridurre il numero di squadre.
        
        Args:
            data_dir: Percorso alla cartella contenente i file CSV
        
        Returns:
            DataFrame con tutte le partite
        """
        print(f"📂 Caricamento dati da: {data_dir}")
        
        # Lista dei codici dei campionati principali da includere (solo Top 5)
        LEAGUES_TO_INCLUDE = [
            'E0',      # Premier League
            'SP1',     # LaLiga
            'I1',      # Serie A
            'D1',      # Bundesliga
            'F1',      # Ligue 1
        ]
        
        all_matches = []
        
        # Leggi tutti i file CSV nella cartella
        for csv_file in data_dir.glob("*.csv"):
            try:
                # Estrai il codice del campionato dal nome del file
                league_code = csv_file.stem.split('_')[0]  # Es. "E0" da "E0_2324.csv"
                
                # Salta i campionati non nella lista
                if league_code not in LEAGUES_TO_INCLUDE:
                    print(f"  ⏭️  Saltato: {csv_file.name} (campionato non incluso)")
                    continue
                
                df = pd.read_csv(csv_file)
                
                # Verifica che ci siano le colonne necessarie
                required_cols = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']
                if all(col in df.columns for col in required_cols):
                    # Aggiungi una colonna con il campionato
                    df['League'] = league_code
                    
                    all_matches.append(df)
                    print(f"  ✅ Caricato: {csv_file.name} ({len(df)} partite)")
                else:
                    print(f"  ⚠️  Saltato: {csv_file.name} (colonne mancanti)")
            
            except Exception as e:
                print(f"  ❌ Errore lettura {csv_file.name}: {e}")
        
        if not all_matches:
            raise ValueError("Nessun file CSV valido trovato!")
        
        # Unisci tutti i DataFrame
        combined_df = pd.concat(all_matches, ignore_index=True)
        
        # Rimuovi partite con dati mancanti
        combined_df = combined_df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR'])
        
        print(f"\n📊 Totale partite caricate: {len(combined_df)}")
        print(f"🏆 Squadre uniche: {combined_df['HomeTeam'].nunique() + combined_df['AwayTeam'].nunique()}")
        
        return combined_df
    
    def fit(self, matches_df: pd.DataFrame):
        """
        Addestra il modello sui dati storici usando il metodo Independent Poisson.
        Calcola attacco e difesa di ogni squadra basandosi sulle medie dei gol.
        
        Args:
            matches_df: DataFrame con le partite storiche
        """
        print("\n🧠 Addestramento modello Independent Poisson...")
        
        # Estrai le squadre uniche
        home_teams = matches_df['HomeTeam'].unique()
        away_teams = matches_df['AwayTeam'].unique()
        self.teams = sorted(list(set(home_teams) | set(away_teams)))
        
        num_teams = len(self.teams)
        print(f"  Squadre trovate: {num_teams}")
        
        # Calcola le medie globali
        avg_home_goals = matches_df['FTHG'].mean()
        avg_away_goals = matches_df['FTAG'].mean()
        
        print(f"  Media gol casa: {avg_home_goals:.2f}")
        print(f"  Media gol trasferta: {avg_away_goals:.2f}")
        
        # Calcola attacco e difesa per ogni squadra (in scala logaritmica)
        # Usiamo il logaritmo per coerenza con la formula exp(attack + defense + home_adv)
        self.attack_params = {}
        self.defense_params = {}
        
        for team in self.teams:
            # Filtra le partite dove questa squadra gioca in casa
            home_matches = matches_df[matches_df['HomeTeam'] == team]
            # Filtra le partite dove questa squadra gioca in trasferta
            away_matches = matches_df[matches_df['AwayTeam'] == team]
            
            # Attacco = log(gol fatti in casa / media gol casa)
            if len(home_matches) > 0:
                avg_goals_scored_home = home_matches['FTHG'].mean()
                self.attack_params[team] = np.log(avg_goals_scored_home / avg_home_goals)
            else:
                self.attack_params[team] = 0.0  # Valore neutro (log(1) = 0)
            
            # Difesa = log(gol subiti in trasferta / media gol trasferta)
            if len(away_matches) > 0:
                avg_goals_conceded_away = away_matches['FTAG'].mean()
                self.defense_params[team] = np.log(avg_goals_conceded_away / avg_away_goals)
            else:
                self.defense_params[team] = 0.0  # Valore neutro (log(1) = 0)
        
        # Calcola il vantaggio casa (in scala logaritmica)
        self.home_advantage = np.log(avg_home_goals / avg_away_goals)
        
        # Rho non serve in questo modello semplificato
        self.rho = 0.0
        
        self.is_fitted = True
        
        print("  ✅ Modello addestrato con successo!")
        print(f"   Vantaggio casa: {self.home_advantage:.3f}")
        
        # Mostra le top 5 squadre per attacco e difesa
        top_attack = sorted(self.attack_params.items(), key=lambda x: x[1], reverse=True)[:5]
        top_defense = sorted(self.defense_params.items(), key=lambda x: x[1])[:5]
        
        print(f"\n  ⚽ Top 5 attacchi:")
        for team, param in top_attack:
            print(f"     {team}: {param:.3f}")
        
        print(f"\n  🛡️  Top 5 difese:")
        for team, param in top_defense:
            print(f"     {team}: {param:.3f}")
    
    def predict_score_probs(self, home_team: str, away_team: str, max_goals: int = 7) -> np.ndarray:
        """
        Calcola la matrice delle probabilità per ogni possibile risultato.
        
        Args:
            home_team: Nome della squadra di casa
            away_team: Nome della squadra in trasferta
            max_goals: Massimo numero di gol da considerare (default 7)
        
        Returns:
            Matrice 2D dove [i, j] = probabilità che casa segni i gol e trasferta segni j gol
        """
        if not self.is_fitted:
            raise RuntimeError("Modello non addestrato! Chiama prima fit().")
        
        if home_team not in self.attack_params or away_team not in self.attack_params:
            raise ValueError(f"Una o entrambe le squadre non trovate: {home_team}, {away_team}")
        
        # Calcola i gol attesi (usando exp perché i parametri sono in scala logaritmica)
        lambda_home = np.exp(
            self.attack_params[home_team] +
            self.defense_params[away_team] +
            self.home_advantage
        )
        lambda_away = np.exp(
            self.attack_params[away_team] +
            self.defense_params[home_team]
        )
        
        # Crea la matrice delle probabilità
        prob_matrix = np.zeros((max_goals + 1, max_goals + 1))
        
        for i in range(max_goals + 1):
            for j in range(max_goals + 1):
                prob_matrix[i, j] = poisson.pmf(i, lambda_home) * poisson.pmf(j, lambda_away)
        
        # Normalizza per assicurarsi che la somma sia 1
        prob_matrix /= prob_matrix.sum()
        
        return prob_matrix
    
    def predict_match(self, home_team: str, away_team: str) -> Dict:
        """
        Calcola tutte le probabilità per una partita.
        
        Args:
            home_team: Nome della squadra di casa
            away_team: Nome della squadra in trasferta
        
        Returns:
            Dizionario con tutte le probabilità
        """
        prob_matrix = self.predict_score_probs(home_team, away_team)
        
        # Probabilità 1X2
        prob_home_win = prob_matrix[np.tril_indices(8, -1)].sum()  # Casa segna più gol
        prob_draw = np.trace(prob_matrix)  # Pareggio
        prob_away_win = prob_matrix[np.triu_indices(8, 1)].sum()  # Trasferta segna più gol
        
        # Over/Under 2.5
        total_goals = np.arange(8).reshape(-1, 1) + np.arange(8).reshape(1, -1)
        prob_over_25 = prob_matrix[total_goals > 2.5].sum()
        prob_under_25 = prob_matrix[total_goals <= 2.5].sum()
        
        # Gol/NoGol (BTTS - Both Teams To Score)
        prob_btts = prob_matrix[1:, 1:].sum()  # Entrambe segnano almeno 1 gol
        prob_no_btts = 1 - prob_btts
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            '1X2': {
                '1': prob_home_win,
                'X': prob_draw,
                '2': prob_away_win
            },
            'OverUnder25': {
                'Over25': prob_over_25,
                'Under25': prob_under_25
            },
            'BTTS': {
                'Gol': prob_btts,
                'NoGol': prob_no_btts
            }
        }


def test_model():
    """
    Funzione di test per verificare che il modello funzioni correttamente.
    """
    print("🧪 Test modello Independent Poisson")
    print("=" * 60)
    
    # Inizializza il modello
    model = DixonColesModel()
    
    # Carica i dati
    data_dir = Path(__file__).parent.parent / "data"
    matches_df = model.load_data(data_dir)
    
    # Addestra il modello
    model.fit(matches_df)
    
    # Mostra le squadre disponibili per aiutare a scegliere il test
    print(f"\n Squadre disponibili (prime 20):")
    for team in model.teams[:20]:
        print(f"   - {team}")
    
    # Testa una previsione con squadre note
    print("\n🔮 Test previsione")
    print("-" * 60)
    
    # Prova con squadre che dovrebbero essere nei Top 5 campionati
    test_cases = [
        ("Barcelona", "Real Madrid"),
        ("Juventus", "Inter"),
        ("Manchester City", "Liverpool"),
    ]
    
    for home, away in test_cases:
        try:
            prediction = model.predict_match(home, away)
            
            print(f"\n🏟️  {home} vs {away}")
            print(f"   1X2 → 1: {prediction['1X2']['1']:.1%} | X: {prediction['1X2']['X']:.1%} | 2: {prediction['1X2']['2']:.1%}")
            print(f"   Over/Under 2.5 → Over: {prediction['OverUnder25']['Over25']:.1%} | Under: {prediction['OverUnder25']['Under25']:.1%}")
            print(f"   Gol/NoGol → Gol: {prediction['BTTS']['Gol']:.1%} | NoGol: {prediction['BTTS']['NoGol']:.1%}")
        
        except ValueError as e:
            print(f"\n⚠️  {home} vs {away}: {e}")
    
    print("\n✅ Modello funzionante!")


if __name__ == "__main__":
    test_model()