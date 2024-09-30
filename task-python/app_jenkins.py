from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# Jenkins configuration
JENKINS_URL = 'http://localhost:8080'  # Base URL of Jenkins
USERNAME = 'admin'  # Jenkins Username
API_TOKEN = '11d01377b7cdab1a1dd108f728f0129476'  # Jenkins API Token
JOB_NAME = 'freestyle1'  # Your Jenkins job name

@app.route('/trigger-job', methods=['POST'])
def trigger_job():
    # Get JSON data from the request
    data = request.get_json()
    
    # Extract the commit ID
    commit_id = data.get('commit_id')
    if not commit_id:
        return jsonify({"error": "Missing commit_id in request"}), 400
    
    # Step 1: Get the crumb for CSRF protection
    crumb_response = requests.get(
        f'{JENKINS_URL}/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,":",//crumb)', 
        auth=HTTPBasicAuth(USERNAME, API_TOKEN)
    )
    
    if crumb_response.status_code != 200:
        return jsonify({"error": "Failed to get crumb", "details": crumb_response.content.decode()}), 500
    
    # Parse the crumb response
    crumb = crumb_response.text.strip()
    crumb_header = crumb.split(":")  # Split into header name and value

    # Step 2: Trigger the job with parameters
    trigger_response = requests.post(
        f'{JENKINS_URL}/job/freestyle1/buildWithParameters',
        headers={crumb_header[0]: crumb_header[1]},  # Use crumb from previous step
        params={'COMMIT_ID': commit_id},
        auth=HTTPBasicAuth(USERNAME, API_TOKEN)
    )

    # Step 3: Check the response
    if trigger_response.status_code == 201:
        return jsonify({"message": "Job triggered successfully"}), 201
    else:
        return jsonify({"error": "Failed to trigger job", "details": trigger_response.content.decode()}), 500

if __name__ == '__main__':
    app.run(port=5001)  # Change the port if needed
