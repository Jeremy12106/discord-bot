import os
import json
import discord
from discord.ext import commands
from discord import app_commands, FFmpegPCMAudio
from loguru import logger

from .common import extract_youtube_id
from .youtube import YouTubeManager
from .ui.controls import RadioControlView

from discord_bot import config

class Radio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_voice_client = None
        self.youtube = YouTubeManager()
        self.current_song = None
        self.current_message = None
        
        self.music_setting = config.music_config
        self.radio_stations = config.music_config.get("radio_station", None)
        logger.info(f"功能 {self.__class__.__name__} 初始化載入成功！")

    @app_commands.command(name="lofi", description="播放Lofi音樂電台")
    async def lofi(self, interaction: discord.Interaction):    
        try:
            if not interaction.user.voice:
                embed = discord.Embed(title="❌ | 請先加入語音頻道！", color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            channel = interaction.user.voice.channel
            if interaction.guild.voice_client is None:
                await channel.connect()

            embed = discord.Embed(title="🎵 | Lofi音樂電台", description="請選擇電台", color=discord.Color.blue())
            await interaction.response.send_message(embed=embed, view=RadioSelectView(self))

        except Exception as e:
            embed = discord.Embed(title="❌ | 連接語音頻道時發生錯誤", description=str(e), color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)


class RadioSelectView(discord.ui.View):
    def __init__(self, radio_cog, *, timeout=180):
        super().__init__(timeout=timeout)
        self.radio_cog = radio_cog
        self.music_setting = radio_cog.music_setting
        
        # Create options list from config
        options = []
        for station_name, station_info in radio_cog.radio_stations.items():
            options.append(
                discord.SelectOption(
                    label=station_name,
                    emoji=station_info['emoji'],
                    description=f"By {station_info['description']}"
                )
            )
        
        # Add the select menu with pre-defined options
        self.select = discord.ui.Select(
            placeholder="選擇",
            min_values=1,
            max_values=1,
            options=options
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=False)
            selected_station = self.radio_cog.radio_stations[self.select.values[0]]
            
            # Get stream URL and setup audio
            stream_url = await self.radio_cog.youtube.get_stream_audio(selected_station['url'], interaction)
            voice_client = interaction.guild.voice_client
            options = self.music_setting.get('options', '-ar 48000 -ac 2')
            before_options = self.music_setting.get('before_options', None)
            
            if voice_client.is_playing():
                voice_client.stop()
                
            voice_client.play(
                FFmpegPCMAudio(
                    stream_url,
                    before_options=before_options,
                    options=options
                )
            )
            logger.info(f"[LOFI] 伺服器 ID： {interaction.guild.id}, 使用者名稱： {interaction.user.name}, 播放 {self.select.values[0]}")
            
            # Update message with final state
            embed = discord.Embed(
                title=f"✅ | 已選擇電台：{selected_station['emoji']} {self.select.values[0]} By {selected_station['description']}",
                color=discord.Color.blue()
            )

            # Disable the view and clear it
            for item in self.children:
                item.disabled = True
            await interaction.edit_original_response(embed=embed, view=self)
            self.stop()

            # Send control view
            embed = discord.Embed(
                title="🎵 | 正在播放音樂",
                description=f"**[{self.select.values[0]}]({selected_station['url']})**",
                color=discord.Color.blue()
            )

            embed.add_field(name="上傳頻道", value=f"> {selected_station['description']}", inline=True)
            embed.add_field(name="播放時長", value=f"> 直播", inline=True)
            embed.add_field(name="觀看次數", value=f"> 直播", inline=True)
            embed.add_field(name="播放清單", value="> 清單為空", inline=False)

            thumbnail = self.radio_cog.youtube.get_thumbnail_url(extract_youtube_id(selected_station['url']))
            embed.set_thumbnail(url=thumbnail)
            embed.set_footer(text=interaction.user.name, icon_url=interaction.user.avatar.url)

            # Create and set current song info 
            self.radio_cog.current_song = {
                "title": self.select.values[0],
                "url": selected_station['url'],
                "duration": float('inf'),  # Live stream
                "thumbnail": thumbnail,
                "channel": selected_station['description']
            }

            # Create control view
            view = RadioControlView(interaction, self.radio_cog)
            # Set current embed for the view
            view.current_embed = embed
            
            # Send message and store reference
            message = await interaction.followup.send(embed=embed, view=view)
            view.message = message
            self.radio_cog.current_message = message
            
        except Exception as e:
            logger.error(f"Error during playback: {e}")
            embed = discord.Embed(title="❌ | 播放時發生錯誤", description=str(e), color=discord.Color.red())
            await interaction.followup.send(embed=embed, ephemeral=True)
