from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import os
import random

def scrape_stake_f1_odds(url, output_file="data/live/stake_odds.csv", max_retries=3):
    """
    Robuster Selenium-Scraper für Stake.com F1-Quoten.
    
    Args:
        url: Stake.com URL für F1 Outright-Quoten
        output_file: Pfad für die Ausgabe-CSV
        max_retries: Maximale Anzahl von Wiederholungsversuchen
    
    Returns:
        List of dictionaries mit Fahrer und Quoten
    """
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    import random
    
    # Verschiedene CSS-Selektoren für Robustheit
    SELECTORS = {
        'market_rows': [
            ".MarketRow__row",
            "[data-testid='market-row']",
            ".market-row",
            ".outcome-row",
            "[class*='market'][class*='row']"
        ],
        'driver_names': [
            ".MarketRow__name",
            "[data-testid='outcome-name']",
            ".outcome-name",
            ".driver-name",
            "[class*='name']"
        ],
        'odds_prices': [
            ".MarketRow__price",
            "[data-testid='outcome-price']",
            ".outcome-price",
            ".odds-price",
            "[class*='price']",
            "[class*='odd']"
        ]
    }
    
    for attempt in range(max_retries):
        driver = None
        try:
            print(f"🔄 Versuch {attempt + 1}/{max_retries} - Scraping Stake.com...")
            
            # Chrome-Optionen für Robustheit
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            driver = webdriver.Chrome(options=options)
            driver.implicitly_wait(10)
            
            print(f"📡 Lade URL: {url}")
            driver.get(url)
            
            # Warte auf Seitenladung mit zufälliger Verzögerung
            wait_time = random.uniform(3, 7)
            print(f"⏳ Warte {wait_time:.1f} Sekunden auf Seitenladung...")
            time.sleep(wait_time)
            
            # Versuche verschiedene Selektoren
            records = []
            wait = WebDriverWait(driver, 15)
            
            # Scroll nach unten für dynamisches Laden
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Versuche verschiedene Selector-Kombinationen
            for market_selector in SELECTORS['market_rows']:
                try:
                    print(f"🔍 Versuche Selector: {market_selector}")
                    
                    # Warte auf Elemente
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, market_selector)))
                    
                    items = driver.find_elements(By.CSS_SELECTOR, market_selector)
                    print(f"📊 {len(items)} Markt-Zeilen gefunden")
                    
                    if len(items) == 0:
                        continue
                    
                    # Extrahiere Daten aus gefundenen Elementen
                    for item in items:
                        driver_name = None
                        odds_value = None
                        
                        # Versuche verschiedene Name-Selektoren
                        for name_selector in SELECTORS['driver_names']:
                            try:
                                name_element = item.find_element(By.CSS_SELECTOR, name_selector)
                                driver_name = name_element.text.strip()
                                if driver_name:
                                    break
                            except NoSuchElementException:
                                continue
                        
                        # Versuche verschiedene Preis-Selektoren
                        for price_selector in SELECTORS['odds_prices']:
                            try:
                                price_element = item.find_element(By.CSS_SELECTOR, price_selector)
                                odds_text = price_element.text.strip()
                                # Bereinige Odds-Text (entferne Währungssymbole, etc.)
                                odds_clean = ''.join(c for c in odds_text if c.isdigit() or c == '.')
                                if odds_clean:
                                    odds_value = float(odds_clean)
                                    break
                            except (NoSuchElementException, ValueError):
                                continue
                        
                        # Füge gültige Daten hinzu
                        if driver_name and odds_value and odds_value > 1.0:
                            # Normalisiere Fahrernamen
                            driver_clean = clean_driver_name(driver_name)
                            if driver_clean:
                                records.append({
                                    "driver": driver_clean,
                                    "odds": odds_value,
                                    "raw_name": driver_name
                                })
                    
                    if records:
                        break  # Erfolgreich, verlasse Selector-Schleife
                        
                except TimeoutException:
                    print(f"⏰ Timeout für Selector: {market_selector}")
                    continue
                except Exception as e:
                    print(f"❌ Fehler mit Selector {market_selector}: {e}")
                    continue
            
            if records:
                print(f"✅ {len(records)} Quoten erfolgreich extrahiert")
                
                # Speichere in CSV
                df = pd.DataFrame(records)
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                df.to_csv(output_file, index=False)
                print(f"💾 Quoten gespeichert: {output_file}")
                
                return records
            else:
                print("⚠️ Keine Quoten gefunden, versuche erneut...")
                
        except Exception as e:
            print(f"❌ Fehler beim Scraping (Versuch {attempt + 1}): {e}")
            
        finally:
            if driver:
                driver.quit()
        
        # Warte vor erneutem Versuch
        if attempt < max_retries - 1:
            wait_time = random.uniform(5, 10)
            print(f"⏳ Warte {wait_time:.1f} Sekunden vor erneutem Versuch...")
            time.sleep(wait_time)
    
    print(f"❌ Scraping nach {max_retries} Versuchen fehlgeschlagen")
    return []

