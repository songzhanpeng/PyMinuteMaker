#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图片单词生成器
将文件夹中的图片作为背景，在图片中央添加英语单词和中文释义
"""

import os
import sys
import argparse
import platform
import random
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Union

# 第三方库
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps

class ImageWordGenerator:
    """图片单词生成器主类"""
    
    def __init__(self, 
                 images_folder: str,
                 output_folder: str = "output_images",
                 font_size_en: int = 80,  # 进一步降低默认英文字体大小
                 font_size_cn: int = 55,   # 进一步降低默认中文字体大小
                 font_size_phonetic: int = None,
                 font_path_en: str = None,
                 font_path_cn: str = None,
                 theme: str = "standard",
                 device_mode: str = "mobile",
                 bg_style: str = "rectangle"):  # 新增背景样式参数
        """
        初始化图片单词生成器
        
        参数:
            images_folder: 背景图片文件夹路径
            output_folder: 输出图片文件夹路径
            font_size_en: 英文字体大小
            font_size_cn: 中文字体大小
            font_size_phonetic: 音标字体大小，不指定则默认为英文字体大小的35%
            font_path_en: 英文字体路径，不指定则使用系统字体
            font_path_cn: 中文字体路径，不指定则使用系统字体
            theme: 主题风格，可选 "standard"(标准), "focus"(专注), "elegant"(优雅), "dark"(暗黑), "minimal"(极简)
            device_mode: 设备模式，可选 "auto"(自动), "mobile"(手机), "tablet"(平板), "desktop"(桌面)
            bg_style: 背景样式，可选 "rectangle"(矩形), "wave"(海浪形状)
        """
        self.images_folder = images_folder
        self.output_folder = output_folder
        self.font_size_en = font_size_en
        self.font_size_cn = font_size_cn
        self.font_size_phonetic = font_size_phonetic if font_size_phonetic is not None else int(font_size_en * 0.35)  # 更小的音标字体比例
        self.font_path_en = font_path_en
        self.font_path_cn = font_path_cn
        self.theme = theme
        self.device_mode = device_mode
        self.bg_style = bg_style
        
        # 设备模式配置
        self.device_configs = {
            "auto": {
                "keep_original": True,
                "target_width": None,
                "target_height": None,
                "aspect_ratio": None
            },
            "mobile": {
                "keep_original": False,
                "target_width": 1080,
                "target_height": 1920,
                "aspect_ratio": 9/16,  # 适合大多数手机屏幕的比例
                "font_size_multiplier": 1.2  # 手机上字体需要略大
            },
            "tablet": {
                "keep_original": False,
                "target_width": 1536,
                "target_height": 2048,
                "aspect_ratio": 3/4,  # 平板比例
                "font_size_multiplier": 1.1
            },
            "desktop": {
                "keep_original": False,
                "target_width": 1920,
                "target_height": 1080,
                "aspect_ratio": 16/9,  # 桌面宽屏比例
                "font_size_multiplier": 1.0
            }
        }
        
        # 获取设备配置
        self.device_config = self.device_configs.get(device_mode, self.device_configs["auto"])
        
        # 根据设备模式调整字体大小
        if device_mode != "auto" and "font_size_multiplier" in self.device_config:
            self.font_size_en = int(self.font_size_en * self.device_config["font_size_multiplier"])
            self.font_size_cn = int(self.font_size_cn * self.device_config["font_size_multiplier"])
            self.font_size_phonetic = int(self.font_size_phonetic * self.device_config["font_size_multiplier"])
        
        # 主题配置
        self.theme_configs = {
            "standard": {
                "blur_radius": 0,
                "brightness": 1.0,
                "bg_opacity": 128,
                "text_color": (255, 255, 255, 255),
                "bg_color": (0, 0, 0, 128),
                "shadow_offset": 2,
                "shadow_color": (0, 0, 0, 255),
                "decoration": True,
                "rounded_bg": False,
                "gradient_bg": False
            },
            "focus": {
                "blur_radius": 8,
                "brightness": 0.6,
                "bg_opacity": 160,
                "text_color": (255, 255, 255, 255),
                "bg_color": (20, 20, 20, 160),
                "shadow_offset": 3,
                "shadow_color": (0, 0, 0, 200),
                "decoration": True,
                "rounded_bg": True,
                "gradient_bg": False
            },
            "elegant": {
                "blur_radius": 5,
                "brightness": 0.85,
                "bg_opacity": 120,
                "text_color": (255, 255, 255, 255),
                "bg_color": (40, 40, 40, 120),
                "shadow_offset": 2,
                "shadow_color": (0, 0, 0, 180),
                "decoration": True,
                "rounded_bg": True,
                "gradient_bg": True
            },
            "dark": {
                "blur_radius": 3,
                "brightness": 0.5,
                "bg_opacity": 200,
                "text_color": (230, 230, 230, 255),
                "bg_color": (10, 10, 10, 200),
                "shadow_offset": 0,
                "shadow_color": (0, 0, 0, 0),
                "decoration": True,
                "rounded_bg": False,
                "gradient_bg": False
            },
            "minimal": {
                "blur_radius": 10,
                "brightness": 0.4,
                "bg_opacity": 0,
                "text_color": (255, 255, 255, 255),
                "bg_color": (0, 0, 0, 0),
                "shadow_offset": 4,
                "shadow_color": (0, 0, 0, 230),
                "decoration": False,
                "rounded_bg": False,
                "gradient_bg": False
            }
        }
        
        # 获取当前主题的配置
        self.config = self.theme_configs.get(theme, self.theme_configs["standard"])
        
        # 创建输出目录
        os.makedirs(output_folder, exist_ok=True)
        
        # 获取图片文件列表
        self.image_files = []
        for ext in ['jpg', 'jpeg', 'png', 'gif']:
            self.image_files.extend(list(Path(images_folder).glob(f"*.{ext}")))
        
        if not self.image_files:
            print(f"警告: 在 {images_folder} 中没有找到图片文件")
        else:
            print(f"找到 {len(self.image_files)} 张背景图片")
            
        # 加载字体
        self.font_en = self._load_font(font_path_en, self.font_size_en, "en")
        self.font_cn = self._load_font(font_path_cn, self.font_size_cn, "cn")
    
    def _load_font(self, font_path: str, font_size: int, font_type: str) -> ImageFont:
        """
        加载字体，根据操作系统和字体类型选择合适的字体
        
        参数:
            font_path: 字体文件路径
            font_size: 字体大小
            font_type: 字体类型，'en'为英文，'cn'为中文，'phonetic'为音标
            
        返回:
            PIL字体对象
        """
        try:
            # 如果指定了字体路径，尝试加载
            if font_path and os.path.exists(font_path):
                return ImageFont.truetype(font_path, font_size)
            
            # 否则根据操作系统选择默认字体
            system = platform.system()
            
            if system == "Windows":
                # Windows系统字体
                if font_type == "phonetic":
                    # Windows下支持音标的字体
                    font_paths = [
                        "arial.ttf", "Arial Unicode MS", "segoeui.ttf", 
                        "C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialuni.ttf", 
                        "C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/seguisym.ttf",
                        "C:/Windows/Fonts/calibri.ttf", "C:/Windows/Fonts/cambria.ttc"
                    ]
                elif font_type == "en":
                    font_paths = ["arial.ttf", "calibri.ttf", "C:/Windows/Fonts/arial.ttf"]
                else:  # cn
                    font_paths = ["simhei.ttf", "simsun.ttc", "C:/Windows/Fonts/simhei.ttf", "C:/Windows/Fonts/simsun.ttc"]
            elif system == "Darwin":  # macOS
                # macOS系统字体
                if font_type == "phonetic" or font_type == "en":
                    # macOS下支持音标的字体
                    font_paths = [
                        "/System/Library/Fonts/Helvetica.ttc", 
                        "/Library/Fonts/Arial Unicode.ttf",
                        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
                        "/System/Library/Fonts/STHeiti Light.ttc",
                        "/System/Library/Fonts/Supplemental/Courier New.ttf",
                        "/Library/Fonts/Arial.ttf"
                    ]
                else:  # cn
                    font_paths = ["/System/Library/Fonts/PingFang.ttc", "/Library/Fonts/Arial Unicode.ttf"]
            else:  # Linux或其他
                # Linux系统字体
                if font_type == "phonetic" or font_type == "en":
                    # Linux下支持音标的字体
                    font_paths = [
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
                        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
                        "/usr/share/fonts/TTF/Arial.ttf"
                    ]
                else:  # cn
                    font_paths = ["/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]
            
            # 尝试加载系统字体
            for path in font_paths:
                try:
                    if os.path.exists(path):
                        return ImageFont.truetype(path, font_size)
                except Exception:
                    continue
            
            # 如果都失败，使用默认字体
            print(f"警告: 无法加载{font_type}字体，使用默认字体")
            return ImageFont.load_default()
            
        except Exception as e:
            print(f"加载字体出错: {e}")
            return ImageFont.load_default()
    
    def get_text_size(self, text: str, font: ImageFont) -> Tuple[int, int]:
        """
        获取文本尺寸，兼容不同版本的PIL库
        
        参数:
            text: 文本
            font: 字体
            
        返回:
            文本尺寸 (宽度, 高度)
        """
        try:
            # 尝试使用 getsize 方法 (PIL < 9.2.0)
            return font.getsize(text)
        except AttributeError:
            try:
                # 尝试使用 getbbox 方法 (PIL >= 9.2.0)
                bbox = font.getbbox(text)
                return bbox[2] - bbox[0], bbox[3] - bbox[1]
            except Exception as e:
                # 如果都失败，使用临时图像计算
                print(f"警告: 计算文本尺寸时出错: {e}")
                img = Image.new('RGBA', (1, 1))
                draw = ImageDraw.Draw(img)
                
                # 使用 textbbox 方法
                try:
                    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
                    return right - left, bottom - top
                except AttributeError:
                    # 如果都失败，返回估计值
                    return len(text) * font.size // 2, font.size
    
    def resize_for_device(self, img: Image) -> Image:
        """
        根据设备模式调整图片尺寸
        
        参数:
            img: 原始图片
            
        返回:
            调整后的图片
        """
        # 如果是自动模式或保持原始大小，直接返回
        if self.device_mode == "auto" or self.device_config["keep_original"]:
            return img
        
        # 获取目标尺寸
        target_width = self.device_config["target_width"]
        target_height = self.device_config["target_height"]
        target_ratio = self.device_config["aspect_ratio"]
        
        # 原始尺寸
        orig_width, orig_height = img.size
        orig_ratio = orig_width / orig_height
        
        # 创建一个新的画布，使用目标尺寸和比例
        if target_ratio is not None:
            # 根据目标比例调整尺寸
            if orig_ratio > target_ratio:  # 原图更宽
                # 以高度为基准
                new_height = target_height
                new_width = int(new_height * orig_ratio)
                # 居中裁剪到目标宽度
                img = img.resize((new_width, new_height), Image.LANCZOS)
                left = (new_width - target_width) // 2
                img = img.crop((left, 0, left + target_width, new_height))
            else:  # 原图更窄或相等
                # 以宽度为基准
                new_width = target_width
                new_height = int(new_width / orig_ratio)
                # 居中裁剪到目标高度
                img = img.resize((new_width, new_height), Image.LANCZOS)
                top = (new_height - target_height) // 2
                img = img.crop((0, top, new_width, top + target_height))
        else:
            # 直接调整到目标尺寸，不考虑比例
            img = img.resize((target_width, target_height), Image.LANCZOS)
        
        return img
    
    def draw_rounded_rectangle(self, draw: ImageDraw, xy: Tuple, radius: int = 20, fill: Tuple = None) -> None:
        """
        绘制圆角矩形
        
        参数:
            draw: ImageDraw对象
            xy: 坐标 (x1, y1, x2, y2)
            radius: 圆角半径
            fill: 填充颜色
        """
        x1, y1, x2, y2 = xy
        # 绘制主矩形
        draw.rectangle([(x1+radius, y1), (x2-radius, y2)], fill=fill)
        draw.rectangle([(x1, y1+radius), (x2, y2-radius)], fill=fill)
        # 绘制四个角
        draw.pieslice([(x1, y1), (x1+radius*2, y1+radius*2)], 180, 270, fill=fill)
        draw.pieslice([(x2-radius*2, y1), (x2, y1+radius*2)], 270, 360, fill=fill)
        draw.pieslice([(x1, y2-radius*2), (x1+radius*2, y2)], 90, 180, fill=fill)
        draw.pieslice([(x2-radius*2, y2-radius*2), (x2, y2)], 0, 90, fill=fill)
    
    def draw_gradient_rectangle(self, img: Image, xy: Tuple, fill_top: Tuple, fill_bottom: Tuple, radius: int = 0) -> None:
        """
        绘制渐变矩形
        
        参数:
            img: Image对象
            xy: 坐标 (x1, y1, x2, y2)
            fill_top: 顶部颜色
            fill_bottom: 底部颜色
            radius: 圆角半径
        """
        x1, y1, x2, y2 = xy
        width = x2 - x1
        height = y2 - y1
        
        # 创建渐变图像
        gradient = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(gradient)
        
        for y in range(height):
            r = int(fill_top[0] + (fill_bottom[0] - fill_top[0]) * y / height)
            g = int(fill_top[1] + (fill_bottom[1] - fill_top[1]) * y / height)
            b = int(fill_top[2] + (fill_bottom[2] - fill_top[2]) * y / height)
            a = int(fill_top[3] + (fill_bottom[3] - fill_top[3]) * y / height)
            draw.line([(0, y), (width, y)], fill=(r, g, b, a))
        
        # 如果需要圆角
        if radius > 0:
            mask = Image.new('L', (width, height), 0)
            mask_draw = ImageDraw.Draw(mask)
            self.draw_rounded_rectangle(mask_draw, (0, 0, width, height), radius, fill=255)
            gradient.putalpha(mask)
        
        # 粘贴到原图
        img.paste(gradient, (x1, y1), gradient)
    
    def draw_wave_background(self, img: Image, xy: Tuple, bg_color: Tuple, radius: int = 20) -> Image:
        """
        绘制海浪形状的背景
        
        参数:
            img: 原始图像
            xy: 坐标 (x1, y1, x2, y2)
            bg_color: 背景颜色
            radius: 波浪半径
            
        返回:
            添加海浪背景的图像
        """
        x1, y1, x2, y2 = xy
        width = x2 - x1
        height = y2 - y1
        
        # 创建一个透明图层
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # 绘制主矩形背景
        draw.rectangle([x1+radius, y1, x2-radius, y2], fill=bg_color)
        draw.rectangle([x1, y1+radius, x2, y2-radius], fill=bg_color)
        
        # 绘制四个圆角
        draw.pieslice([x1, y1, x1+radius*2, y1+radius*2], 180, 270, fill=bg_color)
        draw.pieslice([x2-radius*2, y1, x2, y1+radius*2], 270, 360, fill=bg_color)
        draw.pieslice([x1, y2-radius*2, x1+radius*2, y2], 90, 180, fill=bg_color)
        draw.pieslice([x2-radius*2, y2-radius*2, x2, y2], 0, 90, fill=bg_color)
        
        # 添加波浪效果 - 顶部
        wave_height = radius * 0.7
        wave_width = width / 8  # 8个波
        
        # 绘制顶部波浪
        for i in range(9):  # 9个点可以形成8个波
            x_pos = x1 + i * wave_width
            if i % 2 == 0:
                y_pos = y1 - wave_height
            else:
                y_pos = y1
            
            if i == 0:
                # 起始点
                path = [(x_pos, y1)]
            else:
                # 添加控制点和目标点来创建贝塞尔曲线
                control_x = x1 + (i - 0.5) * wave_width
                control_y = y1 - wave_height if i % 2 == 1 else y1
                path.append((control_x, control_y))
                path.append((x_pos, y_pos))
        
        # 绘制底部波浪
        for i in range(9):  # 9个点可以形成8个波
            x_pos = x2 - i * wave_width
            if i % 2 == 0:
                y_pos = y2 + wave_height
            else:
                y_pos = y2
            
            # 添加控制点和目标点来创建贝塞尔曲线
            if i > 0:
                control_x = x2 - (i - 0.5) * wave_width
                control_y = y2 + wave_height if i % 2 == 1 else y2
                path.append((control_x, control_y))
            path.append((x_pos, y_pos))
        
        # 完成路径
        path.append((x1, y2))
        path.append((x1, y1))
        
        # 填充路径
        draw.polygon(path, fill=bg_color)
        
        # 合并图层
        return Image.alpha_composite(img, overlay)
    
    def add_decorative_elements(self, draw: ImageDraw, width: int, height: int, en_text_y: int, cn_text_y: int) -> None:
        """
        添加装饰元素
        
        参数:
            draw: ImageDraw对象
            width: 图像宽度
            height: 图像高度
            en_text_y: 英文文本Y坐标
            cn_text_y: 中文文本Y坐标
        """
        # 在英文和中文之间添加分隔线
        line_y = (en_text_y + cn_text_y) // 2
        line_width = min(width * 0.3, 150)  # 减小分隔线长度（原为0.4和200）
        line_x_start = (width - line_width) // 2
        line_x_end = line_x_start + line_width
        
        # 绘制更细的渐变分隔线
        for i in range(3):  # 减少分隔线厚度（原为5）
            alpha = 130 - i * 40  # 降低透明度起始值（原为150）
            draw.line(
                [(line_x_start, line_y+i), (line_x_end, line_y+i)],
                fill=(255, 255, 255, alpha),
                width=1
            )
    
    def add_text_to_image(self, image_path: str, en_text: str, phonetic_text: str, cn_text: str, output_path: str) -> Optional[str]:
        """
        在图片中添加英文、音标和中文文本
        
        参数:
            image_path: 背景图片路径
            en_text: 英文文本
            phonetic_text: 音标文本
            cn_text: 中文文本
            output_path: 输出图片路径
            
        返回:
            输出图片路径，出错时返回None
        """
        try:
            # 打开图片并转换为RGBA
            img = Image.open(image_path).convert("RGBA")
            
            # 调整图片大小以适应设备
            img = self.resize_for_device(img)
            
            # 应用模糊效果（根据主题配置）
            if self.config["blur_radius"] > 0:
                img = img.filter(ImageFilter.GaussianBlur(radius=self.config["blur_radius"]))
            
            # 调整亮度（根据主题配置）
            if self.config["brightness"] != 1.0:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(self.config["brightness"])
            
            # 获取图片尺寸
            width, height = img.size
            
            # 创建绘图对象
            draw = ImageDraw.Draw(img)
            
            # 动态调整字体大小 - 根据文本长度调整
            adjusted_font_size_en = self.font_size_en
            adjusted_font_size_cn = self.font_size_cn
            adjusted_font_size_phonetic = self.font_size_phonetic
            
            # 对长文本进行动态缩放
            max_width = width * 0.75  # 文本最大宽度为图像宽度的75%，使整体布局更加舒适
            
            # 英文文本缩放 - 更激进的缩放策略
            if len(en_text) > 10:  # 超过10个字符就开始缩放
                scale_factor = min(1.0, 10 / len(en_text) * 1.3)  # 针对长文本缩放系数
                adjusted_font_size_en = max(int(adjusted_font_size_en * scale_factor), 32)  # 降低最小字号为32
            
            # 中文文本缩放 - 更激进的缩放策略
            if len(cn_text) > 5:  # 超过5个字符就开始缩放
                scale_factor = min(1.0, 5 / len(cn_text) * 1.3)  # 针对长文本缩放系数
                adjusted_font_size_cn = max(int(adjusted_font_size_cn * scale_factor), 28)  # 降低最小字号为28
            
            # 音标文本缩放 - 与英文文本成比例
            if phonetic_text:
                phonetic_scale = adjusted_font_size_en / self.font_size_en
                adjusted_font_size_phonetic = max(int(self.font_size_phonetic * phonetic_scale), 15)  # 降低最小字号为15
            
            # 加载调整后的字体
            font_en = self._load_font(self.font_path_en, adjusted_font_size_en, "en")
            font_cn = self._load_font(self.font_path_cn, adjusted_font_size_cn, "cn")
            font_phonetic = self._load_font(self.font_path_en, adjusted_font_size_phonetic, "phonetic")
            
            # 计算文本尺寸
            en_text_width, en_text_height = self.get_text_size(en_text, font_en)
            
            # 确保文本不超过最大宽度
            if en_text_width > max_width:
                # 如果仍然超过最大宽度，继续减小字体大小
                scale_factor = max_width / en_text_width
                adjusted_font_size_en = max(int(adjusted_font_size_en * scale_factor), 28)
                adjusted_font_size_phonetic = max(int(adjusted_font_size_phonetic * scale_factor), 12)
                
                # 重新加载调整后的字体
                font_en = self._load_font(self.font_path_en, adjusted_font_size_en, "en")
                font_phonetic = self._load_font(self.font_path_en, adjusted_font_size_phonetic, "phonetic")
                
                # 重新计算文本尺寸
                en_text_width, en_text_height = self.get_text_size(en_text, font_en)
            
            phonetic_text_width, phonetic_text_height = 0, 0
            if phonetic_text:
                try:
                    # 尝试使用支持音标的字体计算大小
                    phonetic_text_width, phonetic_text_height = self.get_text_size(phonetic_text, font_phonetic)
                except Exception as e:
                    print(f"计算音标尺寸时出错: {e}，将使用估算值")
                    # 如果无法计算音标尺寸，使用估算值
                    phonetic_text_width = len(phonetic_text) * (adjusted_font_size_phonetic // 2)
                    phonetic_text_height = adjusted_font_size_phonetic
            
            # 计算中文文本尺寸
            cn_text_width, cn_text_height = self.get_text_size(cn_text, font_cn)
            
            # 如果中文文本超过最大宽度，继续减小字体大小
            if cn_text_width > max_width:
                scale_factor = max_width / cn_text_width
                adjusted_font_size_cn = max(int(adjusted_font_size_cn * scale_factor), 22)
                
                # 重新加载调整后的字体
                font_cn = self._load_font(self.font_path_cn, adjusted_font_size_cn, "cn")
                
                # 重新计算文本尺寸
                cn_text_width, cn_text_height = self.get_text_size(cn_text, font_cn)
            
            # 进一步减小元素之间的间距，使整体更紧凑
            spacing_en_to_phonetic = 18  # 英文到音标的间距（原为25）
            spacing_phonetic_to_cn = 25  # 音标到中文的间距（原为35）
            spacing_en_to_cn = 30  # 如果没有音标，英文到中文的间距（原为40）
            
            # 计算总文本高度
            if phonetic_text:
                total_text_height = en_text_height + phonetic_text_height + cn_text_height + spacing_en_to_phonetic + spacing_phonetic_to_cn
            else:
                total_text_height = en_text_height + cn_text_height + spacing_en_to_cn
            
            # 计算文本位置 - 上中下布局
            text_y_start = (height - total_text_height) // 2
            en_text_x = (width - en_text_width) // 2
            en_text_y = text_y_start
            
            # 音标位置（如果有）
            phonetic_text_x = 0
            phonetic_text_y = 0
            current_y = en_text_y + en_text_height
            
            if phonetic_text:
                current_y += spacing_en_to_phonetic
                phonetic_text_x = (width - phonetic_text_width) // 2
                phonetic_text_y = current_y
                current_y += phonetic_text_height + spacing_phonetic_to_cn
            else:
                current_y += spacing_en_to_cn
            
            # 中文位置
            cn_text_x = (width - cn_text_width) // 2
            cn_text_y = current_y
            
            # 如果需要背景矩形
            if self.config["bg_opacity"] > 0:
                padding = 25  # 进一步减小内边距（原为30）
                bg_rect_width = max(en_text_width, phonetic_text_width, cn_text_width) + padding * 2
                bg_rect_height = total_text_height + padding * 2
                bg_rect_x = (width - bg_rect_width) // 2
                bg_rect_y = text_y_start - padding
                
                # 降低背景透明度，让背景不那么突兀
                bg_color = list(self.config["bg_color"])
                if bg_color[3] > 60:  # 如果原透明度大于60
                    bg_color[3] = int(bg_color[3] * 0.8)  # 降低透明度到原来的80%
                bg_color = tuple(bg_color)
                
                # 创建透明层
                overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
                
                # 根据背景样式选择不同的绘制方法
                if self.bg_style == "wave":
                    # 绘制海浪形状背景
                    img = self.draw_wave_background(
                        img, 
                        (bg_rect_x, bg_rect_y, bg_rect_x + bg_rect_width, bg_rect_y + bg_rect_height),
                        bg_color
                    )
                    draw = ImageDraw.Draw(img)
                else:
                    # 原有的矩形背景绘制方式
                    overlay_draw = ImageDraw.Draw(overlay)
                    
                    if self.config["rounded_bg"]:
                        # 绘制圆角背景
                        if self.config["gradient_bg"]:
                            # 渐变圆角背景
                            top_color = (bg_color[0], bg_color[1], bg_color[2], bg_color[3])
                            bottom_color = (bg_color[0], bg_color[1], bg_color[2], bg_color[3] // 2)
                            self.draw_gradient_rectangle(
                                overlay, 
                                (bg_rect_x, bg_rect_y, bg_rect_x + bg_rect_width, bg_rect_y + bg_rect_height),
                                top_color, bottom_color, radius=20  # 减小圆角半径（原为30）
                            )
                        else:
                            # 普通圆角背景
                            self.draw_rounded_rectangle(
                                overlay_draw,
                                (bg_rect_x, bg_rect_y, bg_rect_x + bg_rect_width, bg_rect_y + bg_rect_height),
                                radius=20,  # 减小圆角半径（原为30）
                                fill=bg_color
                            )
                        
                        # 合并图层
                        img = Image.alpha_composite(img, overlay)
                        draw = ImageDraw.Draw(img)
                    else:
                        # 普通矩形背景
                        if self.config["gradient_bg"]:
                            # 渐变背景
                            top_color = (bg_color[0], bg_color[1], bg_color[2], bg_color[3])
                            bottom_color = (bg_color[0], bg_color[1], bg_color[2], bg_color[3] // 2)
                            self.draw_gradient_rectangle(
                                overlay, 
                                (bg_rect_x, bg_rect_y, bg_rect_x + bg_rect_width, bg_rect_y + bg_rect_height),
                                top_color, bottom_color
                            )
                        else:
                            # 普通背景
                            overlay_draw.rectangle(
                                [bg_rect_x, bg_rect_y, bg_rect_x + bg_rect_width, bg_rect_y + bg_rect_height],
                                fill=bg_color
                            )
                        
                        # 合并图层
                        img = Image.alpha_composite(img, overlay)
                        draw = ImageDraw.Draw(img)
            
            # 添加装饰元素（如果配置允许）
            if self.config["decoration"]:
                # 缩小装饰线宽度
                self.add_decorative_elements(draw, width, height, en_text_y, phonetic_text_y if phonetic_text else (cn_text_y - spacing_en_to_cn // 2))
            
            # 添加文本阴影效果（如果配置允许）
            shadow_offset = self.config["shadow_offset"]
            shadow_color = self.config["shadow_color"]
            
            if shadow_offset > 0:
                # 绘制英文文本阴影
                draw.text((en_text_x + shadow_offset, en_text_y + shadow_offset), 
                          en_text, font=font_en, fill=shadow_color)
                
                # 绘制音标文本阴影（如果有）
                if phonetic_text:
                    draw.text((phonetic_text_x + shadow_offset, phonetic_text_y + shadow_offset), 
                              phonetic_text, font=font_phonetic, fill=shadow_color)
                
                # 绘制中文文本阴影
                draw.text((cn_text_x + shadow_offset, cn_text_y + shadow_offset), 
                          cn_text, font=font_cn, fill=shadow_color)
            
            # 绘制英文文本
            draw.text((en_text_x, en_text_y), en_text, font=font_en, fill=self.config["text_color"])
            
            # 绘制音标文本（如果有）
            if phonetic_text:
                try:
                    draw.text((phonetic_text_x, phonetic_text_y), phonetic_text, font=font_phonetic, fill=self.config["text_color"])
                except Exception as e:
                    # 如果使用特殊音标字符失败，尝试使用基本字符
                    print(f"绘制音标文本失败: {e}")
                    # 尝试将特殊音标字符替换为基本ASCII字符
                    simplified_phonetic = phonetic_text.encode('ascii', 'replace').decode('ascii')
                    draw.text((phonetic_text_x, phonetic_text_y), simplified_phonetic, font=font_phonetic, fill=self.config["text_color"])
            
            # 绘制中文文本
            draw.text((cn_text_x, cn_text_y), cn_text, font=font_cn, fill=self.config["text_color"])
            
            # 保存图片
            img = img.convert("RGB")  # 转换为RGB以保存为JPG
            img.save(output_path, quality=95)
            print(f"已生成图片: {output_path}")
            
            return output_path
            
        except Exception as e:
            print(f"处理图片 {image_path} 时出错: {e}")
            return None
    
    def process_word_list(self, word_list_file: str):
        """
        处理单词列表文件，为每个单词生成图片
        
        参数:
            word_list_file: 单词列表文件路径，每行格式为 "英文,音标,中文" 或 "英文,中文"
        """
        if not os.path.exists(word_list_file):
            print(f"错误: 单词列表文件 {word_list_file} 不存在")
            return
        
        try:
            # 读取单词列表
            word_pairs = []
            with open(word_list_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:  # 跳过空行
                        continue
                        
                    parts = line.split(',')
                    if len(parts) >= 3:  # 三段式: 英文,音标,中文
                        en_word = parts[0].strip()
                        phonetic = parts[1].strip()
                        cn_word = parts[2].strip()
                        word_pairs.append((en_word, phonetic, cn_word))
                    elif len(parts) == 2:  # 两段式: 英文,中文
                        en_word = parts[0].strip()
                        cn_word = parts[1].strip()
                        word_pairs.append((en_word, "", cn_word))
                    else:
                        print(f"警告: 第{line_num}行格式不正确，已跳过: '{line}'")
            
            if not word_pairs:
                print("错误: 单词列表为空或格式不正确")
                return
            
            print(f"读取了 {len(word_pairs)} 对单词")
            
            # 如果有背景图片，但是数量不足，进行循环使用
            if self.image_files and len(word_pairs) > len(self.image_files):
                repeats = (len(word_pairs) // len(self.image_files)) + 1
                self.image_files = self.image_files * repeats
            
            # 随机打乱图片顺序，增加多样性
            if self.image_files:
                random.shuffle(self.image_files)
            
            # 处理每对单词
            for i, word_data in enumerate(word_pairs):
                if not self.image_files:
                    print("错误: 没有可用的背景图片")
                    break
                
                # 选择背景图片
                image_path = str(self.image_files[i % len(self.image_files)])
                
                # 生成输出文件名
                en_word = word_data[0]
                output_filename = f"{i+1:03d}_{en_word}.jpg"
                output_path = os.path.join(self.output_folder, output_filename)
                
                # 处理图片
                if len(word_data) == 3:  # 三段式
                    self.add_text_to_image(image_path, word_data[0], word_data[1], word_data[2], output_path)
                else:  # 两段式
                    self.add_text_to_image(image_path, word_data[0], "", word_data[1], output_path)
        
        except Exception as e:
            print(f"处理单词列表时出错: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="图片单词生成器 - 将英语单词和中文释义添加到背景图片中")
    parser.add_argument("--images", required=True, help="背景图片文件夹路径")
    parser.add_argument("--words", required=True, help="单词列表文件路径，每行格式为'英文,音标,中文'或'英文,中文'")
    parser.add_argument("--output", default="output_images", help="输出图片文件夹路径")
    parser.add_argument("--font-size-en", type=int, default=80, help="英文字体大小，默认为80")
    parser.add_argument("--font-size-cn", type=int, default=55, help="中文字体大小，默认为55")
    parser.add_argument("--font-size-phonetic", type=int, default=None, help="音标字体大小，默认为英文字体大小的35%")
    parser.add_argument("--font-path-en", help="英文字体文件路径")
    parser.add_argument("--font-path-cn", help="中文字体文件路径")
    parser.add_argument("--theme", default="standard", choices=["standard", "focus", "elegant", "dark", "minimal"], 
                      help="主题风格: standard(标准), focus(专注), elegant(优雅), dark(暗黑), minimal(极简)")
    parser.add_argument("--device", default="auto", choices=["auto", "mobile", "tablet", "desktop"],
                      help="设备模式: auto(自动), mobile(手机), tablet(平板), desktop(桌面)")
    parser.add_argument("--bg-style", default="rectangle", choices=["rectangle", "wave"],
                      help="背景样式: rectangle(矩形), wave(海浪形状)")
    
    args = parser.parse_args()
    
    # 创建图片单词生成器
    generator = ImageWordGenerator(
        images_folder=args.images,
        output_folder=args.output,
        font_size_en=args.font_size_en,
        font_size_cn=args.font_size_cn,
        font_size_phonetic=args.font_size_phonetic,
        font_path_en=args.font_path_en,
        font_path_cn=args.font_path_cn,
        theme=args.theme,
        device_mode=args.device,
        bg_style=args.bg_style
    )
    
    # 处理单词列表
    generator.process_word_list(args.words)
    
    print(f"处理完成，输出图片保存在 {args.output} 文件夹中")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 