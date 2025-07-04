import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.metrics import brier_score_loss, log_loss
import pickle
import os
from typing import Tuple, Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns

class F1ProbabilityCalibrator:
    """
    Klasse zur Kalibrierung von F1-Platzierungswahrscheinlichkeiten.
    Unterstützt Platt Scaling und Isotonic Regression.
    """
    
    def __init__(self, method='platt'):
        """
        Args:
            method: 'platt' für Platt Scaling oder 'isotonic' für Isotonic Regression
        """
        self.method = method
        self.calibrators = {}  # Ein Kalibrator pro Position
        self.is_fitted = False
        
    def fit(self, y_true: np.ndarray, y_prob: np.ndarray, positions: np.ndarray):
        """
        Trainiert die Kalibratoren für jede Position.
        
        Args:
            y_true: Wahre Positionen (1D array)
            y_prob: Vorhergesagte Wahrscheinlichkeiten (2D array: samples x positions)
            positions: Array der Positionen (z.B. [1, 2, 3, ..., 20])
        """
        print(f"🔧 Trainiere {self.method.upper()} Kalibratoren...")
        
        for i, pos in enumerate(positions):
            # Binäre Labels: 1 wenn Fahrer auf Position pos, 0 sonst
            y_binary = (y_true == pos).astype(int)
            y_prob_pos = y_prob[:, i]
            
            if self.method == 'platt':
                # Platt Scaling (Logistische Regression)
                calibrator = LogisticRegression()
                calibrator.fit(y_prob_pos.reshape(-1, 1), y_binary)
            elif self.method == 'isotonic':
                # Isotonic Regression
                calibrator = IsotonicRegression(out_of_bounds='clip')
                calibrator.fit(y_prob_pos, y_binary)
            else:
                raise ValueError(f"Unbekannte Methode: {self.method}")
            
            self.calibrators[pos] = calibrator
            
        self.is_fitted = True
        print(f"✅ Kalibrierung für {len(positions)} Positionen abgeschlossen")
    
    def predict_proba(self, y_prob: np.ndarray, positions: np.ndarray) -> np.ndarray:
        """
        Kalibriert Wahrscheinlichkeiten.
        
        Args:
            y_prob: Unkalibrierte Wahrscheinlichkeiten (2D array)
            positions: Array der Positionen
        
        Returns:
            Kalibrierte Wahrscheinlichkeiten (2D array)
        """
        if not self.is_fitted:
            raise ValueError("Kalibrator muss erst trainiert werden")
        
        calibrated_probs = np.zeros_like(y_prob)
        
        for i, pos in enumerate(positions):
            if pos in self.calibrators:
                calibrator = self.calibrators[pos]
                
                if self.method == 'platt':
                    calibrated_probs[:, i] = calibrator.predict_proba(
                        y_prob[:, i].reshape(-1, 1)
                    )[:, 1]  # Wahrscheinlichkeit für Klasse 1
                elif self.method == 'isotonic':
                    calibrated_probs[:, i] = calibrator.predict(y_prob[:, i])
            else:
                # Falls Position nicht trainiert, verwende ursprüngliche Wahrscheinlichkeit
                calibrated_probs[:, i] = y_prob[:, i]
        
        # Normalisiere Wahrscheinlichkeiten pro Zeile (Fahrer)
        row_sums = calibrated_probs.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1  # Vermeide Division durch 0
        calibrated_probs = calibrated_probs / row_sums
        
        return calibrated_probs
    
    def save(self, filepath: str):
        """Speichert den trainierten Kalibrator."""
        if not self.is_fitted:
            raise ValueError("Kalibrator muss erst trainiert werden")
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
        print(f"💾 Kalibrator gespeichert: {filepath}")
    
    @classmethod
    def load(cls, filepath: str):
        """Lädt einen gespeicherten Kalibrator."""
        with open(filepath, 'rb') as f:
            calibrator = pickle.load(f)
        print(f"📂 Kalibrator geladen: {filepath}")
        return calibrator

