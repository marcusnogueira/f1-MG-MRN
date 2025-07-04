# GitHub Setup Anleitung für F1 Predict Pro

## 🚀 Schritt-für-Schritt Anleitung

### 1. Repository auf GitHub erstellen

1. Gehen Sie zu: https://github.com/new
2. **Repository name**: `f1predictpro`
3. **Description**: `F1 Predict Pro - Machine Learning based Formula 1 race prediction and betting analysis system`
4. **Visibility**: Public (oder Private nach Wunsch)
5. **WICHTIG**: ❌ NICHT "Add a README file" ankreuzen
6. **WICHTIG**: ❌ NICHT ".gitignore" hinzufügen
7. **WICHTIG**: ❌ NICHT "Choose a license" auswählen
8. Klicken Sie auf "Create repository"

### 2. Git-Kommandos ausführen

Öffnen Sie PowerShell oder Command Prompt und führen Sie diese Kommandos aus:

```bash
# 1. Zum Projektverzeichnis navigieren
cd "c:\Users\mgoeb\Desktop\Projekt\f1predictpro"

# 2. Git Repository initialisieren
git init

# 3. Alle Dateien hinzufügen
git add .

# 4. Ersten Commit erstellen
git commit -m "Initial commit: F1 Predict Pro - ML-based F1 prediction system"

# 5. Main Branch erstellen
git branch -M main

# 6. Remote Repository hinzufügen (ERSETZEN SIE 'IHR_USERNAME')
git remote add origin https://github.com/IHR_USERNAME/f1predictpro.git

# 7. Code zu GitHub pushen
git push -u origin main
```

### 3. Wichtige Hinweise

- **Ersetzen Sie `IHR_USERNAME`** in Schritt 6 durch Ihren tatsächlichen GitHub-Benutzernamen
- Falls Sie nach Anmeldedaten gefragt werden, verwenden Sie:
  - **Username**: Ihr GitHub-Benutzername
  - **Password**: Ihr Personal Access Token (NICHT Ihr GitHub-Passwort)

### 4. Troubleshooting

#### Problem: "Authentication failed"
**Lösung**: Verwenden Sie Ihren Personal Access Token als Passwort, nicht Ihr GitHub-Passwort.

#### Problem: "Repository not found"
**Lösung**: Überprüfen Sie, ob:
- Das Repository auf GitHub erstellt wurde
- Der Username in der URL korrekt ist
- Das Repository öffentlich ist (falls Sie keinen Zugriff haben)

#### Problem: "Permission denied"
**Lösung**: Stellen Sie sicher, dass Ihr Personal Access Token die folgenden Berechtigungen hat:
- ✅ `repo` (Full control of private repositories)
- ✅ `public_repo` (Access public repositories)

### 5. Nach erfolgreichem Push

Ihr Repository sollte jetzt verfügbar sein unter:
`https://github.com/IHR_USERNAME/f1predictpro`

### 6. Zukünftige Updates

Für zukünftige Änderungen verwenden Sie:
```bash
git add .
git commit -m "Beschreibung der Änderungen"
git push
```

---

## 📁 Was wird hochgeladen?

✅ **Enthalten**:
- Alle Python-Dateien (.py)
- Konfigurationsdateien (.json)
- README.md und Dokumentation
- requirements.txt
- .gitignore

❌ **Ausgeschlossen** (durch .gitignore):
- Virtual Environment (venv/)
- Cache-Dateien (__pycache__/)
- .env Datei (Umgebungsvariablen)
- Große Datenfiles und Modelle
- Log-Dateien

Dies ist korrekt und gewünscht für ein sauberes Repository!

---

**Bei Problemen**: Erstellen Sie ein Issue oder kontaktieren Sie den Support.