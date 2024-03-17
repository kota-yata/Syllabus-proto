import csv
from datetime import datetime

from selenium import webdriver as selenium_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


# google colab用のセットアップ
def setup_webdriver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--no-sandbox")
    options.add_argument("--lang=ja")

    return selenium_webdriver.Chrome(options=options)


# calculate year and semester
YEAR = str(datetime.now().year)
# 春休みの始まり(2月)から春学期の終わり(7月)まではspring、それ以外はfall
SEMESTER = "spring" if 2 <= datetime.now().month <= 7 else "fall"


# Function to scrape and save data
def scrape_and_save_data(driver, start_page=1, end_page=10):
    # ここのリンクは、シラバス検索で春学期の授業を検索したすべての検索結果
    base_url = f"https://syllabus.sfc.keio.ac.jp/courses?button=&locale=ja&page={{}}&search%5Bsemester%5D={SEMESTER}&search%5Bsfc_guide_title%5D=&search%5Bsub_semester%5D=&search%5Bsummary%5D=&search%5Bteacher_name%5D=&search%5Btitle%5D=&search%5Byear%5D={YEAR}"
    output_file = "syllabus_data.csv"
    link_list = []

    # csvの作成
    with open(output_file, mode='w', encoding='utf-8', newline='') as new_file:
        writer = csv.writer(new_file)
        writer.writerow(["index", "subject_name", "term", "about", "method", "place", "lang", "year", "semester",
                         "is_giga", "url", "faculty", "field", "credit", "day", "period", "staff_name", "style"])

    # 合計ページの計算
    total_pages = end_page - start_page + 1

    # スクレイピングの開始。ここで授業詳細が存在するページを抽出する
    for page_num in range(start_page, end_page + 1):
        print(f"Scraping data from page {page_num} ({(page_num - start_page + 1) / total_pages * 100:.2f}% complete)")
        driver.get(base_url.format(page_num))

        # 「詳細」のxpathのリンクを記録
        for link_num in range(1, 26):
            link_xpath = f"/html/body/div[2]/div/div[1]/div[2]/ul/li[{link_num}]/div[4]/a"
            course_link = driver.find_elements(By.XPATH, link_xpath)

            # 存在しなければ次に
            if not course_link:
                continue

            # リンクを記録
            href = course_link[0].get_attribute("href")
            course_id = href.replace("https://syllabus.sfc.keio.ac.jp/courses/2024_", "").replace("?locale=ja", "")
            link_list.append(course_id)

        # 最後まで行ったら次ページへ遷移
        next_page_button = driver.find_elements(By.XPATH, "/html/body/div[2]/div/div[1]/div[3]/nav/span[7]/a")
        if next_page_button:
            next_page_button[0].click()

    # 合計のコース数を計算
    total_courses = len(link_list)

    # 記録されたリンクの情報を抽出
    for i, course_id in enumerate(link_list, start=1):
        print(f"Scraping data for course ID: {course_id} ({i / total_courses * 100:.2f}% complete)")

        course_url = f"https://syllabus.sfc.keio.ac.jp/courses/2024_{course_id}?locale=ja"

        driver.get(course_url)

        # 研究会と授業で2パターンあるので、分野が研究プロジェクト科目かどうかで判断する
        field_xpath = "/html/body/div[2]/div/div[1]/div[1]/div/dl[3]/dd[1]"
        field_elements = driver.find_elements(By.XPATH, field_xpath)
        if field_elements and field_elements[0].text == "研究プロジェクト科目":
            # 研究会用
            day_xpath = "/html/body/div[2]/div/div[1]/div[2]/dl[3]/dd"
            place_xpath = "/html/body/div[2]/div/div[1]/div[2]/dl[7]/dd"
            staff_name_xpath = "/html/body/div[2]/div/div[1]/div[2]/dl[4]/dd"
            lang_xpath = "/html/body/div[2]/div/div[1]/div[2]/dl[6]/dd"
            style_xpath = "/html/body/div[2]/div/div[1]/div[2]/dl[8]/dd"
            method_xpath = "/html/body/div[2]/div/div[1]/div[2]/dl[5]/dd"
            giga_xpath = "/html/body/div[2]/div/div[1]/div[2]/dl[9]/dd"
        else:
            # 授業
            day_xpath = "/html/body/div[2]/div/div[1]/div[2]/dl[2]/dd"
            place_xpath = "/html/body/div[2]/div/div[1]/div[2]/dl[6]/dd"
            staff_name_xpath = "/html/body/div[2]/div/div[1]/div[2]/dl[3]/dd"
            lang_xpath = "/html/body/div[2]/div/div[1]/div[2]/dl[5]/dd"
            style_xpath = "/html/body/div[2]/div/div[1]/div[2]/dl[7]/dd"
            method_xpath = "/html/body/div[2]/div/div[1]/div[2]/dl[4]/dd"
            giga_xpath = "/html/body/div[2]/div/div[1]/div[2]/dl[8]/dd"

        # 情報を抽出
        try:
            subject_name = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[1]/div[1]/div/dl[2]/dd[2]").text
        except:
            subject_name = ""

        try:
            term_element = driver.find_element(By.XPATH, "/html/body/div[2]/div/h2/span[2]")
            term_text = term_element.text
            term = term_text.strip("【】") if "【" in term_text else "通期"
        except:
            term = ""

        try:
            about = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/dl/dd/p").text
        except:
            about = ""

        try:
            method = driver.find_element(By.XPATH, method_xpath).text
        except:
            method = ""

        try:
            place = driver.find_element(By.XPATH, place_xpath).text
        except:
            place = ""

        try:
            lang = driver.find_element(By.XPATH, lang_xpath).text
        except:
            lang = ""

        giga_text = driver.find_element(By.XPATH, giga_xpath).text
        is_giga = (giga_text == "対象")
        if not is_giga and giga_text != "非対象":
            raise ValueError("GIGA text not found.")

        url = driver.current_url

        try:
            faculty = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[1]/div[1]/div/dl[1]/dd[1]").text
        except:
            faculty = ""

        try:
            field = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[1]/div[1]/div/dl[3]/dd[1]").text
            field = field.replace("データサイエンス科目-", "").replace("先端科目-", "")
        except:
            field = ""

        try:
            credit = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[1]/div[1]/div/dl[3]/dd[2]").text
        except:
            credit = ""

        try:
            day = driver.find_element(By.XPATH, day_xpath).text
        except:
            day = ""

        try:
            period = driver.find_element(By.XPATH, day_xpath).text
        except:
            period = ""

        try:
            staff_name = driver.find_element(By.XPATH, staff_name_xpath).text
        except:
            staff_name = ""

        try:
            style = driver.find_element(By.XPATH, style_xpath).text
        except:
            style = ""

        # csvに出力
        with open(output_file, mode='a', encoding='utf-8', newline='') as existing_file:
            writer = csv.writer(existing_file)
            semester_str = "春" if SEMESTER == "spring" else "秋"
            writer.writerow([course_id, subject_name, term, about, method, place, lang, YEAR, semester_str,
                             is_giga, url, faculty, field, credit, day, period, staff_name, style])

        print(f"Scraping data complete for course ID: {course_id} ({i / total_courses * 100:.2f}% complete)")

    print("Scraping complete!")


webdriver = setup_webdriver()

# リンクの抽出用関数
scrape_and_save_data(webdriver, start_page=1, end_page=53)
webdriver.quit()
