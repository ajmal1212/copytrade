from flask import Flask, request, render_template, jsonify
import json
import mysql.connector
import requests

app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'your_db_host',
    'user': 'your_db_user',
    'password': 'your_db_password',
    'database': 'your_db_name'
}

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

def fetch_jkey_and_user_info():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT jkey, uid, actid FROM user_info WHERE id = 1')  # Adjust the query and condition as needed
    user_info = cursor.fetchone()
    cursor.close()
    conn.close()
    return user_info['jkey'], user_info['uid'], user_info['actid']

def send_to_another_api(data, jkey_value):
    api_url = "https://example.com/target-api"  # Replace with your target API URL
    headers = {
        "Content-Type": "application/json",
#        "Authorization": "Bearer YOUR_BEARER_TOKEN"  # Replace with your Bearer token
    }
    
    # Add the jkey to the data
    data['jkey'] = jkey_value
    
    response = requests.post(api_url, headers=headers, json=data)
    return response.status_code, response.json()

@app.route("/webhook", methods=['POST'])
def hook():
    if request.headers['Content-Type'] == 'application/json':
        data = request.json
        
        # Fetch jkey, uid, and actid from the database
        jkey_value, uid_value, actid_value = fetch_jkey_and_user_info()
        
        # Define the field mappings from incoming JSON to target JSON
        field_mappings = {
            "uid": uid_value,
            "actid": actid_value,
            "exch": "exchange",
            "tsym": "symbol",
            "qty": "quantity",
            "prc": "price",
            "prd": "product",
            "trantype": "transaction_type",
            "prctyp": "price_type",
            "ret": "retention",
            "ordersource": "ordersource"
        }
        
        # Create a new dictionary with the mapped fields
        subset_data = {
            "uid": uid_value,
            "actid": actid_value,
            "exch": data.get("exch"),
            "tsym": data.get("tsym"),
            "qty": data.get("qty"),
            "prc": data.get("prc"),
            "prd": data.get("prd"),
            "trantype": data.get("trantype"),
            "prctyp": data.get("prctyp"),
            "ret": data.get("ret"),
            "ordersource": data.get("ordersource", "API")  # Default to "API" if not provided
        }
        
        my_info = json.dumps(subset_data, indent=4)  # Pretty print the JSON
        print(my_info)
        
        # Forward the subset data with jkey to another API
        status_code, response_data = send_to_another_api(subset_data, jkey_value)
        print(f"Forwarded data to another API, response status: {status_code}, response data: {response_data}")

        return my_info, 200  # Return the JSON and a 200 OK status
    else:
        error_message = "Content-Type not supported!"
        print(f"Unsupported Content-Type: {request.headers['Content-Type']}")
        return error_message, 415  # Return an error for unsupported Content-Type

if __name__ == "__main__":
    app.run(debug=True)
