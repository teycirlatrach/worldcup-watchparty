import math
import streamlit as st
import json
import os
import numpy as np
import plotly.graph_objects as go
from excitement_engine import calculate_watch_score, get_recommendation_badge

# -----------------------------------------------------------------------------
# 1. CONFIGURATION & CHARGEMENT
# -----------------------------------------------------------------------------
st.set_page_config(page_title="World Cup 2026 Watch-Party Predictor", layout="wide", page_icon="⚽")

@st.cache_data
def load_teams_data():
    json_path = os.path.join('data', 'teams_stats.json')
    if not os.path.exists(json_path):
        st.error("Le fichier 'data/teams_stats.json' n'existe pas. Veuillez exécuter 'python 1_train_match_predictor.py' d'abord.")
        st.stop()
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

TEAMS_DATA = load_teams_data()

st.title("⚽ World Cup 2026: Match & Watch-Party Predictor")
st.markdown("Anticipez l'issue des rencontres et identifiez les matchs les plus excitants à regarder en direct !")

# -----------------------------------------------------------------------------
# 2. MOTEUR DE PRÉDICTION (Simulation de Poisson)
# -----------------------------------------------------------------------------
def predict_match(home_team, away_team, is_knockout):
    t1_stats = TEAMS_DATA[home_team]
    t2_stats = TEAMS_DATA[away_team]
    
    # Calcul des buts attendus (xG) par combinaison attaque / défense
    home_xg = max(0.2, (t1_stats['avg_goals_scored'] + t2_stats['avg_goals_conceded']) / 2.0)
    away_xg = max(0.2, (t2_stats['avg_goals_scored'] + t1_stats['avg_goals_conceded']) / 2.0)

    # Matrice de probabilité Poisson (0 à 5 buts)
    max_goals = 6
    matrix = np.zeros((max_goals, max_goals))
    for h in range(max_goals):
        for a in range(max_goals):
            p_h = (np.exp(-home_xg) * (home_xg**h)) / math.factorial(h)
            p_a = (np.exp(-away_xg) * (away_xg**a)) / math.factorial(a)
            matrix[h, a] = p_h * p_a

    matrix /= matrix.sum()

    prob_home = float(np.sum(np.tril(matrix, -1)))
    prob_draw = float(np.sum(np.diag(matrix)))
    prob_away = float(np.sum(np.triu(matrix, 1)))
    
    most_probable_score = np.unravel_index(np.argmax(matrix), matrix.shape)
    
    excitement_score = calculate_watch_score(
       prob_home, prob_draw, prob_away, home_xg, away_xg, 
        home_team, away_team, TEAMS_DATA, is_knockout
    )

    return {
        "prob_home": round(prob_home * 100, 1),
        "prob_draw": round(prob_draw * 100, 1),
        "prob_away": round(prob_away * 100, 1),
        "expected_score": f"{most_probable_score[0]} - {most_probable_score[1]}",
        "home_xg": round(home_xg, 2),
        "away_xg": round(away_xg, 2),
        "excitement_score": excitement_score
    }

# -----------------------------------------------------------------------------
# 3. INTERFACE UTILISATEUR
# -----------------------------------------------------------------------------
st.sidebar.header("🎛️ Sélection des Nations")
teams_list = sorted(list(TEAMS_DATA.keys()))

default_home = "France" if "France" in teams_list else teams_list[0]
default_away = "Brazil" if "Brazil" in teams_list else teams_list[1]

team_1 = st.sidebar.selectbox("Équipe A (Domicile)", teams_list, index=teams_list.index(default_home))
team_2 = st.sidebar.selectbox("Équipe B (Extérieur)", teams_list, index=teams_list.index(default_away))

is_knockout = st.sidebar.checkbox("Match à élimination directe (Knockout)", value=False)

if team_1 == team_2:
    st.warning("Veuillez sélectionner deux équipes différentes.")
else:
    results = predict_match(team_1, team_2, is_knockout)
    
    # Block 1: Watch-Party Recommender
    st.subheader("🔥 Watch-Party Recommender")
    col_w1, col_w2 = st.columns([1, 2])
    
    with col_w1:
        st.metric("Watch-Worthiness Score", f"{results['excitement_score']} / 10")
        
    with col_w2:
        badge_title, badge_type, badge_msg = get_recommendation_badge(results['excitement_score'])
        if badge_type == "success":
            st.success(f"**{badge_title}** : {badge_msg}")
        elif badge_type == "info":
            st.info(f"**{badge_title}** : {badge_msg}")
        else:
            st.warning(f"**{badge_title}** : {badge_msg}")
            
    st.progress(results['excitement_score'] / 10.0)

    st.markdown("---")

    # Block 2: Probabilités du résultat
    st.subheader(f"📊 Prédiction : {team_1} vs {team_2}")
    
    m1, m2, m3 = st.columns(3)
    m1.metric(f"Victoire {team_1}", f"{results['prob_home']} %")
    m2.metric("Match Nul", f"{results['prob_draw']} %")
    m3.metric(f"Victoire {team_2}", f"{results['prob_away']} %")

    fig = go.Figure(data=[go.Bar(
        x=[team_1, 'Match Nul', team_2],
        y=[results['prob_home'], results['prob_draw'], results['prob_away']],
        marker_color=['#1f77b4', '#94a3b8', '#2ca02c'],
        text=[f"{results['prob_home']}%", f"{results['prob_draw']}%", f"{results['prob_away']}%"],
        textposition='auto'
    )])
    fig.update_layout(yaxis_title="Probabilité (%)", height=320, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    # Block 3: Metrics xG & Score
    c_s1, c_s2 = st.columns(2)
    c_s1.info(f"⚽ **Score le plus probable :** {results['expected_score']}")
    c_s2.info(f"📈 **Buts attendus (xG) :** {team_1} ({results['home_xg']}) - ({results['away_xg']}) {team_2}")

    # Block 4: Player Stats Tracker
    st.markdown("---")
    st.subheader("⭐ Player Stats Tracker (Meilleurs Buteurs Récents)")
    
    p1, p2 = st.columns(2)
    
    with p1:
        st.write(f"### {team_1}")
        scorers_1 = TEAMS_DATA[team_1]['top_scorers']
        if scorers_1:
            for player, goals in scorers_1.items():
                st.write(f"- ⚽ **{player}** : `{goals} buts`")
        else:
            st.write("Aucune donnée de buteur répertoriée.")
            
    with p2:
        st.write(f"### {team_2}")
        scorers_2 = TEAMS_DATA[team_2]['top_scorers']
        if scorers_2:
            for player, goals in scorers_2.items():
                st.write(f"- ⚽ **{player}** : `{goals} buts`")
        else:
            st.write("Aucune donnée de buteur répertoriée.")