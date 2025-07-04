import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import pickle
import os
import time
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

class F1ModelOptimizer:
    """
    Klasse zur Optimierung von F1-Platzierungsmodellen mit GridSearchCV.
    """
    
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.best_model = None
        self.best_params = None
        self.best_score = None
        self.grid_search = None
        self.optimization_history = []
        
    def prepare_data(self, data_path: str) -> Tuple[np.ndarray, np.ndarray, list]:
        """
        Bereitet die Trainingsdaten vor.
        
        Args:
            data_path: Pfad zur CSV-Datei mit Trainingsdaten
            
        Returns:
            Tuple aus (X, y, feature_names)
        """
        print(f"📊 Lade Trainingsdaten: {data_path}")
        df = pd.read_csv(data_path)
        
        print(f"📈 Datensatz-Info: {df.shape[0]} Zeilen, {df.shape[1]} Spalten")
        
        # Feature-Spalten identifizieren
        exclude_cols = ['final_position', 'driver', 'race', 'year', 'date']
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        print(f"🔧 Features: {len(feature_cols)} Spalten")
        print(f"📋 Feature-Liste: {feature_cols[:10]}{'...' if len(feature_cols) > 10 else ''}")
        
        # Bereite Features und Target vor
        X = df[feature_cols].values
        y = df['final_position'].values
        
        # Überprüfe auf fehlende Werte
        if np.isnan(X).any():
            print("⚠️ Fehlende Werte in Features gefunden - werden mit 0 ersetzt")
            X = np.nan_to_num(X, 0)
        
        print(f"✅ Daten vorbereitet: X={X.shape}, y={y.shape}")
        print(f"📊 Ziel-Verteilung: {np.bincount(y.astype(int))}")
        
        return X, y, feature_cols
    
    def get_parameter_grid(self, grid_type: str = 'comprehensive') -> Dict[str, Any]:
        """
        Definiert Parameter-Grids für GridSearchCV.
        
        Args:
            grid_type: 'quick', 'comprehensive', oder 'extensive'
            
        Returns:
            Parameter-Grid Dictionary
        """
        if grid_type == 'quick':
            # Schnelle Suche für Tests
            param_grid = {
                'n_estimators': [50, 100],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5],
                'min_samples_leaf': [1, 2],
                'max_features': ['sqrt', 'log2']
            }
        elif grid_type == 'comprehensive':
            # Umfassende Suche (empfohlen)
            param_grid = {
                'n_estimators': [100, 200, 300],
                'max_depth': [10, 20, 30, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4],
                'max_features': ['sqrt', 'log2', None],
                'bootstrap': [True, False]
            }
        elif grid_type == 'extensive':
            # Sehr umfassende Suche (dauert lange)
            param_grid = {
                'n_estimators': [50, 100, 200, 300, 500],
                'max_depth': [5, 10, 15, 20, 25, 30, None],
                'min_samples_split': [2, 5, 10, 15],
                'min_samples_leaf': [1, 2, 4, 8],
                'max_features': ['sqrt', 'log2', 0.3, 0.5, None],
                'bootstrap': [True, False],
                'criterion': ['gini', 'entropy']
            }
        else:
            raise ValueError(f"Unbekannter grid_type: {grid_type}")
        
        total_combinations = 1
        for param, values in param_grid.items():
            total_combinations *= len(values)
        
        print(f"🔍 Parameter-Grid '{grid_type}': {total_combinations} Kombinationen")
        return param_grid
    
    def optimize_model(self, X: np.ndarray, y: np.ndarray, 
                      grid_type: str = 'comprehensive',
                      cv_folds: int = 5, 
                      scoring: str = 'accuracy',
                      n_jobs: int = -1) -> Dict[str, Any]:
        """
        Führt GridSearchCV zur Modell-Optimierung durch.
        
        Args:
            X: Feature-Matrix
            y: Target-Vektor
            grid_type: Art des Parameter-Grids
            cv_folds: Anzahl Cross-Validation Folds
            scoring: Scoring-Metrik
            n_jobs: Anzahl paralleler Jobs
            
        Returns:
            Dictionary mit Optimierungsergebnissen
        """
        print(f"🚀 Starte GridSearchCV-Optimierung...")
        start_time = time.time()
        
        # Parameter-Grid
        param_grid = self.get_parameter_grid(grid_type)
        
        # Base-Modell
        rf = RandomForestClassifier(random_state=self.random_state)
        
        # Cross-Validation Strategy
        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=self.random_state)
        
        # GridSearchCV
        self.grid_search = GridSearchCV(
            estimator=rf,
            param_grid=param_grid,
            cv=cv,
            scoring=scoring,
            n_jobs=n_jobs,
            verbose=1,
            return_train_score=True
        )
        
        print(f"⏱️ Starte Suche mit {cv_folds}-Fold CV...")
        self.grid_search.fit(X, y)
        
        # Beste Parameter und Score
        self.best_model = self.grid_search.best_estimator_
        self.best_params = self.grid_search.best_params_
        self.best_score = self.grid_search.best_score_
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Ergebnisse
        results = {
            'best_score': self.best_score,
            'best_params': self.best_params,
            'duration_minutes': duration / 60,
            'total_fits': len(self.grid_search.cv_results_['params']),
            'cv_folds': cv_folds,
            'scoring': scoring,
            'grid_type': grid_type
        }
        
        self.optimization_history.append({
            'timestamp': datetime.now(),
            'results': results
        })
        
        print(f"\n✅ Optimierung abgeschlossen!")
        print(f"⏱️ Dauer: {duration/60:.1f} Minuten")
        print(f"🏆 Bester Score: {self.best_score:.4f}")
        print(f"🔧 Beste Parameter:")
        for param, value in self.best_params.items():
            print(f"   {param}: {value}")
        
        return results
    
    def evaluate_model(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """
        Evaluiert das beste Modell.
        
        Args:
            X: Feature-Matrix
            y: Target-Vektor
            
        Returns:
            Dictionary mit Evaluationsmetriken
        """
        if self.best_model is None:
            raise ValueError("Modell muss erst optimiert werden")
        
        print(f"📊 Evaluiere bestes Modell...")
        
        # Cross-Validation Scores
        cv_scores = cross_val_score(
            self.best_model, X, y, 
            cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=self.random_state),
            scoring='accuracy'
        )
        
        # Feature Importance
        feature_importance = self.best_model.feature_importances_
        
        # Vorhersagen für Confusion Matrix
        y_pred = self.best_model.predict(X)
        
        results = {
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'cv_scores': cv_scores.tolist(),
            'train_accuracy': accuracy_score(y, y_pred),
            'feature_importance': feature_importance.tolist(),
            'confusion_matrix': confusion_matrix(y, y_pred).tolist()
        }
        
        print(f"📈 CV-Score: {results['cv_mean']:.4f} ± {results['cv_std']:.4f}")
        print(f"📈 Train-Accuracy: {results['train_accuracy']:.4f}")
        
        return results
    
    def save_best_model(self, filepath: str, include_metadata: bool = True):
        """
        Speichert das beste Modell.
        
        Args:
            filepath: Pfad für das gespeicherte Modell
            include_metadata: Ob Metadaten mit gespeichert werden sollen
        """
        if self.best_model is None:
            raise ValueError("Kein optimiertes Modell vorhanden")
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        if include_metadata:
            # Speichere Modell mit Metadaten
            model_data = {
                'model': self.best_model,
                'best_params': self.best_params,
                'best_score': self.best_score,
                'optimization_history': self.optimization_history,
                'timestamp': datetime.now()
            }
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
        else:
            # Speichere nur das Modell
            with open(filepath, 'wb') as f:
                pickle.dump(self.best_model, f)
        
        print(f"💾 Bestes Modell gespeichert: {filepath}")
    
    def create_optimization_report(self, output_dir: str = "data/processed/optimization"):
        """
        Erstellt einen detaillierten Optimierungsbericht.
        
        Args:
            output_dir: Ausgabeverzeichnis für den Bericht
        """
        if self.grid_search is None:
            raise ValueError("GridSearchCV muss erst durchgeführt werden")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # DataFrame mit allen Ergebnissen
        results_df = pd.DataFrame(self.grid_search.cv_results_)
        
        # Top 10 Modelle
        top_models = results_df.nlargest(10, 'mean_test_score')
        
        # Speichere detaillierte Ergebnisse
        results_df.to_csv(f"{output_dir}/grid_search_results.csv", index=False)
        top_models.to_csv(f"{output_dir}/top_10_models.csv", index=False)
        
        # Visualisierungen
        self._create_optimization_plots(results_df, output_dir)
        
        # Text-Bericht
        report_path = f"{output_dir}/optimization_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("F1 MODEL OPTIMIZATION REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Timestamp: {datetime.now()}\n")
            f.write(f"Best Score: {self.best_score:.4f}\n")
            f.write(f"Best Parameters:\n")
            for param, value in self.best_params.items():
                f.write(f"  {param}: {value}\n")
            f.write(f"\nTop 10 Models:\n")
            for i, (_, row) in enumerate(top_models.iterrows(), 1):
                f.write(f"{i}. Score: {row['mean_test_score']:.4f} ± {row['std_test_score']:.4f}\n")
        
        print(f"📊 Optimierungsbericht erstellt: {output_dir}")
    
    def _create_optimization_plots(self, results_df: pd.DataFrame, output_dir: str):
        """
        Erstellt Visualisierungen der Optimierungsergebnisse.
        """
        # Parameter-Wichtigkeit Plot
        plt.figure(figsize=(15, 10))
        
        # Extrahiere Parameter-Werte
        param_cols = [col for col in results_df.columns if col.startswith('param_')]
        
        n_params = len(param_cols)
        n_cols = 3
        n_rows = (n_params + n_cols - 1) // n_cols
        
        for i, param_col in enumerate(param_cols):
            plt.subplot(n_rows, n_cols, i + 1)
            
            param_name = param_col.replace('param_', '')
            
            # Gruppiere nach Parameter-Wert
            grouped = results_df.groupby(param_col)['mean_test_score'].agg(['mean', 'std']).reset_index()
            
            if len(grouped) > 1:
                plt.errorbar(range(len(grouped)), grouped['mean'], yerr=grouped['std'], 
                           marker='o', capsize=5)
                plt.xticks(range(len(grouped)), grouped[param_col], rotation=45)
                plt.title(f'{param_name}')
                plt.ylabel('CV Score')
                plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/parameter_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # Score-Verteilung
        plt.figure(figsize=(10, 6))
        plt.hist(results_df['mean_test_score'], bins=30, alpha=0.7, edgecolor='black')
        plt.axvline(self.best_score, color='red', linestyle='--', 
                   label=f'Best Score: {self.best_score:.4f}')
        plt.xlabel('CV Score')
        plt.ylabel('Häufigkeit')
        plt.title('Verteilung der CV-Scores')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(f"{output_dir}/score_distribution.png", dpi=300, bbox_inches='tight')
        plt.close()

