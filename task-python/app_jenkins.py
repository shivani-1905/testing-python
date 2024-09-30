from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth


app = Flask(__name__)

JENKINS_URL ='http://localhost:8080/job/freestyle1/buildWithParameters?COMMIT_ID=<commit_id>' 
USERNAME = 'admin'  # Jenkins Username
API_TOKEN = '11d01377b7cdab1a1dd108f728f0129476'  # Jenkins API Token
JOB_NAME = 'freestyle1'  # Your Jenkins job name


@app.route('/trigger-job', methods=['POST'])
def trigger_jenkins_job():
    try:
        # Print received request data
        data = request.get_json()
        print("Received data:", data)
        commit_id = data.get('commit_id')

        if not commit_id:
            print("Missing commit ID in request data.")
            return jsonify({'error': 'Missing commit ID'}), 400

        # Fetch Jenkins Crumb for CSRF protection
        crumb_response = requests.get(f'{JENKINS_URL}/crumbIssuer/api/json', auth=HTTPBasicAuth(USERNAME, API_TOKEN))
        print("Crumb response status:", crumb_response.status_code)
        print("Crumb response body:", crumb_response.text)

        if crumb_response.status_code == 200:
            crumb_data = crumb_response.json()
            crumb_field = crumb_data['crumbRequestField']
            crumb_value = crumb_data['crumb']

            # Jenkins job URL to trigger the build
            trigger_url = f'{JENKINS_URL}/job/{JOB_NAME}/buildWithParameters?COMMIT_ID={commit_id}'
            headers = {crumb_field: crumb_value}

            # Send POST request to trigger the Jenkins job
            response = requests.post(trigger_url, auth=HTTPBasicAuth(USERNAME, API_TOKEN), headers=headers)
            print("Jenkins trigger response status:", response.status_code)
            print("Jenkins trigger response body:", response.text)

            if response.status_code == 201:
                return jsonify({'message': f'Jenkins job {JOB_NAME} triggered successfully with commit ID {commit_id}!'}), 201
            else:
                return jsonify({'error': f'Failed to trigger Jenkins job', 'status_code': response.status_code}), response.status_code
        else:
            return jsonify({'error': 'Failed to fetch Jenkins crumb', 'status_code': crumb_response.status_code}), crumb_response.status_code

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(port=5001)
