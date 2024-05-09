from nltk.stem.snowball import SnowballStemmer
from bs4 import BeautifulSoup
from tqdm import tqdm
import string
from nltk.tokenize import word_tokenize
import os


class Cleaner:
    def __init__(self, stop_words_file: str, language: str,
                 perform_stop_words_removal: bool, perform_accents_removal: bool,
                 perform_stemming: bool):
        self.set_stop_words = self.read_stop_words(stop_words_file)

        self.stemmer = SnowballStemmer(language)
        in_table = "áéíóúâêôçãẽõü"
        out_table = "aeiouaeocaeou"
        # altere a linha abaixo para remoção de acentos (Atividade 11)
        self.accents_translation_table = "".maketrans(in_table, out_table)
        self.set_punctuation = set(string.punctuation)

        # flags
        self.perform_stop_words_removal = perform_stop_words_removal
        self.perform_accents_removal = perform_accents_removal
        self.perform_stemming = perform_stemming

    def html_to_plain_text(self, html_doc: str) -> str:
        soup = BeautifulSoup(html_doc, 'html.parser')
        return soup.get_text()

    @staticmethod
    def read_stop_words(str_file) -> set:
        set_stop_words = set()
        with open(str_file, encoding='utf-8') as stop_words_file:
            for line in stop_words_file:
                arr_words = line.split(",")
                [set_stop_words.add(word) for word in arr_words]
        return set_stop_words

    def is_stop_word(self, term: str):
        return term in self.set_stop_words

    def word_stem(self, term: str):
        return self.stemmer.stem(term)

    def remove_accents(self, term: str) -> str:
        return term.translate(self.accents_translation_table)

    def preprocess_word(self, term: str) -> str or None:

        if self.perform_stemming:
            term = self.word_stem(term)
        
        if self.perform_stop_words_removal:
            if self.is_stop_word(term) or term in self.set_punctuation:
                return None                
        return term

    def preprocess_text(self, text: str) -> str or None:
        return self.remove_accents(text.lower())
        
class HTMLIndexer:
    cleaner = Cleaner(stop_words_file="stopwords.txt",
                      language="portuguese",
                      perform_stop_words_removal=True,
                      perform_accents_removal=True,
                      perform_stemming=True)

    def __init__(self, index):
        self.index = index

    def text_word_count(self, plain_text: str):
        dic_word_count = {}
        plain_text = self.cleaner.preprocess_text(plain_text)
        words = word_tokenize(plain_text)
        for word in words:
            preprocessWord = self.cleaner.preprocess_word(word) 
            if preprocessWord is not None:      
                if preprocessWord in dic_word_count.keys():  
                    dic_word_count[preprocessWord] += 1
                else:
                    dic_word_count[preprocessWord] = 1    
        return dic_word_count

    def index_text(self, doc_id: int, text_html: str):
        plain_text = self.cleaner.html_to_plain_text(text_html)
        words = self.text_word_count(plain_text)
        [self.index.index(word, doc_id, words[word]) for word in words]  
        
    
    def index_text_dir(self, path: str):
        for str_sub_dir in tqdm(os.listdir(path)):
            path_sub_dir = f"{path}/{str_sub_dir}"

            for file in os.listdir(path_sub_dir):
                path_file = f"{path}/{str_sub_dir}/{file}"
                with open(path_file, encoding='utf-8') as file_content:
                    doc_id = int(file.split(".")[0])
                    self.index_text(doc_id, file_content)
                    
        self.index.finish_indexing()  