def optimize_f1_model(data_path: str, output_model_path: str = "models/rf_model_best.pkl",
                     grid_type: str = 'comprehensive', cv_folds: int = 5) -> F1ModelOptimizer:
    """
    Hauptfunktion zur F1-Modell-Optimierung.
    
    Args:
        data_path: Pfad zu den Trainingsdaten
        output_model_path: Pfad für das optimierte Modell
        grid_type: Art der Parameter-Suche
        cv_folds: Anzahl CV-Folds
        
    Returns:
        F1ModelOptimizer Instanz
    """
    print(f"🏎️ F1 MODEL OPTIMIZATION PIPELINE")
    print(f"=" * 50)
    
    # Initialisiere Optimizer
    optimizer = F1ModelOptimizer()
    
    # Lade und bereite Daten vor
    X, y, feature_names = optimizer.prepare_data(data_path)
    
    # Optimiere Modell
    optimization_results = optimizer.optimize_model(
        X, y, 
        grid_type=grid_type, 
        cv_folds=cv_folds
    )
    
    # Evaluiere Modell
    evaluation_results = optimizer.evaluate_model(X, y)
    
    # Speichere bestes Modell
    optimizer.save_best_model(output_model_path)
    
    # Erstelle Bericht
    optimizer.create_optimization_report()
    
    print(f"\n🎉 OPTIMIERUNG ABGESCHLOSSEN!")
    print(f"📁 Bestes Modell: {output_model_path}")
    print(f"📊 Bericht: data/processed/optimization/")
    
    return optimizer

