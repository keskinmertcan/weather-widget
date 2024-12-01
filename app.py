import customtkinter as ctk
import requests
from customtkinter import CTkImage
from PIL import Image, ImageTk
import io

# OpenWeatherMap API credentials
API_KEY = "API_KEY"
BASE_URL = "https://api.openweathermap.org/data/2.5/"

# Automatically detect location based on IP
def get_current_location():
    try:
        response = requests.get("https://ipinfo.io", params={"token": "API_KEY"})
        data = response.json()
        if "loc" in data:
            lat, lon = map(float, data["loc"].split(","))
            return lat, lon, data["city"]
        else:
            raise Exception("Failed to detect location")
    except Exception as e:
        print("Location Error:", e)
        return None, None, None

# Fetch weather data using latitude and longitude
def get_weather(lat, lon):
    try:
        response = requests.get(f"{BASE_URL}weather", params={
            "lat": lat,
            "lon": lon,
            "appid": API_KEY,
            "units": "metric",
            "lang": "tr"
        })
        return response.json()
    except Exception as e:
        print("Weather Data Error:", e)
        return None

# Update the UI with weather data
def update_weather():
    global latitude, longitude
    weather = get_weather(latitude, longitude)
    if weather and weather.get("cod") == 200:
        # Update city and temperature labels
        city_label.configure(text=f"{weather['name']}")
        temp_label.configure(text=f"{weather['main']['temp']}°C")
        
        # Update additional weather details
        wind_label.configure(text=f"Wind: {weather['wind']['speed']} m/s")
        humidity_label.configure(text=f"Humidity: {weather['main']['humidity']}%")
        pressure_label.configure(text=f"Pressure: {weather['main']['pressure']}mb")
        description_label.configure(text=f"{weather['weather'][0]['description'].title()}")
        
        # Update weather icon
        icon_code = weather['weather'][0]['icon']
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        icon_response = requests.get(icon_url)
        icon_data = Image.open(io.BytesIO(icon_response.content))
        
        # Use CTkImage for better DPI scaling
        icon_image = CTkImage(light_image=icon_data, size=(75, 75))
        weather_icon_label.configure(image=icon_image)
        weather_icon_label.image = icon_image
    else:
        city_label.configure(text="Unable to fetch data")

# Auto-refresh weather data every 10 minutes
def auto_refresh():
    update_weather()
    app.after(600000, auto_refresh)  # Refresh every 600,000 ms (10 minutes)

# Initialize main application window
app = ctk.CTk()
app.title("Lemusk | Weather Forecast")
app.geometry("350x150")
app.resizable(False, False)
app.configure(fg_color="#1A1A1A")
app.wm_attributes("-topmost", 1)  # Keep window always on top

# Main layout frame
main_frame = ctk.CTkFrame(app, fg_color="#1A1A1A")
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Left section: Weather icon and description
icon_frame = ctk.CTkFrame(main_frame, fg_color="#1A1A1A")
icon_frame.grid(row=0, column=0, padx=10, pady=5)

# Weather icon
weather_icon_label = ctk.CTkLabel(icon_frame, text="")
weather_icon_label.pack(anchor="center", pady=(0, 0))

# Weather description
description_label = ctk.CTkLabel(icon_frame, text="", font=("Arial", 12, "italic"), text_color="gray")
description_label.pack(anchor="center", pady=(0, 0))

# Center section: City name, temperature, and refresh button
center_frame = ctk.CTkFrame(main_frame, fg_color="#1A1A1A")
center_frame.grid(row=0, column=1, sticky="n", padx=10, pady=10)

city_label = ctk.CTkLabel(center_frame, text="", font=("Arial", 14, "bold"), text_color="white")
city_label.pack(anchor="center")

temp_label = ctk.CTkLabel(center_frame, text="", font=("Arial", 20, "bold"), text_color="#00CCFF")
temp_label.pack(anchor="center")

refresh_button = ctk.CTkButton(center_frame, text="Refresh", command=update_weather, border_color="#00CCFF", text_color="#00CCFF", border_width=1, fg_color="transparent", width=80)
refresh_button.pack(anchor="center", pady=5)

# Right section: Additional weather details
info_frame = ctk.CTkFrame(main_frame, fg_color="#1A1A1A")
info_frame.grid(row=0, column=2, sticky="e", padx=10, pady=10)

wind_label = ctk.CTkLabel(info_frame, text="", font=("Arial", 12), text_color="gray")
wind_label.pack(anchor="e")

humidity_label = ctk.CTkLabel(info_frame, text="", font=("Arial", 12), text_color="gray")
humidity_label.pack(anchor="e")

pressure_label = ctk.CTkLabel(info_frame, text="", font=("Arial", 12), text_color="gray")
pressure_label.pack(anchor="e")

# Fetch initial weather data and start auto-refresh
latitude, longitude, city = get_current_location()
if latitude and longitude:
    update_weather()
auto_refresh()

# Start the application loop
app.mainloop()
