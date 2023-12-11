# Updated Python file (app.py)
from flask import Flask, render_template, request
import requests
import os
import json
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from markupsafe import escape

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///D:/PycharmProjects/openweather_request.py/SQLdata.db"
db = SQLAlchemy(app)

db_name = r'D:\PycharmProjects\openweather_request.py'



my_bot = ChatBot(
    name="PyBot",
    read_only=True,
    logic_adapters=["chatterbot.logic.MathematicalEvaluation",
                    "chatterbot.logic.BestMatch"]
)

small_talk = [
    "Hello",
    "Hi there!",
    "How are you doing?",
    "I'm doing great.",
    "That is good to hear",
    "Thank you.",
    "You're welcome."
]

math_talk_1 = [
    'pythagorean theorem',
    'a squared plus b squared equals c squared.'
]

math_talk_2 = [
    'law of cosines',
    'c**2 = a**2 + b**2 - 2 * a * b * cos(gamma)'
]

list_trainer = ListTrainer(my_bot)

for item in (small_talk, math_talk_1, math_talk_2):
    list_trainer.train(item)

corpus_trainer = ChatterBotCorpusTrainer(my_bot)
corpus_trainer.train('chatterbot.corpus.english')

print(my_bot.get_response("Hi"))
print(my_bot.get_response("How are you?"))
print(my_bot.get_response("What is your name?"))


while True:
    try:
        bot_input = input("You: ")
        bot_response = my_bot.get_response(bot_input)
        print(f"{my_bot.name}: {bot_response}")
    except(KeyboardInterrupt, EOFError, SystemExit):
        break


@app.route('/', methods=['GET', 'POST'])
def index():
    # Get the user query from the URL parameters
    user_query = request.args.get('query', '')

    # store the API key locally
    API_key = '2e0d287575c019f52bbdafd1ea979dee'

    # Define a list of locations with their coordinates
    locations = [
        {"name": "Lake District National Park", "lat": 54.4609, "lon": -3.0886},
        {"name": "Corfe Castle", "lat": 50.6395, "lon": -2.0566},
        {"name": "The Cotswolds", "lat": 51.8330, "lon": -1.8433},
        {"name": "Cambridge", "lat": 52.2053, "lon": 0.1218},
        {"name": "Bristol", "lat": 51.4545, "lon": -2.5879},
        {"name": "Oxford", "lat": 51.7520, "lon": -1.2577},
        {"name": "Norwich", "lat": 52.6309, "lon": 1.2974},
        {"name": "Stonehenge", "lat": 51.1789, "lon": -1.8262},
        {"name": "Watergate Bay", "lat": 50.4429, "lon": -5.0553},
        {"name": "Birmingham ", "lat": 52.4862, "lon": -1.8904},
    ]

    weather_data = []

    # Handle form submission
    if request.method == 'POST':
        selected_location = request.form.get('location')
        user_query = selected_location  # Update the user query based on the selected location

        # Fetch weather data for the selected location
        location = next((loc for loc in locations if loc['name'] == selected_location), None)
        if location:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={location['lat']}&lon={location['lon']}&appid={API_key}"
            resp = requests.get(url)

            if resp.status_code == 200:
                content = json.loads(resp.text)

                # Extract relevant weather information
                temperature = round(content['main']['temp'] - 273.15, 2)
                feels_like_temperature = round(content['main']['feels_like'] - 273.15, 2)
                humidity = content['main']['humidity']
                weather_description = content['weather'][0]['description']
                wind_speed = content['wind']['speed']

                # Store the weather data
                weather_data.append({
                    "location": location['name'],
                    "temperature": temperature,
                    "feels_like_temperature": feels_like_temperature,
                    "humidity": humidity,
                    "weather_description": weather_description,
                    "wind_speed": wind_speed
                })

    return render_template('index.html', user_query=user_query, weather_data=weather_data, locations=locations)

@app.route('/test')
def testdb():
   try:
       db.session.query(text('1')).from_statement(text('SELECT 1')).all()
       return '<h1>Successful connection.</h1>'
   except Exception as er:
       # er describes the error
       error_text = "<p>The error:<br>" + str(er) + "</p>"
       state = '<h1>Connection unsuccessful.</h1>'
       return state + error_text

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

