from transformers import pipeline
from sentence_transformers import SentenceTransformer
from flair.data import Sentence
from flair.models import SequenceTagger

# Load model pipelines
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
doc2vec = SentenceTransformer("sentence-transformers/allenai-specter")
ner_tagger = SequenceTagger.load("flair/ner-english")


def summarize_text(text):
    summary = []
    for start in range(0, len(text), 1024):
        end = start + 1024
        text_snippet = text[start:end]
        if len(text_snippet) > 200:
            summary.append(summarizer(text_snippet)[0]["summary_text"])
    return "\n".join(summary)


def NER_tag_text(text):
    sentence = Sentence(text)
    ner_tagger.predict(sentence)
    return sentence.get_spans("ner")
