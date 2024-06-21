import fitz  # PyMuPDF
import nltk
import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer


# NLTK에서 영어의 불용어(stopwords) 다운로드
nltk.download("stopwords")
nltk.download("punkt")

def calculate_tfidf(text):
    """
    Calculate TF-IDF scores for each word in the text and return a dictionary of words and their TF-IDF scores.
    """
    # Check if the input text is empty or contains only stop words
    if not isinstance(text, list):
        if not text.strip():
            raise ValueError("The input text is empty.")
        docs = [text]
    else:
        docs = text

    # TF-IDF vectorization
    tfidf_vectorizer = TfidfVectorizer(stop_words=stopwords.words("english"))

    tfidf_matrix = tfidf_vectorizer.fit_transform(docs)

    # Check if the resulting matrix is empty
    if tfidf_matrix.shape[1] == 0:
        raise ValueError("The input text contains only stop words or no valid words for TF-IDF calculation.")

    feature_names = tfidf_vectorizer.get_feature_names_out()

    # Create a dictionary of words and their TF-IDF scores
    word_tfidf = [{word: score for word, score in zip(feature_names, tfidf_matrix.toarray()[idx])}
                  for idx, _ in enumerate(docs)]

    return word_tfidf


def chunkify(lst, n):
    """리스트를 n 개의 청크로 나누는 함수"""
    chunk_size = len(lst) // n + (len(lst) % n > 0)
    for i in range(0, len(lst), chunk_size):
        yield lst[i: i + chunk_size]


def download_pdf_from_url(pdf_url):
    """
    Download a PDF file from a URL and return the file content as bytes.
    """
    response = requests.get(pdf_url)
    response.raise_for_status()
    return response.content


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
