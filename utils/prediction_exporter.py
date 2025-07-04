import pandas as pd
import numpy as np
from datetime import datetime
import os
from typing import Optional, Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import warnings
warnings.filterwarnings('ignore')

class F1PredictionExporter:
    """
    Klasse zum Export von F1-Vorhersagen als formatierte PDF oder CSV.
    """
    
    def __init__(self):
        self.driver_colors = {
            'Max Verstappen': '#0600EF',
            'Sergio Perez': '#0600EF',
            'Lewis Hamilton': '#00D2BE',
            'George Russell': '#00D2BE',
            'Charles Leclerc': '#DC143C',
            'Carlos Sainz': '#DC143C',
            'Lando Norris': '#FF8700',
            'Oscar Piastri': '#FF8700',
            'Fernando Alonso': '#006F62',
            'Lance Stroll': '#006F62',
            'Esteban Ocon': '#0090FF',
            'Pierre Gasly': '#0090FF',
            'Alexander Albon': '#005AFF',
            'Logan Sargeant': '#005AFF',
            'Valtteri Bottas': '#900000',
            'Zhou Guanyu': '#900000',
            'Kevin Magnussen': '#FFFFFF',
            'Nico Hulkenberg': '#FFFFFF',
            'Yuki Tsunoda': '#2B4562',
            'Daniel Ricciardo': '#2B4562'
        }
    
    def load_probabilities(self, csv_path: str) -> pd.DataFrame:
        """
        Lädt Wahrscheinlichkeiten aus CSV-Datei.
        
        Args:
            csv_path: Pfad zur CSV-Datei mit Wahrscheinlichkeiten
            
        Returns:
            DataFrame mit Wahrscheinlichkeiten
        """
        try:
            df = pd.read_csv(csv_path)
            print(f"📊 Wahrscheinlichkeiten geladen: {df.shape}")
            return df
        except FileNotFoundError:
            print(f"❌ Datei nicht gefunden: {csv_path}")
            raise
        except Exception as e:
            print(f"❌ Fehler beim Laden: {e}")
            raise
    
    def prepare_export_data(self, df: pd.DataFrame, race_name: str = None) -> Dict:
        """
        Bereitet Daten für den Export vor.
        
        Args:
            df: DataFrame mit Wahrscheinlichkeiten
            race_name: Name des Rennens
            
        Returns:
            Dictionary mit aufbereiteten Daten
        """
        # Extrahiere Fahrer-Spalte
        if 'driver' in df.columns:
            drivers = df['driver'].tolist()
        elif 'Driver' in df.columns:
            drivers = df['Driver'].tolist()
        else:
            drivers = [f"Driver {i+1}" for i in range(len(df))]
        
        # Extrahiere Wahrscheinlichkeits-Spalten (P1, P2, etc.)
        prob_cols = [col for col in df.columns if col.startswith('P') and col[1:].isdigit()]
        prob_cols = sorted(prob_cols, key=lambda x: int(x[1:]))
        
        if not prob_cols:
            # Fallback: alle numerischen Spalten außer driver
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            prob_cols = [col for col in numeric_cols if col not in ['driver', 'Driver']]
        
        # Erstelle Export-DataFrame
        export_data = {
            'Fahrer': drivers,
            'Höchste Wahrscheinlichkeit': [],
            'Wahrscheinlichste Position': [],
            'P1 Chance': [],
            'P2 Chance': [],
            'P3 Chance': [],
            'Top 5 Chance': [],
            'Top 10 Chance': []
        }
        
        for i, driver in enumerate(drivers):
            # Wahrscheinlichkeiten für diesen Fahrer
            probs = df.iloc[i][prob_cols].values
            
            # Höchste Wahrscheinlichkeit und Position
            max_prob_idx = np.argmax(probs)
            max_prob = probs[max_prob_idx]
            most_likely_pos = int(prob_cols[max_prob_idx][1:])
            
            export_data['Höchste Wahrscheinlichkeit'].append(f"{max_prob:.1%}")
            export_data['Wahrscheinlichste Position'].append(f"P{most_likely_pos}")
            
            # Spezifische Positionen
            p1_prob = probs[0] if len(probs) > 0 else 0
            p2_prob = probs[1] if len(probs) > 1 else 0
            p3_prob = probs[2] if len(probs) > 2 else 0
            
            export_data['P1 Chance'].append(f"{p1_prob:.1%}")
            export_data['P2 Chance'].append(f"{p2_prob:.1%}")
            export_data['P3 Chance'].append(f"{p3_prob:.1%}")
            
            # Top 5 und Top 10 Chancen
            top5_prob = sum(probs[:5]) if len(probs) >= 5 else sum(probs)
            top10_prob = sum(probs[:10]) if len(probs) >= 10 else sum(probs)
            
            export_data['Top 5 Chance'].append(f"{top5_prob:.1%}")
            export_data['Top 10 Chance'].append(f"{top10_prob:.1%}")
        
        # Bestimme beste Wetten (höchste P1-P3 Wahrscheinlichkeiten)
        p1_probs = df[prob_cols[0]].values if len(prob_cols) > 0 else np.zeros(len(drivers))
        p2_probs = df[prob_cols[1]].values if len(prob_cols) > 1 else np.zeros(len(drivers))
        p3_probs = df[prob_cols[2]].values if len(prob_cols) > 2 else np.zeros(len(drivers))
        
        best_bets = {
            'P1': {
                'driver': drivers[np.argmax(p1_probs)],
                'probability': f"{np.max(p1_probs):.1%}"
            },
            'P2': {
                'driver': drivers[np.argmax(p2_probs)],
                'probability': f"{np.max(p2_probs):.1%}"
            },
            'P3': {
                'driver': drivers[np.argmax(p3_probs)],
                'probability': f"{np.max(p3_probs):.1%}"
            }
        }
        
        return {
            'export_df': pd.DataFrame(export_data),
            'race_name': race_name or "F1 Grand Prix",
            'timestamp': datetime.now(),
            'best_bets': best_bets,
            'total_drivers': len(drivers)
        }
    
    def export_to_csv(self, data: Dict, output_path: str) -> str:
        """
        Exportiert Daten als formatierte CSV.
        
        Args:
            data: Aufbereitete Export-Daten
            output_path: Ausgabepfad
            
        Returns:
            Pfad zur erstellten CSV-Datei
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Haupttabelle
        df = data['export_df']
        
        # Füge Metadaten hinzu
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# F1 VORHERSAGE EXPORT\n")
            f.write(f"# Rennen: {data['race_name']}\n")
            f.write(f"# Erstellt: {data['timestamp'].strftime('%d.%m.%Y %H:%M')}\n")
            f.write(f"# Anzahl Fahrer: {data['total_drivers']}\n")
            f.write(f"#\n")
            f.write(f"# BESTE WETTEN:\n")
            for pos, bet_info in data['best_bets'].items():
                f.write(f"# {pos}: {bet_info['driver']} ({bet_info['probability']})\n")
            f.write(f"#\n")
            f.write(f"\n")
        
        # Füge DataFrame hinzu
        df.to_csv(output_path, mode='a', index=False, encoding='utf-8')
        
        print(f"📄 CSV exportiert: {output_path}")
        return output_path
    
    def export_to_pdf(self, data: Dict, output_path: str) -> str:
        """
        Exportiert Daten als formatierte PDF.
        
        Args:
            data: Aufbereitete Export-Daten
            output_path: Ausgabepfad
            
        Returns:
            Pfad zur erstellten PDF-Datei
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with PdfPages(output_path) as pdf:
            # Seite 1: Übersicht und beste Wetten
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle(f"F1 Vorhersage: {data['race_name']}", fontsize=20, fontweight='bold')
            
            # Titel-Info
            ax1.text(0.5, 0.8, f"Rennen: {data['race_name']}", 
                    ha='center', va='center', fontsize=16, fontweight='bold',
                    transform=ax1.transAxes)
            ax1.text(0.5, 0.6, f"Erstellt: {data['timestamp'].strftime('%d.%m.%Y %H:%M')}", 
                    ha='center', va='center', fontsize=12,
                    transform=ax1.transAxes)
            ax1.text(0.5, 0.4, f"Anzahl Fahrer: {data['total_drivers']}", 
                    ha='center', va='center', fontsize=12,
                    transform=ax1.transAxes)
            ax1.axis('off')
            
            # Beste Wetten
            ax2.text(0.5, 0.9, "BESTE WETTEN", ha='center', va='center', 
                    fontsize=16, fontweight='bold', transform=ax2.transAxes)
            
            y_pos = 0.7
            for pos, bet_info in data['best_bets'].items():
                ax2.text(0.1, y_pos, f"{pos}:", ha='left', va='center', 
                        fontsize=12, fontweight='bold', transform=ax2.transAxes)
                ax2.text(0.3, y_pos, f"{bet_info['driver']}", ha='left', va='center', 
                        fontsize=12, transform=ax2.transAxes)
                ax2.text(0.8, y_pos, f"{bet_info['probability']}", ha='right', va='center', 
                        fontsize=12, fontweight='bold', color='green', transform=ax2.transAxes)
                y_pos -= 0.15
            ax2.axis('off')
            
            # P1 Wahrscheinlichkeiten (Top 10)
            df = data['export_df']
            p1_data = df[['Fahrer', 'P1 Chance']].copy()
            p1_data['P1_numeric'] = p1_data['P1 Chance'].str.rstrip('%').astype(float)
            p1_top10 = p1_data.nlargest(10, 'P1_numeric')
            
            bars = ax3.barh(range(len(p1_top10)), p1_top10['P1_numeric'])
            ax3.set_yticks(range(len(p1_top10)))
            ax3.set_yticklabels(p1_top10['Fahrer'], fontsize=10)
            ax3.set_xlabel('P1 Wahrscheinlichkeit (%)')
            ax3.set_title('Top 10 P1 Chancen', fontweight='bold')
            ax3.grid(True, alpha=0.3)
            
            # Farbkodierung der Balken
            for i, (bar, driver) in enumerate(zip(bars, p1_top10['Fahrer'])):
                if driver in self.driver_colors:
                    bar.set_color(self.driver_colors[driver])
                else:
                    bar.set_color(f'C{i}')
            
            # Wahrscheinlichkeitsverteilung
            positions = ['P1', 'P2', 'P3', 'Top 5', 'Top 10']
            avg_probs = []
            for pos in positions:
                if pos + ' Chance' in df.columns:
                    prob_col = df[pos + ' Chance'].str.rstrip('%').astype(float)
                    avg_probs.append(prob_col.mean())
                else:
                    avg_probs.append(0)
            
            ax4.bar(positions, avg_probs, color=['gold', 'silver', '#CD7F32', 'lightblue', 'lightgreen'])
            ax4.set_ylabel('Durchschnittliche Wahrscheinlichkeit (%)')
            ax4.set_title('Durchschnittliche Chancen', fontweight='bold')
            ax4.grid(True, alpha=0.3)
            
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()
            
            # Seite 2: Detaillierte Tabelle
            fig, ax = plt.subplots(figsize=(16, 12))
            fig.suptitle(f"Detaillierte Wahrscheinlichkeiten - {data['race_name']}", 
                        fontsize=16, fontweight='bold')
            
            # Tabelle erstellen
            table_data = df.values
            table = ax.table(cellText=table_data, colLabels=df.columns,
                           cellLoc='center', loc='center')
            
            # Tabellen-Styling
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1, 2)
            
            # Header-Styling
            for i in range(len(df.columns)):
                table[(0, i)].set_facecolor('#4CAF50')
                table[(0, i)].set_text_props(weight='bold', color='white')
            
            # Zeilen-Styling (abwechselnde Farben)
            for i in range(1, len(df) + 1):
                for j in range(len(df.columns)):
                    if i % 2 == 0:
                        table[(i, j)].set_facecolor('#f0f0f0')
            
            ax.axis('off')
            
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()
        
        print(f"📄 PDF exportiert: {output_path}")
        return output_path
    
    def export_predictions(self, csv_path: str, race_name: str = None, 
                         output_dir: str = "data/exports", 
                         formats: List[str] = ['csv', 'pdf']) -> Dict[str, str]:
        """
        Hauptfunktion zum Export von Vorhersagen.
        
        Args:
            csv_path: Pfad zur CSV-Datei mit Wahrscheinlichkeiten
            race_name: Name des Rennens
            output_dir: Ausgabeverzeichnis
            formats: Liste der Export-Formate ('csv', 'pdf')
            
        Returns:
            Dictionary mit Pfaden zu den erstellten Dateien
        """
        print(f"📦 Starte Vorhersage-Export...")
        
        # Lade Daten
        df = self.load_probabilities(csv_path)
        
        # Bereite Export-Daten vor
        data = self.prepare_export_data(df, race_name)
        
        # Erstelle Ausgabeverzeichnis
        os.makedirs(output_dir, exist_ok=True)
        
        # Dateinamen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        race_safe = (race_name or "F1_Race").replace(" ", "_").replace("/", "_")
        
        exported_files = {}
        
        # Export in gewünschten Formaten
        if 'csv' in formats:
            csv_path = os.path.join(output_dir, f"F1_Prediction_{race_safe}_{timestamp}.csv")
            exported_files['csv'] = self.export_to_csv(data, csv_path)
        
        if 'pdf' in formats:
            pdf_path = os.path.join(output_dir, f"F1_Prediction_{race_safe}_{timestamp}.pdf")
            exported_files['pdf'] = self.export_to_pdf(data, pdf_path)
        
        print(f"✅ Export abgeschlossen!")
        print(f"📁 Dateien: {list(exported_files.values())}")
        
        return exported_files

