import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Disables SSL certificate verification warnings in the logs
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Dynamic routing configuration for Render paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(BASE_DIR, 'index.html')

@app.route('/')
def home():
    try:
        with open(HTML_PATH, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"<h3>Frontend Layout Error: index.html missing! Error details: {str(e)}</h3>", 404

# THE INTENTIONAL VULNERABILITY SIMULATOR TARGET
@app.route('/vulnerable-demo')
def vulnerable_demo():
    user_query = request.args.get('search', '')
    return f"<html><body><h1>Search Results</h1><p>You searched for: {user_query}</p></body></html>"

# UNRESTRICTED DAST SCANNING LOOP ENGINE
def scan_xss(url):
    url = url.strip()
    
    if " " in url or "," in url:
        return {
            "status": "⚠️ INVALID TARGET", 
            "flaw": "The target string pattern contains invalid formatting characters or spaces.", 
            "legal_exposure": "N/A"
        }
        
    if url.startswith("https://"):
        url = url.replace("https://", "")
    if url.startswith("http://"):
        url = url.replace("http://", "")
    if url.startswith("www."):
        url = url.replace("www.", "")
        
    clean_url = f"http://{url}"
    xss_payload = "<script>alert('Vulnerable')</script>"
    target_url = f"{clean_url}?search={xss_payload}"
    
    try:
        # Render has an open network layer, allowing requests to hit the actual internet!
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(target_url, timeout=6, verify=False, allow_redirects=True, headers=headers)
        
        if response.status_code >= 400:
            return {
                "status": "⚠️ INVALID TARGET", 
                "flaw": f"Target unreachable or actively dropped request connection. HTTP Status Code: {response.status_code}.", 
                "legal_exposure": "N/A"
            }
            
        if xss_payload in response.text:
            return {
                "status": "🔴 VULNERABLE",
                "flaw": "Cross-Site Scripting (XSS) - Input parameters reflected unescaped inside text nodes.",
                "legal_exposure": "Triggers statutory penalty guidelines under Section 43 & 66 of the Indian IT Act."
            }
        else:
            return {
                "status": "🟢 SECURE",
                "flaw": "No direct XSS execution vector found in the initial page text signature layers.",
                "legal_exposure": "Compliant with standard secure application design guidelines."
            }
            
    except Exception as e:
        return {
            "status": "⚠️ INVALID TARGET", 
            "flaw": "The website address is dead, completely offline, or blocking automated script traffic entirely.", 
            "legal_exposure": "N/A"
        }

@app.route('/api/scan', methods=['POST'])
def handle_scan():
    data = request.get_json()
    target_url = data.get('url')
    result = scan_xss(target_url)
    return jsonify(result)

if __name__ == '__main__':
    # Tells Render to bind its external public environment ports automatically
    app.run(host='0.0.0.0', port=10000)
