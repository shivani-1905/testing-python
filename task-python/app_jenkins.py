from flask import Flask, request, jsonify
import requests  
from requests.auth import HTTPBasicAuth
import os
app = Flask(__name__)
JENKINS_URL = os.environ.get('JENKINS_URL')
USERNAME = os.environ.get('JENKINS_USERNAME') 
API_TOKEN = os.environ.get('JENKINS_API_TOKEN')

@app.route('/jenkins/job', methods=['POST'])
def get_jenkins_job_details():
    """
    Extracts job details from Jenkins based on the incoming request.
    """
    data = request.get_json()

    # Validate that 'git_repo_name' and 'job_name' exist in the request data
    if not data or 'git_repo_name' not in data or 'job_name' not in data:
        return jsonify({"error": "Missing required data in JSON"}), 400

    git_repo_name = data['git_repo_name']
    job_name = data['job_name']  # Get the job name from the request data

    # Jenkins URL based on the provided job name
    url = f"{JENKINS_URL}/job/{job_name}/api/json"
    
    try:
        # Make a GET request to Jenkins using HTTP Basic Authentication
        response = requests.get(url, auth=HTTPBasicAuth(USERNAME, API_TOKEN))
        
        if response.status_code == 200:
            job_details = response.json()
            return jsonify(job_details), 200
        else:
            return jsonify({"error": f"Failed to retrieve job details: {response.status_code} - {response.text}"}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(port=5001, debug=True)