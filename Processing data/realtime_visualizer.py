#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-time MPU6050 Data Visualizer
实时MPU6050数据可视化程序
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from realtime_receiver import MPU6050Receiver
import threading
import time

class RealtimeVisualizer:
    def __init__(self):
        """Initialize the real-time visualizer / 初始化实时可视化器"""
        self.receiver = MPU6050Receiver()
        self.running = False
        
        # Create main window
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("MPU6050 实时数据可视化")
        self.root.geometry("1200x800")
        
        # Create GUI elements
        # 创建GUI元素
        self.create_widgets()
        
        # Animation objects
        # 动画对象
        self.animations = {}
        
        print("实时可视化器初始化完成")
    
    def create_widgets(self):
        """Create GUI widgets / 创建GUI组件"""
        # Control frame
        # 控制框架
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Start/Stop buttons
        # 开始/停止按钮
        self.start_btn = ttk.Button(control_frame, text="开始接收", command=self.start_visualization)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="停止接收", command=self.stop_visualization, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Reset button
        # 重置按钮
        self.reset_btn = ttk.Button(control_frame, text="重置积分", command=self.reset_integration)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Save button
        # 保存按钮
        self.save_btn = ttk.Button(control_frame, text="保存数据", command=self.save_data)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label
        # 状态标签
        self.status_label = ttk.Label(control_frame, text="状态: 未连接")
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # Create notebook for different views
        # 创建不同视图的选项卡
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create different visualization tabs
        # 创建不同的可视化选项卡
        self.create_acceleration_tab()
        self.create_rotation_tab()
        self.create_position_tab()
        self.create_3d_tab()
    
    def create_acceleration_tab(self):
        """Create acceleration visualization tab / 创建加速度可视化选项卡"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="加速度数据")
        
        # Create matplotlib figure
        # 创建matplotlib图形
        self.acc_fig, self.acc_axes = plt.subplots(2, 2, figsize=(10, 6))
        self.acc_fig.suptitle('加速度和陀螺仪数据')
        
        # Setup subplots
        # 设置子图
        self.acc_axes[0, 0].set_title('原始加速度')
        self.acc_axes[0, 0].set_ylabel('加速度 (LSB)')
        self.acc_axes[0, 1].set_title('线性加速度')
        self.acc_axes[0, 1].set_ylabel('加速度 (LSB)')
        self.acc_axes[1, 0].set_title('陀螺仪数据')
        self.acc_axes[1, 0].set_ylabel('角速度 (LSB)')
        self.acc_axes[1, 1].set_title('速度 (积分)')
        self.acc_axes[1, 1].set_ylabel('速度 (m/s)')
        
        for ax in self.acc_axes.flat:
            ax.grid(True, alpha=0.3)
            ax.set_xlabel('时间 (ms)')
        
        # Create canvas
        # 创建画布
        canvas = FigureCanvasTkAgg(self.acc_fig, frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize line objects
        # 初始化线条对象
        self.acc_lines = {}
        colors = ['red', 'green', 'blue']
        labels = ['X', 'Y', 'Z']
        
        for i, (color, label) in enumerate(zip(colors, labels)):
            self.acc_lines[f'acc_{label}'], = self.acc_axes[0, 0].plot([], [], color=color, label=label)
            self.acc_lines[f'linear_acc_{label}'], = self.acc_axes[0, 1].plot([], [], color=color, label=label)
            self.acc_lines[f'gyr_{label}'], = self.acc_axes[1, 0].plot([], [], color=color, label=label)
            self.acc_lines[f'vel_{label}'], = self.acc_axes[1, 1].plot([], [], color=color, label=label)
        
        for ax in self.acc_axes.flat:
            ax.legend()
    
    def create_rotation_tab(self):
        """Create rotation visualization tab / 创建旋转可视化选项卡"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="旋转数据")
        
        # Create matplotlib figure
        # 创建matplotlib图形
        self.rot_fig, self.rot_axes = plt.subplots(2, 2, figsize=(10, 6))
        self.rot_fig.suptitle('旋转数据')
        
        # Setup subplots
        # 设置子图
        self.rot_axes[0, 0].set_title('四元数')
        self.rot_axes[0, 0].set_ylabel('四元数值')
        self.rot_axes[0, 1].set_title('欧拉角')
        self.rot_axes[0, 1].set_ylabel('角度 (弧度)')
        self.rot_axes[1, 0].set_title('欧拉角 (度)')
        self.rot_axes[1, 0].set_ylabel('角度 (度)')
        self.rot_axes[1, 1].set_title('角速度')
        self.rot_axes[1, 1].set_ylabel('角速度 (度/秒)')
        
        for ax in self.rot_axes.flat:
            ax.grid(True, alpha=0.3)
            ax.set_xlabel('时间 (ms)')
        
        # Create canvas
        # 创建画布
        canvas = FigureCanvasTkAgg(self.rot_fig, frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize line objects
        # 初始化线条对象
        self.rot_lines = {}
        quat_colors = ['black', 'red', 'green', 'blue']
        quat_labels = ['W', 'X', 'Y', 'Z']
        euler_colors = ['red', 'green', 'blue']
        euler_labels = ['Roll', 'Pitch', 'Yaw']
        
        for i, (color, label) in enumerate(zip(quat_colors, quat_labels)):
            self.rot_lines[f'quat_{label}'], = self.rot_axes[0, 0].plot([], [], color=color, label=label)
        
        for i, (color, label) in enumerate(zip(euler_colors, euler_labels)):
            self.rot_lines[f'euler_{label}'], = self.rot_axes[0, 1].plot([], [], color=color, label=label)
            self.rot_lines[f'euler_deg_{label}'], = self.rot_axes[1, 0].plot([], [], color=color, label=label)
            self.rot_lines[f'angular_vel_{label}'], = self.rot_axes[1, 1].plot([], [], color=color, label=label)
        
        for ax in self.rot_axes.flat:
            ax.legend()
    
    def create_position_tab(self):
        """Create position visualization tab / 创建位置可视化选项卡"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="位置数据")
        
        # Create matplotlib figure
        # 创建matplotlib图形
        self.pos_fig, self.pos_axes = plt.subplots(2, 2, figsize=(10, 6))
        self.pos_fig.suptitle('位置和轨迹数据')
        
        # Setup subplots
        # 设置子图
        self.pos_axes[0, 0].set_title('位置 (X, Y, Z)')
        self.pos_axes[0, 0].set_ylabel('位置 (m)')
        self.pos_axes[0, 1].set_title('XY平面轨迹')
        self.pos_axes[0, 1].set_ylabel('Y位置 (m)')
        self.pos_axes[0, 1].set_xlabel('X位置 (m)')
        self.pos_axes[1, 0].set_title('XZ平面轨迹')
        self.pos_axes[1, 0].set_ylabel('Z位置 (m)')
        self.pos_axes[1, 0].set_xlabel('X位置 (m)')
        self.pos_axes[1, 1].set_title('YZ平面轨迹')
        self.pos_axes[1, 1].set_ylabel('Z位置 (m)')
        self.pos_axes[1, 1].set_xlabel('Y位置 (m)')
        
        for ax in self.pos_axes.flat:
            ax.grid(True, alpha=0.3)
        
        self.pos_axes[0, 0].set_xlabel('时间 (ms)')
        
        # Create canvas
        # 创建画布
        canvas = FigureCanvasTkAgg(self.pos_fig, frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize line objects
        # 初始化线条对象
        self.pos_lines = {}
        colors = ['red', 'green', 'blue']
        labels = ['X', 'Y', 'Z']
        
        for i, (color, label) in enumerate(zip(colors, labels)):
            self.pos_lines[f'pos_{label}'], = self.pos_axes[0, 0].plot([], [], color=color, label=label)
        
        self.pos_lines['trajectory_xy'], = self.pos_axes[0, 1].plot([], [], 'b-', alpha=0.7)
        self.pos_lines['trajectory_xz'], = self.pos_axes[1, 0].plot([], [], 'g-', alpha=0.7)
        self.pos_lines['trajectory_yz'], = self.pos_axes[1, 1].plot([], [], 'r-', alpha=0.7)
        
        self.pos_axes[0, 0].legend()
    
    def create_3d_tab(self):
        """Create 3D visualization tab / 创建3D可视化选项卡"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="3D可视化")
        
        # Create matplotlib figure with 3D subplot
        # 创建带3D子图的matplotlib图形
        self.fig_3d = plt.figure(figsize=(10, 8))
        self.ax_3d = self.fig_3d.add_subplot(111, projection='3d')
        self.ax_3d.set_title('3D位置和方向')
        self.ax_3d.set_xlabel('X (m)')
        self.ax_3d.set_ylabel('Y (m)')
        self.ax_3d.set_zlabel('Z (m)')
        
        # Create canvas
        # 创建画布
        canvas = FigureCanvasTkAgg(self.fig_3d, frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize 3D objects
        # 初始化3D对象
        self.trajectory_3d, = self.ax_3d.plot([], [], [], 'b-', alpha=0.7, label='轨迹')
        self.current_pos_3d, = self.ax_3d.plot([], [], [], 'ro', markersize=8, label='当前位置')
        
        # Orientation arrows
        # 方向箭头
        self.orientation_arrows = {
            'x': None,
            'y': None,
            'z': None
        }
        
        self.ax_3d.legend()
    
    def start_visualization(self):
        """Start the visualization / 开始可视化"""
        if self.receiver.start_receiver():
            self.running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="状态: 正在接收数据")
            
            # Start animation
            # 开始动画
            self.start_animations()
            
            print("可视化已开始")
        else:
            messagebox.showerror("错误", "无法启动数据接收器")
    
    def stop_visualization(self):
        """Stop the visualization / 停止可视化"""
        self.running = False
        self.receiver.stop_receiver()
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="状态: 已停止")
        
        # Stop animations
        # 停止动画
        self.stop_animations()
        
        print("可视化已停止")
    
    def reset_integration(self):
        """Reset integration / 重置积分"""
        self.receiver.reset_integration()
        messagebox.showinfo("信息", "积分已重置")
    
    def save_data(self):
        """Save current data / 保存当前数据"""
        self.receiver.save_data_to_csv("realtime_data")
        messagebox.showinfo("信息", "数据已保存")
    
    def start_animations(self):
        """Start all animations / 开始所有动画"""
        self.animations['acc'] = FuncAnimation(self.acc_fig, self.update_acceleration_plot, 
                                             interval=50, blit=False)
        self.animations['rot'] = FuncAnimation(self.rot_fig, self.update_rotation_plot, 
                                             interval=50, blit=False)
        self.animations['pos'] = FuncAnimation(self.pos_fig, self.update_position_plot, 
                                             interval=50, blit=False)
        self.animations['3d'] = FuncAnimation(self.fig_3d, self.update_3d_plot, 
                                            interval=100, blit=False)
    
    def stop_animations(self):
        """Stop all animations / 停止所有动画"""
        for anim in self.animations.values():
            if anim:
                anim.event_source.stop()
        self.animations.clear()
    
    def update_acceleration_plot(self, frame):
        """Update acceleration plot / 更新加速度图"""
        data = self.receiver.get_latest_data(200)
        if not data or not data['timestamps']:
            return
        
        times = np.array(data['timestamps'])
        
        # Update acceleration data
        # 更新加速度数据
        if data['acceleration']:
            acc_data = np.array(data['acceleration'])
            for i, label in enumerate(['X', 'Y', 'Z']):
                self.acc_lines[f'acc_{label}'].set_data(times, acc_data[:, i])
        
        # Update linear acceleration data
        # 更新线性加速度数据
        if data['linear_acceleration']:
            linear_acc_data = np.array(data['linear_acceleration'])
            for i, label in enumerate(['X', 'Y', 'Z']):
                self.acc_lines[f'linear_acc_{label}'].set_data(times, linear_acc_data[:, i])
        
        # Update gyroscope data
        # 更新陀螺仪数据
        if data['gyroscope']:
            gyr_data = np.array(data['gyroscope'])
            for i, label in enumerate(['X', 'Y', 'Z']):
                self.acc_lines[f'gyr_{label}'].set_data(times, gyr_data[:, i])
        
        # Update velocity data
        # 更新速度数据
        if data['velocity']:
            vel_data = np.array(data['velocity'])
            for i, label in enumerate(['X', 'Y', 'Z']):
                self.acc_lines[f'vel_{label}'].set_data(times, vel_data[:, i])
        
        # Auto-scale axes
        # 自动缩放坐标轴
        for ax in self.acc_axes.flat:
            ax.relim()
            ax.autoscale_view()
    
    def update_rotation_plot(self, frame):
        """Update rotation plot / 更新旋转图"""
        data = self.receiver.get_latest_data(200)
        if not data or not data['timestamps']:
            return
        
        times = np.array(data['timestamps'])
        
        # Update quaternion data
        # 更新四元数据
        if data['quaternion']:
            quat_data = np.array(data['quaternion'])
            for i, label in enumerate(['W', 'X', 'Y', 'Z']):
                self.rot_lines[f'quat_{label}'].set_data(times, quat_data[:, i])
        
        # Update Euler angles
        # 更新欧拉角
        if data['euler']:
            euler_data = np.array(data['euler'])
            euler_deg = euler_data * 180 / np.pi
            
            for i, label in enumerate(['Roll', 'Pitch', 'Yaw']):
                self.rot_lines[f'euler_{label}'].set_data(times, euler_data[:, i])
                self.rot_lines[f'euler_deg_{label}'].set_data(times, euler_deg[:, i])
        
        # Calculate angular velocity from gyroscope
        # 从陀螺仪计算角速度
        if data['gyroscope']:
            gyr_data = np.array(data['gyroscope'])
            gyr_deg = gyr_data / 131.0  # Convert to degrees/second (assuming ±250°/s range)
            
            for i, label in enumerate(['Roll', 'Pitch', 'Yaw']):
                self.rot_lines[f'angular_vel_{label}'].set_data(times, gyr_deg[:, i])
        
        # Auto-scale axes
        # 自动缩放坐标轴
        for ax in self.rot_axes.flat:
            ax.relim()
            ax.autoscale_view()
    
    def update_position_plot(self, frame):
        """Update position plot / 更新位置图"""
        data = self.receiver.get_latest_data(200)
        if not data or not data['timestamps']:
            return
        
        times = np.array(data['timestamps'])
        
        # Update position data
        # 更新位置数据
        if data['position']:
            pos_data = np.array(data['position'])
            
            for i, label in enumerate(['X', 'Y', 'Z']):
                self.pos_lines[f'pos_{label}'].set_data(times, pos_data[:, i])
            
            # Update trajectory plots
            # 更新轨迹图
            self.pos_lines['trajectory_xy'].set_data(pos_data[:, 0], pos_data[:, 1])
            self.pos_lines['trajectory_xz'].set_data(pos_data[:, 0], pos_data[:, 2])
            self.pos_lines['trajectory_yz'].set_data(pos_data[:, 1], pos_data[:, 2])
        
        # Auto-scale axes
        # 自动缩放坐标轴
        for ax in self.pos_axes.flat:
            ax.relim()
            ax.autoscale_view()
    
    def update_3d_plot(self, frame):
        """Update 3D plot / 更新3D图"""
        data = self.receiver.get_latest_data(200)
        if not data or not data['timestamps']:
            return
        
        # Update 3D trajectory
        # 更新3D轨迹
        if data['position']:
            pos_data = np.array(data['position'])
            
            # Update trajectory
            # 更新轨迹
            self.trajectory_3d.set_data_3d(pos_data[:, 0], pos_data[:, 1], pos_data[:, 2])
            
            # Update current position
            # 更新当前位置
            if len(pos_data) > 0:
                current_pos = pos_data[-1]
                self.current_pos_3d.set_data_3d([current_pos[0]], [current_pos[1]], [current_pos[2]])
                
                # Update orientation arrows (simplified)
                # 更新方向箭头（简化版）
                if data['quaternion']:
                    quat = data['quaternion'][-1]
                    # Here you could add orientation visualization
                    # 这里可以添加方向可视化
        
        # Auto-scale 3D axes
        # 自动缩放3D坐标轴
        if data['position'] and len(data['position']) > 0:
            pos_data = np.array(data['position'])
            if len(pos_data) > 0:
                self.ax_3d.set_xlim([pos_data[:, 0].min() - 0.1, pos_data[:, 0].max() + 0.1])
                self.ax_3d.set_ylim([pos_data[:, 1].min() - 0.1, pos_data[:, 1].max() + 0.1])
                self.ax_3d.set_zlim([pos_data[:, 2].min() - 0.1, pos_data[:, 2].max() + 0.1])
    
    def run(self):
        """Run the visualizer / 运行可视化器"""
        self.root.mainloop()


if __name__ == "__main__":
    # Create and run the visualizer
    # 创建并运行可视化器
    visualizer = RealtimeVisualizer()
    visualizer.run() 