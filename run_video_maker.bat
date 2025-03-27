@echo off
echo Python一分钟视频制造机
echo =============================================

set DEFAULT_IMAGE_FOLDER=output_images
set DEFAULT_NUM_IMAGES=6
set DEFAULT_OUTPUT=一分钟视频.mp4

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
echo 选择要使用的图片数量:
echo 1. 使用默认数量 (%DEFAULT_NUM_IMAGES%张)
echo 2. 自定义数量
set /p num_choice=请选择 (1/2):

if "%num_choice%"=="1" (
    set NUM_IMAGES=%DEFAULT_NUM_IMAGES%
) else (
    set /p NUM_IMAGES=请输入图片数量:
)

echo.
echo 选择输出视频文件名:
echo 1. 使用默认文件名 (%DEFAULT_OUTPUT%)
echo 2. 自定义文件名
set /p output_choice=请选择 (1/2):

if "%output_choice%"=="1" (
    set OUTPUT_FILE=%DEFAULT_OUTPUT%
) else (
    set /p OUTPUT_FILE=请输入输出视频文件名:
)

echo.
echo 是否在完成后清理临时文件?
set /p cleanup_choice=清理临时文件? (y/n):

if /i "%cleanup_choice%"=="y" (
    set CLEANUP=--cleanup
) else (
    set CLEANUP=
)

echo.
echo 准备开始生成视频，参数如下:
echo 图片文件夹: %IMAGE_FOLDER%
echo 图片数量: %NUM_IMAGES%
echo 输出文件: %OUTPUT_FILE%
echo 清理临时文件: %CLEANUP%

echo.
echo 按任意键开始生成视频...
pause > nul

python one_minute_video_maker.py --images "%IMAGE_FOLDER%" --num-images %NUM_IMAGES% --output "%OUTPUT_FILE%" %CLEANUP%

echo.
echo 完成!
echo 按任意键退出...
pause > nul 