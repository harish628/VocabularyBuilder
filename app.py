from flask import Flask, render_template, request, jsonify, send_file
import os
from datetime import datetime

app = Flask(__name__)

# File to store vocabulary
VOCAB_FILE = "vocabulary_document.txt"

def init_vocabulary_file():
    """Initialize vocabulary file with header if it doesn't exist"""
    if not os.path.exists(VOCAB_FILE):
        with open(VOCAB_FILE, 'w', encoding='utf-8') as f:
            f.write("╔" + "═" * 78 + "╗\n")
            f.write("║" + " " * 20 + "VOCABULARY DOCUMENT" + " " * 39 + "║\n")
            f.write("╚" + "═" * 78 + "╝\n")
            f.write("Created on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")

def read_vocabulary():
    """Read existing vocabulary from file"""
    try:
        if not os.path.exists(VOCAB_FILE):
            return ""
        
        with open(VOCAB_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            return content if content.strip() else ""
    except Exception as e:
        return f"Error reading file: {str(e)}"

def save_vocabulary(word, english_meaning, telugu_meaning, examples):
    """Save new vocabulary entry to file"""
    try:
        # Clean up all inputs - remove leading/trailing whitespace
        word = word.strip()
        english_meaning = english_meaning.strip()
        telugu_meaning = telugu_meaning.strip()
        
        # Format examples - each on a new line with numbers and consistent indentation
        example_lines = [ex.strip() for ex in examples.split('\n') if ex.strip()]
        formatted_examples = ""
        for i, ex in enumerate(example_lines, 1):
            formatted_examples += f"           {i}. {ex}\n\n"
        
        # Format the entry
        entry = f"""
================================================================================
{word.upper()}
----------------------------------------
       Meaning (English): 
           {english_meaning}
       
       Meaning (Telugu): 
           {telugu_meaning}
       
       Examples:
{formatted_examples}================================================================================
"""
        
        # Read existing content
        existing_content = read_vocabulary()
        
        # Append new entry
        new_content = existing_content + entry + "\n"
        
        # Save to file
        with open(VOCAB_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
        
    except Exception as e:
        raise Exception(f"Error saving vocabulary: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_word', methods=['POST'])
def add_word():
    try:
        word = request.form.get('word', '').strip()
        english_meaning = request.form.get('english_meaning', '').strip()
        telugu_meaning = request.form.get('telugu_meaning', '').strip()
        examples = request.form.get('examples', '').strip()
        
        if not word:
            return jsonify({'success': False, 'message': 'Word is required!'})
        if not english_meaning:
            return jsonify({'success': False, 'message': 'English meaning is required!'})
        if not telugu_meaning:
            return jsonify({'success': False, 'message': 'Telugu meaning is required!'})
        if not examples:
            return jsonify({'success': False, 'message': 'Examples are required!'})
        
        # Save to file
        save_vocabulary(word, english_meaning, telugu_meaning, examples)
        
        return jsonify({
            'success': True, 
            'message': f'✓ "{word}" has been added successfully!',
            'word': word
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/view_document')
def view_document():
    """Return the entire vocabulary document"""
    content = read_vocabulary()
    return jsonify({'content': content})

@app.route('/download_document')
def download_document():
    """Download the vocabulary document"""
    if not os.path.exists(VOCAB_FILE):
        init_vocabulary_file()
    
    return send_file(
        VOCAB_FILE,
        as_attachment=True,
        download_name=f"vocabulary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mimetype='text/plain'
    )

@app.route('/clear_document', methods=['POST'])
def clear_document():
    """Clear all vocabulary entries (keep header)"""
    try:
        # Reinitialize with just header
        init_vocabulary_file()
        
        return jsonify({
            'success': True, 
            'message': '✓ Document cleared successfully!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    # Initialize vocabulary file
    init_vocabulary_file()
    
    # Run app
    app.run(debug=False, port=5000, host='0.0.0.0')