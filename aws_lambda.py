from datetime import datetime
from urllib.request import urlopen
import json

def lambda_handler(event, context):
    place = event['queryStringParameters']['location']
    with urlopen("https://geocode.maps.co/search?q=" + place) as location_response:
        location_content = location_response.read()
    location_content.decode('utf-8')
    location_json = json.loads(location_content)
    x_coord = location_json[0]['lat']
    y_coord = location_json[0]['lon']

    # convert lat/long coordinates to NOAA grid points
    with request.urlopen("https://api.weather.gov/points/" + str(x_coord) + "," + str(y_coord)) as points_response:
        points_content = points_response.read()
    points_content.decode('utf-8')
    points_json = json.loads(points_content)

    # parse grid points JSON data
    hourly_api_url = points_json["properties"]["forecastHourly"]
    city = points_json["properties"]["relativeLocation"]["properties"]["city"]
    state = points_json["properties"]["relativeLocation"]["properties"]["state"]

    # get hourly weather data for the NOAA grid points
    with request.urlopen(hourly_api_url) as weather_response:
        weather_content = weather_response.read()
    weather_content.decode('utf-8')
    forecast_json = json.loads(weather_content)

    forcast_hours = forecast_json["properties"]["periods"]
    forecast_dict = {}
    forecast_dict['location'] = place
    forecast_dict['city'] = city
    forecast_dict['state'] = state
    forecast_dict['latitude'] = x_coord
    forecast_dict['longitude'] = y_coord
    for count, value in enumerate(forcast_hours):
        # parse wind
        wind = value["windSpeed"].split(" ")
        wind = wind[0]
        # parse weather
        short_weather = ""
        weather = value["shortForecast"]
        if "Thunderstorms" in weather:
            short_weather = "Thunderstorms"
        elif "Rain" in weather or "Showers" in weather:
            short_weather = "Rainy"
        elif "Snow" in weather:
            short_weather = "Snow"
        elif "Cloudy" in weather:
            short_weather = "Cloudy"
        elif "Sunny" in weather:
            short_weather = "Sunny"
        elif "Clear" in weather:
            short_weather = "Clear"
        elif "Fog" in weather:
            short_weather = "Foggy"
        else:
            short_weather = value["shortForecast"]
        # parse time
        dt = datetime.strptime(value["startTime"][0:16], "%Y-%m-%dT%H:%M")
        date = dt.date()
        time = dt.time()
        forecast_dict[count] = {"date": date.strftime("%m/%d/%Y"),
                                "time": time.strftime("%H:%M"),
                                "daytime": value["isDaytime"],
                                "temperature": value["temperature"],
                                "wind_speed": wind,
                                "humidity": value["relativeHumidity"]["value"],
                                "weather": short_weather,
                                }
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(forecast_dict),
        'headers': {
            'Content-Type': 'application/json',
        },
    }
