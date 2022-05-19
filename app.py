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

def scheduled_task():
    url = 'http://ipinfo.io/json'
    response = urllib.request.urlopen(url)
    data = json.load(response)

    new_city_obj = City(name=data['city'], time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-7])

    db.session.add(new_city_obj)
    db.session.commit()
    cities = City.query.all()

    url = 'http://ipinfo.io/json'
    response = urllib.request.urlopen(url)
    data = json.load(response)

    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=271d1234d3f497eed5b1d80a07b3fcd1'

    weather_data = []

    for city in cities:

        r = requests.get(url.format(data['city'])).json()

        weather = {
            'city' : data['city'],
            'temperature' : r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
            'timestamp' : city.time
        }

        weather_data.append(weather)

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_task,'interval',minutes=60)
scheduler.start()

@app.route('/', methods=['GET', 'POST'])
def index():
    url = 'http://ipinfo.io/json'
    response = urllib.request.urlopen(url)
    data = json.load(response)
    
    if request.method == 'POST':
        new_city = request.form.get('radio')
        if new_city == 'update':
            new_city_obj = City(name=data['city'], time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-7])

            db.session.add(new_city_obj)
            db.session.commit()
        elif new_city == 'clear':
            # Delete all rows if entered string is empty
            City.query.delete()
            db.session.commit()
    cities = City.query.all()

    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=271d1234d3f497eed5b1d80a07b3fcd1'

    weather_data = []

    for city in cities:

        r = requests.get(url.format(data['city'])).json()

        weather = {
            'city' : data['city'],
            'temperature' : r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
            'timestamp' : city.time
        }

        weather_data.append(weather)

    return render_template('weather.html', weather_data=weather_data)

atexit.register(lambda: scheduler.shutdown())