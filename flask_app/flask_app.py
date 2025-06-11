from flask import Flask, render_template, request, jsonify
import requests
import asyncio
import aiohttp
import os

app = Flask(__name__)

# Configuration
TORNADO_BASE_URL = os.getenv("TORNADO_BASE_URL", "http://localhost:8888")

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/call-tornado', methods=['POST'])
def call_tornado():
    """Make a request to the Tornado app and return the response"""
    try:
        # Get the endpoint from the form (default to root)
        endpoint = request.form.get('endpoint', '/')
        
        # Ensure endpoint starts with /
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        
        # Make request to Tornado app
        tornado_url = f"{TORNADO_BASE_URL}{endpoint}"
        response = requests.get(tornado_url, timeout=30)
        
        return jsonify({
            'success': True,
            'status_code': response.status_code,
            'response_text': response.text,
            'url_called': tornado_url
        })
        
    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': False,
            'error': 'Could not connect to Tornado app. Make sure it\'s running on port 8888.'
        }), 503
        
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'Request to Tornado app timed out.'
        }), 504
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/call-tornado-async', methods=['POST'])
async def call_tornado_async():
    """Async version of the Tornado call using aiohttp"""
    try:
        endpoint = request.form.get('endpoint', '/')
        
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        
        tornado_url = f"{TORNADO_BASE_URL}{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(tornado_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                response_text = await response.text()
                
                return jsonify({
                    'success': True,
                    'status_code': response.status,
                    'response_text': response_text,
                    'url_called': tornado_url
                })
                
    except aiohttp.ClientConnectorError:
        return jsonify({
            'success': False,
            'error': 'Could not connect to Tornado app. Make sure it\'s running on port 8888.'
        }), 503
        
    except asyncio.TimeoutError:
        return jsonify({
            'success': False,
            'error': 'Request to Tornado app timed out.'
        }), 504
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Flask Tornado Proxy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)