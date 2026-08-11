import numpy as np

def calculate_watch_score(prob_home, prob_draw, prob_away, home_xg, away_xg, home_team, away_team, teams_data, is_knockout=False):
    """
    Calcule un Watch-Worthiness Score (0 à 10) parfaitement étalonné pour la Coupe du Monde.
    """
    # 1. Incertitude du résultat (Max 4.0 pts) - Plus le match est serré, plus c'est excitant
    max_prob = max(prob_home, prob_draw, prob_away)
    uncertainty_score = (1.0 - max_prob) * 6.0
    
    # 2. Potentiel de buts (Max 3.0 pts)
    total_xg = min(home_xg + away_xg, 4.0)
    goals_score = (total_xg / 4.0) * 3.0
    
    # 3. Bonus "Choc de Titans" / Prestige (Up to +2.5 pts)
    t1 = teams_data.get(home_team, {})
    t2 = teams_data.get(away_team, {})
    
    # Calcul de l'indice de puissance (Attaque / Défense)
    p1 = t1.get('avg_goals_scored', 1.0) / (t1.get('avg_goals_conceded', 1.0) + 0.3)
    p2 = t2.get('avg_goals_scored', 1.0) / (t2.get('avg_goals_conceded', 1.0) + 0.3)
    
    # Si les DEUX équipes sont très fortes, on applique un gros bonus d'affiche
    top_clash_bonus = min(p1, p2) * 0.9
    
    base_score = uncertainty_score + goals_score + top_clash_bonus
    
    # Bonus de phase finale
    if is_knockout:
        base_score += 1.0

    final_score = min(max(base_score, 1.0), 10.0)
    return round(final_score, 1)


def get_recommendation_badge(score):
    if score >= 7.5:
        return "🔥 MUST WATCH", "success", "Affiche explosive et indécise à ne manquer sous aucun prétexte !"
    elif score >= 5.5:
        return "👍 BON MATCH", "info", "Rencontre très intéressante avec du spectacle potentiel."
    else:
        return "😴 RISQUE DE PURGE", "warning", "Match peu attrayant, à sens unique ou tactiquement fermé."