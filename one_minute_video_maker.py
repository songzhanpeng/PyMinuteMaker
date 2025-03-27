#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Python一分钟视频制造机
自动生成一分钟长度的视频内容，指定使用的图片素材张数（默认6张）
"""

import os
import sys
import argparse
import time
from pathlib import Path
import random
from typing import List, Tuple, Dict, Optional

# 第三方库
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    VideoFileClip, ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips
)

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
        
        print(f"初始化一分钟视频制造机 - 目标时长: {target_duration}秒")
    
    def add_images(self, image_folder: str, num_images: int = 6):
        """
        从文件夹添加指定数量的图片幻灯片
        
        参数:
            image_folder: 图片文件夹路径
            num_images: 要使用的图片数量，默认为6张
        """
        image_files = []
        for ext in ['jpg', 'jpeg', 'png', 'gif']:
            image_files.extend(list(Path(image_folder).glob(f"*.{ext}")))
        
        if not image_files:
            print(f"警告: 在 {image_folder} 中没有找到图片文件")
            return
        
        # 排序图片文件
        image_files.sort()
        
        # 如果图片数量超过需要的数量，随机选择指定数量的图片
        if len(image_files) > num_images:
            print(f"在文件夹中找到 {len(image_files)} 张图片，将随机选择 {num_images} 张")
            image_files = random.sample(image_files, num_images)
        else:
            print(f"在文件夹中找到 {len(image_files)} 张图片，将全部使用")
        
        # 确定每张图片的时长
        duration_per_image = self.target_duration / len(image_files)
        
        print(f"每张图片时长: {duration_per_image:.2f}秒")
        
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
    
    def create_video(self):
        """生成最终视频"""
        if not self.clips:
            print("错误: 没有添加任何视频内容")
            return False
        
        print("开始生成视频...")
        
        # 合并所有视频片段
        final_clip = concatenate_videoclips(self.clips)
        
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
    parser.add_argument("--images", required=True, help="图片文件夹路径")
    parser.add_argument("--num-images", type=int, default=6, help="要使用的图片数量，默认为6张")
    parser.add_argument("--output", default="一分钟视频.mp4", help="输出视频文件路径")
    parser.add_argument("--duration", type=float, default=60.0, help="视频时长(秒)")
    parser.add_argument("--cleanup", action="store_true", help="完成后清理临时文件")
    
    args = parser.parse_args()
    
    # 创建视频制造机
    maker = OneMinuteVideoMaker(
        output_file=args.output,
        target_duration=args.duration
    )
    
    # 添加图片
    maker.add_images(args.images, args.num_images)
    
    # 生成视频
    success = maker.create_video()
    
    # 清理临时文件
    if args.cleanup and success:
        maker.cleanup()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 