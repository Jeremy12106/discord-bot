import os
import yt_dlp
import discord
from pytubefix import YouTube
from youtube_search import YoutubeSearch
from loguru import logger

from utils.models import VideoInfo

class YouTubeManager:
    def __init__(self, time_limit=1800):  # 30分鐘限制
        self.time_limit = time_limit

    async def search_videos(self, query, max_results=10):
        """搜尋YouTube影片"""
        try:
            results = YoutubeSearch(query, max_results=max_results).to_dict()
            return results if results else []
        except Exception as e:
            logger.error(f"[音樂] YouTube搜尋失敗: {e}")
            return []

    async def extract_audio(self, url, interaction: discord.Interaction):
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'extract_flat': False
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            
            video_info = VideoInfo(
                file_path = info.get('url'),
                title = info.get('title'),
                url=url,
                duration = info.get('duration', None),
                video_id = info.get('id'),
                author = info.get('uploader'),
                views = info.get('view_count', None),
                requester=interaction.user,
                user_avatar=interaction.user.avatar.url if interaction.user.avatar else None
            )

            return video_info, None
        except Exception as e:
            logger.error(f"[音樂] 伺服器 ID: {interaction.guild.id}, 下載失敗: {e}")
            return None, "下載失敗"

    async def download_audio(self, url, folder, interaction: discord.Interaction):
        """下載YouTube影片的音訊"""
        try:
            yt = YouTube(url)
            
            # 檢查時長限制
            if yt.length > self.time_limit:
                logger.info(f"[音樂] 伺服器 ID: {interaction.guild.id}, 影片時間過長！")
                return None, "影片時間過長！超過 30 分鐘"

            audio_stream = yt.streams.get_audio_only()
            file_path = os.path.join(folder, f"{yt.video_id}.mp4")

            # 避免重複下載
            if not os.path.exists(file_path):
                audio_stream.download(output_path=folder, filename=f"{yt.video_id}.mp4")

            # 返回影片資訊
            video_info = VideoInfo(
                file_path=file_path,
                title=yt.title,
                url=url,
                duration=yt.length,
                video_id=yt.video_id,
                author=yt.author,
                views=yt.views,
                requester=interaction.user,
                user_avatar=interaction.user.avatar.url if interaction.user.avatar else None
            )
            
            return video_info, None

        except Exception as e:
            logger.error(f"[音樂] 伺服器 ID: {interaction.guild.id}, 下載失敗: {e}")
            return None, "下載失敗"

    def get_thumbnail_url(self, video_id):
        """獲取影片縮圖URL"""
        return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    
    async def get_stream_audio(self, url, interaction: discord.Interaction):
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'extract_flat': False
        }
        url = str(url).strip()
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info['url'] if 'url' in info else None
        except Exception as e:
            logger.error(f"[音樂] 伺服器 ID: {interaction.guild.id}, 獲取音訊串流URL失敗: {e}")
            return None


    # async def download_audio(self, url, folder, interaction):
    #     """下載YouTube影片的音訊"""
    #     file_path = os.path.join(folder, '%(id)s.%(ext)s')
    #     ydl_opts = {
    #         'format': 'bestaudio/best',
    #         'outtmpl': file_path,
    #         'noplaylist': True,
    #         'quiet': False,
    #         'geo_bypass': False,
    #         'extractaudio': True,
    #         'postprocessors': [{
    #             'key': 'FFmpegExtractAudio',
    #             'preferredcodec': 'mp3',
    #             'preferredquality': '192',
    #         }],
    #         'concurrent_fragment_downloads': 3,
    #     }
    #     try:
    #         # 取得影片資訊
    #         with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
    #             video_info = ydl.extract_info(url, download=False)
            
    #         # 檢查時長限制
    #         video_duration = video_info['duration']
    #         if video_duration > self.time_limit:
    #             logger.info(f"[音樂] 伺服器 ID: {interaction.guild.id}, 影片時間過長！")
    #             return None, "影片時間過長！超過 30 分鐘"

    #         # 避免重複下載
    #         file_path = os.path.join(folder, f"{video_info['id']}.mp3")
    #         if not os.path.exists(file_path):
    #             with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    #                 ydl.download([url])

    #         # 返回影片資訊
    #         video_info = {
    #             "file_path": file_path,
    #             "title": video_info['title'],
    #             "url": url,
    #             "duration": video_info['duration'],
    #             "video_id": video_info['id'],
    #             "author": video_info['uploader'],
    #             "views": video_info['view_count'],
    #             "requester": interaction.user,
    #             "user_avatar": interaction.user.avatar.url
    #         }
            
    #         return video_info, None

    #     except Exception as e:
    #         logger.error(f"[音樂] 伺服器 ID: {interaction.guild.id}, 下載失敗: {e}")
    #         return None, "下載失敗"