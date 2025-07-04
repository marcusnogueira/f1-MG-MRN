# F1 Predict Pro 🏎️

Ein Machine Learning-basiertes System zur Vorhersage von Formel 1-Rennergebnissen und Wettanalyse.

## 🚀 Features

- **ML-Vorhersagen**: Fortgeschrittene Random Forest Modelle für Positionsvorhersagen
- **Wettanalyse**: Value Bet Calculator und ROI-Simulation
- **Live Dashboard**: Streamlit-basierte Benutzeroberfläche
- **Automatisierung**: Race Monitor und Auto-Evaluator
- **Datenverarbeitung**: FastF1 API Integration für aktuelle F1-Daten

## 📁 Projektstruktur

```
f1predictpro/
├── ml/                     # Machine Learning Module
│   ├── train_model.py      # Modell-Training
│   ├── predict_live_race.py # Live-Vorhersagen
│   ├── bet_simulator.py    # Wettsimulation
│   └── value_bet_calculator.py # Value Bet Berechnung
├── dashboard/              # Streamlit Dashboard
│   └── app.py             # Haupt-Dashboard
├── utils/                  # Hilfsfunktionen
│   ├── feature_engineering.py
│   ├── odds_api_fetcher.py
│   └── prediction_exporter.py
├── data/                   # Datenverzeichnisse
│   ├── live/              # Live-Daten
│   ├── processed/         # Verarbeitete Daten
│   └── batch/             # Batch-Verarbeitung
├── models/                 # Trainierte ML-Modelle
├── config/                 # Konfigurationsdateien
└── cache/                  # FastF1 Cache
```

## 🛠️ Installation

1. **Repository klonen:**
```bash
git clone https://github.com/IHR_USERNAME/f1predictpro.git
cd f1predictpro
```

2. **Virtual Environment erstellen:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Dependencies installieren:**
```bash
pip install -r requirements.txt
```

4. **Umgebungsvariablen konfigurieren:**
```bash
cp .env.example .env
# .env Datei mit API-Keys bearbeiten
```

## 🚀 Verwendung

### Dashboard starten
```bash
streamlit run dashboard/app.py
```

### Modell trainieren
```bash
python ml/train_model.py
```

### Live-Vorhersage erstellen
```bash
python ml/predict_live_race.py
```

### Wettsimulation ausführen
```bash
python ml/bet_simulator.py
```

## 📊 ML-Modelle

- **Position Classifier**: Vorhersage der Endpositionen (1-20)
- **Top 10 Classifier**: Wahrscheinlichkeit für Top-10-Platzierung
- **Regression Model**: Kontinuierliche Positionsvorhersage
- **Full Model**: Erweiterte Features für höhere Genauigkeit

## 🎯 Features im Detail

### Automatisierte Systeme
- **Race Monitor**: Überwacht neue Rennen und aktualisiert Vorhersagen
- **Auto Evaluator**: Bewertet Modellleistung nach Rennen automatisch
- **Live Dashboard Updater**: Aktualisiert Dashboard-Daten in Echtzeit

### Wettanalyse
- **Value Bet Calculator**: Identifiziert profitable Wettmöglichkeiten
- **ROI Simulation**: Simuliert Wettstrategien über mehrere Rennen
- **Odds Integration**: Automatischer Abruf von Wettquoten

### Datenverarbeitung
- **Feature Engineering**: Erweiterte Merkmalsextraktion
- **FastF1 Integration**: Aktuelle F1-Telemetriedaten
- **Caching System**: Effiziente Datenspeicherung

## 📈 Modellleistung

Die Modelle werden kontinuierlich evaluiert und optimiert:
- **Accuracy**: ~65-75% für Positionsvorhersagen
- **ROI**: Positive Rendite bei Value Bet Strategien
- **Feature Importance**: Qualifying-Position, Streckencharakteristika, Fahrerform

## 🔧 Konfiguration

### API-Keys erforderlich
- **Odds API**: Für Wettquoten (optional)
- **FastF1**: Automatisch über Ergast API

### Konfigurationsdateien
- `config/auto_evaluator_config.json`: Auto-Evaluator Einstellungen
- `config/race_monitor_config.json`: Race Monitor Konfiguration

## 📝 Lizenz

MIT License - siehe LICENSE Datei für Details.

## 🤝 Beitragen

1. Fork das Repository
2. Erstelle einen Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

## 📞 Support

Bei Fragen oder Problemen erstelle bitte ein Issue im Repository.

---

**Hinweis**: Dieses Projekt dient zu Bildungs- und Forschungszwecken. Wetten kann süchtig machen - bitte spiele verantwortungsbewusst.