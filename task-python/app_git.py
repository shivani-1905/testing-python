from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)

# URL of the second Flask app that triggers Jenkins
SECOND_FLASK_APP_URL = 'http://localhost:5000/trigger-job'

@app.route('/github-webhook', methods=['POST'])
def github_webhook():
    # Get the JSON data from the request
    data = request.get_json()

    # Extract relevant details
    try:
        repo_name = data['repository']['name']
        git_url = data['repository']['git_url']
        latest_commit_id = data['head_commit']['id']

        # Prepare the payload for the second Flask app
        payload = {
            'repository_name': repo_name,
            'git_url': git_url,
            'latest_commit_id': latest_commit_id
        }

        # Print the payload for debugging purposes
        print(json.dumps(payload, indent=4))

        # Send the payload to the second Flask app to trigger the Jenkins job
        response = requests.post(SECOND_FLASK_APP_URL, json=payload)

        if response.status_code == 201:
            return jsonify({'message': 'Jenkins job triggered successfully!'}), 201
        else:
            return jsonify({'error': 'Failed to trigger Jenkins job', 'status_code': response.status_code}), response.status_code

    except KeyError as e:
        error_response = {'error': f'Missing key: {str(e)}'}
        print(json.dumps(error_response, indent=4))  # Print the error response
        return jsonify(error_response), 400

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
