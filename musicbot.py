# -*- coding: utf-8 -*-
import time
import youtube_dl
import os
import shutil
import discord
from discord.ext import commands
from config import token
from queue import Queue
from colorama import init

init()

ffmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

ydl_opts = {'format': 'bestaudio/best'}

MAX_LEN = 2000
current_playlist = Queue()
current_playlist_titles = Queue()
track = ''

bot = commands.Bot(command_prefix='!', case_insensitive=True)

server, server_id, name_channel = None, None, None

badwords = ['nigger']

domains = ['https://www.youtube.com/', 'http://www.youtube.com/', 'https://youtu.be/', 'http://youtu.be/']

@bot.event
async def on_message(message):
	author = message.author
	for i in badwords:  # Go through the list of bad words;
		if i in message.content:
			await message.delete()
			bot.dispatch('prof', message, i)
			return  # So that it doesn't try to delete the message again, which will cause an error.
	if '!stop' in message.content or '!skip' in message.content or '!song' in message.content or '!pause' in message.content or '!resume' in message.content:
		await message.delete()
		print('deleted')
	await bot.process_commands(message)

@bot.event
async def on_prof(ctx, word, *, command=None):
	embed = discord.Embed(title="Profanity Alert!",description=f"{ctx.author.name} just said ||{word}||", color=discord.Color.blurple()) # Let's make an embed!
	await ctx.channel.send(embed=embed)


@bot.event
async def on_ready():
	print('Bot online!')
	global server, server_id, name_channel
	print(server)
	print(server_id)
	print(name_channel)

def next(ctx):
	global track, current_playlist_titles, current_playlist
	voice = discord.utils.get(bot.voice_clients, guild=server)
	time.sleep(1)
	if not voice is None and not voice.is_playing() and not current_playlist.empty():
		source = current_playlist.get()
		track = current_playlist_titles.get()

		try:
			voice.play(source, after=lambda e: next(ctx))
		except discord.ClientException:
			print('voice is already playing')
			voice.stop()
			voice.play(source, after=lambda e: next(ctx))
			return
	if current_playlist.empty():
		print('playlist is empty')


async def check_domains(link):
	for x in domains:
		if link.startswith(x):
			return True
	return False

@bot.command()
async def stream(ctx, *, command = None):
	"""Воспроизводит трек или плейлист с youtube по ссылке. Загрузка не производится."""
	global server, server_id, name_channel, current_playlist, current_playlist_titles, track
	author = ctx.author
	if command is None:
		await ctx.channel.send(f'{author.mention}, команда некорректна!')
		return
	params = command.split(' ')
	ffmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

	ydl_opts = {'format': 'bestaudio/best'}

	server = ctx.guild
	voice = discord.utils.get(bot.voice_clients, guild=server)
	voice_channel = discord.utils.get(server.voice_channels, id=616285165328662601)

	if voice is None:
		await voice_channel.connect()
	voice = discord.utils.get(bot.voice_clients, guild=server)

	url = params[0]

	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		info = ydl.extract_info(url, download=False)
		
		if 'entries' in info:
			playlist_title_info = info['entries'][0]['playlist_title']
			msg = f'Плейлист \"{playlist_title_info}\" загружен. В этом плейлисте присутствуют треки:\n'
			msg_old = msg
			counter = 1
			for video in info['entries']:
				track_item = video['title']
				msg_old = msg
				msg += f'{counter}.\"{track_item}\"\n'
				if len(msg) > MAX_LEN:
					await ctx.channel.send(msg_old)
					msg = f'{counter}.\"{track_item}\"\n'
				counter += 1
			if voice is None:
				await voice_channel.connect()
			voice = discord.utils.get(bot.voice_clients, guild=server)

			await ctx.channel.send(msg)
			for video in info['entries']:
				i_url = video['formats'][0]['url']
				current_playlist_titles.put(video['title'])
				source = await discord.FFmpegOpusAudio.from_probe(i_url, **ffmpeg_opts)
				current_playlist.put(source)
				print(video['title'])
				if voice is None:
					await voice_channel.connect()
				voice = discord.utils.get(bot.voice_clients, guild=server)				
				if not voice.is_playing():
					track = current_playlist_titles.get()
					time.sleep(1)
					voice.play(current_playlist.get(), after=lambda e: next(ctx))
		else:
			title_info = info['title']
			await ctx.channel.send(f'Трек \"{title_info}\" загружен.')
			i_url = info['formats'][0]['url']
			source = await discord.FFmpegOpusAudio.from_probe(i_url, **ffmpeg_opts)
			current_playlist.put(source)
			current_playlist_titles.put(title_info)
			if not voice.is_playing():
				track = current_playlist_titles.get()
				time.sleep(1)
				voice.play(current_playlist.get(), after=lambda e: next(ctx))

@bot.command()
async def skip(ctx):
	'''Пропускает текущий трек.'''
	voice = discord.utils.get(bot.voice_clients, guild=server)
	if voice.is_playing():
		voice.stop()

@bot.command()
async def song(ctx):
	'''Выводит название текущего трека.'''
	global track
	voice = discord.utils.get(bot.voice_clients, guild=server)
	if voice.is_playing():
		await ctx.channel.send(f'Сейчас играет \"{track}\"')
	else:
		await ctx.channel.send(f'Сейчас играет... А ничего сейчас и не играет=(')

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
			voice_id = int(voice_id)
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
		await ctx.channel.send(f'{ctx.author.mention}, бот уже не сидит в войсе.')

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
	global current_playlist, current_playlist_titles
	voice = discord.utils.get(bot.voice_clients, guild=server)
	current_playlist = Queue()
	current_playlist_titles = Queue()
	voice.stop()

bot.run(token)