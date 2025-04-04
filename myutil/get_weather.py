import requests

def get_weather(openweather_api_key,location):

    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={openweather_api_key}&units=metric"

    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        return round(data["main"]["temp"])
        # temperature = data["main"]["temp"]
        # condition = data["weather"][0]["description"]
        # print(f"Current temperature in {CITY}: {temperature}°C, {condition}")
    else:
        raise Exception(f"Cannot get weather information: {data}")
