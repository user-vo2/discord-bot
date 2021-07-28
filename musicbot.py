# -*- coding: utf-8 -*-
import time
import asyncio
import youtube_dl
import os
import shutil
import discord
from discord.ext import commands
from config import token
from queue import Queue

queue_size = 0

num_stream = 0

ffmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

ydl_opts = {'format': 'bestaudio/best'}

current_playlist = Queue()

bot = commands.Bot(command_prefix='!', case_insensitive=True)

server, server_id, name_channel = None, None, None

badwords = ['nigger']

domains = ['https://www.youtube.com/', 'http://www.youtube.com/', 'https://youtu.be/', 'http://youtu.be/']

@bot.event
async def on_message(message):
	print('processing1')
	author = message.author
	#await message.channel.send(f"{message.author.mention}, done!")
	'''for i in domains:
		if i in message.content:
			#await message.delete()
			global server, server_id, name_channel
			print(message)
			#if command is None:
			#	await message.channel.send(f'{author.mention}, команда некорректна!')
			#	return
			params = message.content.split(' ')

			server = message.guild
			name_channel = author.voice.channel.name
			voice_channel = discord.utils.get(server.voice_channels, name = name_channel)
			voice = discord.utils.get(bot.voice_clients, guild = server)

			if voice is None:
				await voice_channel.connect()
				voice = discord.utils.get(bot.voice_clients, guild = server)

			voice = discord.utils.get(bot.voice_clients, guild = server)

			url = params[1]

			with youtube_dl.YoutubeDL(ydl_opts) as ydl:
				info = ydl.extract_info(url, download=False)
				i_url = info['formats'][0]['url']
				dur = info['duration']
				print(dur)
				source = await discord.FFmpegOpusAudio.from_probe(i_url, **ffmpeg_opts)
				if voice.is_playing():
					current_playlist.put(source)
					return

			current_playlist.put(source)
			print(voice.is_playing())
			if not voice.is_playing() and not current_playlist.empty():
				await bot.process_commands(message)
				print('ended')
			return'''
	for i in badwords: # Go through the list of bad words;
		if i in message.content:
			await message.delete()
			await message.channel.send(f"{message.author.mention}, материться можно только на русском!")
			bot.dispatch('prof', message, i)
			return # So that it doesn't try to delete the message again, which will cause an error.
	if '!stop' in message.content:
		await message.delete()
		#await message.channel.send('')
		await bot.process_commands(message)
		return
	#if not author == bot.user:
	#	await message.channel.send(f'{message.author.mention}, некорректный домен.')
	await bot.process_commands(message)

@bot.event
async def on_prof(ctx, word, *, command=None):
	print('processing2')
	#channel = bot.get_channel(message.channel) # for me it's bot.get_channel(817421787289485322)
	embed = discord.Embed(title="Profanity Alert!",description=f"{ctx.author.name} just said ||{word}||", color=discord.Color.blurple()) # Let's make an embed!
	#print(channel)
	await ctx.channel.send(embed=embed)


@bot.event
async def on_ready():
	print('Bot online!')
	global server, server_id, name_channel
	print(server)
	print(server_id)
	print(name_channel)
	time.sleep(1)
	voice = discord.utils.get(bot.voice_clients, guild = server)
	if not voice is None and not voice.is_playing() and not current_playlist.empty():
		await bot.process_commands(current_playlist.get())
		print('ended')

def next(ctx, parent_idx):
	print('next started')
	print(f'next : {os.getpid()}')
	global queue_size, num_stream
	voice = discord.utils.get(bot.voice_clients, guild = server)
	print(voice)
	print(voice.is_playing())
	print(current_playlist.qsize())
	print(f'parent_idx = {parent_idx}, num_stream = {num_stream}')
	'''if not parent_idx == num_stream:
		print('side process')
		return'''
	time.sleep(1)
	print(1)
	print(2)
	queue_size = current_playlist.qsize()
	print(3)
	print(voice)
	print(voice.is_playing())
	print(current_playlist.qsize())
	if not voice is None and not voice.is_playing() and not current_playlist.empty():
		print(4)
		source = current_playlist.get()
		print(source)
		num_stream += 1
		print(5)
		try:
			voice.play(source, after = lambda e : next(ctx, parent_idx + 1))#
		except discord.ClientException:
			print('Audio is already playing!')
			voice.stop()
			voice.play(source, after = lambda e : next(ctx, parent_idx + 1))
		print(6)
		return

	print('next finished with error')

async def check_domains(link):
	for x in domains:
		if link.startswith(x):
			return True
	return False

@bot.command()
async def stream(ctx, *, command = None):
	"""Воспроизводит трек с youtube по ссылке. Загрузка не производится."""
	print(f'stream : {os.getpid()}')
	global server, server_id, name_channel, queue_size, num_stream
	author = ctx.author
	if command is None:
		await ctx.channel.send(f'{author.mention}, команда некорректна!')
		return
	params = command.split(' ')
	ffmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

	ydl_opts = {'format': 'bestaudio/best'}

	server = ctx.guild
	name_channel = author.voice.channel.name
	voice_channel = discord.utils.get(server.voice_channels, name = name_channel)
	voice = discord.utils.get(bot.voice_clients, guild = server)

	if voice is None:
		await voice_channel.connect()
		voice = discord.utils.get(bot.voice_clients, guild = server)
	voice = discord.utils.get(bot.voice_clients, guild = server)
	
	#voice.stop()
	url = params[0]

	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		info = ydl.extract_info(url, download=False)
		#print(info)
		i_url = info['formats'][0]['url']
		dur = info['duration']
		#print(dur)
		source = await discord.FFmpegOpusAudio.from_probe(i_url, **ffmpeg_opts)
		if voice.is_playing():
			current_playlist.put(source)
			queue_size = current_playlist.qsize()
			num_stream += 1
			return
		
		voice.play(source, after = lambda e : next(ctx, num_stream))

