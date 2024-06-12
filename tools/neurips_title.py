import requests
from bs4 import BeautifulSoup

def crawl_neurips_papers(year):
    # NeurIPS 논문 목록 페이지 URL
    url = f'https://papers.nips.cc/paper_files/paper/{year}'
    
    # 웹 페이지 요청
    response = requests.get(url)
    response.raise_for_status()  # 요청 실패 시 예외 발생

    # BeautifulSoup을 사용하여 HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')

    # 논문 제목을 포함하는 HTML 요소 찾기 ('a' 태그 중 특정 클래스 속성을 가진 요소 찾기)
    paper_links = soup.find_all('a', href=True)

    # 논문 제목 리스트 추출
    paper_titles = [link.text for link in paper_links if '/paper_files/paper/' in link['href']]

    # 논문 제목 리스트 출력
    for title in paper_titles:
        print(title)

    # 논문 수 카운트
    paper_count = len(paper_titles)
    print(f'Total number of papers in Neurips {year}: {paper_count}')
    return paper_count

# 예시: 2023년 NeurIPS 논문 크롤링
year = 2023
total_papers = crawl_neurips_papers(year)
