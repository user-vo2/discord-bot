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

'''
	Commands !play and !showlist were never updated since first commit
	and may not work properly
'''

ffmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

ydl_opts = {'format': 'bestaudio/best'}

MAX_LEN = 2000
current_playlist = Queue()
current_playlist_titles = Queue()
track = ''

bot = commands.Bot(command_prefix='!', case_insensitive=True)

server, server_id, name_channel = None, None, None

domains = ['https://www.youtube.com/', 'http://www.youtube.com/', 'https://youtu.be/', 'http://youtu.be/']

removable_commands = ['!stop', '!skip', '!song', '!quit']

@bot.event
async def on_message(message):
	author = message.author
	for current_command in removable_commands:
		if current_command in message.content: 
			await message.delete()
			print('message deleted')
	await bot.process_commands(message)


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

	server = ctx.guild
	name_channel = author.voice.channel.name
	voice_channel = discord.utils.get(server.voice_channels, name = name_channel)
	voice = discord.utils.get(bot.voice_clients, guild = server)

	if voice is None:
		await voice_channel.connect()
	voice = discord.utils.get(bot.voice_clients, guild=server)

	url = params[0]

	standart_ydl_opts = {
		'format': 'bestaudio/best',
		'playlist_items': '1',
		'age_limit': '23',
		'ignore_errors': True,
	}
	playlist_ydl_opts = standart_ydl_opts
	info = youtube_dl.YoutubeDL(standart_ydl_opts).extract_info(url, download = False)

	if info['webpage_url_basename'] == 'playlist':
		print('it\'s whole playlist!')
		i = 1
		while not len(info['entries']) == 0:
			print(info['entries'][0]['title'])
			
			title_info = info['entries'][0]['title']
			i_url = info['entries'][0]['formats'][0]['url']
			source = await discord.FFmpegOpusAudio.from_probe(i_url, **ffmpeg_opts)
			current_playlist.put(source)
			current_playlist_titles.put(title_info)
			if not voice.is_playing() and not voice.is_paused():
				track = current_playlist_titles.get()
				voice.play(current_playlist.get(), after=lambda e: next(ctx))
			i += 1
			playlist_ydl_opts['playlist_items'] = str(i)
			try:
				info = youtube_dl.YoutubeDL(playlist_ydl_opts).extract_info(url, download = False)
			except youtube_dl.utils.DownloadError:
				i += 1
				continue
	else:
		print('it\'s just one video')
		title_info = info['title']
		i_url = info['formats'][0]['url']
		source = await discord.FFmpegOpusAudio.from_probe(i_url, **ffmpeg_opts)
		current_playlist.put(source)
		current_playlist_titles.put(title_info)
		if not voice.is_playing() and not voice.is_paused():
			track = current_playlist_titles.get()
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
		await stop(ctx)
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
		await ctx.channel.send(f'{ctx.author.mention}, трек не загружен или музыка уже играет.')

@bot.command()
async def stop(ctx):
	"""Останавливает воспроизведение музыки."""
	global current_playlist, current_playlist_titles, track
	voice = discord.utils.get(bot.voice_clients, guild=server)
	current_playlist = Queue()
	current_playlist_titles = Queue()
	track = ''
	voice.stop()

@bot.command()
async def quit(ctx):
	"""Выключает бота"""
	await ctx.channel.send('Отключаюсь, мой господин.')
	exit(0)

bot.run(token)