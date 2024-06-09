from flask import Flask, request, jsonify, render_template
import json
import pymysql
import requests
import logging
import pyotp
import qrcode  # Make sure to add this import
from io import BytesIO
import base64

app = Flask(__name__, static_url_path='/static')

TOTP_SECRET = 'JBSWY3DPEHPK3PXP'

# Setup logging
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

@app.route("/")
def html():
    return render_template("index.html")

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/apexcharts")
def apexcharts():
    return render_template("charts-apexcharts.html")
 
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
def html1():
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
def error():
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
            # Here, we'll just print the username and password for demonstration
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
    
@app.route("/register.html")
def register():
    return render_template("register.html")

@app.route("/tables-data.html")
def data():
    return render_template("tables-data.html")

@app.route("/tables-general.html")
def general():
    return render_template("tables-general.html")

@app.route("/users-profile.html")
def html2():
    return render_template("users-profile.html")

# Database configuration
db_config = {
    'host': 'sql.freedb.tech',
    'user': 'freedb_Ajmal',
    'password': 'f8PbPDFWub$&4@$',
    'database': 'freedb_Levels'
}

def get_db_connection():
    conn = pymysql.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

def fetch_jkey_and_user_info():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute('SELECT jkey, uid, actid FROM user_info WHERE id = 1')  # Adjust the query and condition as needed
        user_info = cursor.fetchone()
    conn.close()
    return user_info['jkey'], user_info['uid'], user_info['actid']

def send_to_another_api(data_with_jkey):
    api_url = "https://skypro.skybroking.com/NorenWClientTP/PlaceOrder"  # Replace with your target API URL
    headers = {
        "Content-Type": "application/json",
        # "Authorization": "Bearer YOUR_BEARER_TOKEN"  # Replace with your Bearer token
    }
    
    response = requests.post(api_url, headers=headers, data=data_with_jkey)
    return response.status_code, response.json()

@app.route("/webhook", methods=['POST'])
def hook():
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
            "prd": data.get("pcode"),  # Map pcode to prd
            "trantype": data.get("trantype"),
            "prctyp": data.get("prctyp"),
            "ret": data.get("ret"),
            "ordersource": data.get("ordersource", "API")  # Default to "API" if not provided
        }
        
        # Convert the dictionary to a JSON string
        json_data = json.dumps(subset_data)
        
        # Format the final data string with jdata= and jkey
        data_with_jkey = f"jData={json_data}&jKey={jkey_value}"
        
        print(data_with_jkey)
        
        # Forward the formatted string with jkey to another API
        status_code, response_data = send_to_another_api(data_with_jkey)
        print(f"Forwarded data to another API, response status: {status_code}, response data: {response_data}")

        return data_with_jkey, 200  # Return the formatted string and a 200 OK status
    else:
        error_message = "Content-Type not supported!"
        print(f"Unsupported Content-Type: {request.headers['Content-Type']}")
        return error_message, 415  # Return an error for unsupported Content-Type

if __name__ == "__main__":
    app.run(debug=True)
