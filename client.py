import requests
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import random
nltk.download('stopwords')

def generateData(): 

    sources = ["bbc-news","usa-today", "the-washington-post", "abc-news", "cnn"]
    l = len(sources)-1
    r = random.randint(0, l)
    query_params = {
          "sources": sources[r],
          "apiKey": "25f71e1077ca4f39835807678883b777"
    }
    main_url = "https://newsapi.org/v2/everything"
    response = requests.get(main_url, params=query_params)

    data = response.json()['articles']
    res = []
    for d in data:
        res.append(d['title'])

    stopWordsSet = set(stopwords.words('english'))

    proccessedData = []
    import re
    tag = '[^a-zA-Z]'

    for x in res:
        list = word_tokenize(x)
        for y in list:
            y = re.sub(tag, '', y)
            if (y.lower() not in stopWordsSet and len(y) > 3):
                proccessedData.append(y.lower())

    sentence = " ".join(proccessedData)
    print(sentence)
    return sentence

if __name__ == "__main__":
    generateData()


