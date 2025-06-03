from pydantic import BaseModel, Field
from dataclasses import dataclass
from typing import Optional, List


class BotSettings(BaseModel):
    prefix: str
    status: str = Field(default="online")
    activity: Optional[str] = Field(default=None)

class LLMSettings(BaseModel):
    gpt_api: str
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

class BotConfig(BaseModel):
    bot_config: BotSettings
    llm_config: LLMSettings

class MusicConfig(BaseModel):
    music_config: MusicSettings
    radio_stations: List[RadioStation]