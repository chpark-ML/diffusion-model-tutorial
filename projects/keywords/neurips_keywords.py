import argparse
import functools
import multiprocessing
import logging
import os

import fitz  # PyMuPDF
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from commons.utils import chunkify, extract_paper_info

logger = logging.getLogger(__name__)

MAX_NUM_PAPER = 10000


def process(paper_links_chunks, base_url, is_sanity=False):
    """
    Given a NeurIPS conference year, extracts paper titles, authors, abstracts, PDF URLs, and publication dates,
    and returns them as a DataFrame.
    """
    paper_data = []
    for link in tqdm(
            paper_links_chunks, total=len(paper_links_chunks), desc="Processing Papers"
    ):
        link = BeautifulSoup(link, "html.parser").a
        breakpoint()
        if "/paper/" not in link["href"]:
            continue

        paper_id = link["href"].split("/")[-1]
        paper_url = f"{base_url}/hash/{paper_id}"
        

        # 논문 정보 추출
        title, authors, abstract, pdf_url, publication_date = extract_paper_info(paper_url)

        # PDF 파일 다운로드, 텍스트 추출
    #     pdf_content = download_pdf_from_url(pdf_url)
    #     pdf_text = extract_text_from_pdf(pdf_content)

    #     # 논문 데이터 추가
    #     paper_data.append({"Title": title,
    #                        "Authors": authors,
    #                        "Abstract": abstract,
    #                        "PDF Text": pdf_text,
    #                        "PDF URL": pdf_url,
    #                        "Publication date": publication_date})
    # if len(paper_data) == 0:
    #     return pd.DataFrame(
    #         pd.DataFrame(columns=["Title",
    #                               "Authors",
    #                               "Abstract",
    #                               "PDF Text",
    #                               "PDF_URL",
    #                               "Publication_Date"]))
    # else:
    #     return pd.DataFrame(paper_data)
    

def main():
    parser = argparse.ArgumentParser(description="neurips info extraction")
    parser.add_argument("--year", default=2023, type=int)
    parser.add_argument("--sanity_check", type=bool, default=False)
    parser.add_argument("--num_shards", default=32, type=int)
    args = parser.parse_args()

    base_url = f"https://openreview.net/group?id=NeurIPS.cc/{args.year}/Conference#tab-accept-oral"
    response = requests.get(base_url)
    response.raise_for_status()


    # Find all links related to papers
    soup = BeautifulSoup(response.text, "html.parser")
    papers = soup.find_all('a', href=True)

    /html/body/div/div[3]/div/div/main/div/div[3]/div/div[2]/div[2]/div/div/ul/li[1]/div/h4/a[1]

    # Filter links that seem to be paper links (you may need to adjust this based on the actual structure)
    paper_links = [a['href'] for a in papers if 'forum?id=' in a['href']]

    paper_links = []
    for link in soup.find_all('a', href=True):
        print(link)
        # href = link['href']
        # print(href)
        # if 'forum?id=' in href:
        #     paper_links.append(href)
    breakpoint()
    
    paper_links = soup.find_all("a", href=True)
    paper_links = paper_links[:MAX_NUM_PAPER]
    logger.info(f"number of paper link to process : {len(paper_links)}.")

    # multiprocessing에서 beautifulsoup 객체를 받으니 에러 발생, str으로 변환하고 process 함수안에서 역변환 수행
    paper_links = [str(link) for link in paper_links]
    paper_links_chunks = list(chunkify(paper_links, args.num_shards))
    breakpoint()
    results = process(paper_links_chunks[0], base_url=base_url, is_sanity=True)

if __name__ == "__main__":
    main()

