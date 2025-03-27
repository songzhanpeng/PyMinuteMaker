#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Python一分钟视频制造机
自动生成一分钟长度的视频内容
"""

import os
import sys
import argparse
import time
from pathlib import Path
import random
import textwrap
from typing import List, Tuple, Dict, Optional

# 第三方库
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    VideoFileClip, AudioFileClip, ImageClip, 
    TextClip, CompositeVideoClip, concatenate_videoclips
)
import pyttsx3
from gtts import gTTS

class OneMinuteVideoMaker:
    """一分钟视频制造机主类"""
    
    def __init__(self, 
                 output_file: str = "output.mp4",
                 target_duration: float = 60.0,
                 resolution: Tuple[int, int] = (1080, 1920),
                 temp_dir: str = "temp"):
        """
        初始化视频制造机
        
        参数:
            output_file: 输出文件路径
            target_duration: 目标视频时长(秒)
            resolution: 视频分辨率 (宽, 高)
            temp_dir: 临时文件目录
        """
        self.output_file = output_file
        self.target_duration = target_duration
        self.resolution = resolution
        self.temp_dir = temp_dir
        
        # 创建临时目录
        os.makedirs(temp_dir, exist_ok=True)
        
        # 视频片段列表
        self.clips = []
        
        # 音频文件
        self.audio_file = None
        
        print(f"初始化一分钟视频制造机 - 目标时长: {target_duration}秒")
    
    def add_text_to_speech(self, text: str, output_audio: str = None) -> str:
        """
        将文本转换为语音
        
        参数:
            text: 要转换的文本
            output_audio: 输出音频文件路径
            
        返回:
            生成的音频文件路径
        """
        if output_audio is None:
            output_audio = os.path.join(self.temp_dir, "narration.mp3")
        
        try:
            # 使用Google TTS生成音频
            tts = gTTS(text=text, lang='zh-cn')
            tts.save(output_audio)
            print(f"成功生成语音文件: {output_audio}")
        except Exception as e:
            print(f"Google TTS失败，使用离线TTS引擎: {e}")
            # 备用: 使用离线TTS引擎
            engine = pyttsx3.init()
            engine.save_to_file(text, output_audio)
            engine.runAndWait()
        
        self.audio_file = output_audio
        return output_audio
    
    def add_images(self, image_folder: str, duration_per_image: float = None):
        """
        从文件夹添加图片幻灯片
        
        参数:
            image_folder: 图片文件夹路径
            duration_per_image: 每张图片显示时长(秒)，如不指定则根据图片数量和目标时长自动计算
        """
        image_files = []
        for ext in ['jpg', 'jpeg', 'png', 'gif']:
            image_files.extend(list(Path(image_folder).glob(f"*.{ext}")))
        
        if not image_files:
            print(f"警告: 在 {image_folder} 中没有找到图片文件")
            return
        
        # 排序图片文件
        image_files.sort()
        
        # 确定每张图片的时长
        if duration_per_image is None:
            duration_per_image = self.target_duration / len(image_files)
        
        print(f"添加 {len(image_files)} 张图片，每张图片时长: {duration_per_image:.2f}秒")
        
        # 创建视频片段
        for img_path in image_files:
            img_clip = ImageClip(str(img_path), duration=duration_per_image)
            img_clip = img_clip.resize(height=self.resolution[1])
            
            # 居中裁剪以适应分辨率
            if img_clip.w > self.resolution[0]:
                x_center = img_clip.w / 2
                x1 = max(0, x_center - self.resolution[0] / 2)
                img_clip = img_clip.crop(x1=x1, y1=0, 
                                         width=self.resolution[0], 
                                         height=self.resolution[1])
            
            # 应用简单的淡入淡出效果
            img_clip = img_clip.crossfadein(0.5).crossfadeout(0.5)
            
            self.clips.append(img_clip)
    
    def add_background_music(self, music_file: str, volume: float = 0.3):
        """
        添加背景音乐
        
        参数:
            music_file: 音乐文件路径
            volume: 音量大小 (0.0 - 1.0)
        """
        if not os.path.exists(music_file):
            print(f"警告: 音乐文件 {music_file} 不存在")
            return
        
        self.background_music = music_file
        self.background_volume = volume
        print(f"已添加背景音乐: {music_file}")
    
    def create_video(self):
        """生成最终视频"""
        if not self.clips:
            print("错误: 没有添加任何视频内容")
            return False
        
        print("开始生成视频...")
        
        # 合并所有视频片段
        final_clip = concatenate_videoclips(self.clips)
        
        # 添加音频
        audio_clips = []
        
        # 添加旁白音频（如果有）
        if self.audio_file and os.path.exists(self.audio_file):
            narration = AudioFileClip(self.audio_file)
            audio_clips.append(narration)
        
        # 添加背景音乐（如果有）
        if hasattr(self, 'background_music') and os.path.exists(self.background_music):
            music = AudioFileClip(self.background_music)
            
            # 循环音乐以匹配视频长度
            if music.duration < final_clip.duration:
                repeats = int(final_clip.duration / music.duration) + 1
                music = concatenate_videoclips([music] * repeats).subclip(0, final_clip.duration)
            else:
                music = music.subclip(0, final_clip.duration)
            
            # 设置音量
            music = music.volumex(self.background_volume)
            audio_clips.append(music)
        
        # 合并音频
        if audio_clips:
            if len(audio_clips) > 1:
                from moviepy.editor import CompositeAudioClip
                final_audio = CompositeAudioClip(audio_clips)
            else:
                final_audio = audio_clips[0]
            
            final_clip = final_clip.set_audio(final_audio)
        
        # 确保视频时长为一分钟
        if abs(final_clip.duration - self.target_duration) > 1.0:
            if final_clip.duration > self.target_duration:
                print(f"视频时长 ({final_clip.duration:.2f}秒) 超过目标时长，进行裁剪...")
                final_clip = final_clip.subclip(0, self.target_duration)
            else:
                print(f"视频时长 ({final_clip.duration:.2f}秒) 小于目标时长，进行循环...")
                repeat_times = int(self.target_duration / final_clip.duration) + 1
                final_clip = concatenate_videoclips([final_clip] * repeat_times).subclip(0, self.target_duration)
        
        # 写入文件
        print(f"正在写入视频到 {self.output_file}...")
        final_clip.write_videofile(
            self.output_file, 
            codec='libx264', 
            audio_codec='aac', 
            temp_audiofile=os.path.join(self.temp_dir, "temp_audio.m4a"),
            remove_temp=True,
            fps=30
        )
        
        print(f"视频生成完成: {self.output_file}")
        print(f"视频时长: {final_clip.duration:.2f}秒")
        return True
    
    def cleanup(self):
        """清理临时文件"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"已清理临时文件目录: {self.temp_dir}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Python一分钟视频制造机")
    parser.add_argument("--text", help="文本文件路径，用于生成旁白")
    parser.add_argument("--images", help="图片文件夹路径")
    parser.add_argument("--music", help="背景音乐文件路径")
    parser.add_argument("--output", default="一分钟视频.mp4", help="输出视频文件路径")
    parser.add_argument("--duration", type=float, default=60.0, help="视频时长(秒)")
    parser.add_argument("--cleanup", action="store_true", help="完成后清理临时文件")
    
    args = parser.parse_args()
    
    if not (args.text or args.images):
        parser.print_help()
        print("\n错误: 至少需要提供文本文件或图片文件夹")
        return 1
    
    # 创建视频制造机
    maker = OneMinuteVideoMaker(
        output_file=args.output,
        target_duration=args.duration
    )
    
    # 添加文本旁白
    if args.text and os.path.exists(args.text):
        with open(args.text, 'r', encoding='utf-8') as f:
            text_content = f.read()
        maker.add_text_to_speech(text_content)
    
    # 添加图片
    if args.images and os.path.exists(args.images):
        maker.add_images(args.images)
    
    # 添加背景音乐
    if args.music and os.path.exists(args.music):
        maker.add_background_music(args.music)
    
    # 生成视频
    success = maker.create_video()
    
    # 清理临时文件
    if args.cleanup and success:
        maker.cleanup()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 