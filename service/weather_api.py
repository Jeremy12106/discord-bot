import requests
import json
from typing import Dict

from utils.env_loader import WEATHER_API_KEY

def get_weather(region) -> Dict:
    # API 設定
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
    params = {
        "Authorization": WEATHER_API_KEY,
        "locationName": region,
    }

    # 呼叫 API 並處理回應
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {}