def create_sample_predictions(output_path: str = "data/live/sample_predictions.csv"):
    """
    Erstellt Beispiel-Vorhersagedaten für Tests.
    
    Args:
        output_path: Pfad für die Beispiel-CSV
    """
    drivers = [
        'Max Verstappen', 'Sergio Perez', 'Lewis Hamilton', 'George Russell',
        'Charles Leclerc', 'Carlos Sainz', 'Lando Norris', 'Oscar Piastri',
        'Fernando Alonso', 'Lance Stroll', 'Esteban Ocon', 'Pierre Gasly',
        'Alexander Albon', 'Logan Sargeant', 'Valtteri Bottas', 'Zhou Guanyu',
        'Kevin Magnussen', 'Nico Hulkenberg', 'Yuki Tsunoda', 'Daniel Ricciardo'
    ]
    
    np.random.seed(42)
    
    # Erstelle realistische Wahrscheinlichkeitsverteilungen
    data = {'driver': drivers}
    
    for pos in range(1, 21):
        # Höhere Wahrscheinlichkeiten für bessere Fahrer in vorderen Positionen
        probs = []
        for i, driver in enumerate(drivers):
            if pos <= 3:  # Podium
                base_prob = max(0.01, 0.3 - i * 0.02)  # Bessere Fahrer haben höhere Chancen
            elif pos <= 10:  # Punkte
                base_prob = max(0.01, 0.15 - abs(pos - 5 - i) * 0.01)
            else:  # Hinteres Feld
                base_prob = max(0.01, 0.1 - abs(pos - 15 - i) * 0.005)
            
            # Füge Zufälligkeit hinzu
            prob = base_prob + np.random.normal(0, 0.02)
            prob = max(0.001, min(0.5, prob))  # Begrenze Wahrscheinlichkeiten
            probs.append(prob)
        
        data[f'P{pos}'] = probs
    
    # Normalisiere Wahrscheinlichkeiten pro Fahrer
    df = pd.DataFrame(data)
    prob_cols = [f'P{i}' for i in range(1, 21)]
    
    for i in range(len(drivers)):
        row_sum = df.loc[i, prob_cols].sum()
        df.loc[i, prob_cols] = df.loc[i, prob_cols] / row_sum
    
    # Speichere
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"📊 Beispiel-Vorhersagen erstellt: {output_path}")
    return output_path

if __name__ == "__main__":
    # Beispiel-Verwendung
    exporter = F1PredictionExporter()
    
    # Erstelle Beispiel-Daten falls nötig
    sample_path = "data/live/sample_predictions.csv"
    if not os.path.exists(sample_path):
        create_sample_predictions(sample_path)
    
    try:
        # Exportiere Vorhersagen
        exported_files = exporter.export_predictions(
            csv_path=sample_path,
            race_name="Spanish Grand Prix 2025",
            output_dir="data/exports",
            formats=['csv', 'pdf']
        )
        
        print("\n🎉 Export-Demo erfolgreich!")
        for format_type, file_path in exported_files.items():
            print(f"📄 {format_type.upper()}: {file_path}")
        
    except Exception as e:
        print(f"❌ Fehler beim Export: {e}")
        import traceback
        traceback.print_exc()