if __name__ == "__main__":
    # Konfiguration
    DATA_PATH = "data/full/full_training_data.csv"
    MODEL_OUTPUT = "models/rf_model_best.pkl"
    GRID_TYPE = "comprehensive"  # 'quick', 'comprehensive', 'extensive'
    CV_FOLDS = 5
    
    try:
        # Starte Optimierung
        optimizer = optimize_f1_model(
            data_path=DATA_PATH,
            output_model_path=MODEL_OUTPUT,
            grid_type=GRID_TYPE,
            cv_folds=CV_FOLDS
        )
        
        print("\n✅ F1-Modell-Optimierung erfolgreich!")
        
    except FileNotFoundError as e:
        print(f"❌ Datei nicht gefunden: {e}")
        print("💡 Erstelle Beispiel-Trainingsdaten...")
        
        # Erstelle Beispiel-Daten für Demo
        np.random.seed(42)
        n_samples = 1000
        n_features = 15
        
        X_demo = np.random.randn(n_samples, n_features)
        y_demo = np.random.randint(1, 21, n_samples)  # Positionen 1-20
        
        # Feature-Namen
        feature_names = [f'feature_{i}' for i in range(n_features)]
        
        # DataFrame erstellen
        demo_df = pd.DataFrame(X_demo, columns=feature_names)
        demo_df['final_position'] = y_demo
        demo_df['driver'] = [f'Driver_{i%20}' for i in range(n_samples)]
        demo_df['race'] = [f'Race_{i//50}' for i in range(n_samples)]
        demo_df['year'] = 2023
        
        # Speichere Demo-Daten
        os.makedirs("data/full", exist_ok=True)
        demo_df.to_csv(DATA_PATH, index=False)
        
        print(f"📊 Demo-Daten erstellt: {DATA_PATH}")
        print("🔄 Starte Optimierung mit Demo-Daten...")
        
        # Optimierung mit Demo-Daten
        optimizer = optimize_f1_model(
            data_path=DATA_PATH,
            output_model_path=MODEL_OUTPUT,
            grid_type="quick",  # Schnelle Suche für Demo
            cv_folds=3
        )
        
    except Exception as e:
        print(f"❌ Fehler bei der Optimierung: {e}")
        import traceback
        traceback.print_exc()