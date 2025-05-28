#!/bin/bash

echo "=== MPU6050 原始数据收集程序测试脚本 ==="
echo

# 检查当前目录
if [ ! -f "collect_data.cpp" ]; then
    echo "错误: 请在 'MPU6050-MotionTracking/Collect data' 目录下运行此脚本"
    exit 1
fi

echo "1. 检查依赖..."

# 检查wiringPi
if ! command -v gpio &> /dev/null; then
    echo "警告: wiringPi 未安装或未在PATH中"
    echo "请运行: sudo apt-get install wiringpi"
else
    echo "? wiringPi 已安装"
fi

# 检查gtkmm
if ! pkg-config --exists gtkmm-3.0; then
    echo "警告: gtkmm-3.0 未安装"
    echo "请运行: sudo apt-get install libgtkmm-3.0-dev"
else
    echo "? gtkmm-3.0 已安装"
fi

# 检查I2C
if [ ! -e "/dev/i2c-1" ]; then
    echo "警告: I2C设备 /dev/i2c-1 不存在"
    echo "请确保I2C已启用: sudo raspi-config -> Interface Options -> I2C"
else
    echo "? I2C设备存在"
fi

echo
echo "2. 编译程序..."

# 清理旧文件
make clean 2>/dev/null

# 编译
if make; then
    echo "? 编译成功"
else
    echo "? 编译失败"
    echo "请检查依赖是否正确安装"
    exit 1
fi

echo
echo "3. 检查可执行文件..."

if [ -f "collect_data" ]; then
    echo "? collect_data 已生成"
    ls -la collect_data
else
    echo "? collect_data 未生成"
    exit 1
fi

if [ -f "IMU_zero" ]; then
    echo "? IMU_zero 已生成"
    ls -la IMU_zero
else
    echo "? IMU_zero 未生成"
fi

echo
echo "4. 检查数据目录..."

if [ ! -d "Datas" ]; then
    echo "创建 Datas 目录..."
    mkdir -p Datas
fi

echo "当前数据文件夹:"
ls -la Datas/ 2>/dev/null || echo "Datas目录为空"

echo
echo "5. 检查I2C设备..."

if command -v i2cdetect &> /dev/null; then
    echo "扫描I2C设备..."
    sudo i2cdetect -y 1 2>/dev/null || echo "无法扫描I2C设备，可能需要root权限"
else
    echo "i2cdetect 未安装，跳过I2C扫描"
fi

echo
echo "=== 测试完成 ==="
echo
echo "如果所有检查都通过，你可以运行:"
echo "  sudo ./collect_data    # 运行数据收集程序"
echo "  sudo ./IMU_zero        # 运行校准程序"
echo
echo "程序运行说明:"
echo "1. 运行后等待25秒初始化"
echo "2. 绿灯亮起后可以按按钮开始收集"
echo "3. 再次按按钮停止收集"
echo "4. 数据保存在 Datas/data_X/ 目录中"
echo
echo "LED状态:"
echo "  红灯亮 = 等待中"
echo "  红+绿灯亮 = 准备就绪"
echo "  绿灯亮 = 正在收集数据" 