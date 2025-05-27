#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MPU6050 Real-time Visualizer Launcher
MPU6050实时可视化启动器
"""

import sys
import os

def check_dependencies():
    """Check if required packages are installed / 检查必需的包是否已安装"""
    required_packages = ['numpy', 'pandas', 'matplotlib', 'scipy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("缺少以下Python包:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n请运行以下命令安装:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def show_menu():
    """Show program selection menu / 显示程序选择菜单"""
    print("\n请选择要启动的程序:")
    print("1. 基础实时可视化器 (多标签页显示所有数据)")
    print("2. 运动轨迹检测器 (专注于运动轨迹分析)")
    print("3. 退出")
    
    while True:
        try:
            choice = input("\n请输入选择 (1-3): ").strip()
            if choice in ['1', '2', '3']:
                return int(choice)
            else:
                print("无效选择，请输入 1、2 或 3")
        except KeyboardInterrupt:
            print("\n\n程序已取消")
            sys.exit(0)

def main():
    """Main function / 主函数"""
    print("=" * 60)
    print("MPU6050 实时数据可视化系统")
    print("=" * 60)
    
    # Check dependencies
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # Show menu and get user choice
    # 显示菜单并获取用户选择
    choice = show_menu()
    
    if choice == 3:
        print("程序已退出")
        sys.exit(0)
    
    try:
        if choice == 1:
            print("\n正在启动基础实时可视化器...")
            from realtime_visualizer import RealtimeVisualizer
            
            visualizer = RealtimeVisualizer()
            print("基础可视化器已启动!")
            print("\n使用说明:")
            print("1. 点击'开始接收'按钮开始监听数据")
            print("2. 在树莓派上运行程序并按's'开始传输")
            print("3. 查看不同标签页的实时数据")
            print("4. 使用控制按钮管理数据收集")
            
            visualizer.run()
            
        elif choice == 2:
            print("\n正在启动运动轨迹检测器...")
            from realtime_motion_tracker import MotionTracker
            
            tracker = MotionTracker()
            print("运动轨迹检测器已启动!")
            print("\n使用说明:")
            print("1. 点击'开始检测'按钮开始监听数据")
            print("2. 在树莓派上运行程序并按's'开始传输")
            print("3. 实时查看运动轨迹和状态分析")
            print("4. 使用控制按钮管理轨迹检测")
            
            tracker.run()
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保所有必需的文件都在当前目录中")
        sys.exit(1)
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 