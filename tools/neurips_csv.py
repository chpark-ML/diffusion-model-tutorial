import pandas as pd
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm

import fitz  # PyMuPDF
from io import BytesIO
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# NLTK에서 영어의 불용어(stopwords) 다운로드
nltk.download('stopwords')
nltk.download('punkt')

YEAR = 2023
BASE_URL = f"https://papers.nips.cc/paper_files/paper/{YEAR}"
MAX_NUM_PAPER = 10000
TOP_K = 10

def download_pdf_from_url(pdf_url):
    """
    Download a PDF file from a URL and return the file content as bytes.
    """
    response = requests.get(pdf_url)
    response.raise_for_status()
    return response.content

def extract_text_from_pdf(pdf_content, stop_pattern='References\n'):
    """
    Extract text content from a PDF file until the stop pattern is encountered.
    """
    doc = fitz.open(stream=pdf_content, filetype="pdf")
    text = ""
    for page in doc:
        page_text = page.get_text()
        if stop_pattern in page_text:
            # References 패턴이 나오면 그 이전까지의 텍스트만 추출
            text += page_text.split(stop_pattern)[0]
            break
        text += page_text
    return text

def calculate_tfidf(text):
    """
    Calculate TF-IDF scores for each word in the text and return a dictionary of words and their TF-IDF scores.
    """
    # TF-IDF vectorization
    tfidf_vectorizer = TfidfVectorizer(stop_words=stopwords.words('english'))
    tfidf_matrix = tfidf_vectorizer.fit_transform([text])
    feature_names = tfidf_vectorizer.get_feature_names_out()

    # Create a dictionary of words and their TF-IDF scores
    word_tfidf = {word: score for word, score in zip(feature_names, tfidf_matrix.toarray()[0])}
    return word_tfidf

def extract_key_words_in_abstract(text):
    """
    Given text, returns key words using TF-IDF.
    """
    # Initialize TF-IDF vectorizer
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    
    # Fit the vectorizer and transform the text
    tfidf_matrix = tfidf_vectorizer.fit_transform([text])
    
    # Get feature names (words)
    feature_names = tfidf_vectorizer.get_feature_names_out()
    
    # Get TF-IDF scores
    tfidf_scores = tfidf_matrix.toarray()[0]
    
    # Create a dictionary of words and their TF-IDF scores
    word_tfidf = {word: score for word, score in zip(feature_names, tfidf_scores)}
    
    # Select top 5 words with highest TF-IDF scores
    top_words = sorted(word_tfidf.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Return only the words (without scores)
    return [word for word, _ in top_words]


def extract_paper_info(url):
    """
    Given a URL of a NeurIPS paper, extracts the title, authors, abstract, PDF URL, and publication date.
    """
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.find('title').get_text(strip=True)
    
    # 클래스 이름이 있는 요소를 필터링하여 제외합니다.
    exclusion = ['fa-sign-in-alt', 'fa-sign-out-alt']
    authors = ', '.join([author.get_text(strip=True) for author in soup.find_all('i') if not any(ex in author.get('class', []) for ex in exclusion)])


    abstract = soup.find('h4', string='Abstract').find_next('p').get_text(strip=True)
    pdf_url = soup.find('meta', {'name': 'citation_pdf_url'})['content']
    publication_date = soup.find('meta', {'name': 'citation_publication_date'})['content']

    return title, authors, abstract, pdf_url, publication_date


def create_paper_dataframe():
    """
    Given a NeurIPS conference year, extracts paper titles, authors, abstracts, PDF URLs, and publication dates,
    and returns them as a DataFrame.
    """
    response = requests.get(BASE_URL)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    paper_links = soup.find_all('a', href=True)

    _counter = 0
    paper_data = []
    # tqdm 루프를 사용하여 진행 상황을 표시하며, 최대 10개의 논문만 처리합니다.
    for link in tqdm(paper_links, total=len(paper_links), desc="Processing Papers"):
        _counter += 1
        if _counter >= MAX_NUM_PAPER:
            break
        if '/paper/' not in link['href']:
            continue
        
        paper_id = link['href'].split('/')[-1]
        paper_url = f'{BASE_URL}/hash/{paper_id}'

        # 논문 정보 추출
        title, authors, abstract, pdf_url, publication_date = extract_paper_info(paper_url)
        key_words_in_abstract = extract_key_words_in_abstract(abstract)

        # PDF 파일 다운로드
        pdf_content = download_pdf_from_url(pdf_url)

        # PDF 파일에서 텍스트 추출
        pdf_text = extract_text_from_pdf(pdf_content)

        # TF-IDF 계산
        word_tfidf = calculate_tfidf(pdf_text)

        # TF-IDF가 높은 단어 10개 출력
        key_words_in_paper = sorted(word_tfidf.items(), key=lambda x: x[1], reverse=True)[:TOP_K]
        # key_words_in_paper_str = ', '.join([f"{word} ({score:.2f})" for word, score in key_words_in_paper])
        key_words_in_paper_str = ', '.join([f"{word}" for word, score in key_words_in_paper])

        # 논문 데이터 추가
        paper_data.append({
            'Title': title,
            'Authors': authors,
            'Abstract': abstract,
            'PDF_URL': pdf_url,
            'Publication_Date': publication_date,
            'Key_Words_in_Abstract': ', '.join(key_words_in_abstract),
            'Key_Words_in_Paper': key_words_in_paper_str
        })

    return pd.DataFrame(paper_data)


def save_dataframe_to_csv(dataframe, filename):
    """
    Saves a DataFrame to a CSV file.
    """
    dataframe.to_csv(filename, index=False)

# 예시: 2023년 NeurIPS 논문 추출하여 데이터프레임 생성하고 CSV 파일로 저장
papers_df = create_paper_dataframe()
save_dataframe_to_csv(papers_df, f'neurips_papers_{YEAR}.csv')
