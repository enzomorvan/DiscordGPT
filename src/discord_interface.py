import os
import datetime
import random

import time
import sys
import traceback

import discord
import tracemalloc
from discord.ext import commands

import open_ai_interface as gpt

from api_tokens import discord_token

tracemalloc.start()

TOKEN = discord_token
LISTEN_CHANNEL_NAME = 'insane-asylum'



intents = discord.Intents.default()
intents.messages = True  # Enable the bot to receive messages
intents.message_content = True

client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix='!', intents=intents)


class MessagesManager:
	def __init__(self, max_messages_in_memory: int):
		self.max_messages_in_memory: int = max_messages_in_memory

		self.messages: list = []
		
		self.messsages_since_last_meme_count = 0
		self.messsages_since_last_message_count = 0
		
		
		self.last_message_timestamp: int = 0 
		self.last_meme_timestamp: int = 0

	def add_message(self, message):
		if len(message.content) == 0: 
			return
	
		self.messages.append(message)
		
		self.messsages_since_last_message_count += 1 
		self.messsages_since_last_meme_count    += 1
		
		print('added message')
		print('text answer count:', self.messsages_since_last_message_count, self.is_it_time_for_a_text_answer() )
		print('meme answer count:', self.messsages_since_last_meme_count, self.is_it_time_for_a_meme_answer() )

		while len(self.messages) > self.max_messages_in_memory:
			self.messages = self.messages[1:]


	def is_it_time_for_a_text_answer(self) -> bool:
		if time.time() - self.last_message_timestamp > 20*60:
			return self.messsages_since_last_message_count > 15
		
		return False
		
	def is_it_time_for_a_meme_answer(self) -> bool:
		if time.time() - self.last_meme_timestamp > 2*60*60:#30*60:
			return self.messsages_since_last_meme_count > 40
		
		return False

	def did_a_text_answer(self):
		self.last_message_timestamp = time.time()
		self.messsages_since_last_message_count = 0
	
	def did_a_meme_answer(self):
		self.last_meme_timestamp = time.time()
		self.messsages_since_last_meme_count = 0


	def get_conversation_history_as_prompt(self, how_many_messages: int):
		how_many_messages = min(how_many_messages, len(self.messages))
		
		prompt = ''
		last_user = None
		
		for message in self.messages[-how_many_messages :]:
			if last_user != message.author.name:
				prompt += 'user ' + message.author.name + ' said :\n'
				last_user = message.author.name
			
			prompt += message.content + '\n'
		
		
		return prompt


manager = MessagesManager(500)


def cut_in_parts(message, part_size):
	split = message.split("\n")
	
	parts = []
	current_part = ""
	for sub in split:
		if len(sub) > part_size:
			parts.append(current_part)
			current_part = ""
			
			number = (len(sub)/part_size) + 1
			for i in number-1:
				parts.append( sub[i*part_size:(i+1)*part_size] )
				
			parts.append( sub[(number-1)*part_size:-1] )
		
		elif len(sub) + len(current_part) > part_size:
			parts.append(current_part)
			current_part = sub
		else:
			current_part += "\n" + sub
		
	parts.append("\n" + current_part)	

	return parts


# dd/mm/YY H:M:S
def get_current_time_str():
	return datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

async def send_message(message, channel):
	parts = cut_in_parts(message, 1970)
	
	for part in parts:
		await channel.send(part)
		time.sleep(1)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')

@bot.event
async def on_message(message):
	if message.channel.name != LISTEN_CHANNEL_NAME: #message.author == bot.user or 
		return

	if 'http://' in message.content or 'https://' in message.content:
		return

	manager.add_message(message)
	
	if manager.is_it_time_for_a_text_answer():
		manager.did_a_text_answer()
		
		
		print(get_current_time_str(), 'doing a text answer')
		
		prompt = manager.get_conversation_history_as_prompt(5)
		answer = gpt.get_discord_text_answer(prompt)

		await send_message(answer, message.channel)
		return
	
	if manager.is_it_time_for_a_meme_answer():
		manager.did_a_meme_answer()
		
		print(get_current_time_str(), 'doing a meme answer')
	
		prompt = manager.get_conversation_history_as_prompt(10)
		url = gpt.get_discord_image_answer(prompt)
		
		await send_message(url, message.channel)
		return

if __name__ == "__main__":
	bot.run(TOKEN)