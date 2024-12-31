import boto3
from flask import Flask, jsonify, abort
from botocore.exceptions import ClientError
from OpenSSL import SSL

app = Flask(__name__)

# Initialize the S3 client using IAM role (credentials automatically handled)
s3 = boto3.client('s3')
BUCKET_NAME = "your-bucket-name"  # Replace with your actual bucket name

@app.route('/list-bucket-content', defaults={'path': ''})
@app.route('/list-bucket-content/<path:path>')
def list_bucket_content(path):
    try:
        # Ensure the path ends with a slash (to simulate a directory)
        if path and not path.endswith('/'):
            path += '/'

        # List objects in the bucket with the specified prefix (path) and delimiter '/'
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=path, Delimiter='/')

        # Handle cases where the path doesn't exist (no objects found)
        if 'Contents' not in response and 'CommonPrefixes' not in response:
            return jsonify({"error": f"Path '{path}' does not exist or has no content."}), 404

        # Collect the content (directories or files)
        content = []
        if 'CommonPrefixes' in response:
            # If there are directories (folders), add them
            content.extend([prefix['Prefix'][:-1] for prefix in response['CommonPrefixes']])
        if 'Contents' in response:
            # If there are files, add them (but exclude the folder path)
            content.extend([obj['Key'].split('/')[-1] for obj in response['Contents'] if obj['Key'] != path])

        return jsonify({"content": content})

    except ClientError as e:
        # Catch general AWS errors and handle them
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        # Catch other exceptions, e.g., connectivity issues, and return a 500 error
        return jsonify({"error": "An unexpected error occurred: " + str(e)}), 500


if __name__ == '__main__':
    # Run Flask app with HTTPS
    context = ('mycert.pem', 'mykey.key')  # Path to the certificate and key
    app.run(host='0.0.0.0', port=5000, ssl_context=context)
