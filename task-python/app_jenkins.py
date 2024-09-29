from flask import Flask, jsonify, request
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# Jenkins server details
JENKINS_URL = 'http://localhost:8080'
USERNAME = 'admin'
API_TOKEN = '11d01377b7cdab1a1dd108f728f0129476'
JOB_NAME = 'freestyle1'  # Your Jenkins job name

@app.route('/trigger-job', methods=['POST'])
def trigger_jenkins_job():
    try:
        # Get the payload from the first Flask app
        data = request.get_json()

        # Extract repository details from the payload
        repo_name = data.get('repository_name')
        git_url = data.get('git_url')
        latest_commit_id = data.get('latest_commit_id')

        # Prepare any Jenkins parameters (if needed) with the commit details
        # You can send these parameters to Jenkins depending on your job configuration

        # Fetch Jenkins Crumb for CSRF protection
        crumb_response = requests.get(f'{JENKINS_URL}/crumbIssuer/api/json', auth=HTTPBasicAuth(USERNAME, API_TOKEN))
        
        if crumb_response.status_code == 200:
            crumb_data = crumb_response.json()
            crumb_field = crumb_data['crumbRequestField']
            crumb_value = crumb_data['crumb']

            # Jenkins job URL to trigger the build
            trigger_url = f'{JENKINS_URL}/job/{JOB_NAME}/buildWithParameters'
            headers = {crumb_field: crumb_value}

            # Prepare parameters to send along with the build trigger
            params = {
                'REPO_NAME': repo_name,
                'GIT_URL': git_url,
                'COMMIT_ID': latest_commit_id
            }

            # Send POST request to trigger the Jenkins job
            response = requests.post(trigger_url, auth=HTTPBasicAuth(USERNAME, API_TOKEN), headers=headers, params=params)

            if response.status_code == 201:
                return jsonify({'message': f'Jenkins job {JOB_NAME} triggered successfully with commit {latest_commit_id}!'}), 201
            else:
                return jsonify({'error': f'Failed to trigger Jenkins job', 'status_code': response.status_code}), response.status_code
        else:
            return jsonify({'error': 'Failed to fetch Jenkins crumb', 'status_code': crumb_response.status_code}), crumb_response.status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
