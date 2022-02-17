from transformers import pipeline
from sentence_transformers import SentenceTransformer
from flair.data import Sentence
from flair.models import SequenceTagger
import numpy as np
import fasttext
from veritas import config

models_dir = config["models_dir"]

# Load model pipelines
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
doc2vec = SentenceTransformer("sentence-transformers/allenai-specter")
ner_tagger = SequenceTagger.load("flair/ner-english")
pos_tagger = SequenceTagger.load("flair/pos-english")

language_detector = fasttext.load_model(str(models_dir / "lid.176.bin"))


def language_detect(text: str):
    lang, prob = language_detector.predict(text.replace("\n", ""))
    return lang[0].replace("__label__", "")


def embed(text: str) -> np.array:
    return doc2vec.encode(text)


def summarize(text: str) -> str:
    summary = []
    for start in range(0, len(text), 1024):
        end = start + 1024
        text_snippet = text[start:end]
        if len(text_snippet) > 200:
            summary.append(summarizer(text_snippet)[0]["summary_text"])
    return "\n".join(summary)


def NER(text: str):
    sentence = Sentence(text)
    ner_tagger.predict(sentence)
    return sentence.get_spans("ner")


def POS(text: str):
    sentence = Sentence(text)
    pos_tagger.predict(sentence)
    return sentence.get_spans("pos")
