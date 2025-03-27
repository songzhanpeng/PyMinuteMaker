# Python一分钟视频制造机

一个简单易用的自动化工具，用于快速生成一分钟长度的视频内容。通过简单的命令行操作，将图片转换成精美的短视频。

## 新功能

- **指定图片张数**：现在可以指定使用多少张图片来生成视频，默认为6张
- **海浪形状背景**：单词卡片现在支持海浪形状的背景样式，更有活力

## 功能特点

- 从图片集合创建幻灯片视频
- 支持指定使用的图片张数（默认6张）
- 添加淡入淡出过渡效果
- 智能调整内容以确保视频长度为一分钟
- 支持多种图片格式（jpg、jpeg、png、gif）
- **图片单词生成器**: 将英语单词和中文释义添加到背景图片中
  - 提供5种精美主题风格，满足不同场景需求
  - 支持4种设备模式，适配手机、平板和桌面显示

## 安装要求

1. 克隆此仓库
2. 安装依赖库：`pip install -r requirements.txt`

## 使用说明

### 一分钟视频制造机

一个简单易用的自动化工具，用于快速生成一分钟长度的视频内容。

#### 基本用法

```bash
python one_minute_video_maker.py --images 图片文件夹路径
```

这将使用默认6张图片从指定文件夹生成一个一分钟的视频。

#### 完整参数说明

```bash
python one_minute_video_maker.py --images 图片文件夹路径 [选项]
```

可用选项：
- `--num-images N`：指定使用的图片数量，默认为6张
- `--output 文件名.mp4`：指定输出视频文件名，默认为"一分钟视频.mp4"
- `--duration 秒数`：指定视频时长，默认为60秒
- `--cleanup`：生成视频后删除临时文件

#### 示例

1. 使用默认6张图片：
```bash
python one_minute_video_maker.py --images my_photos
```

2. 指定使用10张图片：
```bash
python one_minute_video_maker.py --images my_photos --num-images 10
```

3. 生成30秒视频，指定输出文件名：
```bash
python one_minute_video_maker.py --images my_photos --duration 30 --output short_video.mp4
```

### 图片单词生成器

图片单词生成器可以将英语单词和中文释义添加到背景图片的中央，适用于制作单词记忆卡片。

#### 快速启动

我们提供了两个便捷的启动脚本，让您可以更简单地使用图片单词生成器：

- **Windows系统**：双击运行 `run_image_generator.bat` 文件
- **macOS/Linux系统**：在终端中运行 `bash run_image_generator.sh` 或先执行 `chmod +x run_image_generator.sh` 后运行 `./run_image_generator.sh`

这些脚本将自动检查依赖，引导您选择单词列表、主题风格和设备模式，并帮助您管理图片文件。

#### 主题风格

我们提供了5种精美的主题风格，可以满足不同的学习场景和视觉偏好：

1. **standard** - 标准风格：白色文字，黑色半透明背景
2. **focus** - 专注风格：背景模糊，文字突出，适合专注学习
3. **elegant** - 优雅风格：圆角渐变背景，精致分隔线，视觉效果更加精美
4. **dark** - 暗黑风格：深色背景，适合夜间学习
5. **minimal** - 极简风格：无背景，仅文字和阴影，保持背景图片的完整视觉效果

#### 背景样式

您可以选择两种不同的背景样式，为您的单词卡片增添视觉趣味：

1. **rectangle** - 矩形背景：传统的矩形或圆角矩形背景
2. **wave** - 海浪形状：顶部和底部采用波浪线条设计，为卡片增添活力和趣味

#### 设备模式

为了确保图片在不同设备上都能得到最佳显示效果，我们提供了4种设备模式：

1. **auto** - 自动模式：保持原始图片尺寸和比例
2. **mobile** - 手机模式：垂直 9:16 比例，优化为 1080×1920 分辨率，字体略大
3. **tablet** - 平板模式：垂直 3:4 比例，优化为 1536×2048 分辨率
4. **desktop** - 桌面模式：横向 16:9 比例，优化为 1920×1080 分辨率

手机模式特别适合在手机上浏览学习，图片会自动调整为竖屏比例，便于在手机上全屏显示。

#### 命令行使用方法

如果您喜欢手动使用命令行，请按照以下步骤操作：

1. 准备背景图片文件夹（支持jpg、jpeg、png、gif格式）
2. 创建单词列表文件（格式为"英文,中文"，每行一对单词）
3. 运行脚本：

```bash
python image_word_generator.py --images 背景图片文件夹 --words 单词列表文件路径 --theme 主题名称 --device 设备模式
```

#### 参数说明

- `--images`：背景图片文件夹路径（必填）
- `--words`：单词列表文件路径，每行格式为"英文,中文"（必填）
- `--output`：输出图片文件夹路径（默认为"output_images"）
- `--font-size-en`：英文字体大小（默认为60）
- `--font-size-cn`：中文字体大小（默认为45）
- `--font-size-phonetic`：音标字体大小（默认为英文字体大小的30%）
- `--font-path-en`：英文字体文件路径（可选，默认使用系统字体）
- `--font-path-cn`：中文字体文件路径（可选，默认使用系统字体）
- `--theme`：主题风格（可选，默认为"standard"）
  - 可选值：standard, focus, elegant, dark, minimal
- `--device`：设备模式（可选，默认为"auto"）
  - 可选值：auto, mobile, tablet, desktop
- `--bg-style`：背景样式（可选，默认为"rectangle"）
  - 可选值：rectangle, wave

#### 字体说明

程序会根据操作系统自动选择合适的字体：

- Windows: 默认使用Arial（英文）和微软黑体（中文）
- macOS: 默认使用Helvetica（英文）和苹方/Arial Unicode（中文）
- Linux: 默认使用DejaVu Sans（英文）和Noto Sans CJK（中文）

如果需要使用自定义字体，可以通过`--font-path-en`和`--font-path-cn`参数指定字体文件路径。

#### 示例单词列表文件（words.txt）

```
apple,苹果
book,书
cat,猫
dog,狗
elephant,大象
```

#### 示例命令

```bash
# 基本用法
python image_word_generator.py --images background_images --words words.txt

# 使用专注主题和手机模式
python image_word_generator.py --images background_images --words words.txt --theme focus --device mobile

# 使用海浪形状背景
python image_word_generator.py --images background_images --words words.txt --bg-style wave

# 自定义音标字体大小
python image_word_generator.py --images background_images --words words.txt --font-size-phonetic 20

# 自定义输出文件夹、字体大小、主题、设备模式和背景样式
python image_word_generator.py --images background_images --words words.txt --output vocabulary_cards --font-size-en 60 --font-size-cn 45 --font-size-phonetic 24 --theme elegant --device tablet --bg-style wave
```

这将生成一系列图片，每张图片包含一个英语单词和对应的中文释义，保存在vocabulary_cards文件夹中。

#### 示例单词列表

项目中已包含一个示例单词列表文件`example_words.txt`，您可以直接使用：

```bash
python image_word_generator.py --images 您的图片文件夹 --words example_words.txt --theme minimal --device mobile
```