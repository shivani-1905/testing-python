flask app
from flask import Flask, request, jsonify

app = Flask(__name__)

# Define the route for GitHub webhook
@app.route('/github-webhook', methods=['POST'])
def github_webhook():
    if request.method == 'POST':
        # Get JSON payload from GitHub webhook
        data = request.json
        
        # Extract necessary details
        repository_name = data['repository']['name']
        repository_url = data['repository']['html_url']
        latest_commit_id = data['head_commit']['id']
        
        # Create a response dictionary
        response_data = {
            "repository_name": repository_name,
            "repository_url": repository_url,
            "latest_commit_id": latest_commit_id
        }
        
        return jsonify(response_data), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
