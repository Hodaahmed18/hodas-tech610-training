import requests 

response = requests.get("https://api.open-meteo.com/v1/forecast?latitude=51.5&longitude=-0.1&current_weather=true")

data = response.json()

temperature = data["current_weather"] ["temperature"] 

print ("temp in london at the moment folks is", temperature, ":)" )

import sqlite3

conn = sqlite3.connect("weather.db")
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS weather (temperature REAL, time TEXT)")
cursor.execute("INSERT INTO weather VALUES (?, ?)", (temperature, "now"))

conn.commit()
conn.close()

print("saved to database")

conn = sqlite3.connect("weather.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM weather")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
