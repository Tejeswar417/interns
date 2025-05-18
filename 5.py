import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
import io
from datetime import datetime
from collections import defaultdict
import time

# ---- Theme Setup ----
light_theme = {
    "bg": "#f0f0f0", "fg": "#2F4F4F", "button": "#e0e0e0", "entry": "#ffffff"
}
dark_theme = {
    "bg": "#2b2b2b", "fg": "#f5f5f5", "button": "#444444", "entry": "#3a3a3a"
}
current_theme = light_theme

def switch_theme():
    global current_theme
    current_theme = dark_theme if theme_var.get() == "Dark" else light_theme
    apply_theme()

def apply_theme():
    window.config(bg=current_theme["bg"])
    for widget in window.winfo_children():
        try:
            widget.config(bg=current_theme["bg"], fg=current_theme["fg"])
            if isinstance(widget, tk.Button):
                widget.config(bg=current_theme["button"])
            if isinstance(widget, tk.Entry):
                widget.config(bg=current_theme["entry"], fg=current_theme["fg"])
        except:
            pass
    weather_label.config(bg=current_theme["bg"], fg=current_theme["fg"])

# ---- Weather Helper Functions ----
def get_weather_emoji(description):
    description = description.lower()
    if "clear" in description:
        return "☀"
    elif "few clouds" in description or "scattered clouds" in description:
        return "🌤"
    elif "clouds" in description:
        return "☁"
    elif "rain" in description:
        return "🌧"
    elif "thunderstorm" in description:
        return "⛈"
    elif "snow" in description:
        return "🌨"
    elif "mist" in description or "fog" in description or "haze" in description:
        return "🌫"
    else:
        return "🌈"

def format_unix_time(unix_utc, timezone_offset):
    local_time = time.gmtime(unix_utc + timezone_offset)
    return time.strftime('%H:%M', local_time)

def get_weather(city):
    if city:
        try:
            api_key = "38137c968a5d1d542c1817135e20adbf"
            unit = "metric" if unit_toggle.get() == "Celsius" else "imperial"
            unit_symbol = "°C" if unit == "metric" else "°F"
            speed_unit = "km/h" if unit == "metric" else "mph"

            url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units={unit}"
            response = requests.get(url)
            data = response.json()

            if data.get("list"):
                timezone_offset = data["city"]["timezone"]
                sunrise = format_unix_time(data["city"]["sunrise"], timezone_offset)
                sunset = format_unix_time(data["city"]["sunset"], timezone_offset)

                daily_forecast = defaultdict(list)
                for entry in data["list"]:
                    date_str = entry["dt_txt"].split(" ")[0]
                    daily_forecast[date_str].append(entry)

                forecast_text = f"📍 Weather in {data['city']['name']}, {data['city']['country']}\n"
                forecast_text += f"🌅 Sunrise: {sunrise}   🌇 Sunset: {sunset}\n\n"

                count = 0
                today = datetime.now().date()

                for date_str in sorted(daily_forecast.keys()):
                    forecast_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    if forecast_date >= today and count < 3:
                        entries = daily_forecast[date_str]
                        noon_forecast = next((e for e in entries if "12:00:00" in e["dt_txt"]), entries[0])
                        temp = noon_forecast["main"]["temp"]
                        humidity = noon_forecast["main"]["humidity"]
                        description = noon_forecast["weather"][0]["description"].capitalize()
                        wind_speed = noon_forecast["wind"]["speed"]
                        emoji = get_weather_emoji(description)

                        date_label = forecast_date.strftime("%A, %d %b")
                        forecast_text += f"{date_label}\n"
                        forecast_text += f"{emoji} {description}\n"
                        forecast_text += f"🌡 Temp: {temp}{unit_symbol}\n"
                        forecast_text += f"💧 Humidity: {humidity}%\n"
                        forecast_text += f"🌬 Wind: {wind_speed} {speed_unit}\n\n"

                        count += 1

                weather_label.config(text=forecast_text.strip(), fg=current_theme["fg"], bg=current_theme["bg"])

                icon_code = data["list"][0]["weather"][0]["icon"]
                icon_url = f"http://openweathermap.org/img/wn/{icon_code}.png"
                icon_response = requests.get(icon_url)
                icon_image = Image.open(io.BytesIO(icon_response.content))
                icon_image = icon_image.resize((50, 50), Image.Resampling.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon_image)
                weather_icon.config(image=icon_photo)
                weather_icon.image = icon_photo
            else:
                messagebox.showerror("Error", data.get("message", "City not found or data unavailable."))
        except Exception as e:
            messagebox.showerror("Error", f"Unable to fetch data.\n{e}")
    else:
        messagebox.showwarning("Input Error", "Please enter a city name.")

# ---- GUI Setup ----
window = tk.Tk()
window.title("Weather Forecast App")
window.geometry("420x550")

theme_var = tk.StringVar(value="Light")
theme_frame = tk.Frame(window, bg=light_theme["bg"])
tk.Label(theme_frame, text="Theme:").pack(side="left")
tk.Radiobutton(theme_frame, text="Light", variable=theme_var, value="Light", command=switch_theme).pack(side="left")
tk.Radiobutton(theme_frame, text="Dark", variable=theme_var, value="Dark", command=switch_theme).pack(side="left")
theme_frame.pack(pady=5)

tk.Label(window, text="Enter City Name:", font=("Helvetica", 12)).pack(pady=5)
city_entry = tk.Entry(window, width=20, font=("Helvetica", 12))
city_entry.pack()

unit_toggle = tk.StringVar(value="Celsius")
unit_frame = tk.Frame(window)
tk.Label(unit_frame, text="Unit:").pack(side="left")
tk.Radiobutton(unit_frame, text="Celsius", variable=unit_toggle, value="Celsius").pack(side="left")
tk.Radiobutton(unit_frame, text="Fahrenheit", variable=unit_toggle, value="Fahrenheit").pack(side="left")
unit_frame.pack(pady=5)

tk.Button(window, text="Fetch Weather", font=("Helvetica", 12), command=lambda: get_weather(city_entry.get())).pack(pady=10)

weather_label = tk.Label(window, text="", font=("Helvetica", 11), justify="left", wraplength=380)
weather_label.pack(pady=10)

weather_icon = tk.Label(window)
weather_icon.pack(pady=10)

apply_theme()
window.mainloop()