# ============================================================
# ISP(인터페이스 분리 원칙) 위반 사례 - 리팩토링 전
# 하나의 거대한 인터페이스(MultimediaPlayer)가 모든 미디어 기능을 포함
# 구현 클래스가 자신과 무관한 메서드까지 강제로 구현해야 하는 문제
# ============================================================

from abc import ABC, abstractmethod


# ISP 위반: 재생, 정지, 가사 표시, 비디오 필터까지 모든 기능을 하나의 인터페이스에 포함
# 이 인터페이스를 구현하는 클래스는 불필요한 메서드도 반드시 구현해야 하는 부담
class MultimediaPlayer(ABC):
    @abstractmethod
    def play_media(self, file: str) -> None:
        pass

    @abstractmethod
    def stop_media(self) -> None:
        pass

    @abstractmethod
    def display_lyrics(self, file: str) -> None:
        pass

    @abstractmethod
    def apply_video_filter(self, filter: str) -> None:
        pass


# MusicPlayer: 음악 관련 기능만 필요하지만 비디오 필터까지 구현 강제
class MusicPlayer(MultimediaPlayer):
    def play_media(self, file: str) -> None:
        # 음악 재생 구현
        print(f"음악 재생 중: {file}")

    def stop_media(self) -> None:
        # 음악 중지 구현
        print("음악 중지 중")

    def display_lyrics(self, file: str) -> None:
        # 가사 표시 구현
        print(f"{file}의 가사 표시 중")

    # ISP 위반의 전형적 증상: 사용하지 않는 메서드를 억지로 구현
    # NotImplementedError를 던지는 것 자체가 설계 결함의 신호
    def apply_video_filter(self, filter: str) -> None:
        # MusicPlayer에 대해 이 메서드는 의미가 없음
        raise NotImplementedError(
            "MusicPlayer가 지원하지 않는 비디오 필터")


class VideoPlayer(MultimediaPlayer):
    # 비디오 플레이어 구현
    ...
