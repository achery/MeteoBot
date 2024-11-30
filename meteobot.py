import requests
import os
from datetime import datetime

# Table de traduction pour les mois et jours en français
MONTHS_FR = {
    1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: "mai", 6: "juin",
    7: "juillet", 8: "août", 9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
}
DAYS_FR = {
    0: "lundi", 1: "mardi", 2: "mercredi", 3: "jeudi", 4: "vendredi", 5: "samedi", 6: "dimanche"
}

def format_date_manual(date_str):
    """Formatte une date ISO (2024-11-28) en texte lisible en français."""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    day_name = DAYS_FR[date_obj.weekday()]  # Nom du jour
    month_name = MONTHS_FR[date_obj.month]  # Nom du mois
    return f"{day_name.capitalize()} {date_obj.day} {month_name}"

def get_weather(city, api_key):
    """Récupère la météo actuelle depuis OpenWeatherMap."""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=fr"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        temp = data['main']['temp']
        description = data['weather'][0]['description']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed'] * 3.6  # Conversion en km/h
        alert = ""
        if "pluie" in description or "orage" in description:
            alert = "\n☔ *Prévoyez un parapluie !*"
        elif "neige" in description:
            alert = "\n❄️ *Attention à la neige !*"
        return (f"🌤️ *Météo actuelle à {city}*\n"
                f"Température : *{temp}°C*\n"
                f"Description : *{description.capitalize()}*\n"
                f"Humidité : *{humidity}%*\n"
                f"Vent : *{wind_speed:.1f} km/h*{alert}")
    except requests.RequestException as e:
        return f"Erreur : Impossible de récupérer la météo actuelle ({e})."

def get_forecast(city, api_key):
    """Récupère les prévisions météo pour les 5 prochains jours à 06:00, 09:00, 12:00 et 15:00."""
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric&lang=fr"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        forecasts = {}
        selected_hours = ["06:00:00", "09:00:00", "12:00:00", "15:00:00"]
        for item in data['list']:
            date, time = item['dt_txt'].split(" ")
            if time in selected_hours:  # Filtrer par les heures spécifiques
                temp = item['main']['temp']
                description = item['weather'][0]['description']
                humidity = item['main']['humidity']
                wind_speed = item['wind']['speed'] * 3.6  # Conversion en km/h
                emoji = get_emoji(description)
                if date not in forecasts:
                    forecasts[date] = {}
                forecasts[date][time] = f"{emoji} {temp}°C, {description.capitalize()}\nHumidité : {humidity}%, Vent : {wind_speed:.1f} km/h"
        return forecasts
    except requests.RequestException as e:
        print(f"Erreur : Impossible de récupérer les prévisions météo ({e}).")
        return {}

def get_emoji(description):
    """Associe un émoji à la description météo en français."""
    description = description.lower()
    if "clair" in description or "ensoleillé" in description or "ciel dégagé" in description:
        return "☀️"
    elif "peu nuageux" in description:
        return "🌤️"
    elif "nuageux" in description or "couvert" in description:
        return "☁️"
    elif "pluie" in description:
        return "🌧️"
    elif "neige" in description:
        return "❄️"
    elif "orage" in description:
        return "⛈️"
    elif "brouillard" in description or "brume" in description:
        return "🌫️"
    else:
        return "🌈"  # Cas par défaut

def post_to_slack(blocks, token, channel_id):
    """Envoie un message formaté avec des blocs sur Slack."""
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {
        "channel": channel_id,
        "blocks": blocks
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200 or not response.json().get('ok'):
        print("Erreur lors de l'envoi du message à Slack :", response.json())

if __name__ == "__main__":
    # Charger les secrets depuis les variables d'environnement
    slack_token = os.getenv("SLACK_TOKEN")
    openweather_api_key = os.getenv("OPENWEATHER_API_KEY")
    channel_id = os.getenv("CHANNEL_ID")
    city = os.getenv("CITY", "Strasbourg")  # Valeur par défaut si CITY n'est pas défini

    # Récupérer la météo actuelle
    weather_message = get_weather(city, openweather_api_key)
    print("Météo actuelle récupérée :", weather_message)

    # Récupérer les prévisions météo
    forecasts = get_forecast(city, openweather_api_key)
    if forecasts:
        print("Prévisions récupérées.")

    # Créer des blocs pour Slack
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": weather_message
            }
        },
        {"type": "divider"}
    ]
    for date, times in list(forecasts.items())[:5]:
        readable_date = format_date_manual(date)
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📅 {readable_date}*"
            }
        })
        # Ajouter les détails horaires
        for time, forecast in times.items():
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{time}*\n{forecast}"
                }
            })
        blocks.append({"type": "divider"})

    # Poster sur Slack
    post_to_slack(blocks, slack_token, channel_id)
