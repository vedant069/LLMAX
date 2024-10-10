# websearch.py
import requests

def search_web(query, base_url="http://localhost:4000/search", top_n=3):
    """
    Perform a web search using SearxNG API and return top N results.
    
    Args:
        query (str): The search query.
        base_url (str): The SearxNG API endpoint.
        top_n (int): Number of top results to return.
        
    Returns:
        list: A list of dictionaries containing 'title', 'url', and 'snippet'.
    """
    params = {
        "q": query,
        "format": "json"
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for result in data.get("results", [])[:top_n]:
            results.append({
                "title": result['title'],
                "url": result['url'],
                "snippet": result.get('content', 'No snippet available')
            })
        return results
    except requests.exceptions.RequestException as e:
        print(f"Error during web search: {e}")
        return []
