# -*- coding: utf-8 -*-
#
#  title_analyzer.py
#
#  This program analyzes the titles of reddit posts in two ways:
#  		1) Keyword Search - Searches titles for a number of keywords, and
#		  returns links to each matching post's comment section.
#
#		2) Word Graph - Counts all the words in a subreddits' post titles,
#			and returns a list of the most commonly used words.
#
#	This program requires the Python Reddit Wrapper.
#		Documentation: https://praw.readthedocs.org/
#		Install (Linux): 'sudo pip install praw'
#
#	Searches are pretty slow because Reddit requires two seconds between
#	each API call. While my code could always improve, the main culprit
#	for this program's (lack of) speed is the API requirements.
#
#  Copyright 2014 Joshua Palmer <palmerjoshua2013@fau.edu>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

import praw
import re
import operator
import string
from collections import defaultdict

# Misc. Functions:
def get_file_data(filename):
	data = []
	with open(filename, "r") as infile:
		print "Reading from file '"+filename+"'..."
		for line in infile:
			if len(line) > 1 and line not in data:
				data.append(line.strip())
	if len(data) > 0:
		return data
	return None

def list_to_string(re_list):
	restring = ''
	for re in re_list:
		restring += re
	return restring

def header(title):
	return '\n{}\n{}:\n{}\n'.format(('-'*60), title, ('-'*60))


# Subreddit Wordcounts and Keyword Matches:
class SubData(object):
	def __init__(self, subreddit_name):
		self.name = subreddit_name
		self.word_counts = defaultdict(int)  # { 'word': count }
		self.keyword_matches = defaultdict(list) # { 'keyword': ['postID1', 'postID2', etc. ] }

	# ignore words if they aren't used a minimum number of times
	def trim(self, minimum):
		for key in self.word_counts.keys():
			if self.word_counts[key] < minimum:
				del self.word_counts[key]

	def add_keyword(self, word, ID):
		if word not in self.keyword_matches or ID not in self.keyword_matches[word]:
			self.keyword_matches[word].append(ID)

	def clear(self):
		self.word_counts = None
		self.keyword_matches = None
		self.word_counts = defaultdict(int)
		self.keyword_matches = defaultdict(list)

	def count_word(self, word):
		if len(word) > 1:
			if word not in self.word_counts.keys():
				self.word_counts[word] = 1
			else:
				self.word_counts[word] += 1

	def get_data_string(self):
		if len(self.word_counts) > 0:
			msg = ""
			for key_val in self.sorted_tuple_list():
				msg += '{}: {}\n'.format(key_val[0], key_val[1])
			msg += '\n\n'

			return msg
		return "/r/{} had no matches.\n".format(self.name)

	def sorted_tuple_list(self):
		return reversed(sorted(self.word_counts.iteritems(), key=operator.itemgetter(1)))

	def keystring(self):
		ks = 'Keyword Matches:\n'
		for word in self.keyword_matches:
			ks += word+': {} matches\n'.format(len(self.keyword_matches[word]))
			for ID in self.keyword_matches[word]:
				ks += '\thttp://redd.it/{}\n'.format(ID)
			ks += '\n'
		return ks



class SearchData(object):
	def __init__(self, r):
		self.r = r
		self.keywords = []
		self.skipwords = []
		self.wordcounts = defaultdict(int)
		self.subreddits = defaultdict(SubData)
		self.get_search_terms()


	def print_keys(self):
		keys = header('Keywords')
		for key in self.keywords:
			keys += key+'\n'
		print keys


	def print_subs(self):
		subs = header('Subreddits')
		for sub in self.subreddits:
			subs += sub+'\n'
		print subs

	def print_skips(self):
		skips = header('Skipped Words')
		for word_or_regex in self.skipwords:
			skips += word_or_regex+'\n'
		print skips

	def add_subreddit(self, subreddit_name):
		if subreddit_name not in self.subreddits:
			self.subreddits[subreddit_name] = SubData(subreddit_name)
			print '/r/{} added to list of subreddits.\n'.format(subreddit_name)
		else:
			print '/r/{} is already in the list.\n'.format(subreddit_name)

	def delete_subreddit(self, subreddit_name):
		if subreddit_name in self.subreddits:
			del self.subreddits[subreddit_name]
			print '/r/{} deleted from list.\n'.format(subreddit_name)
			print
		else:
			print '/r/{} is not in the list\n.'.format(subreddit_name)

	def add_keyword(self, keyword):
		if keyword not in self.keywords:
			self.keywords.append(keyword)
			print keyword, 'added to the list.\n'
		else:
			print keyword, 'already in list.\n'

	def delete_keyword(self, keyword):
		if keyword in self.keywords:
			self.keywords.remove(keyword)
			print keyword, 'removed from list\n'
		else:
			print keyword, 'not in list.\n'

	def add_skipped(self, word):
		if word not in self.skipwords:
			self.skipwords.append('|'+word)
			print word, 'added to the list.\n'
		else:
			print word, 'already in list.\n'

	def delete_skipped(self, word):
		if word in self.skipwords:
			self.skipwords.remove(word)
			print word, 'removed from list.\n'
		else:
			print word, 'not in list.\n'

	def clear_subs(self):
		self.subreddits = None
		self.subreddits = defaultdict(SubData)
	def clear_keys(self):
		self.keywords = []
	def clear_skips(self):
		self.skipwords = []

