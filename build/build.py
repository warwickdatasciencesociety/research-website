import os
import re
import shutil

import docker


#### SETUP ####

# Connect to Docker daemon
client = docker.from_env()

# Parameters
TO_SKIP = (
    '.ipynb_checkpoints'
)

# Verify directory structure
if not os.path.exists('content'):
    raise OSError(f"expected directory `content` in working directory")
	
# Remove existing source files
if os.path.exists('source'):
    shutil.rmtree('source')
os.mkdir('source')

#### BUILD ####

posts = [post for post in os.listdir('content') if not post in TO_SKIP]
n = len(posts)
for i, post in enumerate(posts):
    print(f"Processing post {i+1} of {n}: {post}")

    # Ignore none post directories
    if post in TO_SKIP:
        continue

    # Verify directory structure
    post_dir = os.path.join('content', post)
    if not os.path.exists(os.path.join(post_dir, 'Dockerfile')):
        raise OSError(f"couldn't find Dockerfile for post {post}")
    if not os.path.exists(os.path.join(post_dir, 'post.ipynb')):
        raise OSError(f"couldn't find notebook for post {post}")
    
    # Remove existing support files
    post_support_files_dir = os.path.join(post_dir, 'post_files')
    if os.path.exists(post_support_files_dir):
	    shutil.rmtree(post_support_files_dir)

    # Build docker image
    client.images.build(path=post_dir, tag=post)
    
    # Execute and convert post notebook
    con = client.containers.run(
        image=post,
        # TODO: run as Python script
        command=' '.join([
            'ls /home/jovyan/work -alR && jupyter nbconvert',
            '--execute',
            '/home/jovyan/work/post.ipynb',
            '--MarkdownExporter.preprocessors',
            '"nbconvert.preprocessors.TagRemovePreprocessor"',
	        '--TagRemovePreprocessor.remove_cell_tags',
	        '"remove_cell"',
	        '--TagRemovePreprocessor.remove_input_tags',
	        '"remove_input"',
	        '--TagRemovePreprocessor.remove_single_output_tags',
	        '"remove_single_output"',
	        '--TagRemovePreprocessor.remove_all_outputs_tags', 
	        '"remove_all_output"',
	        '--to markdown',
        ]),
        remove=True,
        volumes={
            os.path.join(os.getcwd(), post_dir): {'bind': '/home/jovyan/work',
                                                  'mode': 'rw'},
        },
        detach=True
    )
    
    # Stream conversion logs
    gen = con.logs(stream=True)
    while True:
        try:
            print(gen.__next__().decode('utf-8').strip())
        except StopIteration:
            break
    
    # Format notebook
    # TODO: move formatting into Docker container
    post_path = os.path.join(post_dir, 'post.md')
    with open(post_path, 'r', encoding='utf8') as f:
        contents = f.read()

        # Correct image paths
        contents = re.sub(f'post_files/', f'/images/{post}/', contents)

        # Remove captions
        contents = re.sub(r'!\[\w+\]', '![]', contents)

    with open(post_path, 'w', encoding='utf8') as f:
        f.write(contents)
    
    # Move files
    shutil.move(post_path, os.path.join(post_src_dir, f'{post}.md'))
    if os.path.exists(post_support_files_dir):
        os.mkdir(os.path.join(img_src_dir, post))
        for image in os.listdir(post_support_files_dir):
            shutil.move(os.path.join(post_support_files_dir, image),
                        os.path.join(img_src_dir, post, image))
        shutil.rmtree(post_support_files_dir)

