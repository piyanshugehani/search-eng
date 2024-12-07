from form import SearchForm  # Ensure the file is named correctly as 'form.py'
from flask import Flask, render_template, request, redirect, url_for, flash
import pymongo
# from scraper import scrape_data

# MongoDB connection
client = pymongo.MongoClient('mongodb+srv://piyanshu:piyanshug@cluster0.sghco.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0', serverSelectionTimeoutMS=5000)
try:
    db = client['search_engine']  # Replace 'python_search' with your database name
    print("Connection successful!")
    print(db.list_collection_names())  # Print the collection names in the database
except pymongo.errors.OperationFailure as e:
    print(f"Authentication failureeee: {e}")

# Create a text index on title, description, and links fields
db.data.create_index([('title', 'text'), ('description', 'text'), ('links', 'text')])


# Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = '0000'

@app.route('/')
def home():
    """
    Render the home page.
    """
    return render_template('home.html')

@app.route('/about')
def about():
    """
    Render the about page.
    """
    return render_template('about.html')

@app.context_processor
def base():
    """
    Provide the search form to all templates.
    """
    form = SearchForm()
    return dict(form=form)

@app.route('/results', methods=["POST"])
def results():
    """
    Handle search requests and display results.
    """
    form = SearchForm()
    if form.validate_on_submit():
        searched = request.form['searched']
        try:
            # Perform a text search in the MongoDB collection
            # Ensure the 'title' field is indexed in MongoDB for text search
            output = list(db.data.find({'$text': {'$search': searched}}))

            # Handle the case where no results are found
            if not output:
                flash("No results found for your search query.", 'info')

            # Render the results on the page
            return render_template("results.html", form=form, searched=searched, output=output)

        except Exception as e:
            print(f"Error during search: {e}")
            flash(f"An error occurred while fetching results: {str(e)}", 'error')
            return redirect(url_for('home'))

    else:
        flash("Search form validation failed.", 'warning')
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
