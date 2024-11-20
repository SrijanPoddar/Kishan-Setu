import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,  -- Rate in Rs/kg
            quantity INTEGER NOT NULL,  -- Quantity in kg
            farmer_id INTEGER NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consumer_name TEXT NOT NULL,
            item_name TEXT NOT NULL,
            quantity REAL NOT NULL,  -- Quantity in kg
            farmer_id INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

import google.generativeai as genai

gem_api = os.getenv('gem_api')
genai.configure(api_key=gem_api)


model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
  system_instruction="""you are an chatbot helper for an organic
    farming website we connect organic farmer to the buyers  if relevant questio
  n is asked reply accordingly else ask to ask a relevent questions reply in hindi""",
)

chat_session = model.start_chat(
  history=[
  ]
)
# Allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return redirect(url_for('register'))

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, role))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            if user[3] == 'farmer':
                return redirect(url_for('farmer_dashboard'))
            elif user[3] == 'consumer':
                return redirect(url_for('consumer_dashboard'))
    return render_template('login.html')

# Farmer Dashboard Route
@app.route('/farmer_dashboard', methods=['GET', 'POST'])
def farmer_dashboard():
    if 'role' in session and session['role'] == 'farmer':
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # Fetch consumer requests for the farmer
        c.execute('SELECT * FROM requests WHERE farmer_id = ?', (session['user_id'],))
        requests = c.fetchall()

        # Add items for sale
        if request.method == 'POST':
            name = request.form['name']
            price = float(request.form['price'])  # Rate in Rs/kg
            quantity = int(request.form['quantity'])  # Quantity in kg

            # Insert item into the database
            c.execute('INSERT INTO items (name, price, quantity, farmer_id) VALUES (?, ?, ?, ?)', 
                      (name, price, quantity, session['user_id']))
            conn.commit()
            # Success message (can be implemented in front-end as a pop-up)
            success_message = "Item added successfully!"
            conn.close()
            return render_template('farmer_dashboard.html', username=session['username'], requests=requests, success_message=success_message)

        conn.close()
        return render_template('farmer_dashboard.html', username=session['username'], requests=requests)

    return redirect(url_for('login'))

# Consumer Dashboard Route
@app.route('/consumer_dashboard', methods=['GET', 'POST'])
def consumer_dashboard():
    if 'role' in session and session['role'] == 'consumer':
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # Fetch available items
        c.execute('SELECT * FROM items')
        items = c.fetchall()

        # Handle consumer's request to a farmer
        if request.method == 'POST':
            quantity = float(request.form['quantity'])
            item_name = request.form['item_name']
            farmer_id = int(request.form['farmer_id'])
            consumer_name = session['username']

            # Insert the request into the database
            c.execute('INSERT INTO requests (consumer_name, item_name, quantity, farmer_id) VALUES (?, ?, ?, ?)', 
                      (consumer_name, item_name, quantity, farmer_id))
            conn.commit()
            conn.close()
            # Success message
            success_message = "Your request has been sent successfully!"
            return render_template('consumer_dashboard.html', items=items, success_message=success_message)

        conn.close()
        return render_template('consumer_dashboard.html', items=items)

    return redirect(url_for('login'))

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    response = chat_session.send_message(user_message)
    response = str(response.candidates[0].content.parts[0].text)
    print(response)
    return jsonify({'message': response})

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Initialize Database
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
