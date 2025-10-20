"""
Flask Web Application for eCourts Scraper
"""
from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scraper import eCourtsScraper
from src.utils import get_today_date, get_tomorrow_date
import config

app = Flask(__name__)

# Store active scraper instance
scraper = None

def get_scraper():
    global scraper
    if scraper is None:
        scraper = eCourtsScraper(headless=True)
    return scraper

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_cnr', methods=['POST'])
def search_cnr():
    try:
        data = request.json
        cnr = data.get('cnr')

        if not cnr:
            return jsonify({'error': 'CNR number is required'}), 400

        s = get_scraper()
        result = s.search_by_cnr(cnr)

        if result:
            return jsonify({'success': True, 'data': result})
        else:
            return jsonify({'error': 'Case not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/check_listing', methods=['POST'])
def check_listing():
    try:
        data = request.json
        cnr = data.get('cnr')
        check_type = data.get('type', 'today')  # 'today' or 'tomorrow'

        if not cnr:
            return jsonify({'error': 'CNR number is required'}), 400

        s = get_scraper()

        if check_type == 'today':
            result = s.check_case_today(cnr)
        else:
            result = s.check_case_tomorrow(cnr)

        if result:
            return jsonify({'success': True, 'data': result})
        else:
            return jsonify({'error': 'Could not check listing'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_causelist', methods=['POST'])
def download_causelist():
    try:
        data = request.json
        state = data.get('state')
        district = data.get('district')
        court_complex = data.get('court_complex')
        court_name = data.get('court_name')
        date = data.get('date') or get_today_date()
        list_type = data.get('list_type', 'Civil')

        if not all([state, district, court_complex]):
            return jsonify({'error': 'State, district, and court complex are required'}), 400

        s = get_scraper()
        result = s.download_cause_list(
            state=state,
            district=district,
            court_complex=court_complex,
            court_name=court_name,
            date=date,
            list_type=list_type
        )

        if result:
            return jsonify({
                'success': True, 
                'message': 'Cause list downloaded successfully',
                'file': result
            })
        else:
            return jsonify({'error': 'Failed to download cause list'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_states')
def get_states():
    # Return list of Indian states
    states = [
        "Andaman and Nicobar", "Andhra Pradesh", "Arunachal Pradesh", "Assam", 
        "Bihar", "Chandigarh", "Chhattisgarh", "Delhi", "Goa", "Gujarat", 
        "Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Jharkhand", 
        "Karnataka", "Kerala", "Ladakh", "Lakshadweep", "Madhya Pradesh", 
        "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", 
        "Odisha", "Puducherry", "Punjab", "Rajasthan", "Sikkim", 
        "Tamil Nadu", "Telangana", "Tripura", "Uttarakhand", "Uttar Pradesh", 
        "West Bengal"
    ]
    return jsonify(states)

@app.teardown_appcontext
def cleanup(error=None):
    global scraper
    if scraper:
        scraper.close()
        scraper = None

if __name__ == '__main__':
    print("Starting eCourts Scraper Web Interface...")
    print("Open your browser and navigate to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
