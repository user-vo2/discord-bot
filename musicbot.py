# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
from config import token

import youtube_dl
import os
import shutil

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
	print('Bot online!')

server, server_id, name_channel = None, None, None

domains = ['https://www.youtube.com/', 'http://www.youtube.com/', 'https://youtu.be/', 'http://youtu.be/']
async def check_domains(link):
	for x in domains:
		if link.startswith(x):
			return true
	return false

@bot.command()
async def play(ctx, *, command = None):
	"""Воспроизводит музыку с youtube по ссылке."""
	global server, server_id, name_channel
	author = ctx.author
	if command == None:
		server = ctx.guild
		name_channel = author.voice.channel.name
		voice_channel = discord.utils.get(server.voice_channels, name = name_channel)
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
	print ('voice is ok!')
	if source is None:
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
				shutil.copyfile(f'{file}', f'music/{file_copy}')
				os.rename(file, 'song.mp3')
		voice.play(discord.FFmpegPCMAudio('song.mp3'))
	else:
		for track in os.listdir('music/'):
			if track.endswith('mp3') and track.startswith(f'{source}'):
				voice.play(discord.FFmpegPCMAudio(f'music/{track}'))

@bot.command()
async def list(ctx):
	"""Выводит список сохраненных треков"""
	voice = discord.utils.get(bot.voice_clients, guild = server)
	i = 0
	for track in os.listdir('music/'):
		await ctx.channel.send(f'{track}')

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