import os
from flask import Flask, render_template, request, redirect, url_for, send_file
from model import extract_text_and_translate
from pymongo import MongoClient

app = Flask(__name__)

mongo_connection_string = "LINK_OF_MONGODB"
client = MongoClient(mongo_connection_string)
db = client["translated_pdfs"]
collection = db["file_names"] 

def upload_file(file):
    if file:
        file_path = os.path.join("raw_files", file.filename)
        file.save(file_path)
        return file_path
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        file_path = upload_file(uploaded_file)
        file_name = uploaded_file.filename
        if file_path:
            collection.insert_one({"filename": file_name})
            result = extract_text_and_translate(file_path, file_name)
            if result == 'success':
                return redirect(url_for('success'))
            else:
                return "Error processing file"
        else:
            return "Error uploading file"
    return redirect(url_for('index'))

@app.route('/success')
def success():
    return "File uploaded successfully and processed."

@app.route('/library')
def library():
    files = collection.find()
    return render_template('library.html', files=files)

@app.route('/download/<filename>')
def download(filename):
    return send_file(f"output_files\{filename}", as_attachment=True)

@app.route('/view/<filename>')
def view(filename):
    return send_file(f"output_files\{filename}", as_attachment=False)

if __name__ == '__main__':
    app.run(debug=True)
