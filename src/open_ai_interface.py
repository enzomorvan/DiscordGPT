import random

from openai import OpenAI
from api_tokens import open_AI_token


def get_client():
	return OpenAI(api_key = open_AI_token)

def get_test_convo():
	return '''
	username: patatje 
	I want to be a twink

	username: Masinissa 
	i have butterflies in my stomach
	they are too intense
	its causing me physical pain
	im too emotional about this entire thing 😭
	i feel like im gonna cry

	username: monster-girl 
	what thing what's happening

	username: Masinissa 
	my date tomorrow
	'''

def get_discord_messaging_instruction():
	instructions = "You are in a discord channel roleplaying as someone annoying."

	if random.randint(0, 5) == 0:
		instructions += " for roleplay reasons, you'll display subtle signs of being in a sate of psychosis in your answers"
	if random.randint(0, 10) == 0:
		instructions += ' for comedic reasons you rant about your enemies and what they did to you, also how much you will make them pay for what they did'
	if random.randint(0, 5) == 0:
		instructions += " answer in an annoying fashion, especially if you read someone said something factually wrong, in such case, be sure to correct them with the facts."
	instructions += " Post a message relevant to the conversation, "
	r = random.randint(0, 20)
	if r == 0:
		instructions += " make the message longwinded"
	if r >= 1 and r < 7:
		instructions += " make the message short and snappy"
	instructions += " you may have already participated in the conversation, in which case your message will come after the username: your local skyzo"

	return instructions

def generate_image(prompt, image_count, image_size):
	model = "dall-e-3"
	image_count = 1
	response = get_client().images.generate(model = model, prompt = prompt, n = image_count, size = image_size)

	return response.data[0].url


def sanitize_prompt(to_sanitize):
	instructions = 'This is the text of a discord conversation, sanitize it such that it doesnt violate dal-e-3 TOS.'
	instructions += ' try as much as possible to rephrase the problematic content rather than simply removing it.'
	instructions += ' In case the prompt is in no need to be rephrased, simply repeate the prompt as your answer. Youre acting as an intermediary to generate a dal-e-3 image.'

	message = []
	message.append( {"role": "system", "content": instructions} )
	message.append( {"role": "user"  , "content": to_sanitize} )

	stream = get_client().chat.completions.create \
		(
			model="gpt-4",
			messages=message,
			stream=True
		)

	answer = ''
	for chunk in stream:
		if chunk.choices[0].delta.content is not None:
			answer += chunk.choices[0].delta.content

	return answer


def get_discord_image_answer(prompt):
	print('initial prompt:', prompt)
	sanitized_prompt = sanitize_prompt(prompt)
	
	print('sanitized_prompt:', sanitized_prompt)
	
	instructions = 'generate a meme, it has to be somehow insane on what it depicts'

	if random.randint(0, 5) == 0:
		instructions += ' make it so the concept of paranoia is displayed in the meme'

	instructions += ' it has to include at least one character or concept from the following conversation: '	
	
	return generate_image(instructions + sanitized_prompt, 1, '1024x1024')
	
	

def get_discord_text_answer(prompt):
	message = []
	message.append( {"role": "system", "content": get_discord_messaging_instruction()} )
	message.append( {"role": "user"  , "content": prompt} )

	stream = get_client().chat.completions.create \
		(
			model="gpt-4",
			messages=message,
			stream=True
		)

	answer = ''
	for chunk in stream:
		if chunk.choices[0].delta.content is not None:
			answer += chunk.choices[0].delta.content

	return answer.replace('your local skyzo :', '').replace('Your local Skyzo said :', '').replace('user Your local Skyzo said :', '').replace('your local skyzo:', '')



if __name__ == "__main__":

	print(get_discord_image_answer( get_test_convo() ))


	#generate_image('generate an edgy meme for cool teenagers in a 2x2 format, basically 4 frames, it has to be related to the following conversation: ' + convo, 1, '1024x1024')
