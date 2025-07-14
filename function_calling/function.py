from curl_cffi import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from io import BytesIO
from webdriver_manager.chrome import ChromeDriverManager
import fitz
import yfinance as yf
import re
import warnings
warnings.filterwarnings('ignore')

########################################################################################################################################################################

# 원하는 날짜의 종목 종가, 최고가, 최저가, 시가, 거래량 가져오는 함수.
def get_finance_info(symbols, start, end):
    print("get_finance_info")
    df = yf.download(symbols, start, end)
    infos = []

    for symbol in symbols:
        close = df.Close[symbol].values.tolist()
        high = df.High[symbol].values.tolist()
        low = df.Low[symbol].values.tolist()
        open = df.Open[symbol].values.tolist()
        volume = df.Volume[symbol].values.tolist()

        data = {
            f"{symbol}": {
                "종가": close,
                "최고가": high,
                "최저가": low,
                "시가": open,
                "거래량": volume,
            }
        }

        infos.append(data)

    return infos

########################################################################################################################################################################

# 분석가들의 평가를 가져오는 함수.
def get_finance_analized(symbols):
    print("get_finance_analized")
    infos = []

    for symbol in symbols:
        df = yf.Ticker(symbol)

        recommendations = df.recommendations

        recommendations.dropna(inplace=True)

        if recommendations.empty:
            continue

        strongBuy = recommendations.get("strongBuy").values.tolist()
        buy = recommendations.get("buy").values.tolist()
        hold = recommendations.get("hold").values.tolist()
        sell = recommendations.get("sell").values.tolist()
        strongSell = recommendations.get("strongSell").values.tolist()

        data = {
            f"{symbol}": {
                "strongBuy": strongBuy,
                "buy": buy,
                "hold": hold,
                "sell": sell,
                "strongSell": strongSell,
            }
        }

        infos.append(data)

    return infos

########################################################################################################################################################################

# 주어진 회사의 재무제표를 제공하는 함수.
def get_financial(symbols):
    print("get_financial")
    infos = {}

    for symbol in symbols:
        data = {}
        df = yf.Ticker(symbol).financials
        if df.empty:
            continue
        columns = df.columns.tolist()
        indexes = df.index.tolist()

        for column in columns:
            col = str(column.year) + '-' + str(column.month) + '-' + str(column.day)
            data[col] = {}
            for index in indexes:
                data[col][index] = df.loc[index, column]

        infos[symbol] = data

    return infos

########################################################################################################################################################################

# 네이버에서 최근 글로벌 경제 뉴스를 가져오는 함수.
def bring_recent_news_naver_global(top_n=30):
    print("bring_recent_news_naver_global")
    links, titles = bring_recent_news_links_naver_global(top_n=top_n)
    infos = {}

    for link, title in zip(links, titles):

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(link, headers=headers)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select("#dic_area")
        summary = soup.select_one(".media_end_summary")
        if summary is not None:
            content = summary.text

        content = ''

        for item in items:
            content += ' ' + item.text

        content = content.replace('\n', '').replace('\t', '')
        infos[title] = content

    return infos

def bring_recent_news_links_naver_global(top_n=30):
    url = "https://news.naver.com/breakingnews/section/101/262"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    link_items = soup.select(".sa_text > a")
    title_items = soup.select(".sa_text_strong")
    links = []
    titles = []

    for i, link_item in enumerate(link_items):
        if i >= top_n:
            break
        links.append(link_item['href'])

    for i, title_item in enumerate(title_items):
        if i >= top_n:
            break
        titles.append(title_item.text)

    return links, titles

########################################################################################################################################################################

# 네이버 최근 한국 경제 뉴스 가져오는 함수.
def bring_recent_news_naver_korea(top_n=30):
    print("bring_recent_news_naver_korea")
    links, titles = bring_recent_news_links_naver_korea(top_n=top_n)
    infos = {}

    for link, title in zip(links, titles):

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(link, headers=headers)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select("#dic_area")
        summary = soup.select_one(".media_end_summary")
        if summary is not None:
            content = summary.text

        content = ''

        for item in items:
            content += ' ' + item.text

        content = content.replace('\n', '').replace('\t', '')
        infos[title] = content

    return infos

