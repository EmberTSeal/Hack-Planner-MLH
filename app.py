# import functionality into our project so we don't have to write it   
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

items = []

# CRUD Operations

# add functionality
@app.route('/add', methods = ['POST'])

def add_item():
    item = request.form['item']
    items.append(item)  # Append the new item to the list
    # not using database 
    return redirect('/')


# read functionality
# not specifying method bcz default method is GET (for reading)
@app.route('/')

def checklist():
    return render_template('checklist.html', items= items)

@app.route('/edit/<int:item_id>', methods = ['GET', 'POST'])

def edit_item(item_id):
    item = items[item_id-1] # retrieve item based on index

    if request.method == 'POST':
        new_item = request.form['item']
        items[item_id-1] = new_item
        return redirect('/')
    
    return render_template('edit.html', item = item , item_id = item_id)

@app.route('/delete/<int:item_id>')

def delete_item(item_id):
    del items[item_id-1]
    return redirect('/')

