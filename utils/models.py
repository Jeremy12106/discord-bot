from enum import Enum
from typing import Optional, List, Any
from pydantic import BaseModel, Field

class GPTAPI(str, Enum):
    gemini = 'gemini'
    github = 'github'

class Status(str, Enum):
    online = 'online'
    offline = 'offline'
    idle = 'idle'
    dnd = 'dnd'
    invisible = 'invisible'

class BotSettings(BaseModel):
    prefix: str
    status: Status = Field(default="online")
    activity: Optional[str] = Field(default=None)

class LLMSettings(BaseModel):
    gpt_api: GPTAPI
    model: str
    system_prompt: Optional[str] = Field(default="You are a helpful assistant.")
    personality: Optional[str] = Field(default=None)
    chat_memory: bool = Field(default=False)
    use_search_engine: bool = Field(default=False)

class MusicSettings(BaseModel):
    display_progress_bar: bool = Field(default=False)
    search_count: int = Field(default=10)
    time_limit: int = Field(default=1800)
    before_options: Optional[str] = Field(default=None)
    options: Optional[str] = Field(default=None)

class RadioStation(BaseModel):
    name: str
    url: str
    description: Optional[str] = Field(default=None)
    emoji: Optional[str] = Field(default=None)

class Config(BaseModel):
    bot: BotSettings
    llm: LLMSettings
    music: MusicSettings
    radio_stations: List[RadioStation]

    def get_station_by_name(self, target_name: str) -> Optional[RadioStation]:
        return next((s for s in self.radio_stations if s.name == target_name), None)

class VideoInfo(BaseModel):
    file_path: str
    title: str
    url: str
    duration: int
    video_id: str
    author: str
    views: int
    requester: Any
    user_avatar: Any