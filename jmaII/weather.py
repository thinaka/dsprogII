import sqlite3
import requests
import json
import logging
from datetime import datetime

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# SQLiteデータベース設定
DB_NAME = 'weather.db'

# 天気予報APIのベースURL
BASE_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/"

def load_region_codes(json_file_path):
    """JSONファイルから地域コードを抽出"""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        region_codes = []
        for center in data.get("centers", {}).values():
            region_codes.extend(center.get("children", []))
        logging.info(f"{len(region_codes)} 地域コードを読み込みました。")
        return region_codes
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"地域コードの読み込みに失敗しました: {e}")
        raise


def create_database():
    """SQLiteデータベースとテーブルを作成"""
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        # 既存テーブルがあれば削除（開発中のみ推奨、本番ではALTER TABLEを検討）
        cursor.execute('DROP TABLE IF EXISTS weather_forecast')
        cursor.execute('''
            CREATE TABLE weather_forecast (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area_code TEXT,
                forecast_date TEXT,
                weather_code TEXT
            )
        ''')
        conn.commit()
        logging.info("データベースとテーブルを作成しました。")
    finally:
        conn.close()


def fetch_weather_data(region_code):
    """指定された地域コードから天気予報データを取得"""
    url = f"{BASE_URL}{region_code}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTPエラーがある場合は例外を発生
        logging.info(f"地域コード {region_code} のデータ取得に成功しました。")
        return response.json()
    except requests.RequestException as e:
        logging.warning(f"地域コード {region_code} のデータ取得に失敗しました: {e}")
        return None


def process_region_weather_data(region_code, forecast_json):
    """地域ごとの天気予報データを抽出"""
    result = []
    try:
        for forecast in forecast_json:
            time_series = forecast.get('timeSeries', [])
            # 1週間分のデータを含む部分を探す
            for series in time_series:
                if len(series.get('timeDefines', [])) >= 7:  # 7日以上のデータを探す
                    areas = series.get('areas', [])
                    for area in areas:
                        area_code = area.get('area', {}).get('code', '')
                        weather_codes = area.get('weatherCodes', [])

                        # 日付ごとのデータを保存
                        for i, date in enumerate(series.get('timeDefines', [])):
                            weather_code = weather_codes[i] if i < len(weather_codes) else None
                            if weather_code:  # 天気コードがない場合はスキップ
                                result.append((area_code, date, weather_code))
        return result
    except Exception as e:
        logging.warning(f"データ処理中にエラーが発生しました (地域コード: {region_code}): {e}")
        return []


def save_to_database(data):
    """天気データをSQLiteデータベースに保存"""
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT INTO weather_forecast (area_code, forecast_date, weather_code)
            VALUES (?, ?, ?)
        ''', data)
        conn.commit()
        logging.info(f"{len(data)} 件のデータをデータベースに保存しました。")
    finally:
        conn.close()


def main():
    # JSONファイルから地域コードをロード
    region_codes = load_region_codes('jmaII/area.json')

    # データベースとテーブルを初期化
    create_database()

    # 天気予報データを取得して保存
    for region_code in region_codes:
        forecast_json = fetch_weather_data(region_code)
        if not forecast_json:
            continue

        # 地域ごとの天気データを抽出
        region_weather_data = process_region_weather_data(region_code, forecast_json)
        if region_weather_data:
            save_to_database(region_weather_data)


if __name__ == "__main__":
    main()
