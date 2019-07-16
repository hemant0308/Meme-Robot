import sys

from lxml import html as parser
from lxml import etree

import requests
import time
import threading
import html
import json
import sys

data = {}

def parse_str(raw_str,page_name):
	json_data = json.loads(raw_str)
	html_str = json_data['domops'][0][3]['__html']
	html_str = html.unescape(html_str)
	htmltree = parser.fromstring(html_str)
	posts_el = htmltree.cssselect(".userContentWrapper")
	data_array = json_data['jsmods']['pre_display_requires']
	array_len = len(data_array)
	posts_count = int(array_len/2)

	posts = []
	index = 0
	for post_el in posts_el:
		try:
			post = get_post(post_el)
			feedback_obj = data_array[posts_count + index][3][1]['__bbox']['result']['data']['feedback']
			comment_count = feedback_obj['i18n_comment_count']
			reaction_count = feedback_obj['i18n_reaction_count']
			share_count = feedback_obj['i18n_share_count']
			post.set_feedback(comment_count,reaction_count,share_count,page_name)
			posts.append(post)
		except Exception as e:	
			print(e)
			pass
		index = index + 1
	return posts

def get_el_text_by_css(el,css):
	el = get_el_by_css(el,css)
	return el.text_content() if el is not None else ""

def get_el_by_css(el,css):
	if el != None:
		elems = el.cssselect(css)
		if(elems != None and len(elems) > 0):
			return elems[0]

def get_el_attr_by_css(el,css,attribute):
	el = get_el_by_css(el,css)
	return el.get(attribute) if el is not None else None

def get_post(post_el):
	img_src = get_el_attr_by_css(post_el,".scaledImageFitWidth","src")
	post_msg = get_el_text_by_css(post_el,"div[data-testid='post_message']")
	posted_time = int(get_el_attr_by_css(post_el,'abbr[data-utime]',"data-utime"))
	posted_time = posted_time - (12 * 60 * 60 - 30 * 60) # Removing 12:30 hours to match with indian time.
	return FbPost(img_src=img_src,post_msg=post_msg,posted_time=posted_time)

def get_page_posts(page_id,page_name):
	current_time = time.time()
	prev_filtered_posts = []
	is_all_fetched = False
	posts_count = 5
	while not is_all_fetched:
		url = construct_url(page_id,posts_count)
		response = requests.get(url)
		raw_str = response.content.decode('UTF-8')
		raw_str = raw_str.replace('for (;;);','')
		all_posts = parse_str(raw_str,page_name)
		filtered_posts = []
		exceeded_count = 0
		for post in all_posts:
			if post.posted_time < current_time - (data['timeDuration']):
				exceeded_count = exceeded_count + 1
			filtered_posts.append(post)
		if len(filtered_posts) == len(prev_filtered_posts):
			print("No more posts")
			break
		prev_filtered_posts = filtered_posts
		if exceeded_count > 1:
			is_all_fetched = True
			print("All fetched")
			break
		posts_count = posts_count+5
	return prev_filtered_posts


class FbPost(object):
	"""docstring for FbPost"""
	def __init__(self, **kwargs):
		super(FbPost, self).__init__()
		self.img_src = kwargs["img_src"]
		self.posted_time = kwargs["posted_time"]
		self.post_msg = kwargs["post_msg"]

	def set_feedback(self,comment_count,reaction_count,share_count,page_name):
		self.comment_count = self.convert_to_number(comment_count)
		self.share_count  = self.convert_to_number(share_count)
		self.reaction_count = self.convert_to_number(reaction_count)
		self.page_name = page_name
		if self.img_src is None:
			self.reach_count = 0
		else:
			self.reach_count = (self.share_count * 2) + (self.reaction_count) + (self.comment_count * 1.2)
	
	def convert_to_number(self,reach_count_str = "0"):
		try:
			reach_count_str = reach_count_str.lower()
			if 'k' in reach_count_str or 'వే' in reach_count_str:
				return int(1000 * float(reach_count_str.replace('k','').replace('వే','')))
			elif 'm' in reach_count_str:
				return int(1000000 * float(reach_count_str.replace('m','')))
			else:
				return int(reach_count_str)
		except ValueError as e:
			print(e)
			return 0

	def __str__(self):
		return ("Image Src : "+str(self.img_src)+"\nPosted Time : "+str(time.strftime('%m/%d/%Y, %H:%M:%S',time.localtime(self.posted_time)))
			+"\nTime stamp : "+str(self.posted_time)+"\nShare Count : "+str(self.share_count)+"\nComment Count : "+str(self.share_count)+"\nReaction Count : "+str(self.reaction_count)+"\nPost Message: "+str(self.post_msg)+"\nReach count :"+str(self.reach_count)+"\n");

def get_page_posts_by_pageIds(pagesData):
	total_posts_array = []
	for page in pagesData:
		posts = get_page_posts(page['pageId'],page['pageName'])
		total_posts_array = total_posts_array + posts
	return total_posts_array

def get_top_posts(pagesData):
	posts = get_page_posts_by_pageIds(pagesData)
	posts.sort(key=lambda a: a.reach_count,reverse=True)
	print("Total posts Count : {}".format(len(posts)))
	return posts[:3]

def construct_url(page_id,posts_count):
	url = data["urlFormat"]
	return url.replace("{{pageId}}",page_id).replace("{{postsCount}}",str(posts_count))

def get_random_chunks(pageIds):
	random.shuffle(pageIds)
	chunk_size = math.ceil(len(pageIds)/NO_OF_THREADS)
	remainder = len(pageIds)%NO_OF_THREADS
	iterator = 0
	chunks_count = NO_OF_THREADS
	while  chunks_count > 1:
		yield pageIds[iterator:(iterator+chunk_size)]
		chunks_count = chunks_count - 1
		remainder = remainder - 1
		iterator = iterator + chunk_size
		if remainder == 0:
			chunk_size = chunk_size - 1
	yield pageIds[iterator:]

def main():
	global data
	with open("data.json") as f:
		data = json.load(f)

	starttime = time.time()	
	top_posts = get_top_posts(data['pagesData'])
	print("Top posts : ")
	for post in top_posts:
		print(post)
	print("Duration : ",time.time()-starttime)