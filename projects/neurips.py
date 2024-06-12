import requests
from bs4 import BeautifulSoup
from collections import Counter
import re

# URL of the webpage to be crawled
url = "https://neurips.cc/virtual/2023/papers.html?filter=titles"

# Send a GET request to the webpage
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the content of the webpage
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract text from the webpage
    text = soup.get_text()

    # Use regular expressions to find all words (sequences of alphanumeric characters)
    words = re.findall(r'\b\w+\b', text)

    # Convert all words to lower case to make the word count case-insensitive
    words = [word.lower() for word in words]

    # Count the frequency of each word
    word_counts = Counter(words)

    # Sort the words by their frequency in ascending order
    sorted_word_counts = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)

    # Print the most common words and their counts, ensuring count is aligned
    _num = 100
    max_word_length = max(len(word) for word, _ in sorted_word_counts[:_num])
    max_count_length = max(len(str(count)) for _, count in sorted_word_counts[:_num])
    for word, count in sorted_word_counts[:_num]:
        print(f'{word.ljust(max_word_length)}: {str(count).rjust(max_count_length)}')
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
