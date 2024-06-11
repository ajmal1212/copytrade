from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, current_app
import json
import pymysql
import requests
import logging
import pyotp
import qrcode
from io import BytesIO
import base64
from werkzeug.security import generate_password_hash

app = Flask(__name__, static_url_path='/static')

# Database configuration
db_config = {
    'host': 'sql.freedb.tech',
    'user': 'freedb_Ajmal',
    'password': 'f8PbPDFWub$&4@$',
    'database': 'freedb_Levels'
}

TOTP_SECRET = 'JBSWY3DPEHPK3PXP'

# Setup logging
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

app.secret_key = 'ygjhfgjghkkmb'  # Set a secret key for session management

def get_db_connection():
    connection = pymysql.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_account', methods=['POST'])
def create_account():
    client_code = request.form['client_code']
    name = request.form['name']
    number = request.form['number']
    mail_id = request.form['mail_id']

    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        current_app.logger.info(f"Attempting to insert: {client_code}, {name}, {number}, {mail_id}")
        cursor.execute('INSERT INTO accounts (client_code, name, number, mail_id) VALUES (%s, %s, %s, %s)', 
                       (client_code, name, number, mail_id))
        connection.commit()
        current_app.logger.info("Insert successful, committed to database")
        flash('Account created successfully!', 'success')
    except pymysql.MySQLError as err:
        current_app.logger.error(f"Error: {err}")
        flash(f'Error: {err}', 'danger')
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('index'))

@app.route('/childusers/api', methods=['POST'])
def apidata():
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute('SELECT * FROM accounts')
        accounts = cursor.fetchall()  # Fetch all results
    except pymysql.MySQLError as err:
        current_app.logger.error(f"Error: {err}")
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        connection.close()

    return jsonify(accounts)  # Return the fetched data as JSON

@app.route("/apexcharts")
def apexcharts():
    return render_template("charts-apexcharts.html")

@app.route("/childusers")
def childuser():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('SELECT * FROM accounts')
        accounts_data = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

    return render_template('child-users.html', accounts=accounts_data)

@app.route("/charts-chartjs.html")
def chartjs():
    return render_template("charts-chartjs.html")

@app.route("/charts-echarts.html")
def echarts():
    return render_template("charts-echarts.html")

@app.route("/components-accordion.html")
def accordion():
    return render_template("components-accordion.html")

@app.route("/components-alerts.html")
def alerts():
    return render_template("components-alerts.html")

@app.route("/components-badges.html")
def badges():
    return render_template("components-badges.html")

@app.route("/components-breadcrumbs.html")
def breadcrumbs():
    return render_template("components-breadcrumbs.html")

@app.route("/pages-blank.html")
def blank():
    return render_template("pages-blank.html")

@app.route("/pages-contact.html")
def contact():
    return render_template("pages-contact.html")

@app.route("/pages-error-404.html")
def error_404():
    return render_template("pages-error-404.html")

@app.route("/pages-faq.html")
def faq():
    return render_template("pages-faq.html")

@app.route('/pages-login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        totp_code = request.form['totp']

        # Verify TOTP
        totp = pyotp.TOTP(TOTP_SECRET)
        if totp.verify(totp_code):
            # Proceed with your user authentication logic
            print(f"Username: {username}")
            print(f"Password: {password}")
            return "Login successful"
        else:
            flash("Invalid TOTP code")
            return redirect(url_for('login'))
    return render_template("pages-login.html")

@app.route('/generate-totp', methods=['POST'])
def generate_totp():
    # Generate a new TOTP secret
    new_totp_secret = pyotp.random_base32()

    # Create a TOTP object
    totp = pyotp.TOTP(new_totp_secret)

    # Generate a QR code
    qr_url = totp.provisioning_uri(name="user@example.com", issuer_name="YourApp")
    qr = qrcode.make(qr_url)
    buffered = BytesIO()
    qr.save(buffered, format="PNG")
    qr_code_img = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return jsonify({'secret': new_totp_secret, 'qr_code_img': qr_code_img})

@app.route("/register" , methods=['POST'])
def register():
    # Get form data
    name = request.form['name']
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    
    # Hash the password
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        current_app.logger.info(f"Attempting to insert: {name}, {email}, {username}, {hashed_password}")
        cursor.execute('INSERT INTO users (name, email, username, password) VALUES (%s, %s, %s, %s)', 
                       (name, email, username, hashed_password))
        connection.commit()
        current_app.logger.info("Insert successful, committed to database")
        flash('Account created successfully!', 'success')
    except pymysql.MySQLError as err:
        current_app.logger.error(f"Error: {err}")
        flash(f'Error: {err}', 'danger')
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('index'))

@app.route("/user-register")
def user_register():
    return render_template("register.html")

@app.route("/tables-data.html")
def tables_data():
    return render_template("tables-data.html")

@app.route("/tables-general.html")
def tables_general():
    return render_template("tables-general.html")

@app.route("/users-profile.html")
def users_profile():
    return render_template("users-profile.html")

def fetch_jkey_and_user_info():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute('SELECT jkey, uid, actid FROM user_info WHERE id = 1')
        user_info = cursor.fetchone()
    conn.close()
    return user_info['jkey'], user_info['uid'], user_info['actid']

def send_to_another_api(data_with_jkey):
    api_url = "https://skypro.skybroking.com/NorenWClientTP/PlaceOrder"
    headers = {
        "Content-Type": "application/json",
    }
    
    response = requests.post(api_url, headers=headers, data=data_with_jkey)
    return response.status_code, response.json()

@app.route("/webhook", methods=['POST'])
def webhook():
    if request.headers['Content-Type'] == 'application/json':
        data = request.json
        
        # Print received webhook data
        print("Received webhook data:", data)

        # Fetch jkey, uid, and actid from the database
        jkey_value, uid_value, actid_value = fetch_jkey_and_user_info()
        
        # Create a new dictionary with the mapped fields
        subset_data = {
            "uid": uid_value,
            "actid": actid_value,
            "exch": data.get("exch"),
            "tsym": data.get("tsym"),
            "qty": data.get("qty"),
            "prc": data.get("prc"),
            "prd": data.get("pcode"),
            "trantype": data.get("trantype"),
            "prctyp": data.get("prctyp"),
            "ret": data.get("ret"),
            "ordersource": data.get("ordersource", "API")
        }
        
        # Convert the dictionary to a JSON string
        json_data = json.dumps(subset_data)
        
        # Format the final data string with jdata= and jkey
        data_with_jkey = f"jData={json_data}&jKey={jkey_value}"
        
        print(data_with_jkey)
        
        # Forward the formatted string with jkey to another API
        status_code, response_data = send_to_another_api(data_with_jkey)
        print(f"Forwarded data to another API, response status: {status_code}, response data: {response_data}")

        return data_with_jkey, 200
    else:
        error_message = "Content-Type not supported!"
        print(f"Unsupported Content-Type: {request.headers['Content-Type']}")
        return error_message, 415

if __name__ == "__main__":
    app.run(debug=True)
