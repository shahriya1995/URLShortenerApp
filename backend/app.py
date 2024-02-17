import random
import string
from datetime import datetime, timedelta
from flask import Flask, request, redirect, jsonify
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('mongodb://mongodb:27017/')  # Docker DNS for MongoDB

db = client.url_shortener
urls = db.urls

def generate_short_url():
    """Function to create short url using random characters."""
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for i in range(6))
    return short_url

@app.route('/shorten', methods=['POST'])
def shorten_url():
    """POST endpont to create short urls and store in db"""
    long_url = request.json.get('url')
    short_code = generate_short_url()
    urls.insert_one({'short_code': short_code, 'long_url': long_url, 'access_count': 0, 'access_timestamps': []})
    short_url = f"http://short.url/{short_code}"  # add our own domain in 'short.url'
    return jsonify({'short_url': short_url}), 201


@app.route('/<short_code>')
def redirect_to_long_url(short_code):
    """retrieve short url and redirect to original long url"""
    url_data = urls.find_one({'short_code': short_code})
    if url_data:
        long_url = url_data['long_url']
        # Increment access count
        urls.update_one({'short_code': short_code}, {'$inc': {'access_count': 1}})
        # Log access timestamp
        access_timestamps = url_data.get('access_timestamps', [])
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        access_timestamps.append(current_time)
        urls.update_one({'short_code': short_code}, {'$set': {'access_timestamps': access_timestamps}})
        return redirect(long_url)
    else:
        return jsonify({'error': 'URL not found'}), 404


@app.route('/<short_code>/access_counts')
def get_access_counts(short_code):
    """retrieve short url and access counts from past week, all time and 24 hours"""
    url_data = urls.find_one({'short_code': short_code})
    if url_data:
        access_logs = url_data.get('access_timestamps', [])
        now = datetime.now()
        last_24_hours = now - timedelta(hours=24)
        last_week = now - timedelta(days=7)
        # Filter access logs based on time periods
        access_count_24_hours = sum(1 for log in access_logs if datetime.strptime(log, '%Y-%m-%d %H:%M:%S') > last_24_hours)
        access_count_week = sum(1 for log in access_logs if datetime.strptime(log, '%Y-%m-%d %H:%M:%S') > last_week)
        return jsonify({
            'short_code': short_code,
            'access_count_24_hours': access_count_24_hours,
            'access_count_week': access_count_week,
            'access_count_all_time': len(access_logs)
        }), 200
    else:
        return jsonify({'error': 'URL not found'}), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
