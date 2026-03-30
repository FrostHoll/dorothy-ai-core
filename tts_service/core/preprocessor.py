from num2words import num2words
from transliterate import translit
import re


class Preprocessor:
    @staticmethod
    def preprocess(text: str) -> str:
        text = Preprocessor.transliterate_english(text)
        text = Preprocessor.num_to_words(text)
        return text.strip()

    @staticmethod
    def transliterate_english(text: str) -> str:
        def replace_english(match):
            word = match.group()
            try:
                return translit(word, 'ru')
            except:
                return word

        return re.sub(r'[a-zA-Z]+', replace_english, text)

    @staticmethod
    def num_to_words(text: str) -> str:
        def replace_number(match):
            num = match.group()
            try:
                n = float(num) if '.' in num else int(num)
                return num2words(n, lang='ru')
            except:
                return num

        return re.sub(r'\d+(?:\.\d+)?', replace_number, text)