from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/trigger-job', methods=['POST'])
def trigger_jenkins_job():
    try:
        # Extract commit ID from the request data
        data = request.get_json()
        commit_id = data.get('commit_id')

        if not commit_id:
            return jsonify({'error': 'Missing commit ID'}), 400

        # Fetch Jenkins Crumb for CSRF protection
        crumb_response = requests.get(f'{JENKINS_URL}/crumbIssuer/api/json', auth=HTTPBasicAuth(USERNAME, API_TOKEN))
        
        if crumb_response.status_code == 200:
            crumb_data = crumb_response.json()
            crumb_field = crumb_data['crumbRequestField']
            crumb_value = crumb_data['crumb']

            # Jenkins job URL to trigger the build
            trigger_url = f'{JENKINS_URL}/job/{JOB_NAME}/buildWithParameters?COMMIT_ID={commit_id}'  # Send commit ID as parameter
            headers = {crumb_field: crumb_value}

            # Send POST request to trigger the Jenkins job
            response = requests.post(trigger_url, auth=HTTPBasicAuth(USERNAME, API_TOKEN), headers=headers)

            if response.status_code == 201:
                return jsonify({'message': f'Jenkins job {JOB_NAME} triggered successfully with commit ID {commit_id}!'}), 201
            else:
                return jsonify({'error': f'Failed to trigger Jenkins job', 'status_code': response.status_code}), response.status_code
        else:
            return jsonify({'error': 'Failed to fetch Jenkins crumb', 'status_code': crumb_response.status_code}), crumb_response.status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001)