def bring_recent_news_links_naver_korea(top_n=30):
    url = "https://news.naver.com/section/101"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    link_items = soup.select(".sa_text > a")
    title_items = soup.select(".sa_text_strong")
    links = []
    titles = []

    for i, link_item in enumerate(link_items):
        if i >= top_n:
            break
        links.append(link_item['href'])

    for i, title_item in enumerate(title_items):
        if i >= top_n:
            break
        titles.append(title_item.text)

    return links, titles

########################################################################################################################################################################

# 한국은행에서 pdf 파일 받아와 json형식으로 가져오는 함수.
def Korea_Bank_News_Text(page=5):
    print("Korea_Bank_News_Text")
    infos = []
    driver, situation_links, direction_links = Korea_Bank_News_Links(page=page)

    for link in situation_links:
        info = {}
        driver.get(link)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        item = soup.select_one(".down > dd > ul > li > a")

        pdf_type = "현지 정보"
        pdf_link = "https://www.bok.or.kr" + item["href"]
        pdf_title = item["title"][:item["title"].rfind(".")]
        response = requests.get(pdf_link)

        # 예외처리
        response.raise_for_status()

        doc = fitz.open(stream=BytesIO(response.content), filetype="pdf")
        text = "\n".join(page.get_text() for page in doc)

        info["type"] = pdf_type
        info[pdf_title] = del_chinese(text[:1000].replace("\n", ""))
        infos.append(info)

    for link in direction_links:
        info = {}
        try:
            driver.get(link)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            item = soup.select_one(".down > dd > ul > li > a")

            pdf_type = "동향 분석"
            pdf_link = "https://www.bok.or.kr" + item["href"]
            pdf_title = item["title"][:item["title"].rfind(".")]
            response = requests.get(pdf_link)

            # 예외처리
            response.raise_for_status()

            doc = fitz.open(stream=BytesIO(response.content), filetype="pdf")
            text = "\n".join(page.get_text() for page in doc)

            info["type"] = pdf_type
            info[pdf_title] = del_chinese(text[:1000].replace("\n", ""))
            infos.append(info)
        except requests.HTTPError as e:
            continue
    
    driver.quit()
    
    return infos

def Korea_Bank_News_Links(page=5):
    # ChromeDriver 경로 명시
    chromedriver_path = "/usr/local/bin/chromedriver"  # ChromeDriver 경로
    chrome_path = "/usr/bin/google-chrome"  # Chrome 브라우저 경로

    # Chrome 옵션 설정
    options = Options()
    options.add_argument("--headless")  # GUI 없이 실행
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.binary_location = chrome_path  # Chrome 브라우저 경로 설정

    # ChromeDriver 서비스 설정
    service = Service(chromedriver_path)

    # WebDriver 생성
    driver = webdriver.Chrome(service=service, options=options)
    situation_links = []
    direction_links = []

    for i in range(1, page+1):

        situation_url = f"https://www.bok.or.kr/portal/singl/newsData/list.do?pageIndex={i}&targetDepth=2&menuNo=200080&syncMenuChekKey=4&depthSubMain=&subMainAt=&searchCnd=1&searchKwd=%ED%98%84%EC%A7%80%EC%A0%95%EB%B3%B4&depth2=200080&date=&sdate=&edate=&sort=1&pageUnit=10"
        driver.get(situation_url)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select(".set > a")

        for item in items:
            if item["href"] == "#":
                continue

            situation_links.append("https://www.bok.or.kr" + item["href"])
    
    for i in range(1, page+1):

        direction_url = f"https://www.bok.or.kr/portal/singl/newsData/list.do?pageIndex={i}&targetDepth=2&menuNo=200080&syncMenuChekKey=2&depthSubMain=&subMainAt=&searchCnd=1&searchKwd=%EB%8F%99%ED%96%A5%EB%B6%84%EC%84%9D&depth2=200080&date=&sdate=&edate=&sort=1&pageUnit=10"
        driver.get(direction_url)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select(".set > a")

        for item in items:
            if item["href"] == "#":
                continue

            direction_links.append("https://www.bok.or.kr" + item["href"])

    return driver, situation_links, direction_links

def del_chinese(readData):
    text = re.sub(r'[\u4e00-\u9fff]+', '', readData)
    return text