def clean_driver_name(raw_name):
    """
    Bereinigt und normalisiert Fahrernamen.
    
    Args:
        raw_name: Roher Fahrername von der Website
    
    Returns:
        Bereinigter 3-Buchstaben-Code oder vollständiger Name
    """
    if not raw_name:
        return None
    
    # Mapping für bekannte Fahrer
    DRIVER_MAPPING = {
        'max verstappen': 'VER',
        'verstappen': 'VER',
        'lewis hamilton': 'HAM',
        'hamilton': 'HAM',
        'charles leclerc': 'LEC',
        'leclerc': 'LEC',
        'george russell': 'RUS',
        'russell': 'RUS',
        'fernando alonso': 'ALO',
        'alonso': 'ALO',
        'carlos sainz': 'SAI',
        'sainz': 'SAI',
        'lando norris': 'NOR',
        'norris': 'NOR',
        'oscar piastri': 'PIA',
        'piastri': 'PIA',
        'pierre gasly': 'GAS',
        'gasly': 'GAS',
        'esteban ocon': 'OCO',
        'ocon': 'OCO'
    }
    
    name_lower = raw_name.lower().strip()
    
    # Direkte Zuordnung
    if name_lower in DRIVER_MAPPING:
        return DRIVER_MAPPING[name_lower]
    
    # Versuche Teilstring-Matching
    for full_name, code in DRIVER_MAPPING.items():
        if full_name in name_lower or any(part in name_lower for part in full_name.split()):
            return code
    
    # Falls kein Mapping gefunden, gebe bereinigten Namen zurück
    return raw_name.strip().upper()[:3] if len(raw_name.strip()) >= 3 else raw_name.strip().upper()

def scrape_and_save_stake_odds(stake_url=None, output_file="data/live/stake_odds.csv"):
    """
    Hauptfunktion zum Scrapen und Speichern von Stake.com F1-Quoten.
    
    Args:
        stake_url: URL der Stake.com F1-Seite (optional)
        output_file: Pfad für die Ausgabe-CSV
    
    Returns:
        DataFrame mit gescrapten Quoten
    """
    # Standard-URL falls keine angegeben
    if not stake_url:
        stake_url = "https://stake.com/sports/formula-1"
        print("⚠️ Keine URL angegeben, verwende Standard-URL")
        print("💡 Tipp: Verwende die spezifische Outright-URL für bessere Ergebnisse")
    
    print(f"🏎️ Starte Scraping von Stake.com F1-Quoten...")
    print(f"🌐 URL: {stake_url}")
    
    # Scrape Quoten
    records = scrape_stake_f1_odds(stake_url, output_file)
    
    if records:
        df = pd.DataFrame(records)
        print(f"\n📊 Erfolgreich gescrapte Quoten:")
        print(df[['driver', 'odds']].to_string(index=False))
        return df
    else:
        print("❌ Keine Quoten konnten gescrapt werden")
        return pd.DataFrame()

if __name__ == "__main__":
    # Beispiel-Verwendung
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape F1 odds from Stake.com")
    parser.add_argument("--url", type=str, help="Stake.com F1 URL")
    parser.add_argument("--output", type=str, default="data/live/stake_odds.csv", help="Output CSV file")
    
    args = parser.parse_args()
    
    try:
        df = scrape_and_save_stake_odds(args.url, args.output)
        if not df.empty:
            print(f"\n✅ Scraping erfolgreich abgeschlossen!")
            print(f"📁 Datei gespeichert: {args.output}")
        else:
            print(f"\n❌ Scraping fehlgeschlagen")
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    url = "https://stake.com/de/sports/outright/formula-1/formula-1/formula-1-2025/44940068-formula-1-2024-practice-3-head2head"
    df = scrape_stake_f1_odds(url)
    df.to_csv("../data/stake_odds_next_f1.csv", index=False)  # Speichern im data/
    print(df)
