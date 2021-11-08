# Import "chatbot" from
# chatterbot package.
from app import app
from chatterbot import ChatBot
from flask_restplus import Resource

from chatterbot.trainers import ChatterBotCorpusTrainer

class Chat(Resource):
	# Give a name to the chatbot “corona bot”
	# and assign a trainer component.
	chatbot = ChatBot('corona bot')

	# Create a new trainer for the chatbot
	trainer = ChatterBotCorpusTrainer(chatbot)

	# Now let us train our bot with multiple corpus
	trainer.train("chatterbot.corpus.english.greetings",
				  "chatterbot.corpus.english.conversations")

	response = chatbot.get_response('What is your Number')
	print(response)

	response = chatbot.get_response('Who are you?')
	print(response)
