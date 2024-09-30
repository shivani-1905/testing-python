from flask import Flask, request, jsonify
import json
import requests
app = Flask(__name__)
@app.route('/github-webhook', methods=['POST'])
def github_webhook():
    data = request.get_json()
    try:
        repo_name = data['repository']['name']
        git_url = data['repository']['git_url']
        latest_commit_id = data['head_commit']['id']
        response = {
            'repository_name': repo_name,
            'git_url': git_url,
            'latest_commit_id': latest_commit_id
        }
        print(json.dumps(response, indent=4))  
        jenkins_url = 'http://127.0.0.1:5001/trigger-job' 
        jenkins_payload = {'commit_id': latest_commit_id}  
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
        print(json.dumps(error_response, indent=4)) 
        return jsonify(error_response), 400
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
