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

def porterStemmerA(words: list[list[str]]):
    for section in words:
        i = section
        if not section == []:
            for word in section:
                j = word
                if word.endswith("sses"):
                    word = word[:-4] + "ss"     #SS stemming
                    section[section.index(j)] = word
                    continue
                if len(word) > 4 and word.endswith("ied"):
                    word = word[:-3] + "i"     #ied stemming
                    section[section.index(j)] = word
                    continue
                elif len(word) > 4 and word.endswith("ies"):
                    word = word[:-3] + "i"    
                    section[section.index(j)] = word
                    continue
                elif len(word) <= 4 and word.endswith("ied"):
                    word = word[:-3] + "ie"  
                    section[section.index(j)] = word 
                    continue
                elif len(word) <= 4 and word.endswith("ies"):
                    word = word[:-3] + "ie"   
                    section[section.index(j)] = word
                    continue
                if word.endswith("ss") or word.endswith("us"):
                    section[section.index(j)] = word
                    continue
                if word.endswith("s") and (checkVowels(word[:-2])):
                    word = word[:-1]
                section[section.index(j)] = word
        words[words.index(i)] = section
    return words

def porterStemmerB(words: list[list[str]]):
    for section in words:
        i = section
        if not section == []:
            for word in section:
                j = word
                if j == "":
                    section.remove(j)
                    continue
                if word.endswith("eed"):
                    tracker = word[:-3]
                    if checkVowels(tracker[:-1]) and not checkVowels(tracker[len(tracker) - 1]):
                        word = word[:-3] + "ee"
                elif word.endswith("eedly"):
                    tracker = word[:-5]
                    if (checkVowels(tracker[:-1]) and not checkVowels(tracker[len(tracker) - 1])):
                        word = word[:-5] + "ee"
                if word.endswith("ed") or word.endswith("edly") or word.endswith("ing") or word.endswith("ingly"):
                    if word.endswith("ed") and checkVowels(word[:-2]):
                            word = word[:-2]
                    elif word.endswith("edly") and checkVowels(word[:-4]):
                            word = word[:-4]
                    elif word.endswith("ing") and checkVowels(word[:-3]):
                            word = word[:-3]
                    elif word.endswith("ingly") and checkVowels(word[:-5]):
                            word = word[:-5]
                    if word.endswith("at") or word.endswith("bl") or word.endswith("iz"):
                            word = word + "e"
                    elif word.endswith("bb") or word.endswith("dd") or word.endswith("ff") or word.endswith("gg") or word.endswith("mm") or word.endswith("nn") or word.endswith("pp") or word.endswith("rr") or word.endswith("tt"):
                        word = word[:-1]
                    elif checkShort(word):
                        word = word + "e"
                section[section.index(j)] = word
        words[words.index(i)] = section
    return words

def porterStemmerC(words: list[list[str]]):
    for section in words:
        i = section
        if not section == []:
            for word in section:
                j = word
                if len(word) > 2 and word.endswith("y") and not checkVowels(word[len(word) - 2]):
                    word = word[:-1] + "i"
                section[section.index(j)] = word
        words[words.index(i)] = section

    return words   

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

def textFileProcess(inputZipFile, tokenType, stopList, stemming, stopword_lst):
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
    if stemming == "porterStem":
        words = porterStemmerA(words)
        words = porterStemmerB(words)
        words = porterStemmerC(words)
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
    stemming_type = sys.argv[4] if argv_len >= 6 else "porterStem"

    stopword_lst = ["a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
                        "has", "he", "in", "is", "it", "its", "of", "on", "that", "the", "to",
                        "was", "were", "with", "\n", "\r"]

    textFileProcess(inputing, tokenize_type, stoplist_type, stemming_type, stopword_lst)

stopword_lst = ["a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
                    "has", "he", "in", "is", "it", "its", "of", "on", "that", "the", "to",
                    "was", "were", "with", "\n", "\r"]