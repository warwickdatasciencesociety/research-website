## Notes

- Use `nodejs=12`, preferably through Conda

## Commands

_Note: The following commands should be ran from_ `<repo-root>/content/$POST_TITLE`.

Set post title:

```bash
POST_TITLE=python-example
```

Build image:

```bash
docker build . -t $POST_TITLE
```

Edit a post using Docker:

```bash
docker run --rm -it \
	-p 8888:8888 \
	-v "${PWD}:/home/jovyan/work" \
	$POST_TITLE
```

Build a post using Docker:

```bash
docker run --rm -it \
	-v "${PWD}:/home/jovyan/work" \
	$POST_TITLE \
	jupyter nbconvert --to markdown /home/jovyan/work/post.ipynb
```