def evaluate_calibration(y_true: np.ndarray, y_prob_uncalibrated: np.ndarray, 
                        y_prob_calibrated: np.ndarray, positions: np.ndarray) -> Dict[str, float]:
    """
    Evaluiert die Kalibrierungsqualität.
    
    Args:
        y_true: Wahre Positionen
        y_prob_uncalibrated: Unkalibrierte Wahrscheinlichkeiten
        y_prob_calibrated: Kalibrierte Wahrscheinlichkeiten
        positions: Array der Positionen
    
    Returns:
        Dictionary mit Evaluationsmetriken
    """
    results = {}
    
    for i, pos in enumerate(positions):
        y_binary = (y_true == pos).astype(int)
        
        # Brier Score (niedriger = besser)
        brier_uncal = brier_score_loss(y_binary, y_prob_uncalibrated[:, i])
        brier_cal = brier_score_loss(y_binary, y_prob_calibrated[:, i])
        
        results[f'brier_uncalibrated_P{pos}'] = brier_uncal
        results[f'brier_calibrated_P{pos}'] = brier_cal
        results[f'brier_improvement_P{pos}'] = brier_uncal - brier_cal
    
    # Durchschnittliche Verbesserung
    improvements = [v for k, v in results.items() if 'improvement' in k]
    results['avg_brier_improvement'] = np.mean(improvements)
    
    return results

def calibrate_f1_model(model_path: str, training_data_path: str, 
                      output_path: str = None, method: str = 'platt',
                      test_size: float = 0.2) -> Tuple[Any, F1ProbabilityCalibrator]:
    """
    Kalibriert ein F1-Modell mit historischen Daten.
    
    Args:
        model_path: Pfad zum trainierten Modell
        training_data_path: Pfad zu den Trainingsdaten
        output_path: Pfad für das kalibrierte Modell
        method: Kalibrierungsmethode ('platt' oder 'isotonic')
        test_size: Anteil der Daten für die Kalibrierung
    
    Returns:
        Tuple aus (Original-Modell, Kalibrator)
    """
    print(f"🏎️ Starte F1-Modell-Kalibrierung mit {method.upper()}...")
    
    # Lade Modell
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    print(f"📂 Modell geladen: {model_path}")
    
    # Lade Trainingsdaten
    df = pd.read_csv(training_data_path)
    print(f"📊 Trainingsdaten geladen: {df.shape}")
    
    # Bereite Daten vor
    feature_cols = [col for col in df.columns if col not in ['final_position', 'driver', 'race', 'year']]
    X = df[feature_cols].values
    y = df['final_position'].values
    
    # Split für Kalibrierung
    from sklearn.model_selection import train_test_split
    X_train, X_cal, y_train, y_cal = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )
    
    print(f"📊 Kalibrierungsdaten: {X_cal.shape[0]} Samples")
    
    # Generiere Vorhersagen für Kalibrierung
    positions = np.arange(1, 21)  # P1 bis P20
    
    # Vorhersage-Wahrscheinlichkeiten für alle Positionen
    y_prob_uncalibrated = []
    
    for pos in positions:
        # Erstelle binäre Labels für jede Position
        y_binary = (y_train == pos).astype(int)
        
        # Trainiere binären Klassifikator für diese Position
        from sklearn.ensemble import RandomForestClassifier
        pos_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        pos_classifier.fit(X_train, y_binary)
        
        # Vorhersage für Kalibrierungsdaten
        prob_pos = pos_classifier.predict_proba(X_cal)[:, 1]
        y_prob_uncalibrated.append(prob_pos)
    
    y_prob_uncalibrated = np.column_stack(y_prob_uncalibrated)
    
    # Normalisiere Wahrscheinlichkeiten
    row_sums = y_prob_uncalibrated.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    y_prob_uncalibrated = y_prob_uncalibrated / row_sums
    
    # Trainiere Kalibrator
    calibrator = F1ProbabilityCalibrator(method=method)
    calibrator.fit(y_cal, y_prob_uncalibrated, positions)
    
    # Kalibriere Wahrscheinlichkeiten
    y_prob_calibrated = calibrator.predict_proba(y_prob_uncalibrated, positions)
    
    # Evaluiere Kalibrierung
    eval_results = evaluate_calibration(y_cal, y_prob_uncalibrated, y_prob_calibrated, positions)
    
    print(f"\n📈 Kalibrierungs-Ergebnisse:")
    print(f"Durchschnittliche Brier Score Verbesserung: {eval_results['avg_brier_improvement']:.4f}")
    
    # Speichere Kalibrator
    if output_path:
        calibrator.save(output_path)
    
    return model, calibrator

