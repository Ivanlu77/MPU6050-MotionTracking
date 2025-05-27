#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-time MPU6050 Motion Tracker
实时MPU6050运动轨迹检测程序
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
from scipy.signal import butter, filtfilt

class MotionTracker:
    def __init__(self):
        """Initialize the motion tracker / 初始化运动轨迹检测器"""
        self.receiver = MPU6050Receiver(buffer_size=2000)  # Larger buffer for better tracking
        self.running = False
        
        # Motion detection parameters
        # 运动检测参数
        self.motion_threshold = 0.5  # m/s? threshold for motion detection
        self.stationary_threshold = 0.2  # m/s? threshold for stationary detection
        self.motion_state = "静止"
        self.total_distance = 0.0
        self.max_speed = 0.0
        self.motion_start_time = 0
        
        # Create main window
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("MPU6050 实时运动轨迹检测")
        self.root.geometry("1400x900")
        
        # Create GUI elements
        # 创建GUI元素
        self.create_widgets()
        
        # Animation objects
        # 动画对象
        self.animations = {}
        
        print("实时运动轨迹检测器初始化完成")
    
    def create_widgets(self):
        """Create GUI widgets / 创建GUI组件"""
        # Control frame
        # 控制框架
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Start/Stop buttons
        # 开始/停止按钮
        self.start_btn = ttk.Button(control_frame, text="开始检测", command=self.start_tracking)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="停止检测", command=self.stop_tracking, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Reset button
        # 重置按钮
        self.reset_btn = ttk.Button(control_frame, text="重置轨迹", command=self.reset_tracking)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Save button
        # 保存按钮
        self.save_btn = ttk.Button(control_frame, text="保存轨迹", command=self.save_trajectory)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # Status and info labels
        # 状态和信息标签
        info_frame = ttk.Frame(control_frame)
        info_frame.pack(side=tk.RIGHT, padx=5)
        
        self.status_label = ttk.Label(info_frame, text="状态: 未连接", font=("Arial", 10, "bold"))
        self.status_label.pack(side=tk.TOP)
        
        self.motion_label = ttk.Label(info_frame, text="运动状态: 静止", foreground="blue")
        self.motion_label.pack(side=tk.TOP)
        
        self.distance_label = ttk.Label(info_frame, text="总距离: 0.00 m")
        self.distance_label.pack(side=tk.TOP)
        
        self.speed_label = ttk.Label(info_frame, text="最大速度: 0.00 m/s")
        self.speed_label.pack(side=tk.TOP)
        
        # Create main visualization area
        # 创建主要可视化区域
        self.create_main_visualization()
    
    def create_main_visualization(self):
        """Create the main visualization area / 创建主要可视化区域"""
        # Create matplotlib figure with subplots
        # 创建带子图的matplotlib图形
        self.fig = plt.figure(figsize=(14, 8))
        
        # 3D trajectory plot (main plot)
        # 3D轨迹图（主图）
        self.ax_3d = self.fig.add_subplot(2, 3, (1, 4))
        self.ax_3d.remove()
        self.ax_3d = self.fig.add_subplot(2, 3, (1, 4), projection='3d')
        self.ax_3d.set_title('实时3D运动轨迹', fontsize=14, fontweight='bold')
        self.ax_3d.set_xlabel('X (m)')
        self.ax_3d.set_ylabel('Y (m)')
        self.ax_3d.set_zlabel('Z (m)')
        
        # XY plane trajectory
        # XY平面轨迹
        self.ax_xy = self.fig.add_subplot(2, 3, 2)
        self.ax_xy.set_title('XY平面轨迹')
        self.ax_xy.set_xlabel('X (m)')
        self.ax_xy.set_ylabel('Y (m)')
        self.ax_xy.grid(True, alpha=0.3)
        self.ax_xy.set_aspect('equal', adjustable='box')
        
        # Speed over time
        # 速度随时间变化
        self.ax_speed = self.fig.add_subplot(2, 3, 3)
        self.ax_speed.set_title('速度变化')
        self.ax_speed.set_xlabel('时间 (s)')
        self.ax_speed.set_ylabel('速度 (m/s)')
        self.ax_speed.grid(True, alpha=0.3)
        
        # Acceleration magnitude
        # 加速度幅值
        self.ax_acc = self.fig.add_subplot(2, 3, 5)
        self.ax_acc.set_title('加速度幅值')
        self.ax_acc.set_xlabel('时间 (s)')
        self.ax_acc.set_ylabel('加速度 (m/s?)')
        self.ax_acc.grid(True, alpha=0.3)
        
        # Motion state indicator
        # 运动状态指示器
        self.ax_state = self.fig.add_subplot(2, 3, 6)
        self.ax_state.set_title('运动状态')
        self.ax_state.set_xlim(0, 1)
        self.ax_state.set_ylim(0, 1)
        self.ax_state.axis('off')
        
        # Initialize plot elements
        # 初始化绘图元素
        self.trajectory_3d, = self.ax_3d.plot([], [], [], 'b-', linewidth=2, alpha=0.8, label='轨迹')
        self.current_pos_3d, = self.ax_3d.plot([], [], [], 'ro', markersize=10, label='当前位置')
        self.start_pos_3d, = self.ax_3d.plot([], [], [], 'go', markersize=8, label='起始位置')
        
        self.trajectory_xy, = self.ax_xy.plot([], [], 'b-', linewidth=2, alpha=0.8)
        self.current_pos_xy, = self.ax_xy.plot([], [], 'ro', markersize=8)
        self.start_pos_xy, = self.ax_xy.plot([], [], 'go', markersize=6)
        
        self.speed_line, = self.ax_speed.plot([], [], 'r-', linewidth=2)
        self.acc_line, = self.ax_acc.plot([], [], 'g-', linewidth=2)
        
        # Motion state text
        # 运动状态文本
        self.state_text = self.ax_state.text(0.5, 0.5, '静止', fontsize=20, fontweight='bold',
                                           ha='center', va='center', color='blue')
        
        self.ax_3d.legend()
        
        # Create canvas
        # 创建画布
        canvas = FigureCanvasTkAgg(self.fig, self.root)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        plt.tight_layout()
    
    def start_tracking(self):
        """Start motion tracking / 开始运动跟踪"""
        if self.receiver.start_receiver():
            self.running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="状态: 正在检测运动", foreground="green")
            
            # Reset tracking variables
            # 重置跟踪变量
            self.total_distance = 0.0
            self.max_speed = 0.0
            self.motion_start_time = time.time()
            
            # Start animation
            # 开始动画
            self.start_animation()
            
            print("运动轨迹检测已开始")
        else:
            messagebox.showerror("错误", "无法启动数据接收器")
    
    def stop_tracking(self):
        """Stop motion tracking / 停止运动跟踪"""
        self.running = False
        self.receiver.stop_receiver()
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="状态: 已停止", foreground="red")
        
        # Stop animation
        # 停止动画
        self.stop_animation()
        
        print("运动轨迹检测已停止")
    
    def reset_tracking(self):
        """Reset tracking data / 重置跟踪数据"""
        self.receiver.reset_integration()
        self.total_distance = 0.0
        self.max_speed = 0.0
        self.motion_start_time = time.time()
        self.motion_state = "静止"
        
        # Clear plots
        # 清空图表
        self.trajectory_3d.set_data_3d([], [], [])
        self.current_pos_3d.set_data_3d([], [], [])
        self.start_pos_3d.set_data_3d([], [], [])
        self.trajectory_xy.set_data([], [])
        self.current_pos_xy.set_data([], [])
        self.start_pos_xy.set_data([], [])
        self.speed_line.set_data([], [])
        self.acc_line.set_data([], [])
        
        self.update_info_labels()
        messagebox.showinfo("信息", "轨迹数据已重置")
    
    def save_trajectory(self):
        """Save trajectory data / 保存轨迹数据"""
        self.receiver.save_data_to_csv("motion_trajectory")
        
        # Save additional motion analysis
        # 保存额外的运动分析
        data = self.receiver.get_latest_data(10000)  # Get all data
        if data and data['position']:
            analysis_file = f"motion_analysis_{time.strftime('%Y%m%d_%H%M%S')}.txt"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                f.write("=== 运动轨迹分析报告 ===\n")
                f.write(f"检测时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"总距离: {self.total_distance:.3f} m\n")
                f.write(f"最大速度: {self.max_speed:.3f} m/s\n")
                f.write(f"运动时长: {time.time() - self.motion_start_time:.1f} s\n")
                f.write(f"数据点数: {len(data['position'])}\n")
                
                if len(data['position']) > 0:
                    pos_data = np.array(data['position'])
                    f.write(f"X轴范围: {pos_data[:, 0].min():.3f} ~ {pos_data[:, 0].max():.3f} m\n")
                    f.write(f"Y轴范围: {pos_data[:, 1].min():.3f} ~ {pos_data[:, 1].max():.3f} m\n")
                    f.write(f"Z轴范围: {pos_data[:, 2].min():.3f} ~ {pos_data[:, 2].max():.3f} m\n")
        
        messagebox.showinfo("信息", f"轨迹数据已保存\n分析报告: {analysis_file}")
    
    def start_animation(self):
        """Start animation / 开始动画"""
        self.animation = FuncAnimation(self.fig, self.update_plots, interval=50, blit=False)
    
    def stop_animation(self):
        """Stop animation / 停止动画"""
        if hasattr(self, 'animation'):
            self.animation.event_source.stop()
    
    def detect_motion_state(self, linear_acc_data):
        """Detect motion state based on acceleration / 基于加速度检测运动状态"""
        if len(linear_acc_data) < 10:
            return "静止"
        
        # Calculate acceleration magnitude
        # 计算加速度幅值
        acc_magnitude = np.sqrt(np.sum(np.array(linear_acc_data[-10:]) ** 2, axis=1))
        avg_acc = np.mean(acc_magnitude)
        
        if avg_acc > self.motion_threshold:
            return "运动中"
        elif avg_acc < self.stationary_threshold:
            return "静止"
        else:
            return "缓慢移动"
    
    def calculate_distance(self, positions):
        """Calculate total distance traveled / 计算总移动距离"""
        if len(positions) < 2:
            return 0.0
        
        pos_array = np.array(positions)
        distances = np.sqrt(np.sum(np.diff(pos_array, axis=0) ** 2, axis=1))
        return np.sum(distances)
    
    def update_info_labels(self):
        """Update information labels / 更新信息标签"""
        self.motion_label.config(text=f"运动状态: {self.motion_state}")
        self.distance_label.config(text=f"总距离: {self.total_distance:.3f} m")
        self.speed_label.config(text=f"最大速度: {self.max_speed:.3f} m/s")
        
        # Update motion state color
        # 更新运动状态颜色
        if self.motion_state == "运动中":
            self.motion_label.config(foreground="red")
            self.state_text.set_text("运动中")
            self.state_text.set_color("red")
        elif self.motion_state == "缓慢移动":
            self.motion_label.config(foreground="orange")
            self.state_text.set_text("缓慢移动")
            self.state_text.set_color("orange")
        else:
            self.motion_label.config(foreground="blue")
            self.state_text.set_text("静止")
            self.state_text.set_color("blue")
    
    def update_plots(self, frame):
        """Update all plots / 更新所有图表"""
        data = self.receiver.get_latest_data(500)
        if not data or not data['timestamps']:
            return
        
        times = np.array(data['timestamps']) / 1000.0  # Convert to seconds
        
        # Update motion state
        # 更新运动状态
        if data['linear_acceleration']:
            self.motion_state = self.detect_motion_state(data['linear_acceleration'])
        
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
                
                # Update start position
                # 更新起始位置
                start_pos = pos_data[0]
                self.start_pos_3d.set_data_3d([start_pos[0]], [start_pos[1]], [start_pos[2]])
                
                # Calculate total distance
                # 计算总距离
                self.total_distance = self.calculate_distance(pos_data)
            
            # Update XY trajectory
            # 更新XY轨迹
            self.trajectory_xy.set_data(pos_data[:, 0], pos_data[:, 1])
            if len(pos_data) > 0:
                self.current_pos_xy.set_data([current_pos[0]], [current_pos[1]])
                self.start_pos_xy.set_data([start_pos[0]], [start_pos[1]])
        
        # Update speed plot
        # 更新速度图
        if data['velocity']:
            vel_data = np.array(data['velocity'])
            speed_data = np.sqrt(np.sum(vel_data ** 2, axis=1))
            self.speed_line.set_data(times, speed_data)
            
            if len(speed_data) > 0:
                self.max_speed = max(self.max_speed, np.max(speed_data))
        
        # Update acceleration plot
        # 更新加速度图
        if data['linear_acceleration']:
            acc_data = np.array(data['linear_acceleration'])
            acc_magnitude = np.sqrt(np.sum(acc_data ** 2, axis=1))
            self.acc_line.set_data(times, acc_magnitude)
        
        # Auto-scale axes
        # 自动缩放坐标轴
        if data['position'] and len(data['position']) > 0:
            pos_data = np.array(data['position'])
            
            # 3D plot limits
            # 3D图限制
            margin = 0.1
            self.ax_3d.set_xlim([pos_data[:, 0].min() - margin, pos_data[:, 0].max() + margin])
            self.ax_3d.set_ylim([pos_data[:, 1].min() - margin, pos_data[:, 1].max() + margin])
            self.ax_3d.set_zlim([pos_data[:, 2].min() - margin, pos_data[:, 2].max() + margin])
            
            # XY plot limits
            # XY图限制
            self.ax_xy.set_xlim([pos_data[:, 0].min() - margin, pos_data[:, 0].max() + margin])
            self.ax_xy.set_ylim([pos_data[:, 1].min() - margin, pos_data[:, 1].max() + margin])
        
        # Auto-scale time-based plots
        # 自动缩放基于时间的图表
        for ax in [self.ax_speed, self.ax_acc]:
            ax.relim()
            ax.autoscale_view()
        
        # Update info labels
        # 更新信息标签
        self.update_info_labels()
    
    def run(self):
        """Run the motion tracker / 运行运动轨迹检测器"""
        self.root.mainloop()


if __name__ == "__main__":
    # Create and run the motion tracker
    # 创建并运行运动轨迹检测器
    tracker = MotionTracker()
    tracker.run() 