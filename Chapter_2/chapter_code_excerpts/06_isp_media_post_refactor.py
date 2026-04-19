# ============================================================
# ISP(인터페이스 분리 원칙) 적용 후 - 리팩토링 완료
# 하나의 거대한 인터페이스를 역할별로 분리하여 각 클래스가
# 필요한 인터페이스만 선택적으로 구현하는 구조
# ============================================================

from abc import ABC, abstractmethod


# 미디어 재생/정지 기능만 담당하는 인터페이스 (모든 플레이어 공통)
class MediaPlayable(ABC):
    @abstractmethod
    def play_media(self, file: str) -> None:
        pass

    @abstractmethod
    def stop_media(self) -> None:
        pass


# 가사 표시 기능만 담당하는 인터페이스 (음악 플레이어 전용)
class LyricsDisplayable(ABC):
    @abstractmethod
    def display_lyrics(self, file: str) -> None:
        pass


# 비디오 필터 기능만 담당하는 인터페이스 (비디오 플레이어 전용)
class VideoFilterable(ABC):
    @abstractmethod
    def apply_video_filter(self, filter: str) -> None:
        pass


# MusicPlayer: 재생 + 가사 표시 인터페이스만 구현 (비디오 필터 불필요)
class MusicPlayer(MediaPlayable, LyricsDisplayable):
    def play_media(self, file: str) -> None:
        print(f"음악 재생 중: {file}")

    def stop_media(self) -> None:
        print("음악 중지 중")

    def display_lyrics(self, file: str) -> None:
        print(f"가사 표시 중: {file}")


# VideoPlayer: 재생 + 비디오 필터 인터페이스만 구현 (가사 표시 불필요)
class VideoPlayer(MediaPlayable, VideoFilterable):
    def play_media(self, file: str) -> None:
        print(f"동영상 재생 중: {file}")

    def stop_media(self) -> None:
        print("동영상 중지 중")

    def apply_video_filter(self, filter: str) -> None:
        print(f"비디오 필터 적용: {filter}")


# BasicAudioPlayer: 재생 기능만 필요하므로 MediaPlayable만 구현
# ISP 덕분에 불필요한 가사 표시나 비디오 필터를 구현할 필요 없음
class BasicAudioPlayer(MediaPlayable):
    def play_media(self, file: str) -> None:
        print(f"오디오 재생 중: {file}")

    def stop_media(self) -> None:
        print("오디오 중지 중")
