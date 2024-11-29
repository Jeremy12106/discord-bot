
import os
import json
import random
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class MRT:
    def __init__(self, data_path=f'{PROJECT_ROOT}/assets/data'):
        self.data_path = data_path
        self.stations = self.load_stations()
        self.ramen_shops = self.load_ramen_shops()

        self.line_mapping = {
            "紅線": "red_line", "淡水信義線": "red_line",
            "藍線": "blue_line", "板南線": "blue_line",
            "黃線": "yellow_line", "文湖線": "yellow_line",
            "棕線": "brown_line", "新蘆線": "brown_line",
            "綠線": "green_line", "松山新店線": "green_line",
            "橘線": "orange_line", "中和新蘆線": "orange_line"
        }

    def get_line_aliases(self):
        return list(self.line_mapping.keys())

    def load_stations(self):
        """載入捷運線對應的站資料"""
        stations_file = f"{self.data_path}/stations.json"
        with open(stations_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_ramen_shops(self):
        """載入每條捷運線的拉麵店推薦資料"""
        ramen_shops = {}
        lines = ['red_line', 'blue_line', 'yellow_line', 'brown_line', 'green_line', 'orange_line']
        for line in lines:
            ramen_file = f"{self.data_path}/{line}.json"
            with open(ramen_file, 'r', encoding='utf-8') as f:
                ramen_shops[line] = json.load(f)
        return ramen_shops

    def get_random_station(self, line):
        """隨機選擇某條捷運線上的一個站"""
        if line in self.stations:
            return f"{random.choice(self.stations[line])}好玩"
        else:
            return "?"

    def recommend_ramen(self, station_name):
        """根據站名名稱推薦拉麵店"""
        # 遍歷所有捷運線，檢查每條線的每個站點是否包含該站名
        for line, stations in self.stations.items():
            if station_name in stations:
                # 找到站點後，從對應的拉麵店推薦資料中返回該站點的推薦
                line = self.line_mapping.get(line)
                ramen_list = self.ramen_shops[line].get(station_name)
                if ramen_list:
                    return f"{random.choice(ramen_list)}好吃"
                else:
                    return f"{station_name}還沒有推薦的拉麵店。"
        return f"我只知道台北拉麵的資訊"

if __name__ == "__main__":
    
    mrt = MRT()

    # 假設用戶選擇了紅線
    line = '淡水信義線'

    # 隨機取得紅線上的捷運站
    random_station = mrt.get_random_station(line)
    print(f"隨機捷運站 ({line}): {random_station}")

    # 根據捷運站名稱推薦拉麵店
    ramen_recommendation = mrt.recommend_ramen(random_station)
    print(f"推薦的拉麵店: {ramen_recommendation}")





