import logging
import os
import re
import threading
import uuid
import wave
from datetime import datetime

import pyaudio

logger = logging.getLogger('logger')


class AudioService:
    def __init__(self, channels: int = 2, rate: int = 44100, frames_per_buffer: int = 1024) -> None:
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self.is_recording = False
        self.is_paused = False
        self.frames = []
        self.stream = None
        self.audio = pyaudio.PyAudio()
        self.lock = threading.Lock()
        self.filename = None

    def _start_stream(self) -> None:
        device_index = self.find_device_index(r'立体声混音')
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=self.frames_per_buffer,
        )

    def find_device_index(self, pattern: str) -> int:
        numdevices = self.audio.get_device_count()
        index = None
        for i in range(0, numdevices):
            devinfo = self.audio.get_device_info_by_index(i)
            if re.search(pattern, devinfo.get('name')):
                logger.info(f"Found matching device: {devinfo.get('name')} at index {i}")
                index = i
                break
        return index

    def start_recording(self) -> None:
        with self.lock:
            if self.is_recording:
                logger.info('Recording is already in progress.')
                return
            self.is_recording = True
            self.is_paused = False
            self.frames = []
            self._start_stream()
            self.recording_thread = threading.Thread(target=self._record)
            self.recording_thread.start()

    def _record(self) -> None:
        while self.is_recording:
            if not self.is_paused:
                try:
                    # 读取流数据并添加到 frames 中，确保不丢帧
                    data = self.stream.read(self.frames_per_buffer, exception_on_overflow=False)
                    self.frames.append(data)
                except Exception as e:
                    logger.error(f'Error while recording: {e}', exc_info=True)

    def pause_recording(self) -> None:
        with self.lock:
            if self.is_recording and not self.is_paused:
                self.is_paused = True

    def resume_recording(self) -> None:
        with self.lock:
            if self.is_recording and self.is_paused:
                self.is_paused = False

    def stop_recording(self, seat: str, customer: str, format: str = 'wav') -> str:
        with self.lock:
            if not self.is_recording:
                logger.error('No active recording to stop.')
                return ''

            self.is_recording = False
            self.is_paused = False

            if self.stream is not None:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None

            # 生成保存文件的路径
            self.filename = self._generate_filepath(seat, customer, format)
            self._save_recording(self.filename)
            return self.filename

    @staticmethod
    def _generate_filepath(seat: str, customer: str, format: str) -> str:
        # 获取当前日期并创建 recordings 文件夹
        current_date = datetime.now().strftime('%Y-%m-%d')
        directory = os.path.join(os.getcwd(), 'recordings', current_date)

        # 如果 recordings 目录或当天的目录不存在，则创建
        if not os.path.exists(directory):
            os.makedirs(directory)

        # 生成随机的 32 位 UUID
        random_uuid = uuid.uuid4().hex
        filename = f'{seat}_{customer}_{random_uuid}.{format}'

        # 返回完整路径
        return os.path.join(directory, filename)

    def _save_recording(self, filepath: str) -> None:
        wf = wave.open(filepath, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def terminate(self) -> None:
        self.audio.terminate()
