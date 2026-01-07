import requests
import pandas as pd
from darts import TimeSeries
from darts.models import ExponentialSmoothing
from datetime import datetime
import os
import time

# ============================================
# CONFIGURATION - CHANGE THIS!
# ============================================
ESP32_URL = "http://weather-station.local:81/weather"
LATITUDE = 54.6872   # Your location (Vilnius example)
LONGITUDE = 25.2797
FETCH_INTERVAL = 600  # seconds (10 minutes)

# ============================================
# WEATHER CONDITION PREDICTOR
# ============================================

def predict_weather_condition(temp, humidity, pressure, pressure_change):
    """
    Predict weather based on sensor rules + pressure trends
    This is a simple rule-based system (works offline!)
    """
    
    # Pressure trend analysis
    if pressure_change < -3:
        pressure_trend = "Rapidly Falling"
    elif pressure_change < -1:
        pressure_trend = "Falling"
    elif pressure_change > 3:
        pressure_trend = "Rapidly Rising"
    elif pressure_change > 1:
        pressure_trend = "Rising"
    else:
        pressure_trend = "Stable"
    
    # Weather prediction rules
    if pressure < 1000 and humidity > 80 and pressure_change < -2:
        condition = "⛈️ THUNDERSTORM"
        confidence = 85
    elif pressure < 1005 and humidity > 70 and pressure_change < -1:
        condition = "🌧️ RAIN"
        confidence = 75
    elif pressure < 1010 and humidity > 65:
        condition = "☁️ CLOUDY"
        confidence = 70
    elif pressure > 1020 and humidity < 60 and pressure_change > 0:
        condition = "☀️ SUNNY"
        confidence = 80
    elif pressure > 1015 and humidity < 70:
        condition = "🌤️ PARTLY CLOUDY"
        confidence = 65
    else:
        condition = "☁️ CLOUDY"
        confidence = 50
    
    return {
        'condition': condition,
        'confidence': confidence,
        'pressure_trend': pressure_trend
    }

# ============================================
# MAIN FUNCTIONS
# ============================================

