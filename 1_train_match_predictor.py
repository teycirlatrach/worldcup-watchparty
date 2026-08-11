import pandas as pd
import numpy as np
import json
import os

def process_world_cup_data():
    print("1. Chargement des jeux de données...")
    results_path = os.path.join('data', 'results.csv')
    goals_path = os.path.join('data', 'goalscorers.csv')
    
    results = pd.read_csv(results_path)
    goalscorers = pd.read_csv(goals_path)

    # Conversion des dates
    results['date'] = pd.to_datetime(results['date'])
    goalscorers['date'] = pd.to_datetime(goalscorers['date'])

    # Filtrer les données récentes à partir de 2018 (période représentative de l'effectif actuel)
    results_recent = results[results['date'] >= '2018-01-01'].dropna(subset=['home_score', 'away_score']).copy()
    goals_recent = goalscorers[goalscorers['date'] >= '2018-01-01'].copy()

    print("2. Calcul des métriques réelles par équipe...")
    all_teams = sorted(list(set(results_recent['home_team']).union(set(results_recent['away_team']))))
    
    teams_stats = {}
    
    for team in all_teams:
        h_matches = results_recent[results_recent['home_team'] == team]
        a_matches = results_recent[results_recent['away_team'] == team]
        
        total_games = len(h_matches) + len(a_matches)
        if total_games < 5:  # Élimine les équipes ayant trop peu d'historique récent
            continue
            
        scored = h_matches['home_score'].sum() + a_matches['away_score'].sum()
        conceded = h_matches['away_score'].sum() + a_matches['home_score'].sum()
        
        # Buteurs principaux récents de la sélection
        team_goals = goals_recent[goals_recent['team'] == team]
        if not team_goals.empty:
            top_scorers = team_goals['scorer'].value_counts().head(3).to_dict()
        else:
            top_scorers = {}

        teams_stats[team] = {
            "total_games": int(total_games),
            "avg_goals_scored": round(float(scored / total_games), 2),
            "avg_goals_conceded": round(float(conceded / total_games), 2),
            "top_scorers": top_scorers
        }

    output_json = os.path.join('data', 'teams_stats.json')
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(teams_stats, f, ensure_ascii=False, indent=4)
        
    print(f"✅ Traitement terminé avec succès ! {len(teams_stats)} équipes sauvegardées dans '{output_json}'.")

if __name__ == "__main__":
    process_world_cup_data()