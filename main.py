import json
import time

from utils import get_top_posts,post_FbPosts

if __name__ == '__main__':
	start_time = time.time()
	with open("data.json") as f:
		data = json.load(f)
	top_posts = get_top_posts(data)
	for post in top_posts:
	 	print(post)
	post_FbPosts(data,top_posts)
	print("Total posts posted : "+str(len(top_posts)))
	print("Time taken : "+str(time.time() - start_time))
