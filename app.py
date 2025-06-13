from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import nltk
import random
import re
from PyPDF2 import PdfReader

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')

from nltk import sent_tokenize, word_tokenize, pos_tag

app = Flask(__name__)
Bootstrap(app)

def generate_mcqs(text, num_questions=5):
    if not text:
        return []

    sentences = sent_tokenize(text)
    mcqs = []

    for sentence in sentences:
        words = word_tokenize(sentence)
        tagged_words = pos_tag(words)

        tokens = [word for word, pos in tagged_words if pos in ["NN", "NNS", "NNP", "NNPS", "CD"]]

    
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', sentence)
        ids = re.findall(r'\b\d{5,}\b', sentence)

        all_entities = list(set(tokens + emails + ids))

        if len(all_entities) < 4:
            continue

        subject = random.choice(all_entities)
        question_stem = sentence.replace(subject, "_____")

        distractors = list(set(all_entities) - {subject})
        options = [subject] + random.sample(distractors, min(3, len(distractors)))

        while len(options) < 4:
            options.append("RandomWord")

        random.shuffle(options)
        correct_option_letter = chr(65 + options.index(subject))  

        mcqs.append((question_stem, options, correct_option_letter))

        if len(mcqs) == num_questions:
            break

    return mcqs

def process_pdf(file):
    text = ""
    pdf_reader = PdfReader(file)
    for page_num in range(len(pdf_reader.pages)):
        page_text = pdf_reader.pages[page_num].extract_text()
        if page_text:  
            text += page_text
    return text

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = ""


        files = request.files.getlist('files[]')

       
        if files and any(file.filename != '' for file in files):
            for file in files:
                if file.filename.endswith('.pdf'):
                    text += process_pdf(file)
                elif file.filename.endswith('.txt'):
                    text += file.read().decode('utf-8')
        else:
            text = request.form.get('text', '')

        num_questions = int(request.form['num_questions'])
        mcqs = generate_mcqs(text, num_questions=num_questions)
        mcqs_with_index = [(i + 1, mcq) for i, mcq in enumerate(mcqs)]

        return render_template('mcqs.html', mcqs=mcqs_with_index)

    return render_template('index.html')

# === Main ===

if __name__ == '__main__':
    app.run(debug=True)
