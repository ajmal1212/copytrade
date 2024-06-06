from flask import Flask, request, jsonify
import json
import pymysql
import requests

app = Flask(__name__)

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
