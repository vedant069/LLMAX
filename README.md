# LLMAX
# AI Search Engine and PDF Reader

A full-text search engine with the ability to read and upload PDF documents.

## Overview

This is a simple Flask web application that provides two main functionalities:

*   **Full-Text Search Engine**: Users can enter their search queries, and the application will return relevant results from the indexed documents.
*   **PDF Reader**: Users can upload their PDF documents, and the application will render them for reading.

## Features

### Full-Text Search Engine

*   Supports keyword searches
*   Can be used with multiple documents
*   Indexing is done using a simple text search algorithm

### PDF Reader

*   Allows users to upload PDF files
*   Renders uploaded PDFs using a basic viewer
*   Supports reading and searching within PDF contents

## Technologies Used

*   Flask (Web Framework)
*   RAG (Relevance-based Algorithm for Google's Knowledge Graph) for relevance-based search results
*   PDFmining for PDF rendering

## Installation

1.  Clone the repository using `git clone https://github.com/vedant069/LLMAX`
2.  Install required packages by running `pip install -r requirements.txt`
3.  Set up a database (optional)

## Usage

### Search Functionality

1.  Enter your search query in the input field.
2.  Click the "Search" button to get relevant results.

### Upload PDF Functionality

1.  Click the "Upload PDF" button.
2.  Select a PDF file from your device.
3.  The uploaded PDF will be rendered for reading.
