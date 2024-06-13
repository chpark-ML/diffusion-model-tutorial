import argparse
import functools
import multiprocessing
import logging
import os

import fitz  # PyMuPDF
import nltk
import pandas as pd
import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm


_THIS_DIR = os.path.dirname(os.path.realpath(__file__))
logger = logging.getLogger(__name__)

# NLTK에서 영어의 불용어(stopwords) 다운로드
nltk.download("stopwords")
nltk.download("punkt")

YEAR = 2023
BASE_URL = f"https://papers.nips.cc/paper_files/paper/{YEAR}"
MAX_NUM_PAPER = 10000
TOP_K = 10


def log_error(error_id, error):
    """
    Log the error with the title and error message.
    """
    logger.info(f"ID: {error_id}")
    logger.info(f"Error: {error}")


def download_pdf_from_url(pdf_url):
    """
    Download a PDF file from a URL and return the file content as bytes.
    """
    response = requests.get(pdf_url)
    response.raise_for_status()
    return response.content


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


def calculate_tfidf(text):
    """
    Calculate TF-IDF scores for each word in the text and return a dictionary of words and their TF-IDF scores.
    """
    # Check if the input text is empty or contains only stop words
    if not text.strip():
        raise ValueError("The input text is empty.")

    # TF-IDF vectorization
    tfidf_vectorizer = TfidfVectorizer(stop_words=stopwords.words("english"))
    tfidf_matrix = tfidf_vectorizer.fit_transform([text])

    # Check if the resulting matrix is empty
    if tfidf_matrix.shape[1] == 0:
        raise ValueError("The input text contains only stop words or no valid words for TF-IDF calculation.")

    feature_names = tfidf_vectorizer.get_feature_names_out()

    # Create a dictionary of words and their TF-IDF scores
    word_tfidf = {word: score for word, score in zip(feature_names, tfidf_matrix.toarray()[0])}

    return word_tfidf


def extract_paper_info(url):
    """
    Given a URL of a NeurIPS paper, extracts the title, authors, abstract, PDF URL, and publication date.
    """
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.find("title").get_text(strip=True)

    # 클래스 이름이 있는 요소를 필터링하여 제외합니다.
    exclusion = ["fa-sign-in-alt", "fa-sign-out-alt"]
    authors = ", ".join([author.get_text(strip=True)
                         for author in soup.find_all("i")
                         if not any(ex in author.get("class", []) for ex in exclusion)])

    abstract = soup.find("h4", string="Abstract").find_next("p").get_text(strip=True)
    pdf_url = soup.find("meta", {"name": "citation_pdf_url"})["content"]
    publication_date = soup.find("meta", {"name": "citation_publication_date"})["content"]

    return title, authors, abstract, pdf_url, publication_date


def process(paper_links_chunks, is_sanity=False):
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
        paper_url = f"{BASE_URL}/hash/{paper_id}"

        # 논문 정보 추출
        title, authors, abstract, pdf_url, publication_date = extract_paper_info(
            paper_url
        )
        try:
            key_words_in_abstract = calculate_tfidf(abstract)
        except ValueError as e:
            log_error(title, e)
            continue
        key_words_in_abstract = sorted(
            key_words_in_abstract.items(), key=lambda x: x[1], reverse=True
        )[:TOP_K]
        key_words_in_abstract = [word for word, _ in key_words_in_abstract]

        # PDF 파일 다운로드, 텍스트 추출
        pdf_content = download_pdf_from_url(pdf_url)
        pdf_text = extract_text_from_pdf(pdf_content)

        # TF-IDF 계산
        try:
            word_tfidf = calculate_tfidf(pdf_text)
        except ValueError as e:
            log_error(title, e)
            continue

        # TF-IDF가 높은 단어 topk 출력
        key_words_in_paper = sorted(
            word_tfidf.items(), key=lambda x: x[1], reverse=True
        )[:TOP_K]
        key_words_in_paper = [word for word, _ in key_words_in_paper]

        # 논문 데이터 추가
        paper_data.append({"Title": title,
                           "Authors": authors,
                           "Abstract": abstract,
                           "PDF URL": pdf_url,
                           "Publication date": publication_date,
                           "TF-IDF given Abstract": ", ".join(key_words_in_abstract),
                           "TF-IDF given FullText": ", ".join(key_words_in_paper)})
    if len(paper_data) == 0:
        return pd.DataFrame(
            pd.DataFrame(columns=["Title",
                                  "Authors",
                                  "Abstract",
                                  "PDF_URL",
                                  "Publication_Date",
                                  "Key_Words_in_Abstract",
                                  "Key_Words_in_Paper"]))
    else:
        return pd.DataFrame(paper_data)


def save_dataframe_to_csv(dataframe, filename):
    """
    Saves a DataFrame to a CSV file.
    """
    dataframe.to_csv(filename + ".csv", index=False)
    dataframe.to_excel(filename + ".xlsx", index=False)


def chunkify(lst, n):
    """리스트를 n 개의 청크로 나누는 함수"""
    chunk_size = len(lst) // n + (len(lst) % n > 0)
    for i in range(0, len(lst), chunk_size):
        yield lst[i: i + chunk_size]


def main():
    parser = argparse.ArgumentParser(description="neurips info extraction")
    parser.add_argument("--sanity_check", type=bool, default=False)
    parser.add_argument("--num_shards", default=32, type=int)
    args = parser.parse_args()

    response = requests.get(BASE_URL)
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
        results = process(paper_links_chunks[0], is_sanity=True)

    with multiprocessing.Pool(args.num_shards) as p:
        results = p.map(functools.partial(process, is_sanity=False), paper_links_chunks)

    if isinstance(results, pd.DataFrame):
        papers_df = results
    else:
        papers_df = pd.concat(results, ignore_index=True)
    save_dataframe_to_csv(papers_df, f'neurips_papers_{YEAR}')


if __name__ == "__main__":
    main()
