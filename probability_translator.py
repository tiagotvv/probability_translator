import streamlit as st
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from fractions import Fraction
from itertools import product

# Define base events
game_events = [
    {"prob": 0.5, "desc": "flip a coin and get heads"},     
    {"prob": 1/32, "desc": "flip 5 coins and get 5 heads"},
    {"prob": 1/1024, "desc": "flip 10 coins and get 10 heads"},
    {"prob": 1/6, "desc": "roll a 6-sided die and get a 1"},        
    {"prob": 5/6, "desc": "roll a 6-sided die and NOT get a 1"},        
    {"prob": 1/3, "desc": "roll a 6-sided die and get a 1 or 2"},        
    {"prob": 2/3, "desc": "roll a 6-sided die and get a 3 or higher"},        
    {"prob": 1/36, "desc": "roll double sixes with two 6-sided dice"},
    {"prob": 1/216, "desc": "roll triple sixes with three 6-sided dice"},
    {"prob": 1/7776, "desc": "roll quintuple sixes with five 6-sided dice"},
    {"prob": 32/663, "desc": "Getting a Blackjack (Ace + 10-value) from two cards of a shuffled deck"},
    {"prob": 1/26, "desc": "draw a Red King from a shuffled deck"},
    {"prob": 1/52, "desc": "draw the Ace of Spades from a shuffled deck"},
    {"prob": 51/52, "desc": "draw any card BUT the Ace of Spades from a shuffled deck"},
    {"prob": 1/13, "desc": "draw any Ace from a shuffled deck"},
    {"prob": 1/221, "desc": "draw two Aces from a shuffled deck (without replacement)"},
    {"prob": 4/663, "desc": "draw an Ace followed by a King from a shuffled deck (without replacement)"},
    {"prob": 12/13, "desc": "draw any card BUT Aces from a shuffled deck"},
    {"prob": 6/28, "desc": "pick a domino tile and the sum of its numbers is 9 or greater"},
    {"prob": 0.0045, "desc": "being dealt pocket Aces - Texas Hold'em poker"},
    {"prob": 0.9955, "desc": "not being dealt pocket Aces - Texas Hold'em poker"},
    {"prob": 1/10000, "desc": "guess a 4-digit PIN on the first try"},
]

misc_events = [
    {"prob": 105/205, "desc": "give birth to a baby boy"},     
    {"prob": 1/29, "desc": "have five baby boys in a row"},
    {"prob": 1/1024, "desc": "flip 10 coins and get 10 heads"},
    {"prob": 0.027, "desc": "find two people that share their birthday in a group of 5 random people"},
    {"prob": 0.117, "desc": "find two people that share their birthday in a group of 10 random people"},
    {"prob": 0.2, "desc": "miss a penalty kick in professional football"},            
    {"prob": 0.8, "desc": "score a penalty kick in professional football"},        
    {"prob": 1/3, "desc": "win a Rock-Paper-Scissors round"},        
    {"prob": 1/27, "desc": "win three Rock-Paper-Scissors rounds in a row"},        
    {"prob": 1/85, "desc": "natural conception of twins"},
    {"prob": 1/200, "desc": "natural conception of identical twins"},
    {"prob": 1/7000, "desc": "natural conception of triplets"},
    {"prob": 28/1461, "desc": "select a person born from Jan 1 to Jan 7 from a large crowd"},
    {"prob": 1433/1461, "desc": "select a person born from Jan 8 to Dec 31 from a large crowd"},
    {"prob": 113/1461, "desc": "select a person born in February from a large crowd"},
    {"prob": 1348/1461, "desc": "select a person not born in February from a large crowd"},
    {"prob": 1/10, "desc": "select a left-handed person from a large crowd"},
    {"prob": 1/1461, "desc": "select a person born on Feb 29 from a large crowd"},
    {"prob": 0.9999, "desc": "an ATM correctly dispensing your cash"},
    {"prob": 0.86, "desc": "Amazon Prime package arriving on time (urban areas)"},
    {"prob": 1/10000, "desc": "guess a 4-digit PIN on the first try"},
]

