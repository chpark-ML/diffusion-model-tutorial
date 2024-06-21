import argparse
import functools
import multiprocessing
import logging

import fitz  # PyMuPDF
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from commons.utils import calculate_tfidf, chunkify, download_pdf_from_url, extract_paper_info


logger = logging.getLogger(__name__)

MAX_NUM_PAPER = 10000
TOP_K = 10


def log_error(error_id, error):
    """
    Log the error with the title and error message.
    """
    logger.info(f"ID: {error_id}")
    logger.info(f"Error: {error}")

    
def extract_text_from_pdf(pdf_content, stop_pattern="References\n"):
    """
    Extract text content from a PDF file until the stop pattern is encountered.
    """
    try:
        # Open the PDF file
        doc = fitz.open(stream=pdf_content, filetype="pdf")

        # Extract text from each page
        text = ""
        for page in doc:
            page_text = page.get_text()
            if stop_pattern in page_text:
                # References 패턴이 나오면 그 이전까지의 텍스트만 추출
                text += page_text.split(stop_pattern)[0]
                break
            text += page_text

        return text

    except fitz.FileDataError as e:
        log_error(pdf_content, e)
        return None

    except fitz.FileDataError as e:
        log_error(pdf_content, e)
        return None

    except Exception as e:
        log_error(pdf_content, e)
        return None
    

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
        if "/paper/" not in link["href"]:
            continue

        paper_id = link["href"].split("/")[-1]
        paper_url = f"{base_url}/hash/{paper_id}"

        # 논문 정보 추출
        title, authors, abstract, pdf_url, publication_date = extract_paper_info(paper_url)

        # PDF 파일 다운로드, 텍스트 추출
        pdf_content = download_pdf_from_url(pdf_url)
        pdf_text = extract_text_from_pdf(pdf_content)

        # 논문 데이터 추가
        paper_data.append({"Title": title,
                           "Authors": authors,
                           "Abstract": abstract,
                           "PDF Text": pdf_text,
                           "PDF URL": pdf_url,
                           "Publication date": publication_date})
    if len(paper_data) == 0:
        return pd.DataFrame(
            pd.DataFrame(columns=["Title",
                                  "Authors",
                                  "Abstract",
                                  "PDF Text",
                                  "PDF_URL",
                                  "Publication_Date"]))
    else:
        return pd.DataFrame(paper_data)


def save_dataframe_to_csv(dataframe, filepath, filename):
    """
    Saves a DataFrame to a CSV file.
    """
    dataframe.to_csv(filename + ".csv", index=False)
    dataframe.to_excel(filename + ".xlsx", index=False)


def main():
    parser = argparse.ArgumentParser(description="neurips info extraction")
    parser.add_argument("--year", default=2023, type=int)
    parser.add_argument("--sanity_check", type=bool, default=False)
    parser.add_argument("--num_shards", default=32, type=int)
    args = parser.parse_args()

    base_url = f"https://papers.nips.cc/paper_files/paper/{args.year}"
    response = requests.get(base_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    paper_links = soup.find_all("a", href=True)
    paper_links = paper_links[:MAX_NUM_PAPER]
    logger.info(f"number of paper link to process : {len(paper_links)}.")

    # multiprocessing에서 beautifulsoup 객체를 받으니 에러 발생, str으로 변환하고 process 함수안에서 역변환 수행
    paper_links = [str(link) for link in paper_links]
    paper_links_chunks = list(chunkify(paper_links, args.num_shards))

    # sanity check
    if args.sanity_check:
        results = process(paper_links_chunks[0], base_url=base_url, is_sanity=True)

    with multiprocessing.Pool(args.num_shards) as p:
        results = p.map(functools.partial(process, base_url=base_url, is_sanity=False), paper_links_chunks)

    if isinstance(results, pd.DataFrame):
        papers_df = results
    else:
        papers_df = pd.concat(results, ignore_index=True)

    titles = papers_df["Title"].astype(str).tolist()
    word_tfidf = calculate_tfidf(titles)
    key_words_list = []
    for tfidf_dict in word_tfidf:
        key_words = sorted(tfidf_dict.items(), key=lambda x: x[1], reverse=True)[:TOP_K]
        key_words = {word: score for word, score in key_words if score >= 0.05}  # Title 길이는 짧아서 쓸모없는 Keyword가 많이 들어올 수 있음.
        key_words_list.append(key_words)
    papers_df["TF-IDF given the whole Title"] = key_words_list

    abstracts = papers_df["Abstract"].astype(str).tolist()
    word_tfidf = calculate_tfidf(abstracts)
    key_words_list = []
    for tfidf_dict in word_tfidf:
        key_words = sorted(tfidf_dict.items(), key=lambda x: x[1], reverse=True)[:TOP_K]
        key_words = {word: score for word, score in key_words if score >= 0.05}
        key_words_list.append(key_words)
    papers_df["TF-IDF given the whole Abstract"] = key_words_list

    del papers_df["PDF Text"]

    save_dataframe_to_csv(papers_df, 'assets', f'neurips_papers_{args.year}')


if __name__ == "__main__":
    main()
