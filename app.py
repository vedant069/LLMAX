# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from websearch import search_web
from webscrape import extract_content
from rag import add_document_to_vector_db, generate_response, read_pdf
from urllib.parse import urlparse
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Use a secure, randomly generated secret key

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.
    
    Args:
        filename (str): Name of the uploaded file.
        
    Returns:
        bool: True if allowed, False otherwise.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def home():
    """
    Home page with links to AI Search Engine and AI PDF Reader.
    """
    return render_template('home.html')

# -------- AI Search Engine Routes --------
@app.route('/search', methods=['GET', 'POST'])
def search():
    """
    AI Search Engine page with a search form.
    """
    if request.method == 'POST':
        query = request.form.get('query')
        if not query:
            flash("Please enter a search query.", "warning")
            return redirect(url_for('search'))
        return redirect(url_for('search_results', query=query))
    return render_template('search.html')

@app.route('/search/results')
def search_results():
    """
    Process the search query, perform web search, iterate through search results to scrape content,
    process through RAG pipeline, and display the response.
    """
    query = request.args.get('query')
    if not query:
        flash("No query provided.", "danger")
        return redirect(url_for('search'))
    
    # Step 1: Perform web search
    search_results = search_web(query)
    if not search_results:
        flash("No search results found or an error occurred.", "danger")
        return redirect(url_for('search'))
    
    # Step 2: Iterate through search results to find a website that can be scraped successfully
    scraped_data = None
    selected_result = None
    for result in search_results:
        url = result['url']
        scraped_data = extract_content(url)
        if scraped_data:
            selected_result = result
            break  # Exit the loop once a successful scrape is achieved
    
    if not scraped_data:
        flash("Failed to scrape all the websites in the search results.", "danger")
        return render_template('search_results.html', search_results=search_results, scraped=False)
    
    # Step 3: Add scraped data to vector DB
    document_id = selected_result['url']
    text_content = ' '.join(scraped_data.paragraphs)
    add_document_to_vector_db(document_id, text_content)
    
    # Step 4: Generate response using RAG
    conversation_history = ""  # Initialize as needed
    response = generate_response(conversation_history, query)
    
    return render_template(
        'search_results.html',
        search_results=search_results,
        scraped=True,
        selected_result=selected_result,
        response=response
    )

# -------- AI PDF Reader Routes --------
@app.route('/pdf_search', methods=['GET', 'POST'])
def pdf_search():
    """
    AI PDF Reader page with a PDF upload form.
    """
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            flash("No file part.", "danger")
            return redirect(url_for('pdf_search'))
        pdf_file = request.files['pdf_file']
        if pdf_file.filename == '':
            flash("No selected file.", "warning")
            return redirect(url_for('pdf_search'))
        if pdf_file and allowed_file(pdf_file.filename):
            filename = secure_filename(pdf_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            pdf_file.save(file_path)
            
            # Read and process the PDF
            text_content = read_pdf(file_path)
            if text_content:
                document_id = f"pdf_{filename}"
                add_document_to_vector_db(document_id, text_content)
                flash("PDF has been successfully processed and added to the search engine.", "success")
                return redirect(url_for('pdf_results', document_id=document_id))
            else:
                flash("Failed to extract text from the uploaded PDF.", "danger")
                return redirect(url_for('pdf_search'))
        else:
            flash("Invalid file type. Please upload a PDF file.", "danger")
            return redirect(url_for('pdf_search'))
    return render_template('pdf_search.html')

@app.route('/pdf_results/<document_id>', methods=['GET', 'POST'])
def pdf_results(document_id):
    """
    Display search form and results for a specific uploaded PDF.
    """
    if request.method == 'POST':
        query = request.form.get('pdf_query')
        if not query:
            flash("Please enter a search query.", "warning")
            return redirect(url_for('pdf_results', document_id=document_id))
        return redirect(url_for('pdf_search_results', document_id=document_id, query=query))
    return render_template('pdf_results.html', document_id=document_id)

@app.route('/pdf_search_results')
def pdf_search_results():
    """
    Handle search queries within a specific uploaded PDF and display AI-generated responses.
    """
    document_id = request.args.get('document_id')
    query = request.args.get('query')
    if not document_id or not query:
        flash("Invalid search parameters.", "danger")
        return redirect(url_for('pdf_search'))
    
    # Generate response using RAG based on the uploaded PDF
    conversation_history = ""  # Initialize as needed
    response = generate_response(conversation_history, query)
    
    return render_template(
        'pdf_search_results.html',
        document_id=document_id,
        query=query,
        response=response
    )

def extract_domain(url):
    """
    Extract the domain from a URL.
    
    Args:
        url (str): The URL to extract the domain from.
        
    Returns:
        str: The domain of the URL.
    """
    parsed_url = urlparse(url)
    return parsed_url.netloc

if __name__ == '__main__':
    app.run(debug=True)