def create_calibration_plots(y_true: np.ndarray, y_prob_uncalibrated: np.ndarray,
                           y_prob_calibrated: np.ndarray, positions: list,
                           output_dir: str = "data/processed/calibration_plots"):
    """
    Erstellt Kalibrierungs-Plots für die wichtigsten Positionen.
    
    Args:
        y_true: Wahre Positionen
        y_prob_uncalibrated: Unkalibrierte Wahrscheinlichkeiten
        y_prob_calibrated: Kalibrierte Wahrscheinlichkeiten
        positions: Liste der zu plottenden Positionen
        output_dir: Ausgabeverzeichnis für Plots
    """
    os.makedirs(output_dir, exist_ok=True)
    
    for pos in positions:
        if pos > y_prob_uncalibrated.shape[1]:
            continue
            
        y_binary = (y_true == pos).astype(int)
        
        plt.figure(figsize=(12, 5))
        
        # Reliability Diagram
        plt.subplot(1, 2, 1)
        
        # Binning für Reliability Diagram
        n_bins = 10
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]
        
        # Unkalibriert
        bin_centers_uncal = []
        bin_accuracies_uncal = []
        
        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            in_bin = (y_prob_uncalibrated[:, pos-1] > bin_lower) & (y_prob_uncalibrated[:, pos-1] <= bin_upper)
            prop_in_bin = in_bin.mean()
            
            if prop_in_bin > 0:
                accuracy_in_bin = y_binary[in_bin].mean()
                avg_confidence_in_bin = y_prob_uncalibrated[in_bin, pos-1].mean()
                
                bin_centers_uncal.append(avg_confidence_in_bin)
                bin_accuracies_uncal.append(accuracy_in_bin)
        
        # Kalibriert
        bin_centers_cal = []
        bin_accuracies_cal = []
        
        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            in_bin = (y_prob_calibrated[:, pos-1] > bin_lower) & (y_prob_calibrated[:, pos-1] <= bin_upper)
            prop_in_bin = in_bin.mean()
            
            if prop_in_bin > 0:
                accuracy_in_bin = y_binary[in_bin].mean()
                avg_confidence_in_bin = y_prob_calibrated[in_bin, pos-1].mean()
                
                bin_centers_cal.append(avg_confidence_in_bin)
                bin_accuracies_cal.append(accuracy_in_bin)
        
        # Plot
        plt.plot([0, 1], [0, 1], 'k--', label='Perfekt kalibriert')
        plt.plot(bin_centers_uncal, bin_accuracies_uncal, 'ro-', label='Unkalibriert')
        plt.plot(bin_centers_cal, bin_accuracies_cal, 'bo-', label='Kalibriert')
        
        plt.xlabel('Mittlere vorhergesagte Wahrscheinlichkeit')
        plt.ylabel('Anteil positiver Fälle')
        plt.title(f'Reliability Diagram - Position {pos}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Histogramm der Wahrscheinlichkeiten
        plt.subplot(1, 2, 2)
        plt.hist(y_prob_uncalibrated[:, pos-1], bins=20, alpha=0.5, label='Unkalibriert', density=True)
        plt.hist(y_prob_calibrated[:, pos-1], bins=20, alpha=0.5, label='Kalibriert', density=True)
        plt.xlabel('Wahrscheinlichkeit')
        plt.ylabel('Dichte')
        plt.title(f'Wahrscheinlichkeits-Verteilung - Position {pos}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/calibration_P{pos}.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"📊 Kalibrierungs-Plots gespeichert in: {output_dir}")

if __name__ == "__main__":
    # Beispiel-Verwendung
    MODEL_PATH = "models/rf_model.pkl"
    TRAINING_DATA_PATH = "data/full/full_training_data.csv"
    CALIBRATOR_OUTPUT = "models/probability_calibrator.pkl"
    
    try:
        # Kalibriere Modell
        model, calibrator = calibrate_f1_model(
            MODEL_PATH, 
            TRAINING_DATA_PATH, 
            CALIBRATOR_OUTPUT,
            method='platt'
        )
        
        print("\n✅ Kalibrierung erfolgreich abgeschlossen!")
        print(f"📁 Kalibrator gespeichert: {CALIBRATOR_OUTPUT}")
        
    except FileNotFoundError as e:
        print(f"❌ Datei nicht gefunden: {e}")
        print("💡 Stelle sicher, dass Modell und Trainingsdaten vorhanden sind")
    except Exception as e:
        print(f"❌ Fehler bei der Kalibrierung: {e}")
        import traceback
        traceback.print_exc()