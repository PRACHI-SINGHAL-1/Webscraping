import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# Load the Excel file
df = pd.read_excel('input.xlsx')

def extract_article_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract the title
    title = soup.find('h1').get_text() if soup.find('h1') else "No Title Found"
    
    # Extract the article content
    content_div = soup.find('div', class_='td-post-content tagdiv-type')
    if not content_div:
        content_div = soup.find('div', class_='td_block_wrap tdb_single_content tdi_130 td-pb-border-top td_block_template_1 td-post-content tagdiv-type')
        
    paragraphs = content_div.find_all('p') if content_div else []
    orderlist = content_div.find_all('ol') if content_div else []
    unorderlist = content_div.find_all('ul') if content_div else []
    content = "\n".join([para.get_text() for para in paragraphs])
    ocontent = "\n".join([order.get_text() for order in orderlist])
    ucontent = "\n".join([unorder.get_text() for unorder in unorderlist])
    
    # Combine title and content
    full_text = f"{title}\n\n{content}\n\n{ocontent}\n\n{ucontent}"
    return full_text

# Ensure the output directory exists
output_dir = "articles"
os.makedirs(output_dir, exist_ok=True)

# Iterate through each URL and save the corresponding article
for index, row in df.iterrows():
    url_id = row['URL_ID']
    url = row['URL']
    try:
        article_text = extract_article_text(url)
        with open(f"{output_dir}/{url_id}.txt", "w", encoding='utf-8') as file:
            file.write(article_text)
        print(f"Successfully saved article {url_id}")
    except Exception as e:
        print(f"Failed to save article {url_id} from {url}: {e}")

print("Finished processing all articles.")


############CLEANING###################


import os
import pandas as pd

def load_stop_words(stopwords_folder):
    stop_words = set()
    for filename in os.listdir(stopwords_folder):
        if filename.endswith(".txt"):
            with open(os.path.join(stopwords_folder, filename), 'r', encoding='utf-8', errors='ignore') as file:
                for line in file:
                    stop_words.add(line.strip().lower())
    return stop_words


def clean_text(text, stop_words):
    # Split text into words
    words = text.split()
    # Remove stop words
    cleaned_words = [word for word in words if word.lower() not in stop_words]
    # Join words back into a single string
    cleaned_text = ' '.join(cleaned_words)
    return cleaned_text

# Load stop words
stopwords_folder = r'C:\Users\Administrator\Desktop\Prachi Projects\20211030 Test Assignment\StopWords'  # Replace with the actual path to your StopWords folder
stop_words = load_stop_words(stopwords_folder)

# Ensure the output directory exists
output_dir = "cleaned_articles"
os.makedirs(output_dir, exist_ok=True)

# Load the Excel file
df = pd.read_excel('input.xlsx')

# Iterate through each article and clean the text
for index, row in df.iterrows():
    url_id = row['URL_ID']
    try:
        # Read the article text from the saved file
        with open(f"articles/{url_id}.txt", "r", encoding='utf-8') as file:
            article_text = file.read()
        
        # Clean the article text
        cleaned_text = clean_text(article_text, stop_words)
        
        # Save the cleaned text to a new file
        with open(f"{output_dir}/{url_id}.txt", "w", encoding='utf-8') as file:
            file.write(cleaned_text)
        
        print(f"Successfully cleaned and saved article {url_id}")
    except Exception as e:
        print(f"Failed to clean and save article {url_id}: {e}")

print("Finished cleaning all articles.")

########################################################

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
import re

# Ensure NLTK resources are available
nltk.download('punkt')
# Function to count syllables in a word
def syllable_count(word):
    word = word.lower()
    count = len(re.findall(r'[aeiouy]+', word))
    if word.endswith(('es', 'ed')):
        count -= 1
    return count if count > 0 else 1

# Function to perform text analysis
def text_analysis(text):
    words = word_tokenize(text)
    sentences = sent_tokenize(text)

    positive_score = sum(1 for word in words if word.lower() in positive_words)
    negative_score = sum(1 for word in words if word.lower() in negative_words)
    polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
    subjectivity_score = (positive_score + negative_score) / (len(words) + 0.000001)
    
    avg_sentence_length = len(words) / len(sentences)
    complex_words = [word for word in words if syllable_count(word) > 2]
    percentage_complex_words = len(complex_words) / len(words)
    fog_index = 0.4 * (avg_sentence_length + percentage_complex_words)

    avg_words_per_sentence = len(words) / len(sentences)
    complex_word_count = len(complex_words)
    word_count = len(words)
    syllable_per_word = sum(syllable_count(word) for word in words) / len(words)
    personal_pronouns = len(re.findall(r'\b(I|we|my|ours|us)\b', text, re.I))
    avg_word_length = sum(len(word) for word in words) / len(words)

    return {
        'Positive Score': positive_score,
        'Negative Score': negative_score,
        'Polarity Score': polarity_score,
        'Subjectivity Score': subjectivity_score,
        'Avg Sentence Length': avg_sentence_length,
        'Percentage of Complex Words': percentage_complex_words,
        'Fog Index': fog_index,
        'Avg Number of Words Per Sentence': avg_words_per_sentence,
        'Complex Word Count': complex_word_count,
        'Word Count': word_count,
        'Syllable Per Word': syllable_per_word,
        'Personal Pronouns': personal_pronouns,
        'Avg Word Length': avg_word_length,
    }

# Load positive and negative word dictionaries
positive_words = set()
with open('MasterDictionary/positive-words.txt', 'r') as file:
    for line in file:
        positive_words.add(line.strip().lower())

negative_words = set()
with open('MasterDictionary/negative-words.txt', 'r') as file:
    for line in file:
        negative_words.add(line.strip().lower())

# Perform text analysis on cleaned articles and save results to Excel
results = []
for index, row in df.iterrows():
    url_id = row['URL_ID']
    try:
        with open(f"{output_dir}/{url_id}.txt", "r", encoding='utf-8') as file:
            cleaned_text = file.read()
        analysis = text_analysis(cleaned_text)
        result = {**row, **analysis}
        results.append(result)
        print(f"Successfully analyzed article {url_id}")
    except Exception as e:
        print(f"Failed to analyze article {url_id}: {e}")

# Save results to Excel
output_df = pd.DataFrame(results)
output_df.to_excel('Output Data Structure.xlsx', index=False)

print("Finished text analysis and saved results.")

