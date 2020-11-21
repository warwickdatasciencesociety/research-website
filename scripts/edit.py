"""Script used to launch a containerised instance of JupyterLab for a post."""

import argparse
import os
import socket
import subprocess

# Check script is being ran from correct location
if not os.path.exists('scripts'):
	raise OSError("Script must be ran from repository root")

# Read single argument of post name
parser = argparse.ArgumentParser()
parser.add_argument('post', type=str, help='the name of the post to edit')
parser.add_argument('-p', '--port', nargs='?', const=8888, type=int, 
					help='host port to run JupyterLab on')
args = parser.parse_args()
post, port = args.post, args.port

# Validate arguments
if not os.path.exists(f'content/{post}'):
	raise OSError(f"Could not find post folder")
if not os.path.exists(f'content/{post}/post.ipynb'):
	raise OSError(f"Could not find post notebook")
if not os.path.exists(f'content/{post}/Dockerfile'):
	raise OSError(f"Could not find Dockerfile for post")
if not 0 < port < 65354:
	raise ValueError("Port must be between 0 and 65354, exclusive")
	
# Build Docker image if doesn't exist
matches = subprocess.check_output(
	f"docker images -q {post}",
	shell=True
).decode("utf-8").strip()
if not matches:
	print("Corresponding Docker image not found locally...building")
	os.system(f'docker build -q -f content/{post}/Dockerfile -t {post} .')
	
# Check for port availability
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	if s.connect_ex(('localhost', port)) == 0:
		raise ValueError(f"Port {port} is already in use. Please close this "
					     "connection or specify an alternative port")

# Launch JupyterLab using Docker
os.system(' '.join([
	f'docker run --rm -it -p {port}:8888',
	f'-v "${{PWD}}/content/{post}:/home/jovyan/work"',
	'-e JUPYTER_ENABLE_LAB=yes',
	post
]))

