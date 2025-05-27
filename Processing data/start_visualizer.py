#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MPU6050 Real-time Visualizer Launcher
MPU6050ʵʱ���ӻ�������
"""

import sys
import os

def check_dependencies():
    """Check if required packages are installed / ������İ��Ƿ��Ѱ�װ"""
    required_packages = ['numpy', 'pandas', 'matplotlib', 'scipy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("ȱ������Python��:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n�������������װ:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def show_menu():
    """Show program selection menu / ��ʾ����ѡ��˵�"""
    print("\n��ѡ��Ҫ�����ĳ���:")
    print("1. ����ʵʱ���ӻ��� (���ǩҳ��ʾ��������)")
    print("2. �˶��켣����� (רע���˶��켣����)")
    print("3. �˳�")
    
    while True:
        try:
            choice = input("\n������ѡ�� (1-3): ").strip()
            if choice in ['1', '2', '3']:
                return int(choice)
            else:
                print("��Чѡ�������� 1��2 �� 3")
        except KeyboardInterrupt:
            print("\n\n������ȡ��")
            sys.exit(0)

def main():
    """Main function / ������"""
    print("=" * 60)
    print("MPU6050 ʵʱ���ݿ��ӻ�ϵͳ")
    print("=" * 60)
    
    # Check dependencies
    # �������
    if not check_dependencies():
        sys.exit(1)
    
    # Show menu and get user choice
    # ��ʾ�˵�����ȡ�û�ѡ��
    choice = show_menu()
    
    if choice == 3:
        print("�������˳�")
        sys.exit(0)
    
    try:
        if choice == 1:
            print("\n������������ʵʱ���ӻ���...")
            from realtime_visualizer import RealtimeVisualizer
            
            visualizer = RealtimeVisualizer()
            print("�������ӻ���������!")
            print("\nʹ��˵��:")
            print("1. ���'��ʼ����'��ť��ʼ��������")
            print("2. ����ݮ�������г��򲢰�'s'��ʼ����")
            print("3. �鿴��ͬ��ǩҳ��ʵʱ����")
            print("4. ʹ�ÿ��ư�ť���������ռ�")
            
            visualizer.run()
            
        elif choice == 2:
            print("\n���������˶��켣�����...")
            from realtime_motion_tracker import MotionTracker
            
            tracker = MotionTracker()
            print("�˶��켣�����������!")
            print("\nʹ��˵��:")
            print("1. ���'��ʼ���'��ť��ʼ��������")
            print("2. ����ݮ�������г��򲢰�'s'��ʼ����")
            print("3. ʵʱ�鿴�˶��켣��״̬����")
            print("4. ʹ�ÿ��ư�ť����켣���")
            
            tracker.run()
        
    except ImportError as e:
        print(f"�������: {e}")
        print("��ȷ�����б�����ļ����ڵ�ǰĿ¼��")
        sys.exit(1)
    except Exception as e:
        print(f"����ʧ��: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 