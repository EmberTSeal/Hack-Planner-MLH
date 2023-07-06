# import functionality into our project so we don't have to write it   
from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import os
import sendgrid
from sendgrid.helpers.mail import Mail

sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
reminder_email = os.getenv('REMINDER_EMAIL')


app = Flask(__name__)

items = []

# database
db_path = 'checklist.db'

def create_table():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS checklist 
              (id INTEGER PRIMARY KEY AUTOINCREMENT, item TEXT )''')
    conn.commit()
    conn.close()

def add_item(item):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT INTO checklist(item) VALUES(?)", (item,))
    conn.commit()
    conn.close()

def get_items():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM checklist")
    items = c.fetchall()
    conn.close()
    return items 

def update_item(item_id, new_item):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("UPDATE checklist SET item = ? WHERE id = ?", (new_item, item_id))
    conn.commit()
    conn.close()

def delete_item(item_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DELETE FROM checklist WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    
# CRUD Operations

# add functionality
@app.route('/add', methods = ['POST'])

def add():
    item = request.form['item']
    add_item(item)  
    return redirect('/')

# read
# not specifying method bcz default method is GET (for reading)
@app.route('/')

def checklist():
    create_table()
    items = get_items()
    return render_template('checklist.html', items= items)

# edit
@app.route('/edit/<int:item_id>', methods = ['GET', 'POST'])

def edit(item_id):
    if request.method == 'POST':
        new_item = request.form['item']
        update_item(item_id, new_item)
        return redirect('/')
    else:
        items = get_items()
        item = next((x[1] for x in items if x[0] == item_id), None)
        return render_template('edit.html', item = item , item_id = item_id)

@app.route('/delete/<int:item_id>')

def delete(item_id):
    delete_item(item_id)
    return redirect('/')

def send_email(subject, body):
     message = Mail(
        from_email = reminder_email,
        to_emails = 'trisha.seal.22@aot.edu.in',
        subject = subject,
        plain_text_content = body
     )
     try: 
         sg = sendgrid.SendGridAPIClient(api_key= sendgrid_api_key)
         response = sg.send(message)
         if response.status_code == 202:
            return True
     except Exception as e:
         print("An error occured while sending email :", str(e))
     return False

@app.route('/send_email', methods = ['POST'])
def send_email_route():
    data = request.get_json()
    item = data['item']
    subject = "Reminder: {}".format(item)
    body = "This is a reminder for the task: {}".format(item)
    if send_email(subject, body):
        return jsonify(success = True)
    else:
        return jsonify(success = False), 500
    