import requests
import io
import uuid
import re
import json
import string
from tqdm import tqdm
from pdfminer.high_level import extract_text
import spacy
import os
from langdetect import detect
from googletrans import Translator
from src.model.esg_models import db, ReportHistory

# spacy.cli.download("en_core_web_sm")
# nlp = spacy.load("en_core_web_sm", disable=['ner']) # using later 

# === Load SpaCy NLP model ===
nlp = spacy.load("en_core_web_sm")


# === 1. Extract PDF text from URL ===
def extract_pdf_from_url(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, allow_redirects=True, headers=headers)
        text = extract_text(io.BytesIO(response.content))
        return text
    except Exception as e:
        print(f"❌ PDF extraction failed: {e}")
        return ""


# ====2.Detect the language for multi lingual support ====
def detect_and_translate(text):
    try:
        lang = detect(text[:1000])  # More robust sample
    except Exception as e:
        print(f"Language detection error: {e}")
        return text

    print(f"\n🌐 Detected language: {lang}")

    if lang != 'en':
        print("🔄 Translating to English...")
        try:
            translated = Translator.translate(text, src=lang, dest='en').text
            return translated
        except Exception as e:
            print(f"Translation failed: {e}")
            return text
    return text

# === 3. ESG-focused sentence extraction with enhancements ===
def extract_sentences(text):
    MIN_WORDS_PER_PAGE = 250
    esg_keywords = ["emissions", "climate", "sustainability", "carbon", "diversity",
                    "inclusion", "governance", "audit", "board", "stakeholder"]
    skip_titles = ["forward-looking", "disclaimer", "table of contents", "report overview"]

    def remove_non_ascii(t):
        printable = set(string.printable)
        return ''.join(filter(lambda x: x in printable, t))

    def is_relevant(t):
        return any(k in t.lower() for k in esg_keywords)

    def is_title(line):
        return len(line.split()) < 10 and (line.isupper() or line.strip().endswith(":"))

    pages = text.split("\f")
    sentences = []
    paragraphs = []

    for page_num, page in enumerate(pages):
        page = remove_non_ascii(page)
        if page_num < 2 and not is_relevant(page): continue
        if any(k in page.lower() for k in skip_titles): continue
        if len(page.split()) < MIN_WORDS_PER_PAGE: continue

        prev = ""
        local_paragraphs = []
        for line in page.split('\n\n'):
            if is_title(line): continue
            if line.startswith(" ") or not prev.endswith('.'):
                prev += " " + line
            else:
                local_paragraphs.append(prev.strip())
                prev = line
        local_paragraphs.append(prev.strip())

        for paragraph in local_paragraphs:
            para = re.sub(r"\d{5,}", " ", paragraph)
            para = re.sub(r"^\s?\d+(.*)$", r"\1", para)
            para = re.sub(r"\S*@\S*\s?", "", para)
            para = re.sub(r"(http|https)\:\/\/\S+", " ", para)
            para = re.sub(r"\s+", " ", para)
            para = re.sub(r"\x0c", ' ', para).strip()
            para = re.sub(r"[A-Za-z ]+ Sustainability Report \d{4}", "", para)
            para = re.sub(r"Page \d+ of \d+", "", para)
            paragraphs.append(para)

            for sent in list(nlp(para).sents):
                s = str(sent).strip()
                if 10 <= len(s.split()) <= 100 and re.match(r'^[A-Z][^?!.]*[?.!]$', s):
                    if any(k in s.lower() for k in esg_keywords):
                        sentences.append({
                            "text": s,
                            "page": page_num + 1,
                            "word_count": len(s.split()),
                            "mentions_metric": any(char.isdigit() for char in s)
                        })

    return paragraphs, sentences


def esg_download_extract_save(report_url, company_name, report_year):
    raw_text = extract_pdf_from_url(report_url)
    report_pages, report_sentences = extract_sentences(raw_text)
    new_item = ReportHistory(history_id=uuid.uuid4(),
                             company_code=company_name[:10], #"TestCode", 
                             year=report_year,
                             company_name=company_name, 
                             url=report_url, 
                             file_report_location=None, 
                             esg_content= raw_text,
                             report_pages=report_pages,
                             report_sentences=report_sentences)  # Ensure 'name' corresponds to your model
    db.session.add(new_item)
    db.session.commit()
    return "Successful"