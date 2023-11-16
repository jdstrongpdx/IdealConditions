# IdealConditions

About: This project will take in a location via a web-form and return activites that are ideal for the weather condition forecast in that area.

Setup:
  1. idealConditions.py running on a AWS Lambda Function
  2. AWS API Gateway with proxy integration to the Lambda Function
  3. Website hosted on a server with HTML, JS, Node.js capabilities

Usage: 
  1. Use the following GET endpoint: **https://qnag8pg924.execute-api.us-east-2.amazonaws.com/v1/IdealConditions**
  2. Use a "location" query parameter to serve the location key:pair to the API such as this example:
     https://qnag8pg924.execute-api.us-east-2.amazonaws.com/v1/IdealConditions?location=Tigard,OR

Response:
  The body of the response will have the following data:
  1. Error - 0 if no error, 1 if error
  2. Status - Either complete or contains error description
  3. Information - location information that was fetched from text search (city, state, latitude, longitude)
  4. Forecast - a parsed JSON forecast for the next 155 hours for the entered location
