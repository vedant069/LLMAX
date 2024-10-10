# rag.py
import ollama
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import PyPDF2  # Import PyPDF2 for PDF reading

# Initialize clients and models
client = ollama.Client()
embeddingModel = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
chromaClient = chromadb.Client()

def get_or_create_collection(name="ragDocuments"):
    """
    Retrieve an existing ChromaDB collection or create a new one if it doesn't exist.
    
    Args:
        name (str): Name of the collection.
        
    Returns:
        chromadb.Collection: The ChromaDB collection.
    """
    existing_collections = chromaClient.list_collections()
    for col in existing_collections:
        if col.name == name:
            return chromaClient.get_collection(name=name)
    return chromaClient.create_collection(
        name=name, 
        embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction()
    )

def chunk_text(text, chunk_size=300):
    """
    Divide text into chunks of specified word count.
    
    Args:
        text (str): The text to chunk.
        chunk_size (int): Number of words per chunk.
        
    Returns:
        list: A list of text chunks.
    """
    words = text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

def read_pdf(file_path):
    """
    Extract text from a PDF file.
    
    Args:
        file_path (str): Path to the PDF file.
        
    Returns:
        str: Extracted text from the PDF.
    """
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

# Initialize the collection
collection = get_or_create_collection()

def add_document_to_vector_db(doc_id, text):
    """
    Add document text to the vector database after chunking and embedding.
    
    Args:
        doc_id (str): Unique identifier for the document.
        text (str): The text content of the document.
    """
    chunks = chunk_text(text)
    embeddings = embeddingModel.encode(chunks)
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        collection.add(
            documents=[chunk],
            embeddings=[embedding.tolist()],
            ids=[f"{doc_id}_chunk{i}"]
        )
    print(f"Document '{doc_id}' has been added to the vector database with {len(chunks)} chunks.")

def retrieve_relevant_chunks(query, top_k=3):
    """
    Retrieve the top K relevant chunks from the vector database based on the query.
    
    Args:
        query (str): The user's search query.
        top_k (int): Number of top similar chunks to retrieve.
        
    Returns:
        list: A list of relevant text chunks.
    """
    query_embedding = embeddingModel.encode([query])[0]
    records = collection.get(include=["embeddings", "documents"])
    if len(records["embeddings"]) == 0 or len(records["documents"]) == 0:
        print("No documents are present in the vector database. Please add a document first.")
        return []
    embeddings = np.array(records["embeddings"])
    similarities = cosine_similarity([query_embedding], embeddings)[0]
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    top_chunks = [records["documents"][idx] for idx in top_indices]
    return top_chunks

def generate_response(conversation_history, question):
    """
    Generate a response based on the conversation history and question using RAG.
    
    Args:
        conversation_history (str): The history of the conversation.
        question (str): The user's current question.
        
    Returns:
        str: The generated response.
    """
    relevant_chunks = retrieve_relevant_chunks(question)
    combined_text = ' '.join(relevant_chunks)
    if not combined_text:
        return "No relevant information found in the document."

    prompt = f"HISTORY: \n{conversation_history}\n\nContext:\n{combined_text}\n\nQuestion: {question}"
    response = client.generate(
        model="llama3.2:3b", 
        prompt=prompt
    )['response']

    print(f"Generated response: {response}")  # Debugging statement
    return response
