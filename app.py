import requests, urllib.request, json, datetime, atexit
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy 
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'

db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    temperature = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(50), nullable=False)
    icon = db.Column(db.String(50), nullable=False)

def scheduled_task():
    url = 'http://ipinfo.io/json'
    response = urllib.request.urlopen(url)
    data = json.load(response)

    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=271d1234d3f497eed5b1d80a07b3fcd1'
    r = requests.get(url.format(data['city'])).json()

    new_city_obj = City(name=data['city'], time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-7], temperature=r['main']['temp'], description=r['weather'][0]['description'], icon=r['weather'][0]['icon'])

    db.session.add(new_city_obj)
    db.session.commit()

    cities = City.query.all()

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_task,'interval',seconds=6)
scheduler.start()

@app.route('/', methods=['GET', 'POST'])
def index(): 
    url = 'http://ipinfo.io/json'
    response = urllib.request.urlopen(url)
    data = json.load(response)

    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=271d1234d3f497eed5b1d80a07b3fcd1'
    r = requests.get(url.format(data['city'])).json()

    if request.method == 'POST':
        new_city = request.form.get('radio')
        if new_city == 'update':
            new_city_obj = City(name=data['city'], time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-7], temperature=r['main']['temp'], description=r['weather'][0]['description'], icon=r['weather'][0]['icon'])

            db.session.add(new_city_obj)
            db.session.commit()
        elif new_city == 'clear':
            City.query.delete()
            db.session.commit()

    cities = City.query.all()

    weather_data = []

    for city in cities:

        weather = {
            'city' : city.name,
            'temperature' : city.temperature,
            'description' : city.description,
            'icon' : city.icon,
            'timestamp' : city.time
        }

        weather_data.append(weather)

    return render_template('weather.html', weather_data=weather_data)

atexit.register(lambda: scheduler.shutdown())