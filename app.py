from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

def get_weather_forecast(lat=25.6, lon=85.1):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=rain_sum,temperature_2m_max&timezone=Asia/Kolkata"
        res = requests.get(url).json()
        total_rain = sum(res.get('daily', {}).get('rain_sum', [0]))
        return {"total_rain_mm": total_rain}
    except Exception:
        return {"total_rain_mm": 0}

def predict_price_trend(item, rain_mm):
    trend = "STABLE"
    change_percent = 0
    reason = "सामान्य आपूर्ति और अनुकूल मौसम।"

    if rain_mm > 50:
        trend = "UP"
        change_percent = 8
        reason = "अगले 15 दिनों में भारी बारिश से आपूर्ति प्रभावित होने की आशंका है।"
    elif rain_mm < 5:
        if item in ["चना दाल", "अरहर दाल", "मसूर दाल"]:
            trend = "UP"
            change_percent = 5
            reason = "कम बारिश के कारण मंडियों में आवक घटने से दाम बढ़ सकते हैं।"
    else:
        trend = "DOWN"
        change_percent = -3
        reason = "मौसम अनुकूल है और नई आवक से रेट में हल्की गिरावट आ सकती है।"

    return {
        "item": item,
        "trend": trend,
        "change_percent": change_percent,
        "days_ahead": 15,
        "reason": reason
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.json or {}
    item = data.get('item', 'चना दाल')
    weather = get_weather_forecast()
    result = predict_price_trend(item, weather['total_rain_mm'])
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
  
