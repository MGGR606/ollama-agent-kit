import json
import ollama

def get_stock_price(ticker: str):
    if ticker.upper() == "AAPL":
        return "$220"
    elif ticker.upper() == "GOOGL":
        return "$180"
    else:
        return "Неизвестная акция"
    
def get_weather(city: str):
    if city.lower() == 'москва':
        return '22 градуса'
    elif city.lower() == 'санкт-петербург':
        return '18 градусов'
    else:
        return 'Вызван неверный город'
    
def conversion(value: float, currency: str):
    if currency.lower() == 'usd':
        return round(value / 85.0955, 2)
    elif currency.lower() == 'rub':
        return round(value * 85.0955, 2)
    else:
        return 'Незивестная валюта!'

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Запросить текущую рыночную стоимость акции компании по её биржевому тикеру",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Биржевой тикер ценной бумаги (например, AAPL или GOOGL).",
                    }
                },
                "required": ["ticker"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Запросить актуальные метеоданные для указанного населенного пункта",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Название города.",
                    }
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "conversion",
            "description": "Выполнить конвертацию указанного объема денежных средств в целевую валюту. Пример: '100 рублей в доллары' -> вызвать функцию с параметром currency='USD'",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "float",
                        "description": "Сумма для конвертации.",
                    },
                    "currency": {
                        "type": "string",
                        "description": "Код целевой валюты, в которую производится перевод (USD или RUB)",
                    }
                },
                "required": ["value", "currency"],
            },
        },
    }
]

MODEL = 'qwen2.5-coder:7b'
messages = [{'role': 'system', 'content': """Ты — автоматизированный аналитический ассистент с доступом к внутренним инструментам системы.
            Тебе доступны три функции: get_stock_price (принимает тикер ценной бумаги), get_weather (принимает наименование города) и conversion (выполняет обмен валют).
            Правило для conversion: аргумент currency всегда должен содержать код той целевой валюты, В КОТОРУЮ необходимо перевести средства.
            Если пользователь запрашивает рубли в доллары передавай USD; если доллары в рубли передавай RUB"""}]

while True:
    user_input = input(':')
    if user_input.lower() == 'выход':
        break
    
    messages.append({'role': 'user', 'content': user_input})
    response = ollama.chat(model=MODEL,
                           messages=messages,
                           tools=tools
                            )
    messages.append(response.message)

    if response.message.content and response.message.content.strip().startswith('{'):
        try:
            tool_data = json.loads(response.message.content.strip())
            function_name = tool_data.get('name')
            arguments = tool_data.get('arguments', {})
            
            result = None
            
            if function_name == 'get_stock_price':
                ticker = arguments.get('ticker')
                result = get_stock_price(ticker=ticker)
                print(f"[Система]: Активирован триггер get_stock_price для объекта: {ticker}")
                
            elif function_name == 'get_weather':
                city = arguments.get('city')
                result = get_weather(city=city)
                print(f"[Система]: Активирован триггер get_weather для локации: {city}")
                
            elif function_name == 'conversion':
                value = arguments.get('value')
                currency = arguments.get('currency')
                result = conversion(value=value, currency=currency)
                print(f"[Система]: Активирован триггер conversion для объема {value} в валюту {currency}")
            
            if result:
                messages.append({
                    'role': 'tool',
                    'name': function_name,
                    'content': str(result),
                })

                final_response = ollama.chat(model=MODEL, messages=messages)
                messages.append(final_response.message)
                print(f'ИИ: {final_response.message.content}')
            else:
                print(f"[ОШИБКА]: Неидентифицированный идентификатор функции: {function_name}")

        except json.JSONDecodeError:
            print(f'ИИ (Сбой парсинга JSON-пакета): {response.message.content}')
    else:
        print(f'ИИ: {response.message.content}')