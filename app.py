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
    reason = "सामान्य आपूर्ति और स्थिर मांग।"

    # पैक्ड और एफएमसीजी सामान (बिस्कुट, नमकीन, साबुन)
    if item in ["बिस्कुट", "नमकीन", "साबुन/डिटर्जेंट"]:
        trend = "STABLE"
        change_percent = 0
        reason = "ब्रांडेड पैक्ड सामानों के दाम कंपनियों द्वारा तय होते हैं, मौसम या मंडी से तुरंत बदलाव नहीं होता।"

    # चायपत्ती और मसाले
    elif item in ["चायपत्ती", "मसाले (हल्दी/मिर्च)"]:
        if rain_mm > 60:
            trend = "UP"
            change_percent = 4
            reason = "अत्यधिक बारिश से परिवहन व सुखाने की प्रक्रिया प्रभावित होने के कारण हल्की तेजी आ सकती है।"
        else:
            trend = "STABLE"
            change_percent = 0
            reason = "मसाले व चायपत्ती की आवक और मांग सामान्य बनी हुई है।"

    # दालें और तेल
    elif item in ["चना दाल", "अरहर दाल", "मसूर दाल", "सरसों तेल", "रिफाइंड तेल"]:
        if rain_mm > 50:
            trend = "UP"
            change_percent = 7
            reason = "भारी बारिश से मंडियों में आवक घटने और कच्चे माल की ढुलाई प्रभावित होने से दाम बढ़ सकते हैं।"
        elif rain_mm < 5:
            trend = "UP"
            change_percent = 4
            reason = "कम बारिश से मंडी में नई फसल की आवक धीमी रहने से हल्की तेजी का अनुमान है।"
        else:
            trend = "DOWN"
            change_percent = -3
            reason = "मौसम अनुकूल है और मंडियों में सप्लाई बेहतर होने से रेट में हल्की नरमी आ सकती है।"

    # अनाज (गेहूं, चावल, चीनी)
    else:
        if rain_mm > 50:
            trend = "UP"
            change_percent = 5
            reason = "बारिश के कारण भंडारण और गोदामों से सप्लाई धीमी पड़ने की आशंका है।"
        else:
            trend = "STABLE"
            change_percent = 0
            reason = "सरकारी स्टॉक और मंडी आवक के संतुलन से रेट स्थिर बने रहेंगे।"

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
