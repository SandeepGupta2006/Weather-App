from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from os import getenv
import requests
from datetime import datetime, timedelta, timezone

load_dotenv()

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
API_KEY = getenv("API_KEY")


def weather_icon(icon_id):
    weather_icon = {
        "01d": "☀️",
        "01n": "🌙",
        "02d": "🌤️",
        "02n": "☁️",
        "03d": "☁️",
        "03n": "☁️",
        "04d": "🌥️",
        "04n": "☁️",
        "09d": "🌧️",
        "09n": "🌧️",
        "10d": "🌦️",
        "10n": "🌧️",
        "11d": "⛈️",
        "11n": "⛈️",
        "13d": "❄️",
        "13n": "❄️",
        "50d": "🌫️",
        "50n": "🌫️"
    }

    return weather_icon.get(icon_id)


def wind_direction(degree):
    degree_arrow = {
        0: "↓",
        45: "↙",
        90: "←",
        135: "↖",
        180: "↑",
        225: "↗",
        270: "→",
        315: "↘"
    }

    nearest_degree = ((degree % 360) // 45) * 45

    return degree_arrow.get(nearest_degree, 0)


def epoch_converter(epoch, tz_epoch):
    tz = timezone(timedelta(seconds=tz_epoch))
    dt = datetime.fromtimestamp(epoch, tz)
    suffix = "AM" if dt.hour < 12 else "PM"
    hour = dt.hour % 12
    hour = 12 if hour == 0 else hour
    return f"{hour:02d}:{dt.minute:02d} {suffix}"


def get_timezone(epoch):
    sign = '+' if epoch >= 0 else '-'
    abs_epoch = abs(epoch)
    hr = abs_epoch // 3600
    min = (abs_epoch % 3600) // 60

    return f"UTC{sign}{hr}:{min:02d}"


@app.route("/", methods=['GET', 'POST'])
def main():
    if request.method == "POST":
        city = request.form.get("city")

        if city:
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
                response = requests.get(url)
                all_data = response.json()

                icon = all_data.get("weather")[0].get("icon")

                data = {
                    "city": all_data.get("name"),
                    "temp": round(all_data.get("main").get("temp")),
                    "feels": round(all_data.get("main").get("feels_like")),
                    "pressure": all_data.get("main").get("pressure"),
                    "humidity": all_data.get("main").get("humidity"),
                    "desc": all_data.get("weather")[0].get("description"),
                    "icon": weather_icon(icon),
                    "wind_speed": all_data.get("wind").get("speed"),
                    "wind_direction": wind_direction(all_data.get("wind").get("deg")),
                    "country": all_data.get("sys").get("country"),
                    "date_time": epoch_converter(all_data.get("dt"), all_data.get("timezone")),
                    "sunrise": epoch_converter(all_data.get("sys").get("sunrise"), all_data.get("timezone")),
                    "sunset": epoch_converter(all_data.get("sys").get("sunset"), all_data.get("timezone")),
                    "timezone": get_timezone(all_data.get("timezone")),
                }

                return render_template("show.html", data=data, icon=icon)

            except Exception:
                flash("Error while loading data...Please try again")
                return redirect(url_for("main"))

    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)
