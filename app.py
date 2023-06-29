from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from nltk.tokenize import RegexpTokenizer, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import os
import nltk

nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SecureSecretKey'

def txt6312_clean_files_Method():
    files = [i for i in os.listdir('static') if i.endswith('.txt')]

    ps = PorterStemmer()
    tokenizer = RegexpTokenizer(r'\w+')
    stop_words = set(stopwords.words('english'))

    output_dir = os.path.join('static', 'clean_files')
    os.makedirs(output_dir, exist_ok=True)  # Create the output directory if it doesn't exist

    for file_name in files:
        input_path = os.path.join('static', file_name)
        output_path = os.path.join(output_dir, file_name)

        with open(input_path, 'r', encoding='utf8') as input_file:
            text = input_file.read()
            text = text.encode("ascii", "ignore").decode()  # Remove non-ASCII characters
            text = text.lower()  # Convert to lowercase
            tokens = tokenizer.tokenize(text)
            filtered_words = [w for w in tokens if w.lower() not in stop_words]
            stemmed_words = [ps.stem(w) for w in filtered_words]
            cleaned_text = " ".join(stemmed_words)

        with open(output_path, 'w', encoding='utf8') as output_file:
            output_file.write(cleaned_text)

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        if search_query:
            search_results = search_documents(search_query)
        else:
            search_results = []
        return render_template('txt6312_index.html', search_results=search_results)

    return render_template('txt6312_index.html')

class SearchForm(FlaskForm):
    search_query = StringField('Search Query', validators=[DataRequired()])
    file_name = StringField('File Name', validators=[DataRequired()])  # Add the file_name field
    submit = SubmitField('Search')

@app.route('/search', methods=['GET', 'POST'])
def txt6312_search_from_file():
    form = SearchForm()
    
    # Get the list of available files in the static directory
    available_files = [file for file in os.listdir('static') if file.endswith('.txt')]

    if form.validate_on_submit():
        try:
            search_word = form.search_query.data
            file_name = form.file_name.data  # Get the entered file name

            # Check if the entered file exists
            if not os.path.exists(f'static/{file_name}'):
                error = f"File '{file_name}' does not exist."
                return render_template('txt6312_search_word_from_file.html', form=form, error=error, available_files=available_files)

            search_results = []
            count = 0  # Initialize the count

            path = f'static/{file_name}'
            with open(path, encoding='utf8') as file:
                lines = file.readlines()
                for line_num, line in enumerate(lines, start=1):
                    if search_word.lower() in line.lower():
                        search_results.append((line.strip(), line.lower().count(search_word.lower())))
                        count += line.lower().count(search_word.lower())  # Update the count

            if not search_results:
                message = f"Keyword '{search_word}' not found in the file."
                return render_template('txt6312_search_word_from_file.html', message=message, form=form, available_files=available_files)

            return render_template('txt6312_search_word_from_file.html', search_results=search_results, count=count, form=form, available_files=available_files)

        except Exception as e:
            print(e)
            return render_template('txt6312_search_word_from_file.html', form=form, error=e, available_files=available_files)

    return render_template('txt6312_search_word_from_file.html', form=form, available_files=available_files)


def search_documents(query):
    cleaned_files_dir = os.path.join('static', 'clean_files')
    search_results = []

    for file_name in os.listdir(cleaned_files_dir):
        file_path = os.path.join(cleaned_files_dir, file_name)
        with open(file_path, 'r', encoding='utf8') as file:
            lines = file.readlines()
            for line_num, line in enumerate(lines, start=1):
                if query.lower() in line:
                    result = {
                        'file_name': file_name,
                        'line_num': line_num,
                        'line': line.strip()
                    }
                    search_results.append(result)

    return search_results


if __name__ == "__main__":
    txt6312_clean_files_Method()
    app.run(debug=True, port=8080)
