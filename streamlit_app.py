import streamlit as st
import random
import json
import os
import base64

def set_background_local(bild_pfad):
    """Lädt ein lokales Bild, wandelt es um und setzt es als Hintergrund."""
    if not os.path.exists(bild_pfad):
        st.warning(f"Hinweis: Das Hintergrundbild '{bild_pfad}' wurde nicht gefunden. Standard-Hintergrund wird geladen.")
        return
    
    with open(bild_pfad, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{encoded_string}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    .stApp > header {{
        background-color: transparent;
    }}
    .block-container {{
        background-color: transparent; 
        padding: 2rem;
    }}
    /* Macht den Standard-Text weiß, lässt aber unsere farbigen <span> Tags in Ruhe */
    .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp label {{
        color: white !important;
    }}
    
    /* NEU: Buttons Dunkelblau färben */
    div.stButton > button {{
        background-color: #00008B !important; /* Dunkelblau */
        color: white !important;
        border: 2px solid #00008B !important;
        border-radius: 8px !important; /* Macht die Ecken leicht rund */
    }}
    
    /* Hover-Effekt: Etwas helleres Blau, wenn man mit der Maus darüber fährt */
    div.stButton > button:hover {{
        background-color: #0000CD !important; 
        border-color: #0000CD !important;
        color: white !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def fragen_laden(dateiname="fragen.json"):
    if not os.path.exists(dateiname):
        st.error(f"Fehler: Die Datei '{dateiname}' wurde nicht gefunden!")
        return []
    with open(dateiname, 'r', encoding='utf-8') as datei:
        try:
            return json.load(datei)
        except json.JSONDecodeError:
            st.error(f"Fehler: Die Datei '{dateiname}' ist fehlerhaft formatiert.")
            return []

# --- Initialisierung ---
set_background_local("hintergrund.jpg")

if 'zustand' not in st.session_state:
    st.session_state.zustand = 'start'
    st.session_state.fragen = []
    st.session_state.aktueller_index = 0
    st.session_state.punktestand = 0
    st.session_state.nutzer_auswahl = [] # Speichert die Auswahl für die Anzeige

st.title("🧠 Prüfungsvorbereitung FDL")

# --- ZUSTAND: Startbildschirm ---
if st.session_state.zustand == 'start':
    st.write("Willkommen! Teste dein Wissen. Wähle bei jeder Frage alle richtigen Antworten aus.")
    
    if st.button("Quiz starten", type="primary"):
        alle_fragen = fragen_laden()
        if alle_fragen:
            anzahl = min(10, len(alle_fragen))
            st.session_state.fragen = random.sample(alle_fragen, anzahl)
            st.session_state.aktueller_index = 0
            st.session_state.punktestand = 0
            st.session_state.zustand = 'frage'
            st.rerun()

# --- ZUSTAND: Frage anzeigen ---
elif st.session_state.zustand == 'frage':
    q = st.session_state.fragen[st.session_state.aktueller_index]
    anzahl_fragen = len(st.session_state.fragen)
    
    st.subheader(f"Frage {st.session_state.aktueller_index + 1} von {anzahl_fragen}")
    st.write(f"**{q['frage']}**")
    st.caption("Achtung: Es können mehrere Antworten richtig sein!")
    
    auswahl_user = []
    
    for i, option in enumerate(q['optionen']):
        if st.checkbox(option, key=f"frage_{st.session_state.aktueller_index}_opt_{i}"):
            auswahl_user.append(option[0].upper())
    
    if st.button("Antwort bestätigen"):
        if auswahl_user:
            # Auswahl im Session State speichern, um sie später anzuzeigen
            st.session_state.nutzer_auswahl = auswahl_user
            
            richtige_antworten_string = q['antwort']
            richtige_buchstaben = [buchstabe.strip().upper() for buchstabe in richtige_antworten_string.split(',')]
            
            ist_richtig = (set(auswahl_user) == set(richtige_buchstaben))
            st.session_state.letzte_antwort_richtig = ist_richtig
            
            if ist_richtig:
                st.session_state.punktestand += 1
                
            st.session_state.zustand = 'ergebnis'
            st.rerun()
        else:
            st.warning("Bitte kreuze mindestens eine Antwort an!")

# --- ZUSTAND: Ergebnis der aktuellen Frage anzeigen ---
elif st.session_state.zustand == 'ergebnis':
    q = st.session_state.fragen[st.session_state.aktueller_index]
    
    st.write(f"**Frage:** {q['frage']}")
    
    if st.session_state.letzte_antwort_richtig:
        st.success("✅ Richtig!")
    else:
        st.error(f"❌ Leider falsch.")

    st.markdown("---")
    st.markdown("**Vergleich deiner Auswahl mit der Lösung:**")
    
    richtige_antworten_string = q['antwort']
    richtige_buchstaben = [buchstabe.strip().upper() for buchstabe in richtige_antworten_string.split(',')]
    meine_auswahl = st.session_state.nutzer_auswahl
    
    for option in q['optionen']:
        buchstabe = option[0].upper()
        
        # Logik für die Symbole
        ist_in_loesung = buchstabe in richtige_buchstaben
        wurde_gewaehlt = buchstabe in meine_auswahl
        
        if ist_in_loesung and wurde_gewaehlt:
            # Korrekt gewählt
            st.markdown(f"<span style='color: limegreen; font-weight: bold;'>{option} ✅ (Richtig gewählt)</span>", unsafe_allow_html=True)
        elif ist_in_loesung and not wurde_gewaehlt:
            # Richtige Antwort vergessen
            st.markdown(f"<span style='color: #FFD700; font-weight: bold;'>{option} 🟢 (Das wäre richtig gewesen)</span>", unsafe_allow_html=True)
        elif wurde_gewaehlt and not ist_in_loesung:
            # Falsch gewählt
            st.markdown(f"<span style='color: #FF4B4B;'>{option} 🔵 (Deine Wahl - leider falsch)</span>", unsafe_allow_html=True)
        else:
            # Nicht gewählt und auch nicht richtig
            st.write(option)
            
    st.markdown("---")
    
    if st.button("Weiter zur nächsten Frage", type="primary"):
        st.session_state.aktueller_index += 1
        st.session_state.nutzer_auswahl = [] # Reset der Auswahl
        
        if st.session_state.aktueller_index >= len(st.session_state.fragen):
            st.session_state.zustand = 'ende'
        else:
            st.session_state.zustand = 'frage'
        st.rerun()

# --- ZUSTAND: Quiz Ende & Auswertung ---
elif st.session_state.zustand == 'ende':
    anzahl_fragen = len(st.session_state.fragen)
    st.header("🎉 Quiz beendet!")
    st.write(f"Du hast **{st.session_state.punktestand} von {anzahl_fragen} Punkten** erreicht.")
    
    prozent = st.session_state.punktestand / anzahl_fragen
    st.progress(prozent)
    
    if prozent == 1.0:
        st.success("Perfekt! Du hast alles richtig!")
    elif prozent >= 0.75:
        st.info("Sehr gute Leistung!")
    elif prozent >= 0.50:
        st.warning("Nicht schlecht, aber da ist noch Luft nach oben.")
    else:
        st.error("Das üben wir wohl besser noch mal.")
        
    if st.button("Neues Quiz starten"):
        st.session_state.zustand = 'start'
        st.rerun()