'''
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		result = ydl.extract_info(url, download=False)


	if 'entries' in result:
		# Can be a playlist or a list of videos
		video = result['entries'][0]
	else:
		# Just a video
		video = result

	print(video)
	video_url = video['url']
	print(video_url)
'''
@bot.command()
async def play(ctx, *, command = None):
	"""Воспроизводит трек с youtube по ссылке. Загрузка производится."""

	global server, server_id, name_channel
	author = ctx.author
	if command is None:
		server = ctx.guild
		name_channel = author.voice.channel.name
		voice_channel = discord.utils.get(server.voice_channels, name = name_channel)
		voice = discord.utils.get(bot.voice_clients, guild = server)
		if voice is None:
			await voice_channel.connect()
			voice = discord.utils.get(bot.voice_clients, guild = server)
		voice.play(discord.FFmpegPCMAudio('song.mp3'))
		return
	params = command.split(' ')
	if len(params) == 1:
		source = params[0]
		server = ctx.guild
		name_channel = author.voice.channel.name
		voice_channel = discord.utils.get(server.voice_channels, name = name_channel)
		print('param 1')
	elif len(params) == 3:
		server_id = params[0]
		voice_id = params[1]
		source = params[2]
		try:
			server_id = int(server_id)
			voice_id = int(voise_id)
		except:
			await ctx.channel.send(f'{author.mention}, id сервера или войса должно быть целочисленно!')	
			return
		print('param 3')
		server = bot.get_guild(server_id)
		voice_channel = discord.utils.get(server.voice_channels, id = voice_id)
	else:
		await ctx.channel.send(f'{author.mention}, команда некорректна!')
		return

	voice = discord.utils.get(bot.voice_clients, guild = server)

	if voice is None:
		await voice_channel.connect()
		voice = discord.utils.get(bot.voice_clients, guild = server)

	if source is None:
		if voice.is_playing():
			voice.stop()
		voice.play(discord.FFmpegPCMAudio('song.mp3'))

	elif source.startswith('http'):
		if not check_domains(source):
			await ctx.channel.send(f'{author.mention} ссылка запрещена')
			return

		song_there = os.path.isfile('song.mp3')

		try:
			if song_there:
				os.remove('song.mp3')

		except PermissionError:
			await ctx.channel.send('Недостаточно прав для удаления')
			return

		ydl_opts = {
			'format': 'bestaudio/best',
			'postprocessors': [
				{
					'key': 'FFmpegExtractAudio',
					'preferredcodec': 'mp3',
					'preferredquality': '192',
				}
			],
		}	

		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			ydl.download([source])
		for file in os.listdir('./'):
			if file.endswith('.mp3'):
				file_copy = file
				file_copy = ''.join(file_copy.split())
				print(f'{file_copy}')
				shutil.copyfile(f'{file}', f'playlists/music/{file_copy}')
				os.rename(file, 'song.mp3')
		if voice.is_playing():
			voice.stop()
		voice.play(discord.FFmpegPCMAudio('song.mp3'))
	else:
		for track in os.listdir('playlists/music/'):
			if track.endswith('mp3') and track.startswith(f'{source}'):
				if voice.is_playing():
					voice.stop()
				voice.play(discord.FFmpegPCMAudio(f'playlists/music/{track}'))
				return

@bot.command()
async def showlist(ctx, *, command = None):
	"""Выводит список сохраненных треков"""
	if command is None:
		for track in os.listdir('playlists/music/'):
			await ctx.channel.send(f'{track}')
		return
	params = command.split(' ')
	if len(params) == 1:
		source = params[0]
		for playlist in os.listdir('playlists/'):
			if playlist.startswith(f'{source}'):
				for track in os.listdir(f'playlists/{playlist}'):
					if track.endswith('.mp3'):
						await ctx.channel.send(f'{track}')
	else:
		await ctx.channel.send(f'{ctx.author}, команда некорректна.')

@bot.command()
async def leave(ctx):
	"""Выгоняет бота из войса."""
	global server, name_channel
	voice = discord.utils.get(bot.voice_clients, guild = server)
	if voice.is_connected():
		await voice.disconnect()
	else:
		await ctx.channel.send(f'{ctx.author.mention}, бот уже не сидит в войсе, лол')

@bot.command()
async def pause(ctx):
	"""Ставит музыку на паузу."""
	voice = discord.utils.get(bot.voice_clients, guild = server)
	if voice.is_playing():
		voice.pause()
	else:
		await ctx.channel.send(f'{ctx.author.mention}, музыка не воспроизводится.')

@bot.command()
async def resume(ctx):
	"""Продолжает воспроизведение музыки."""
	voice = discord.utils.get(bot.voice_clients, guild = server)
	if voice.is_paused():
		voice.resume()
	else:
		await ctx.channel.send(f'{ctx.author.mention}, Трек не загружен или музыка уже играет.')

@bot.command()
async def stop(ctx):
	"""Останавливает воспроизведение музыки."""
	voice = discord.utils.get(bot.voice_clients, guild = server)
	voice.stop()

bot.run(token)