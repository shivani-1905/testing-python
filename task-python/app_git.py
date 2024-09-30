from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)

@app.route('/github-webhook', methods=['POST'])
def github_webhook():
    # Get the JSON data from the request
    data = request.get_json()

    # Extract relevant details
    try:
        repo_name = data['repository']['name']
        git_url = data['repository']['git_url']
        latest_commit_id = data['head_commit']['id']

        # Prepare the response
        response = {
            'repository_name': repo_name,
            'git_url': git_url,
            'latest_commit_id': latest_commit_id
        }

        # Print the response in JSON format to the console
        print(json.dumps(response, indent=4))  # Output in pretty JSON format

        # Send a POST request to the second Flask app to trigger Jenkins job
        jenkins_url = 'http://127.0.0.1:5001/trigger-job'  # URL of Jenkins Flask app
        jenkins_payload = {'commit_id': latest_commit_id}  # Payload to be sent

        try:
            jenkins_response = requests.post(jenkins_url, json=jenkins_payload)
            if jenkins_response.status_code == 201:
                print("Jenkins job triggered successfully!")
            else:
                print(f"Failed to trigger Jenkins job: {jenkins_response.status_code}")
        except Exception as e:
            print(f"Error sending request to Jenkins Flask: {str(e)}")

        return jsonify(response), 200
    except KeyError as e:
        error_response = {'error': f'Missing key: {str(e)}'}
        print(json.dumps(error_response, indent=4))  # Print the error response
        return jsonify(error_response), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
