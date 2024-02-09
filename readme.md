# UCG Projekt

## Projektidee
Aus den Positionsdaten der Autos werden Einzelfahrten mit einer konfigurierbaren Mindestpunktanzahl isoliert und je nach Fahrtverlauf als Durchgangsverkehr, Inter-Stadt-Verkehr, oder Ausgehendem Verkehr klassifiziert.

Anhand dieser Einelfahrdaten wird ein ML-Modell mittels TensorFlow trainiert dass anschließend anhand eines Fahrtverlaufs ermittelt  um welchesder Fahrtverlaufsklassen es sich bei der Fahrt handelt.

## How To

1. Einzelfahrten extrahieren.
2. ML Modell trainieren

### 1. Einzelfahrten extrahieren
seperate_singles.py ausführen: Die Fahrtdaten werden automatisch in das data/ Verzeichnis geleaden.

### 2. ML Modell trainieren
machine_learning.py ausführen. 

### Config
Das Projekt ist per YAML Konfigurationsdateien im config/ Ordner anpassbar.
