import re
from functools import lru_cache

from nltk.stem.snowball import SnowballStemmer

PORTUGUESE_STOPWORDS = {
    "a",
    "à",
    "ao",
    "aos",
    "aquela",
    "aquele",
    "aqueles",
    "as",
    "até",
    "com",
    "como",
    "da",
    "das",
    "de",
    "dela",
    "dele",
    "deles",
    "depois",
    "do",
    "dos",
    "e",
    "é",
    "ela",
    "elas",
    "ele",
    "eles",
    "em",
    "entre",
    "era",
    "essa",
    "esse",
    "esta",
    "este",
    "eu",
    "foi",
    "foram",
    "há",
    "isso",
    "isto",
    "já",
    "la",
    "lhe",
    "mais",
    "mas",
    "me",
    "mesmo",
    "meu",
    "minha",
    "muito",
    "na",
    "não",
    "nas",
    "nem",
    "no",
    "nos",
    "nós",
    "o",
    "os",
    "ou",
    "para",
    "pela",
    "pelas",
    "pelo",
    "pelos",
    "por",
    "qual",
    "quando",
    "que",
    "quem",
    "se",
    "sem",
    "ser",
    "seu",
    "sua",
    "suas",
    "também",
    "te",
    "tem",
    "tenho",
    "ter",
    "um",
    "uma",
    "você",
    "vocês",
    "vos",
}


@lru_cache
def get_stemmer() -> SnowballStemmer:
    return SnowballStemmer("portuguese")


def normalize_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def preprocess_text(text: str) -> str:
    stemmer = get_stemmer()
    text = normalize_text(text).lower()
    text = re.sub(r"[^\w\s@?.!-]", " ", text, flags=re.UNICODE)
    tokens = [
        token
        for token in text.split()
        if token not in PORTUGUESE_STOPWORDS and len(token) > 1
    ]
    stems = [stemmer.stem(token) for token in tokens]
    return " ".join(stems)
