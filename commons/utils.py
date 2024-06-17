import nltk
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
