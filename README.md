reddit_title_analyzer
=====================

This program analyzes the titles of reddit posts in two ways:

 		1) Keyword Search - Searches titles for a number of keywords, and
		  returns links to each matching post's comment section.

		2) Word Graph - Counts all the words in a subreddits' post titles,
			and returns a list of the most commonly used words.

Subreddits, keywords, and words to be ignored may be added to
to subreddits.txt, keywords.txt, and skippedwords.txt respectively
before running the program, or you can add terms with the program's
user interface.

The final output will be saved to output.txt, but there are also
commands in the user interface to print the lists of search terms 
to the console.

Searches are pretty slow because Reddit requires two seconds between
each API call. While my code could always improve, the main culprit
for this program's (lack of) speed is the API requirements.

	This program requires the Python Reddit Wrapper.
		Documentation: https://praw.readthedocs.org/
		Install (Linux): 'sudo pip install praw'

