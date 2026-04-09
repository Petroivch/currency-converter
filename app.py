from flask import Flask, request, jsonify, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

# --- Настройка Swagger UI ---
SWAGGER_URL = '/swagger' # URL для доступа к интерфейсу Swagger
API_URL = '/swagger.yaml' # Путь к файлу спецификации (исправлено)

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Currency Converter API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/swagger.yaml')
def send_swagger():
    """Отдает файл swagger.yaml для отображения интерфейса"""
    # Ищет файл swagger.yaml в той же папке, откуда запущен скрипт
    return send_from_directory('.', 'swagger.yaml')
# ----------------------------

MOCK_RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "RUB": 92.50,
    "GBP": 0.79,
    "BTC": 0.000015,
    "ETH": 0.00030
}

@app.route('/api/currencies', methods=['GET'])
def get_currencies():
    """Возвращает список доступных валют"""
    return jsonify(list(MOCK_RATES.keys())), 200

@app.route('/api/rates', methods=['GET'])
def get_rates():
    """Возвращает курсы валют относительно базовой"""
    base = request.args.get('base', 'USD').upper()
    
    if base not in MOCK_RATES:
        return jsonify({"error": "Базовая валюта не найдена"}), 400
        
    base_rate = MOCK_RATES[base]
    rates = {currency: rate / base_rate for currency, rate in MOCK_RATES.items()}
    
    return jsonify({
        "base": base,
        "rates": rates
    }), 200

@app.route('/api/convert', methods=['POST'])
def convert_currency():
    """Конвертирует сумму из одной валюты в другую"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ("from", "to", "amount")):
        return jsonify({"error": "Неверный формат запроса. Ожидается from, to, amount"}), 400
        
    curr_from = data['from'].upper()
    curr_to = data['to'].upper()
    amount = data['amount']
    
    if curr_from not in MOCK_RATES or curr_to not in MOCK_RATES:
        return jsonify({"error": "Одна из валют не поддерживается"}), 400
        
    if amount < 0:
        return jsonify({"error": "Сумма не может быть отрицательной"}), 400
        
    rate_from_to_usd = 1 / MOCK_RATES[curr_from]
    usd_to_target_rate = MOCK_RATES[curr_to]
    final_rate = rate_from_to_usd * usd_to_target_rate
    
    result = amount * final_rate
    
    return jsonify({
        "from": curr_from,
        "to": curr_to,
        "original_amount": amount,
        "converted_amount": round(result, 6),
        "rate_used": round(final_rate, 6)
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)