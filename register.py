import pymysql
from flask import Blueprint, render_template, request, redirect, url_for, flash

# Create a Blueprint for the registration functionality
register_bp = Blueprint('register', __name__)

app = Flask(__name__)
app.secret_key = 'Ajmal@dec12'  # Replace with your own secret key

# Database configuration
db_config = {
    'host': 'sql.freedb.tech',
    'user': 'freedb_Ajmal',
    'password': 'f8PbPDFWub$&4@$',
    'database': 'freedb_Levels'
}

# Route to display the registration form
@app.route("/pages-register.html")
def register():
    return render_template("pages-register.html")

# Route to handle form submission
@app.route('/pages-register.html', methods=['POST'])
def register_user():
    name = request.form['name']
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']

    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        sql = "INSERT INTO users (name, email, username, password) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (name, email, username, password))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Account created successfully!', 'success')
        return redirect(url_for('register'))
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('register'))

if __name__ == '__main__':
    app.run(debug=True)
