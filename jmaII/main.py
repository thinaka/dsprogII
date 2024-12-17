import flet as ft
import json
import sqlite3
from datetime import datetime

# SQLiteのデータベースファイルパス
DB_FILE = "weather.db"

# JSONファイルの読み込み
with open('jma/area.json', 'r', encoding='utf-8') as area_file:
    region_data = json.load(area_file)

def appbar():
    return ft.AppBar(
        leading=ft.Icon(ft.icons.PALETTE),
        leading_width=40,
        title=ft.Text("天気予報"),
        center_title=False,
        bgcolor=ft.colors.SURFACE_VARIANT,
    )

def sidebar(on_select_region):
    region_list = []
    for center_code, center_info in region_data['centers'].items():
        region_list.append(
            ft.ExpansionTile(
                title=ft.Text(center_info["name"]),
                subtitle=ft.Text(f"地域数: {len(center_info['children'])}"),
                controls=[
                    ft.Column(
                        [
                            ft.ListTile(
                                title=ft.Text(get_region_name_by_code(region_code)),
                                on_click=lambda e, region_code=region_code: on_select_region(region_code)
                            )
                            for region_code in center_info["children"]
                        ]
                    )
                ],
                initially_expanded=False
            )
        )
    return ft.Column(
        region_list,
        spacing=10,
        scroll=ft.ScrollMode.AUTO,  # Columnにスクロールを設定
        expand=True
    )

def get_region_name_by_code(code):
    for region_code, region_info in region_data['offices'].items():
        if region_code == code:
            return region_info["name"]
    return None

def get_weather_details(region_name, region_code):
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()

        # weather_forecast と weekly_temp テーブルを結合してデータを取得
        cursor.execute("""
        SELECT f.forecast_date, f.weather_code, t.temps_min, t.temps_max
        FROM weather_forecast AS f
        JOIN weekly_temp AS t
        ON f.area_code = t.area_code AND f.forecast_date = t.forecast_date
        WHERE f.area_code = ?
        ORDER BY f.forecast_date
        """, (region_code,))
        rows = cursor.fetchall()

        if not rows:
            return None

        # データを整形
        forecast_dates = [row[0] for row in rows]
        weather_codes = [row[1] for row in rows]
        temps_min = [row[2] for row in rows]  # 最低気温
        temps_max = [row[3] for row in rows]  # 最高気温

        return {
            'timeDefines': forecast_dates,
            'weatherCodes': weather_codes,
            'tempsMin': temps_min,
            'tempsMax': temps_max,
        }

    except Exception as e:
        print(f"Error fetching data from database: {e}")
        return None
    finally:
        connection.close()

def get_weather_icon_and_description(weather_code):
    # 天気コードに対応するアイコンと説明を返す
    icon_description_map = {
        "100": (ft.icons.WB_SUNNY, "晴れ"),
        "101": (ft.icons.WB_SUNNY, "晴れ時々曇り"),
        "102": (ft.icons.WB_SUNNY, "晴れ一時雨"),
        "106": (ft.icons.WB_SUNNY, "晴れ一時雨か雪"),
        "110": (ft.icons.WB_SUNNY, "晴れ後時々曇り"),
        "111": (ft.icons.WB_SUNNY, "晴れ後曇り"),
        "114": (ft.icons.WB_SUNNY, "晴れのち雨"),
        "200": (ft.icons.CLOUD, "曇り"),
        "201": (ft.icons.CLOUD, "曇り時々晴れ"),
        "202": (ft.icons.CLOUD, "曇り一時雨"),
        "203": (ft.icons.CLOUD, "曇り時々雨"),
        "204": (ft.icons.CLOUD, "曇り一時雪"),
        "205": (ft.icons.CLOUD, "曇り時々雪"),
        "206": (ft.icons.CLOUD, "曇り一時雨か雪"),
        "207": (ft.icons.CLOUD, "曇り時々雨か雪"),
        "211": (ft.icons.CLOUD, "曇り後晴れ"),
        "212": (ft.icons.CLOUD, "曇り後一時雨"),
        "214": (ft.icons.CLOUD, "曇り後雨"),
        "218": (ft.icons.CLOUD, "曇り後雨か雪"),
        "260": (ft.icons.SNOWING, "曇り一時雪か雨"),
        "270": (ft.icons.CLOUD, "曇り時々雪か雨"),
        "302": (ft.icons.UMBRELLA, "雨時々止む"),
        "311": (ft.icons.UMBRELLA, "雨後晴れ"),
        "313": (ft.icons.UMBRELLA, "雨後曇り"),
        "317": (ft.icons.UMBRELLA, "雨か雪後曇り"),
        "402": (ft.icons.SNOWING, "雪時々止む")
    }
    
    return icon_description_map.get(str(weather_code), (ft.icons.WB_SUNNY, "不明"))

def format_weather_info(weekly_weather_forecast):
    if not weekly_weather_forecast:
        return [ft.Text("天気情報がありません")]

    time_defines = weekly_weather_forecast.get('timeDefines', [])
    weather_codes = weekly_weather_forecast.get('weatherCodes', [])
    temps_min = weekly_weather_forecast.get('tempsMin', [])
    temps_max = weekly_weather_forecast.get('tempsMax', [])

    weather_info = []
    
    for i, time_define in enumerate(time_defines):
        try:
            date = datetime.fromisoformat(time_define).strftime("%Y-%m-%d")
        except ValueError:
            date = time_define

        weather_info.append(ft.Text(f"予報日時: {date}"))
        
        # アイコンと説明文を取得
        icon, description = get_weather_icon_and_description(weather_codes[i])

        # アイコンと説明文を表示
        weather_info.append(ft.Row([
            ft.Icon(icon, size=24),
            ft.Text(description, size=12)
        ]))

        weather_info.append(ft.Text(f"最低気温: {temps_min[i] if i < len(temps_min) else ''}°C"))
        weather_info.append(ft.Text(f"最高気温: {temps_max[i] if i < len(temps_max) else ''}°C"))
        weather_info.append(ft.Text("---"))
    
    return weather_info

def main(page: ft.Page):
    page.title = "天気予報"

    page.add(appbar())

    def on_select_region(region_code):
        region_name = get_region_name_by_code(region_code)
        weather_details = get_weather_details(region_name, region_code)
        weather_info = format_weather_info(weather_details)

        page.controls = [
            ft.Row([
                sidebar(on_select_region),
                ft.VerticalDivider(width=1),
                ft.Column(
                    weather_info,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO  # Columnにスクロールを設定
                )
            ], expand=True)
        ]
        page.update()

    first_center = list(region_data['centers'].values())[0]
    page.add(
        ft.Row([
            sidebar(on_select_region),
            ft.VerticalDivider(width=1),
            ft.Column(
                [ft.Text("天気予報:")],
                expand=True,
                scroll=ft.ScrollMode.AUTO  # Columnにスクロールを設定
            )
        ], expand=True)
    )

ft.app(target=main)
