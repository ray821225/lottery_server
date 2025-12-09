from flask import Flask, jsonify
from flask_cors import CORS
import random
import datetime
import requests
from bs4 import BeautifulSoup
from TaiwanLottery import TaiwanLotteryCrawler
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time


app = Flask(__name__)
CORS(app)  # 允許所有來源訪問 API


@app.route("/lotto", methods=["GET"])
def get_lotto_results():

    # 取得今天的日期
    today = datetime.date.today()
    year = str(today.year)
    month = today.month

    # 將月轉為兩位數字字串（例如 5 -> '05'）
    month_str = f"{month:02d}"

    # 取得最新樂透開獎號碼
    lottery = TaiwanLotteryCrawler()
    latest_result = lottery.lotto649([year, month_str])

    # 若當月查無資料，往前一個月試
    if not latest_result:
        # 處理跨年情況
        if month == 1:
            year = str(int(year) - 1)
            month = 12
        else:
            month -= 1

        month_str = f"{month:02d}"
        latest_result = lottery.lotto649([year, month_str])

        # 若還是查無資料
        if not latest_result:
            return jsonify({"error": f"查無 {year} 年 {month_str} 月資料"}), 404

    # 確保資料正確取出
    if isinstance(latest_result, list) and len(latest_result) > 0:
        latest_result = latest_result[0]
    else:
        return jsonify({"error": f"查無 {year} 年 {month_str} 月資料"}), 404

    winning_numbers = latest_result.get("獎號", [])
    special_number = latest_result.get("特別號")
    draw_date = latest_result.get("開獎日期", "")

    return jsonify(
        {
            "draw_date": draw_date,
            "winning_numbers": winning_numbers,
            "special_number": special_number,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
