import sys
import re
from html.parser import HTMLParser
from bs4 import BeautifulSoup

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.data = []

    def handle_data(self, data):
        self.data.append(data)

def checkVowels(word):
    vowels = ["a", "e", "i", "o", "u", "y"]
    check = False
    for vowel in vowels:
        if vowel in word:
            check = True
    return check

def checkShort(word):
    check = False
    if (len(word) == 2) and (checkVowels(word[0]) and not checkVowels(word[1])):
        check = True
    if (not checkVowels(word[len(word) - 1]) and (checkVowels(word[len(word) - 2])) and not (checkVowels(word[:-2])) and (word[len(word) - 1] != 'x') and (word[len(word) - 1] != 'w')):
        check = True
    return check

def tokenizer(data):
    parser = MyHTMLParser()
    parser.feed(data)
    final_ind = []
    for word in parser.data:
        while (word.startswith("http") and ((word.endswith(".") or word.endswith(",")))):    #for links
            word = word[:-1]
        if word.startswith("http"):
            final_ind.append([word])
            continue
        word = word.lower()     #lowercase
        if (word.replace(".", "").replace(",", "").replace("+", "").replace("-", "")).isnumeric():     #numbers
            final_ind.append([word])
            continue
        word = word.replace("'", "")        #apostrophe
        word = word.replace(".", "")
        if "-" in word:
            mid = word.split("-")
            mid.append(word.replace("-", ""))
            mid = tokenizer(' '.join(mid))
            final_ind.append(mid)
            continue
        word = re.split("\!|\@|\#|\$|\%|\^|\;|\:|\||\&|\*|\(|\)|\/|\"|\"|\.|\,|\_|\?|\[|\]|\{|\}", word)
        final_ind.append(word)
    for i in final_ind:
        if isinstance(i[0], list):
            temp = []
            for j in i:
                for k in j:
                    temp.append(k)
            final_ind[final_ind.index(i)] = temp
    for i in final_ind:
        for j in i:
            if j == "" or j == '':
                final_ind[final_ind.index(i)].remove(j)
    return final_ind

def textFileProcess(inputZipFile, tokenType, stopList, stopword_lst):
    information = ""
    soup = BeautifulSoup(inputZipFile, 'html.parser')
    for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        information += header.text.strip() + ' '
    try:
        information += soup.body.get_text(separator=' ').strip()
    except:
        information += soup.get_text(separator=' ').strip()
    if tokenType == "fancy":
        information = [information.split()]
        information = [
            x
            for xs in information
            for x in xs
        ]
        words = tokenizer(information)
    else:
        words = [information.split()]
    if stopList == "yesStop":
        for word in words:
            for i in word:
                if i in stopword_lst:
                    word.remove(i)
    for word in words:
        for i in word:
            if i == '' or i == "":
                word.remove(i)
    return words[0]

if __name__ == '__main__':
    argv_len = len(sys.argv)
    inputing = sys.argv[1] if argv_len >= 2 else """
    <html>
    <head>
        <title>Test HTML Document</title>
    </head>
    <body>
        <h1>Heading 1</h1>
        <p>This is a paragraph.</p>
        <h2>Heading 2</h2>
        <p>Another paragraph.</p>
    </body>
    </html>
    """
    tokenize_type = sys.argv[2] if argv_len >= 4 else "fancy"
    stoplist_type = sys.argv[3] if argv_len >= 5 else "yesStop"

    stopword_lst = ["a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
                        "has", "he", "in", "is", "it", "its", "of", "on", "that", "the", "to",
                        "was", "were", "with", "\n", "\r"]

    textFileProcess(inputing, tokenize_type, stoplist_type, stopword_lst)

stopword_lst = ["a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
                    "has", "he", "in", "is", "it", "its", "of", "on", "that", "the", "to",
                    "was", "were", "with", "\n", "\r"]