def find_best_compound(target_prob, base_events, max_depth=4):
    if target_prob > 1e-2:
        rel_error_threshold = 0.04
    elif target_prob > 1e-4:
        rel_error_threshold = 0.03
    else:
        rel_error_threshold = 0.03
    
    best_combo = None
    best_prob = 0
    best_error = float('inf')
    best_depth = 0

    for depth in range(1, max_depth + 1):
        local_best_error = float('inf')
        local_best_combo = None
        local_best_prob = 0

        for combo in product(base_events, repeat=depth):
            combo_prob = 1
            for event in combo:
                combo_prob *= event["prob"]

            error = abs(combo_prob - target_prob)
            rel_error = error / target_prob if target_prob > 0 else float('inf')

            if error < local_best_error:
                local_best_error = error
                local_best_combo = combo
                local_best_prob = combo_prob

            # 💥 Stop early if relative error is good enough
            if rel_error < rel_error_threshold:
                return local_best_combo, local_best_prob, error

        if local_best_error < best_error:
            best_error = local_best_error
            best_combo = local_best_combo
            best_prob = local_best_prob
            best_depth = depth
        else:
            break

    return best_combo, best_prob, best_error

def one_in_decimal_to_p_in_q(m, max_denominator=20):
    f = Fraction(1 / m).limit_denominator(max_denominator)
    return f.numerator, f.denominator

# --- STREAMLIT APP ---

st.title("🧠 Translating Probabilities")
st.markdown("""Sometimes we are told that something has a “8.3% chance” and had no idea what that really means.
This web app turns abstract probabilities into relatable analogies using coins, dice, cards,
 and more mundane facts, so we can finally have a feel of what the numbers are telling us.""")

mode = st.radio(
    "Choose analogy mode:",
    ["Game-based", "Miscellaneous"],
    horizontal=True
)

base_events = game_events if mode == "Game-based" else misc_events

st.markdown("Enter a probability as a percentage (e.g. `1%`) or odds (`1 in 200`)""")

input_str = st.text_input("Your probability:", "1 in 221")

# --- Parse input ---
def parse_probability(s):
    s = s.strip().lower()
    try:
        if "in" in s:
            parts = s.split("in")
            numerator = float(parts[0].strip())
            denominator = float(parts[1].strip())
            return numerator / denominator
        elif "%" in s:
            return float(s.strip('%')) / 100
        else:
            return float(s)
    except:
        return None

p = parse_probability(input_str)

if p is None or not (0 < p < 1):
    st.error("Please enter a valid probability between 0 and 100% or as odds (1 in N).")
    st.stop()

# --- Display core forms ---
st.subheader("🔢 Equivalent Probability Values")

if p <= 1e-2:
    st.write(f"**Decimal**: {p:.1e}")
    if (round(1/p) == 1/p):
        st.write(f"**Odds**: 1 in {round(1/p)}")
    else:
        st.write(f"**Odds**: ≈ 1 in {round(1/p)}")
else:
    st.write(f"**Decimal**: {round(p, 6)}")
    st.write(f"**Percent**: {round(p * 100, 4)}%")
    #st.write(f"**Odds**: 1 in {round(1/p)}")
    # --- P in Q form ---
    numerator, denominator = one_in_decimal_to_p_in_q(1/p, max_denominator=50)
    if numerator == 1:
        st.write(f"**Odds**: {numerator} in {denominator} (≈ {round(numerator/denominator * 100, 2)}%)")
    else:
        st.write(f"**P in Q format**: {numerator} in {denominator} (≈ {round(numerator/denominator * 100, 2)}%)")

# --- Closest compound analogy ---
st.subheader("🎲 Closest Compound Analogy")

combo, actual_prob, err = find_best_compound(p, base_events)
if combo:
    for e in combo:
        st.write("→", e["desc"])
    if p < 1e-2:
        st.write(f"\n**≈ 1 in {round(1/actual_prob)}** chance - relative error: {round(100*err/p, 2)}%")
        

    else:    
        st.write(f"\n**≈ {round(actual_prob * 100, 2)}%** - relative error: {round(100*err/p, 2)}%") #({round(actual_prob, 8)})")
        

#st.caption("Built with brutal realism and a healthy disrespect for probability illusions.")
