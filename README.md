# Metronome Application

Une application métronome simple avec interface graphique, permettant de régler le tempo en BPM (Battements Par Minute).

## Fonctionnalités

- Interface graphique intuitive
- Contrôle du tempo (BPM) de 40 à 208
- Indicateur visuel des battements
- Bouton Start/Stop

## Installation avec Docker

1. Assurez-vous d'avoir Docker et Docker Compose installés
2. Construisez et lancez l'application :
```bash
docker-compose up --build
```

## Installation manuelle

1. Assurez-vous d'avoir Python 3.x installé
2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

1. Lancez l'application :
```bash
# Avec Docker
docker-compose up

# Sans Docker
python src/metronome.py
```

2. Utilisez le spinbox pour régler le BPM (40-208)
3. Cliquez sur "Start" pour démarrer le métronome
4. Cliquez sur "Stop" pour arrêter

## Structure du projet

```
metronome/
├── src/
│   └── metronome.py
├── assets/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
``` 