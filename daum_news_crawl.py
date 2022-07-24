import requests
import bs4
import time
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import pandas as pd
import re
import warnings
warnings.filterwarnings('ignore')

FROM_DATE = "YYYY-MM-DD"    #크롤링할 기사 날짜 지정
TO_DATE = "YYYY-MM-DD"


def crawling(date, title_list, content_list, date_list, category_list):
    '''
    기사 카테고리 목록
    금융 : finance                  기업산업 : industry         취업직장인 : employ
    경제일반 : others               자동차 : auto               주식 : stock
    시황분석 : stock/market         공시 : stock/publicnotice   해외증시 : stock/world
    채권선물 : stock/bondsfutures   외환 : stock/fx             주식일반 : stock/others
    부동산 : estate                 생활경제 : consumer         국제경제 : world
    '''
    options = Options()
    options.binary_location = r'C:\Program Files\Google\Chrome Beta\Application\chrome.exe'     #크롬 베타버전(104버전)을 사용했습니다
    driver = Chrome(options = options, executable_path = "chromedriver.exe")

    for kind in ['finance', 'stock', 'stock/world', 'world']: # 기사 카테고리
        for page in range(1, 999):  
            url = f'https://news.daum.net/breakingnews/economic/{kind}?page={page}&regDate={date}'
            driver.get(url)
            present_page = driver.find_elements(By.CLASS_NAME, value='num_page')[-1].text

            for num in range(1, 16):    # 해당 페이지의 모든 기사(15개)들을 탐색
                try:
                    time.sleep(0.5)
                    btn_path = f'//*[@id="mArticle"]/div[3]/ul/li[{num}]/div/strong/a'
                    driver.find_element_by_xpath(btn_path).click()

                    response = driver.page_source
                    one_page = bs4.BeautifulSoup(response)
                    
                    title = one_page.find('h3', 'tit_view', ).text
                    texts = one_page.find('div', {'id':'harmonyContainer'}).find('section').find_all('p')[:-1]
                    text = ""
                    for x in texts:
                        text = text + x.text + " "

                    if news_preprocess(text) == False: # 본문이 영어가 50% 이상 또는 본문이 200자 이하(공백 포함)인 경우 추가하지 않음
                        pass 
                    else:
                        title_list.append(title)
                        content_list.append(text)
                        date_list.append(date)
                        category_list.append(kind)
                                    
                    driver.back()
                except:                 # 해당 페이지에 기사가 full(15개)로 없을 경우 예외처리
                    pass

            if (int(present_page) == page):
                try:
                    next_btn = driver.find_element(By.CSS_SELECTOR, value='a.btn_page.btn_next').text
                    if '다음' in next_btn:
                        pass

                except:
                    break

    return title_list, content_list, date_list, category_list


def date_range(start, end): # 두 날짜 사이의 날짜 생성 함수
    start = datetime.strptime(start, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")
    dates = [(start + timedelta(days=i)).strftime("%Y%m%d") for i in range((end-start).days+1)]
    return dates


def news_preprocess(text):  # 문자열 절반이상이 영어인지 검색 (영자신문 제외하기 위해)
    cnt = 0
    if len(text) < 200: #본문이 200자보다 적으면 추가하지 않음 (글이 너무 적으면 기사 요약이 되지 않음)
        return False

    for ch in text:
        if ord('A') <= ord(ch) <= ord('z'):
            cnt += 1
        if cnt >= len(text)/2:
            return False
    return True


def main():
    category_list = []
    title_list = []
    content_list = []
    date_list = []

    for date in date_range(FROM_DATE, TO_DATE):
        title_list, content_list, date_list, category_list  = crawling(date, title_list, content_list, date_list, category_list)

        news_data = {'날짜':date_list, '카테고리':category_list, "긍부정":'', '제목':title_list, '본문':content_list}
        df = pd.DataFrame(news_data)
        csv_name = 'data/' + date + '.csv'
        df.to_csv(csv_name, encoding='utf-8-sig') 

        category_list.clear()
        title_list.clear()
        content_list.clear()
        date_list.clear()


if __name__ == "__main__":
    main()


