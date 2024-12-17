import sqlite3
import requests
import json

DB_FILE = "weather.db"
BASE_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/"
AREA_JSON = "jmaII/area.json"  # area.jsonファイルのパス

def delete_table():
    """テーブルを削除する"""
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute('DROP TABLE IF EXISTS weekly_temp')  # テーブル削除
    connection.commit()
    connection.close()
    print("テーブルが削除されました。")

def create_table():
    """weekly_tempテーブルを作成する"""
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_temp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_code TEXT NOT NULL,
            forecast_date TEXT NOT NULL,
            temps_min REAL,
            temps_max REAL
        )
    ''')
    connection.commit()
    connection.close()
    print("テーブルが作成されました。")

def fetch_weather_data(area_code):
    """気象庁APIからデータを取得"""
    url = f"{BASE_URL}{area_code}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"データ取得成功: {url}")
        return response.json()
    except requests.RequestException as e:
        print(f"データ取得エラー: {e}")
        return None

def parse_and_save_weather(area_code, weather_json):
    """JSONから天気予報データを解析し、データベースに保存"""
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()

        # 予報情報と気温データの解析
        for series in weather_json[1].get("timeSeries", []):
            if "tempsMin" in series["areas"][0]:  # 週間気温データを探す
                for area in series["areas"]:
                    area_name = area.get("area", {}).get("name")
                    temps_min = area.get("tempsMin", [])
                    temps_max = area.get("tempsMax", [])
                    time_defines = series.get("timeDefines", [])

                    # データの整合性を確認しながら挿入
                    for i, date in enumerate(time_defines):
                        temp_min = float(temps_min[i]) if i < len(temps_min) and temps_min[i] else None
                        temp_max = float(temps_max[i]) if i < len(temps_max) and temps_max[i] else None

                        cursor.execute('''
                            INSERT INTO weekly_temp (area_code, forecast_date, temps_min, temps_max)
                            VALUES (?, ?, ?, ?)
                        ''', (area_code, date, temp_min, temp_max))

        connection.commit()
        print(f"{area_code}のデータがデータベースに保存されました。")
    except Exception as e:
        print(f"データ解析エラー: {e}")
    finally:
        connection.close()

def list_all_region_codes():
    """area.jsonから全ての地域コードを取得"""
    with open(AREA_JSON, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    region_codes = []
    for center_code, center_info in data['centers'].items():
        region_codes.extend(center_info['children'])
    
    return region_codes

def main():
    # 既存のテーブルを削除
    delete_table()

    # データベースのテーブルを作成
    create_table()

    # area.jsonからすべての地域コードを取得
    region_codes = list_all_region_codes()
    print(f"取得した地域コード: {region_codes}")

    # 各地域コードごとに天気データを取得し、保存
    for area_code in region_codes:
        print(f"データ取得中: {area_code}")
        weather_json = fetch_weather_data(area_code)
        if weather_json:
            parse_and_save_weather(area_code, weather_json)
        else:
            print(f"地域コード {area_code} のデータ取得に失敗しました。")

if __name__ == "__main__":
    main()
