#README

##Environment:

•	Python 2.7.12

•	Tested under Windows environment, but should also work under UNIX/Linux if Python 2 installed

##Needed files:

•	hangman.py		(main function)

•	game.py		(utility functions, including the letter selection strategy)

•	words_50000.txt (dictionary of words, you can replace with other txt files with words in it)

##Instructions:

I ran the code using the following command (in Windows): 

	python hangman.py words_50000.txt words_50000.txt
	
You can use ‘python hangman.py -h’ for help. 

•	Basically first parameter is the dictionary file and the second (third, fourth…) should be a list of words used for the game or just one string ended with ‘txt’. 

•	The second choice (file) means using all the words in the file for the game.
