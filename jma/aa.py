import requests
import json
import os

# JSONファイルのURL
area_url = "https://www.jma.go.jp/bosai/common/const/area.json"
forecast_url_template = "https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"

# 保存先のファイル
output_file = "all_forecasts.json"

# 地域コードを抽出する関数
def get_area_codes(url):
    response = requests.get(url)
    area_data = response.json()
    
    # 子地域コードを抽出
    area_codes = []
    for center in area_data['centers'].values():
        area_codes.extend(center['children'])
    
    return area_codes

# 天気予報情報を取得する関数
def fetch_forecast(area_code):
    url = forecast_url_template.format(area_code=area_code)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data for area code {area_code}")
        return None

# メイン処理
def main():
    area_codes = get_area_codes(area_url)
    all_forecasts = {}

    for area_code in area_codes:
        forecast_data = fetch_forecast(area_code)
        if forecast_data:
            all_forecasts[area_code] = forecast_data
            print(f"Fetched forecast data for area code {area_code}")
    
    # 全ての天気予報データを一つのJSONファイルに保存
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_forecasts, f, ensure_ascii=False, indent=2)
    print(f"All forecast data has been saved to {output_file}")

if __name__ == "__main__":
    main()