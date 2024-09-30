from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth
from config import JENKINS_URL, USERNAME, API_TOKEN, JOB_NAME
app = Flask(__name__)
@app.route('/trigger-job', methods=['POST'])
def trigger_job():
    data = request.get_json()
    commit_id = data.get('commit_id')
    if not commit_id:
        return jsonify({"error": "Missing commit_id in request"}), 400
    crumb_response = requests.get(
        f'{JENKINS_URL}/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,":",//crumb)', 
        auth=HTTPBasicAuth(USERNAME, API_TOKEN)
    )
    if crumb_response.status_code != 200:
        return jsonify({"error": "Failed to get crumb", "details": crumb_response.content.decode()}), 500
    crumb = crumb_response.text
    trigger_response = requests.post(
        f'{JENKINS_URL}/job/{JOB_NAME}/buildWithParameters',
        headers={crumb.split(":")[0]: crumb.split(":")[1]},
        params={'COMMIT_ID': commit_id},
        auth=HTTPBasicAuth(USERNAME, API_TOKEN)
    )
    if trigger_response.status_code == 201:
        return jsonify({"message": "Job triggered successfully"}), 201
    else:
        print(f"Trigger job failed with status code {trigger_response.status_code} and response: {trigger_response.content.decode()}")
        return jsonify({"error": "Failed to trigger job", "details": trigger_response.content.decode()}), 500
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)