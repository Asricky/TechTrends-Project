import sqlite3
import logging
import sys

from prometheus_client import Counter, generate_latest
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)

# Initialize Metrics
db_connection_count = Counter('db_connection_count', 'Number of database connections')
post_views_total = Counter('post_views_total', 'Total views of posts')
app.config['SECRET_KEY'] = 'your secret key'

# Function to get a post from database
def get_post(post_id):
    connection = sqlite3.connect('database.db')
    db_connection_count.inc() # Increment DB connection counter
    connection.row_factory = sqlite3.Row
    post = connection.execute('SELECT * FROM posts WHERE id = (?)', (post_id,)).fetchone()
    connection.close()
    return post

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post:
        app.logger.info('Article "%s" retrieved!', post['title'])
        post_views_total.inc()
        return render_template('post.html', post=post)
    else:
        app.logger.error('Article with id "%s" does not exist! Returning 404.', post_id)
        return render_template('404.html'), 404

# Define About Us page
@app.route('/about')
def about():
    app.logger.info('The "About Us" page was retrieved.')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            db_connection_count.inc()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                            (title, content))
            connection.commit()
            connection.close()
            app.logger.info('New article "%s" created!', title)
            return redirect(url_for('index'))

    app.logger.info('The "Create new post" page was retrieved (GET request).')
    return render_template('create.html')

# Define Health Check Endpoint
@app.route('/healthz')
def healthz():
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype='application/json'
    )
    app.logger.info('Healthz endpoint was reached.')
    return response

# Define Metrics Endpoint
@app.route('/metrics')
def metrics():
    response = app.response_class(
        response=generate_latest(),
        status=200,
        mimetype='text/plain; version=0.0.4; charset=utf-8'
    )
    app.logger.info('Metrics endpoint was reached.')
    return response

# Define Logging Configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout) # Mengatur DEBUG level dan stream ke stdout

# start the application on port 3111
if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3111')
