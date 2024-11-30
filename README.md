
# Meteobot - Bot Météo Automatisé

Meteobot est un bot Python qui récupère les données météo actuelles et les prévisions sur 5 jours à partir de l'API OpenWeatherMap et les envoie automatiquement sur un canal Slack via des **GitHub Actions**.

## Fonctionnalités

- 📡 **Météo Actuelle** : Affiche la température, la température ressentie, l'humidité, la vitesse du vent et une description de la météo actuelle.
- 📅 **Prévisions à 5 jours** : Prévisions détaillées toutes les 3 heures (06:00, 09:00, 12:00 et 15:00) pour 5 jours.
- 🌟 **Tableau 2x2** : Présentation des prévisions dans un tableau clair et structuré avec des émojis.
- 🔄 **Automatisation** : Envoi automatique des prévisions quotidiennes sur Slack via GitHub Actions.

## Prérequis

1. **Compte OpenWeatherMap** :
   - Obtenez une clé API gratuite sur [OpenWeatherMap](https://openweathermap.org/api).

2. **Espace Slack** :
   - Configurez un token Slack avec des permissions pour envoyer des messages à votre canal Slack.

3. **GitHub Repository** :
   - Créez un dépôt GitHub pour héberger le code et configurer GitHub Actions.

4. **Python** :
   - Python 3.9+ installé pour les tests locaux.

## Installation et Configuration

1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/achery/meteobot.git
   cd meteobot
   ```

2. Installez les dépendances :
   ```bash
   pip install requests
   ```

3. Configurez les secrets GitHub :
   - Accédez à **Settings > Secrets and variables > Actions** et ajoutez les clés suivantes :
     - `SLACK_TOKEN`: Votre token Slack.
     - `OPENWEATHER_API_KEY`: Votre clé API OpenWeatherMap.
     - `CHANNEL_ID`: L'ID de votre canal Slack.
     - `CITY`: Le nom de la ville pour la météo (ex. `Strasbourg`).

4. Testez localement :
   ```bash
   python meteobot.py
   ```

## Automatisation avec GitHub Actions

Le workflow GitHub Actions exécute automatiquement le script chaque jour à une heure définie.

### Configuration du Workflow

Le fichier de workflow se trouve dans `.github/workflows/meteobot.yml` :

```yaml
name: Meteobot Scheduler

on:
  schedule:
    - cron: '0 8 * * *'  # Exécuter tous les jours à 08:00 UTC
  workflow_dispatch:  # Permet d'exécuter manuellement depuis l'interface GitHub

jobs:
  run_meteobot:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests

      - name: Run Meteobot Script
        env:
          SLACK_TOKEN: ${{ secrets.SLACK_TOKEN }}
          OPENWEATHER_API_KEY: ${{ secrets.OPENWEATHER_API_KEY }}
          CHANNEL_ID: ${{ secrets.CHANNEL_ID }}
          CITY: ${{ secrets.CITY }}
        run: |
          python meteobot.py
```

Une fois configuré, le workflow s'exécutera automatiquement chaque jour à 08:00 UTC ou manuellement via l'onglet **Actions**.

## Exemple de Résultat sur Slack

```
🌤️ Météo actuelle à Strasbourg
Température : 12°C (Ressenti : 10°C)
Description : Ensoleillé
Humidité : 60%
Vent : 15 km/h

📅 Lundi 27 novembre
06:00 | 🌤️ 12°C (Ressenti : 11°C)
09:00 | ☁️ 13°C (Ressenti : 12°C)
12:00 | 🌤️ 14°C (Ressenti : 13°C)
15:00 | 🌧️ 15°C (Ressenti : 14°C)
```

## Personnalisation

- **Heures des prévisions** :
  Modifiez la liste `selected_hours` dans le script `meteobot.py` pour inclure d'autres heures :
  ```python
  selected_hours = ["06:00:00", "09:00:00", "12:00:00", "15:00:00"]
  ```

- **Ville par défaut** :
  Remplacez la valeur par défaut de `CITY` dans le script :
  ```python
  city = os.getenv("CITY", "Paris")
  ```

## Contributions

Les contributions sont les bienvenues ! Si vous souhaitez ajouter des fonctionnalités ou corriger un bug, ouvrez une [issue](https://github.com/achery/meteobot/issues) ou soumettez une pull request.

## Licence

Ce projet est sous licence MIT. Consultez le fichier `LICENSE` pour plus de détails.