def fetch_and_save():
    """Fetch current data from ESP32 and save to history"""
    try:
        print(f"   Connecting to {ESP32_URL}...")
        response = requests.get(ESP32_URL, timeout=10)
        
        print(f"   Status code: {response.status_code}")
        print(f"   Raw response: {response.text[:100]}")
        
        if response.status_code != 200:
            print(f"   ❌ Bad status code: {response.status_code}")
            return None
            
        data = response.json()
        
        # Get current time info
        now = datetime.now()
        
        new_reading = {
            'time': now,
            'temp': data['temp'],
            'humidity': data['humidity'],
            'pressure': data['pressure'],
            'hour': now.hour,
            'day_of_year': now.timetuple().tm_yday,
            'month': now.month,
            'latitude': LATITUDE,
            'longitude': LONGITUDE
        }
        
        print(f"✓ Fetched: {data['temp']:.1f}°C, {data['humidity']:.1f}%, {data['pressure']:.1f}hPa")
        
        # Load or create history
        if os.path.exists('weather_data.csv'):
            df = pd.read_csv('weather_data.csv')
            df = pd.concat([df, pd.DataFrame([new_reading])], ignore_index=True)
        else:
            df = pd.DataFrame([new_reading])
        
        # Keep only last 7 days of data (faster predictions)
        if len(df) > 1008:  # 7 days * 24 hours * 6 readings/hour
            df = df.tail(1008)
        
        df.to_csv('weather_data.csv', index=False)
        print(f"✓ Saved (Total: {len(df)} readings)")
        
        return new_reading
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def predict_weather(hours=6):
    """Predict weather for next N hours"""
    
    if not os.path.exists('weather_data.csv'):
        print("❌ No history yet!")
        return None
    
    df = pd.read_csv('weather_data.csv')
    df['time'] = pd.to_datetime(df['time'])
    
    if len(df) < 6:
        print(f"⚠️ Need 6+ readings. Currently: {len(df)}")
        return None
    
    print(f"\n📊 Analyzing {len(df)} readings...")
    
    # Resample data to regular 10-minute intervals
    df = df.set_index('time')
    df = df.resample('10min').mean()  # Average if multiple readings in same period
    df = df.dropna()  # Remove any gaps
    df = df.reset_index()
    
    if len(df) < 3:
        print(f"⚠️ After resampling, only {len(df)} readings. Need more data.")
        return None
    
    print(f"   Resampled to {len(df)} regular 10-min intervals")
    
    # Create TimeSeries for prediction
    series = TimeSeries.from_dataframe(
        df,
        time_col='time',
        value_cols=['temp', 'humidity', 'pressure'],
        freq='10min'
    )
    
    # Train model
    model = ExponentialSmoothing()
    model.fit(series)
    
    # Predict next hours
    steps = hours * 6  # 6 readings per hour
    forecast = model.predict(steps)
    forecast_df = forecast.pd_dataframe()
    
    # Calculate pressure change (current vs 1 hour ago)
    current_pressure = df['pressure'].iloc[-1]
    if len(df) >= 6:
        pressure_1h_ago = df['pressure'].iloc[-6]
        pressure_change = current_pressure - pressure_1h_ago
    else:
        pressure_change = 0
    
    # Predict weather conditions
    print("\n" + "="*70)
    print("🌤️  WEATHER FORECAST")
    print("="*70)
    
    # Current conditions
    current_temp = df['temp'].iloc[-1]
    current_humidity = df['humidity'].iloc[-1]
    
    current_weather = predict_weather_condition(
        current_temp, current_humidity, current_pressure, pressure_change
    )
    
    print(f"\n📍 CURRENT CONDITIONS:")
    print(f"   Condition: {current_weather['condition']}")
    print(f"   Temperature: {current_temp:.1f}°C")
    print(f"   Humidity: {current_humidity:.1f}%")
    print(f"   Pressure: {current_pressure:.1f} hPa ({current_weather['pressure_trend']})")
    print(f"   Confidence: {current_weather['confidence']}%")
    
    # Future predictions (show 3 time points)
    print(f"\n📅 NEXT {hours} HOURS:")
    
    for i in [6, 12, min(len(forecast_df)-1, 18)]:  # 1h, 2h, 3h ahead
        if i >= len(forecast_df):
            continue
            
        pred_temp = forecast_df['temp'].iloc[i]
        pred_humidity = forecast_df['humidity'].iloc[i]
        pred_pressure = forecast_df['pressure'].iloc[i]
        pred_pressure_change = pred_pressure - current_pressure
        
        pred_weather = predict_weather_condition(
            pred_temp, pred_humidity, pred_pressure, pred_pressure_change
        )
        
        hours_ahead = (i + 1) // 6
        print(f"\n   +{hours_ahead}h: {pred_weather['condition']}")
        print(f"      Temp: {pred_temp:.1f}°C | Humidity: {pred_humidity:.1f}% | Pressure: {pred_pressure:.1f} hPa")
    
    print("\n" + "="*70)
    
    return forecast_df


# ============================================
# AUTO-RUN MODE
# ============================================

if __name__ == "__main__":
    
    print("🌡️  SMART WEATHER PREDICTOR")
    print("="*70)
    print(f"📍 Location: {LATITUDE}°N, {LONGITUDE}°E")
    print(f"⚡ Fetch interval: {FETCH_INTERVAL//60} minutes")
    print("⚡ Press CTRL+C to stop")
    print("="*70 + "\n")
    
    while True:
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
            
            # Fetch data
            fetch_and_save()
            
            # Predict
            predict_weather(hours=6)
            
            # Wait
            print(f"\n⏳ Next update in {FETCH_INTERVAL//60} minutes...\n")
            time.sleep(FETCH_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n👋 Stopped!")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")
            print(f"Retrying in {FETCH_INTERVAL//60} minutes...")
            time.sleep(FETCH_INTERVAL)