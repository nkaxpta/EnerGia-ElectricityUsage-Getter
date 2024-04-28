from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import os
import datetime
import pandas
from dotenv import load_dotenv
load_dotenv()
# import openpyxl

def get_dates_between(start_date, end_date):
    
    date_list = []
    current_date = start_date

    while current_date <= end_date:
        date_list = [*date_list, current_date.strftime("%Y%m%d")]
        current_date += datetime.timedelta(days=1)
    return date_list

def get_dates_between_jp(start_date, end_date):
    
    date_list_jp = []
    current_date = start_date

    while current_date <= end_date:
        date_list_jp = [*date_list_jp, f"{current_date.month}月{current_date.day}日"]
        current_date += datetime.timedelta(days=1)
    return date_list_jp

LOGIN_URL = "https://www6.energia.co.jp/LWS8/UI/Login?goto=https%3A%2F%2Fwww7.energia.co.jp%3A443%2Fmy%2Fpage%2FLWSM002.xhtml"
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")

driver = webdriver.Remote(
    command_executor = os.environ["SELENIUM_URL"],
    options = webdriver.ChromeOptions()
)

driver.implicitly_wait(10)

driver.get(LOGIN_URL)

try:
    # ページ遷移
    user_id = driver.find_element(By.NAME, 'IDToken1')
    password = driver.find_element(By.NAME, 'IDToken2')

    user_id.clear()
    password.clear()

    user_id.send_keys(USER)
    password.send_keys(PASSWORD)
    driver.implicitly_wait(5)

    user_id.submit()
    driver.implicitly_wait(30)

    usage = driver.find_element(By.LINK_TEXT, "ご利用状況") 
    usage.click()
    driver.implicitly_wait(1)

    billing_link = driver.find_element(By.LINK_TEXT, "電気料金・使用量照会")
    billing_link.click()
    driver.implicitly_wait(1)

    usage_link = driver.find_element(By.LINK_TEXT, "5110-56211209-1") 
    usage_link.click()
    driver.implicitly_wait(5)

    driver.switch_to.window(driver.window_handles[1])

    payment_link = driver.find_element(By.CLASS_NAME, "snIcon02")
    payment_link.click()
    driver.implicitly_wait(1)

    halfHour_link = driver.find_element(By.LINK_TEXT, "30分値") 
    halfHour_link.click()
    driver.implicitly_wait(1)

    breakingNews_link = driver.find_element(By.LINK_TEXT, "速報値を確認") 
    breakingNews_link.click()
    driver.implicitly_wait(1)


    # 日付取得
    dt_now = datetime.datetime.now()
    end_date = datetime.datetime(dt_now.year, dt_now.month, dt_now.day, dt_now.hour, 0, 0)

    # 9日10時を過ぎているかどうかで分岐
    if end_date > datetime.datetime(dt_now.year, dt_now.month, 9, 10, 0, 0):
        start_date = datetime.datetime(dt_now.year, dt_now.month, 8, 0, 0, 0)
    elif end_date.day == 9 and end_date.hour <= 10:
        start_date = datetime.datetime(dt_now.year, dt_now.month-1, 8, 0, 0, 0)
        end_date = datetime.datetime(dt_now.year, dt_now.month, dt_now.day-1, 0, 0, 0)
    else:
        start_date = datetime.datetime(dt_now.year, dt_now.month-1, 8, 0, 0, 0)

    dates = get_dates_between(start_date, end_date)
    dates_jp = get_dates_between_jp(start_date, end_date)


    # ファイル名の調査&修正
    FILE_PATH = f"./{dt_now.strftime("%Y%m%d")}.xlsx"
    count = 2
    while(os.path.isfile(FILE_PATH)):
        FILE_PATH = f"./{dt_now.strftime("%Y%m%d")}_{count}.xlsx"
        count += 1

    # datesに格納されている日付の表示&値の取得
    for i in range(len(dates)):

        # 0時から6時の間に実行されていたらブレイク処理
        if (dt_now.month == int(dates[i][4:6]) and dt_now.day == int(dates[i][6:8]) and dt_now.hour < 6):
            break

        dayList = driver.find_element(By.CLASS_NAME, "selectShow")
        dayList.click()
        dates_select = Select(dayList)
        print(dates[i])
        dates_select.select_by_value(dates[i])

        table = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/table")
        trList = table.find_elements(By.TAG_NAME, "tr")

        write_arr = []

        for tr in trList:
            tr_data = []

            for data in tr.text.split():
                try:
                    tr_data = [*tr_data, float(data)]
                except ValueError:
                    tr_data = [*tr_data, data]

            write_arr = [*write_arr, tr_data]

        write_arr = [*write_arr, ["計", "=SUM(B2:B25)", "=SUM(C2:C25)", "=SUM(D2:D25)"]]
        
        # xlsxファイルの作成
        df = pandas.DataFrame(write_arr)
        if os.path.isfile(FILE_PATH):
            with pandas.ExcelWriter(FILE_PATH, engine="openpyxl", mode="a") as writer:
                df.to_excel(writer, sheet_name=f"{dates_jp[i]}", index=False, header=False)
        else:
            df.to_excel(FILE_PATH, sheet_name=f"{dates_jp[i]}", index=False, header=False)

        # wb = openpyxl.load_workbook(FILE_PATH)
        # ws = wb[dates_jp[i]]

except Exception as e:
    print(f"Error : {e}")

finally:
    driver.close()
    driver.quit()
