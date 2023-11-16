from datetime import datetime
from urllib import request
import json

def lambda_handler(event, context):
    """Main program that calls run_prog and either returns OK status with 
    results or error status with the error type in the return body"""
    
    return_dict = {
        "error": 0, "status": "start"
        }
    return_dict = run_prog(event, return_dict)
    
    if return_dict["error"] == 0:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(return_dict),
            "isBase64Encoded": False
            }
    else:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(return_dict),
            "isBase64Encoded": False
            }
        
def run_prog(event, return_dict):
    """Runs individual functions checking for errors.  Gets location from 
    the event object, translates into gps coordinates, translates into NOAA
    grid points, fetches weather forecast, parses weather forcast and returns
    result or error."""

    place = get_place(event)
    if not place:
        return_dict["status"] = "Error: Location not provided."
        return_dict["error"] = 1
        return return_dict

    return_dict["status"] = "coords"
    location = get_coords(place)
    if not location:
        return_dict["status"] = "Error: Location not found."
        return_dict["error"] = 1
        return return_dict

    x_coord = location[0]['lat']
    y_coord = location[0]['lon']

    return_dict["status"] = "points"
    points_json = get_grid_points(x_coord, y_coord)
    if not points_json:
        return_dict["status"] = "Error: NOAA Grid Points not found."
        return_dict["error"] = 1
        return return_dict

    # parse grid points JSON data
    hourly_api_url = points_json["properties"]["forecastHourly"]
    city = points_json["properties"]["relativeLocation"]["properties"]["city"]
    state = points_json["properties"]["relativeLocation"]["properties"]["state"]

    return_dict["status"] = "forecast"
    forecast_json = get_weather(hourly_api_url)
    if not forecast_json:
        return_dict["status"] = "Error: Could not get weather forecast."
        return_dict["error"] = 1
        return return_dict

    return_dict["status"] = "parse"
    forecast_dict = parse_weather(forecast_json)
    if not forecast_dict:
        return_dict["status"] = "Error: Could not parse weather forecast."
        return_dict["error"] = 1
        return return_dict

    return_dict["information"] = {"location": place, "city": city, "state": state, "latitude": x_coord, "longitude": y_coord}
    return_dict["forecast"] = forecast_dict
    return_dict["status"] = "complete"
    return return_dict


def get_place(event):
    """Extracts location from the event object and checks it exists"""
    try:
        place = event["queryStringParameters"]["location"]
        if not place:
            return None
        place = place.replace(" ", "")
        return place
    except (Exception):
        return None

def get_coords(place):
    """Converts a text location (city, state) into GPS coordinates"""
    try:
        with request.urlopen("https://geocode.maps.co/search?q=" + place) as location_response:
            location_content = location_response.read()
            location_content.decode('utf-8')
            location_json = json.loads(location_content)
        return location_json
    except (Exception):
        return None


def get_grid_points(x_coord, y_coord):
    """Converts GPS coordinates into NOAA grid points"""
    try:
        with request.urlopen("https://api.weather.gov/points/" + str(x_coord) + "," + str(y_coord)) as points_response:
            response_content = points_response.read()
            response_content.decode('utf-8')
            points_json = json.loads(response_content)
        return points_json
    except (Exception):
        return None

def get_weather(hourly_api_url): 
    """Gets hourly weather data from the NOAA grid point"""
    try:
        with request.urlopen(hourly_api_url) as weather_response:
            response_content = weather_response.read()
            response_content.decode('utf-8')
            forecast_json = json.loads(response_content)
        return forecast_json
    except (Exception):
        return None

def parse_weather(forecast_json):
    """Parses the weather forecast into a simplified output format"""
    try:
        forcast_hours = forecast_json["properties"]["periods"]
        forecast_dict = {}
        for count, value in enumerate(forcast_hours):
            # parse wind
            wind = value["windSpeed"].split(" ")
            wind = int(wind[0])
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
            day = dt.weekday()
            date = dt.date()
            time = dt.time()
            forecast_dict[count] = {"day": day,
                                    "date": date.strftime("%m/%d/%Y"),
                                    "time": time.strftime("%H"),
                                    "daytime": value["isDaytime"],
                                    "temperature": value["temperature"],
                                    "wind_speed": wind,
                                    "humidity": value["relativeHumidity"]["value"],
                                    "weather": short_weather,
                                    }
        return forecast_dict
    except (Exception):
        return None
