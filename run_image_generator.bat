@echo off
echo 图片单词生成器
echo =============================================

set DEFAULT_IMAGE_FOLDER=images
set DEFAULT_WORD_FILE=example_words.txt
set DEFAULT_OUTPUT_FOLDER=output_images
set DEFAULT_FONT_SIZE_EN=60
set DEFAULT_FONT_SIZE_CN=45
set DEFAULT_FONT_SIZE_PHONETIC=24
set DEFAULT_THEME=standard
set DEFAULT_DEVICE=mobile
set DEFAULT_BG_STYLE=rectangle

if not exist %DEFAULT_WORD_FILE% (
    echo 警告: 默认单词文件 %DEFAULT_WORD_FILE% 不存在
)

if not exist %DEFAULT_IMAGE_FOLDER% (
    echo 警告: 默认图片文件夹 %DEFAULT_IMAGE_FOLDER% 不存在
    mkdir %DEFAULT_IMAGE_FOLDER%
    echo 已创建图片文件夹: %DEFAULT_IMAGE_FOLDER%
    echo 请将背景图片放入此文件夹后再运行此脚本
    echo.
    echo 按任意键退出...
    pause > nul
    exit /b 1
)

echo 选择图片文件夹:
echo 1. 使用默认文件夹 (%DEFAULT_IMAGE_FOLDER%)
echo 2. 自定义文件夹
set /p folder_choice=请选择 (1/2):

if "%folder_choice%"=="1" (
    set IMAGE_FOLDER=%DEFAULT_IMAGE_FOLDER%
) else (
    set /p IMAGE_FOLDER=请输入图片文件夹路径:
)

echo.
echo 选择单词列表文件:
echo 1. 使用默认文件 (%DEFAULT_WORD_FILE%)
echo 2. 自定义文件
set /p word_choice=请选择 (1/2):

if "%word_choice%"=="1" (
    set WORD_FILE=%DEFAULT_WORD_FILE%
) else (
    set /p WORD_FILE=请输入单词列表文件路径:
)

echo.
echo 选择字体大小:
echo 1. 使用默认字体大小
echo    英文: %DEFAULT_FONT_SIZE_EN%
echo    中文: %DEFAULT_FONT_SIZE_CN%
echo    音标: %DEFAULT_FONT_SIZE_PHONETIC%
echo 2. 自定义字体大小
set /p font_choice=请选择 (1/2):

if "%font_choice%"=="1" (
    set FONT_SIZE_EN=%DEFAULT_FONT_SIZE_EN%
    set FONT_SIZE_CN=%DEFAULT_FONT_SIZE_CN%
    set FONT_SIZE_PHONETIC=%DEFAULT_FONT_SIZE_PHONETIC%
) else (
    set /p FONT_SIZE_EN=请输入英文字体大小 (默认%DEFAULT_FONT_SIZE_EN%):
    if "%FONT_SIZE_EN%"=="" set FONT_SIZE_EN=%DEFAULT_FONT_SIZE_EN%
    
    set /p FONT_SIZE_CN=请输入中文字体大小 (默认%DEFAULT_FONT_SIZE_CN%):
    if "%FONT_SIZE_CN%"=="" set FONT_SIZE_CN=%DEFAULT_FONT_SIZE_CN%
    
    set /p FONT_SIZE_PHONETIC=请输入音标字体大小 (默认%DEFAULT_FONT_SIZE_PHONETIC%):
    if "%FONT_SIZE_PHONETIC%"=="" set FONT_SIZE_PHONETIC=%DEFAULT_FONT_SIZE_PHONETIC%
)

echo.
echo 选择主题风格:
echo 1. standard - 标准风格
echo 2. focus - 专注风格(背景模糊，文字突出)
echo 3. elegant - 优雅风格(圆角渐变背景)
echo 4. dark - 暗黑风格(深色背景)
echo 5. minimal - 极简风格(无背景，仅文字)
set /p theme_choice=请选择 (1-5，默认1):

if "%theme_choice%"=="1" (
    set THEME=standard
) else if "%theme_choice%"=="2" (
    set THEME=focus
) else if "%theme_choice%"=="3" (
    set THEME=elegant
) else if "%theme_choice%"=="4" (
    set THEME=dark
) else if "%theme_choice%"=="5" (
    set THEME=minimal
) else (
    set THEME=%DEFAULT_THEME%
)

echo.
echo 选择设备模式:
echo 1. auto - 自动模式(保持原始图片尺寸)
echo 2. mobile - 手机模式(9:16比例，优化为手机显示)
echo 3. tablet - 平板模式(3:4比例)
echo 4. desktop - 桌面模式(16:9比例，横向显示)
set /p device_choice=请选择 (1-4，默认2):

if "%device_choice%"=="1" (
    set DEVICE=auto
) else if "%device_choice%"=="2" (
    set DEVICE=mobile
) else if "%device_choice%"=="3" (
    set DEVICE=tablet
) else if "%device_choice%"=="4" (
    set DEVICE=desktop
) else (
    set DEVICE=%DEFAULT_DEVICE%
)

echo.
echo 选择背景样式:
echo 1. rectangle - 矩形背景
echo 2. wave - 海浪形状背景
set /p bg_style_choice=请选择 (1-2，默认1):

if "%bg_style_choice%"=="1" (
    set BG_STYLE=rectangle
) else if "%bg_style_choice%"=="2" (
    set BG_STYLE=wave
) else (
    set BG_STYLE=%DEFAULT_BG_STYLE%
)

echo.
echo 准备开始生成图片，参数如下:
echo 图片文件夹: %IMAGE_FOLDER%
echo 单词文件: %WORD_FILE%
echo 输出文件夹: %DEFAULT_OUTPUT_FOLDER%
echo 英文字体大小: %FONT_SIZE_EN%
echo 中文字体大小: %FONT_SIZE_CN%
echo 音标字体大小: %FONT_SIZE_PHONETIC%
echo 主题风格: %THEME%
echo 设备模式: %DEVICE%
echo 背景样式: %BG_STYLE%

echo.
echo 按任意键开始生成图片...
pause > nul

python image_word_generator.py --images "%IMAGE_FOLDER%" --words "%WORD_FILE%" --output "%DEFAULT_OUTPUT_FOLDER%" --font-size-en %FONT_SIZE_EN% --font-size-cn %FONT_SIZE_CN% --font-size-phonetic %FONT_SIZE_PHONETIC% --theme %THEME% --device %DEVICE% --bg-style %BG_STYLE%

echo.
echo 完成!
echo 输出文件保存在: %DEFAULT_OUTPUT_FOLDER%
echo 按任意键退出...
pause > nul 