# scans subreddit titles for keywords, returns links to matching posts
	def keyword_search(self):
		current_number = 1
		for subreddit in self.subreddits:
			print 'scanning subreddit {} of {}...'.format(current_number, len(self.subreddits))
			posts = self.r.get_subreddit(subreddit).get_hot(limit=None)
			for post in posts:
				for key in self.keywords:
					if key in post.title:
						self.subreddits[subreddit].add_keyword(key, post.id)
			current_number += 1
			print self.subreddits[subreddit].keystring()

# displays a list of the most commonly used words in a subreddit's post titles
	def word_graph(self):
		current_number = 1
		swregex = list_to_string(self.skipwords)

		for subreddit in self.subreddits:
			print 'scanning /r/{}: ({} of {})'.format(self.subreddits[subreddit].name, current_number, len(self.subreddits))
			posts = self.r.get_subreddit(subreddit).get_top_from_all(limit=None)
			for post in posts:
				for word in post.title.split(' '):
					newword = ''
					for ch in word:
						try:
							newword += str(ch)
						except UnicodeEncodeError:
							continue

					newword = newword.translate(string.maketrans('',''), string.punctuation).lower()
					excluded_word = re.match(swregex, newword, re.I)
					if not excluded_word:
						self.subreddits[subreddit].count_word(newword)

			self.subreddits[subreddit].trim(minimum=10)
			current_number += 1
			print self.subreddits[subreddit].get_data_string()


	def combo_search(self):
		skip_regex = list_to_string(self.skipwords)
		current_sub_number = 1

		for subreddit in self.subreddits:
			print "Scanning subreddit {} out of {}...".format(current_sub_number, len(self.subreddits))
			posts = self.r.get_subreddit(subreddit).get_hot(limit=None)

			for post in posts:
				try:
					title = str(post.title)

					for word in title.split(' '):
						word = word.translate(string.maketrans('',''), string.punctuation).lower()
						excluded_word = re.match(skip_regex, word, re.I)
						if not excluded_word:
							self.subreddits[subreddit].count_word(word)
						if word in self.keywords:
							self.subreddits[subreddit].add_keyword(word, post.id)

				except UnicodeEncodeError:
					print "Skipping post ID:", post.id
					continue
			self.subreddits[subreddit].trim(minimum=10)
			current_sub_number += 1

	def save_all_to_file(self):
		outputfilename = 'output.txt'
		with open(outputfilename, 'w') as outfile:
			print "Writing to {}...".format(outputfilename)
			data = ''
			for subreddit in self.subreddits:
				data += '-'*60+'\n'
				data += '/r/{}:\n'.format(self.subreddits[subreddit].name)
				data += '-'*60+'\n'
				data += self.subreddits[subreddit].get_data_string()
				data += self.subreddits[subreddit].keystring()
			outfile.write(data)
		print 'Done.'

	def get_search_terms(self):
		subfile = 'subreddits.txt'
		skipfile = 'skippedwords.txt'
		keyfile = 'keywords.txt'
		self.keywords = get_file_data(keyfile)
		self.skipwords = get_file_data(skipfile)
		for subreddit in get_file_data(subfile):
			self.subreddits[subreddit] = SubData(subreddit)




def run():

	menu = header('Main Menu')
	menu += 'as=add subreddit, ak=add keyword, aw=add skipped word\n'
	menu += 'ds=delete subreddit, dk=delete keyword, dw=delete skipped word\n\n'
	menu += 'ps=print subreddits, pk=print keywords, pw=print skipped words\n'
	menu += 'cs=clear subreddits, ck=clear keywords, cs=clear skipped words\n\n'
	menu += 'ks=keyword search, wg=word graph, bs=combo search, ex=exit\n\n'

	subprompt = 'enter subreddit: /r/'
	keyprompt = 'enter keyword: '
	wrprompt = 'enter word or regex: '

	print 'Connecting to Reddit...'
	reddit = praw.Reddit('parsing post titles')

	searchdata = SearchData(reddit)
	running = True
	while running:
		try:
			print menu
			ui = raw_input('enter command: ').rstrip('\n')
			#ADD
			if ui == 'as':
				searchdata.add_subreddit(raw_input(subprompt))
			elif ui == 'ak':
				searchdata.add_keyword(raw_input(keyprompt))
			elif ui == 'aw':
				searchdata.add_skipped(raw_input(wrprompt))
			#DELETE
			elif ui == 'ds':
				searchdata.delete_subreddit(raw_input(subprompt))
			elif ui == 'dk':
				searchdata.delete_keyword(raw_input(keyprompt))
			elif ui == 'dw':
				searchdata.delete_skipped(raw_input(wrprompt))
			#PRINT
			elif ui == 'ps':
				searchdata.print_subs()
			elif ui == 'pk':
				searchdata.print_keys()
			elif ui == 'pw':
				searchdata.print_skips()
			#CLEAR
			elif ui == 'cs':
				searchdata.clear_subs()
			elif ui == 'ck':
				searchdata.clear_keys()
			elif ui == 'cw':
				searchdata.clear_skips()
			#SEARCH
			elif ui == 'ks':
				searchdata.keyword_search()
			elif ui == 'wg':
				searchdata.word_graph()
			elif ui == 'bs':
				searchdata.scrape_data()

			elif ui == 'ex':
				print '\n\nexit\n\n'
				running = False
			else:
				print '\n\ninvalid input\n\n'
		except KeyboardInterrupt:
			running = True

def main():

	run()

	return 0

if __name__ == '__main__':
	main()

