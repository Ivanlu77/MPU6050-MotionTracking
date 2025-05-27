#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-time MPU6050 Motion Tracker
ʵʱMPU6050�˶��켣������
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
        """Initialize the motion tracker / ��ʼ���˶��켣�����"""
        self.receiver = MPU6050Receiver(buffer_size=2000)  # Larger buffer for better tracking
        self.running = False
        
        # Motion detection parameters
        # �˶�������
        self.motion_threshold = 0.5  # m/s? threshold for motion detection
        self.stationary_threshold = 0.2  # m/s? threshold for stationary detection
        self.motion_state = "��ֹ"
        self.total_distance = 0.0
        self.max_speed = 0.0
        self.motion_start_time = 0
        
        # Create main window
        # ����������
        self.root = tk.Tk()
        self.root.title("MPU6050 ʵʱ�˶��켣���")
        self.root.geometry("1400x900")
        
        # Create GUI elements
        # ����GUIԪ��
        self.create_widgets()
        
        # Animation objects
        # ��������
        self.animations = {}
        
        print("ʵʱ�˶��켣�������ʼ�����")
    
    def create_widgets(self):
        """Create GUI widgets / ����GUI���"""
        # Control frame
        # ���ƿ��
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Start/Stop buttons
        # ��ʼ/ֹͣ��ť
        self.start_btn = ttk.Button(control_frame, text="��ʼ���", command=self.start_tracking)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="ֹͣ���", command=self.stop_tracking, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Reset button
        # ���ð�ť
        self.reset_btn = ttk.Button(control_frame, text="���ù켣", command=self.reset_tracking)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Save button
        # ���水ť
        self.save_btn = ttk.Button(control_frame, text="����켣", command=self.save_trajectory)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # Status and info labels
        # ״̬����Ϣ��ǩ
        info_frame = ttk.Frame(control_frame)
        info_frame.pack(side=tk.RIGHT, padx=5)
        
        self.status_label = ttk.Label(info_frame, text="״̬: δ����", font=("Arial", 10, "bold"))
        self.status_label.pack(side=tk.TOP)
        
        self.motion_label = ttk.Label(info_frame, text="�˶�״̬: ��ֹ", foreground="blue")
        self.motion_label.pack(side=tk.TOP)
        
        self.distance_label = ttk.Label(info_frame, text="�ܾ���: 0.00 m")
        self.distance_label.pack(side=tk.TOP)
        
        self.speed_label = ttk.Label(info_frame, text="����ٶ�: 0.00 m/s")
        self.speed_label.pack(side=tk.TOP)
        
        # Create main visualization area
        # ������Ҫ���ӻ�����
        self.create_main_visualization()
    
    def create_main_visualization(self):
        """Create the main visualization area / ������Ҫ���ӻ�����"""
        # Create matplotlib figure with subplots
        # ��������ͼ��matplotlibͼ��
        self.fig = plt.figure(figsize=(14, 8))
        
        # 3D trajectory plot (main plot)
        # 3D�켣ͼ����ͼ��
        self.ax_3d = self.fig.add_subplot(2, 3, (1, 4))
        self.ax_3d.remove()
        self.ax_3d = self.fig.add_subplot(2, 3, (1, 4), projection='3d')
        self.ax_3d.set_title('ʵʱ3D�˶��켣', fontsize=14, fontweight='bold')
        self.ax_3d.set_xlabel('X (m)')
        self.ax_3d.set_ylabel('Y (m)')
        self.ax_3d.set_zlabel('Z (m)')
        
        # XY plane trajectory
        # XYƽ��켣
        self.ax_xy = self.fig.add_subplot(2, 3, 2)
        self.ax_xy.set_title('XYƽ��켣')
        self.ax_xy.set_xlabel('X (m)')
        self.ax_xy.set_ylabel('Y (m)')
        self.ax_xy.grid(True, alpha=0.3)
        self.ax_xy.set_aspect('equal', adjustable='box')
        
        # Speed over time
        # �ٶ���ʱ��仯
        self.ax_speed = self.fig.add_subplot(2, 3, 3)
        self.ax_speed.set_title('�ٶȱ仯')
        self.ax_speed.set_xlabel('ʱ�� (s)')
        self.ax_speed.set_ylabel('�ٶ� (m/s)')
        self.ax_speed.grid(True, alpha=0.3)
        
        # Acceleration magnitude
        # ���ٶȷ�ֵ
        self.ax_acc = self.fig.add_subplot(2, 3, 5)
        self.ax_acc.set_title('���ٶȷ�ֵ')
        self.ax_acc.set_xlabel('ʱ�� (s)')
        self.ax_acc.set_ylabel('���ٶ� (m/s?)')
        self.ax_acc.grid(True, alpha=0.3)
        
        # Motion state indicator
        # �˶�״ָ̬ʾ��
        self.ax_state = self.fig.add_subplot(2, 3, 6)
        self.ax_state.set_title('�˶�״̬')
        self.ax_state.set_xlim(0, 1)
        self.ax_state.set_ylim(0, 1)
        self.ax_state.axis('off')
        
        # Initialize plot elements
        # ��ʼ����ͼԪ��
        self.trajectory_3d, = self.ax_3d.plot([], [], [], 'b-', linewidth=2, alpha=0.8, label='�켣')
        self.current_pos_3d, = self.ax_3d.plot([], [], [], 'ro', markersize=10, label='��ǰλ��')
        self.start_pos_3d, = self.ax_3d.plot([], [], [], 'go', markersize=8, label='��ʼλ��')
        
        self.trajectory_xy, = self.ax_xy.plot([], [], 'b-', linewidth=2, alpha=0.8)
        self.current_pos_xy, = self.ax_xy.plot([], [], 'ro', markersize=8)
        self.start_pos_xy, = self.ax_xy.plot([], [], 'go', markersize=6)
        
        self.speed_line, = self.ax_speed.plot([], [], 'r-', linewidth=2)
        self.acc_line, = self.ax_acc.plot([], [], 'g-', linewidth=2)
        
        # Motion state text
        # �˶�״̬�ı�
        self.state_text = self.ax_state.text(0.5, 0.5, '��ֹ', fontsize=20, fontweight='bold',
                                           ha='center', va='center', color='blue')
        
        self.ax_3d.legend()
        
        # Create canvas
        # ��������
        canvas = FigureCanvasTkAgg(self.fig, self.root)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        plt.tight_layout()
    
    def start_tracking(self):
        """Start motion tracking / ��ʼ�˶�����"""
        if self.receiver.start_receiver():
            self.running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="״̬: ���ڼ���˶�", foreground="green")
            
            # Reset tracking variables
            # ���ø��ٱ���
            self.total_distance = 0.0
            self.max_speed = 0.0
            self.motion_start_time = time.time()
            
            # Start animation
            # ��ʼ����
            self.start_animation()
            
            print("�˶��켣����ѿ�ʼ")
        else:
            messagebox.showerror("����", "�޷��������ݽ�����")
    
    def stop_tracking(self):
        """Stop motion tracking / ֹͣ�˶�����"""
        self.running = False
        self.receiver.stop_receiver()
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="״̬: ��ֹͣ", foreground="red")
        
        # Stop animation
        # ֹͣ����
        self.stop_animation()
        
        print("�˶��켣�����ֹͣ")
    
    def reset_tracking(self):
        """Reset tracking data / ���ø�������"""
        self.receiver.reset_integration()
        self.total_distance = 0.0
        self.max_speed = 0.0
        self.motion_start_time = time.time()
        self.motion_state = "��ֹ"
        
        # Clear plots
        # ���ͼ��
        self.trajectory_3d.set_data_3d([], [], [])
        self.current_pos_3d.set_data_3d([], [], [])
        self.start_pos_3d.set_data_3d([], [], [])
        self.trajectory_xy.set_data([], [])
        self.current_pos_xy.set_data([], [])
        self.start_pos_xy.set_data([], [])
        self.speed_line.set_data([], [])
        self.acc_line.set_data([], [])
        
        self.update_info_labels()
        messagebox.showinfo("��Ϣ", "�켣����������")
    
    def save_trajectory(self):
        """Save trajectory data / ����켣����"""
        self.receiver.save_data_to_csv("motion_trajectory")
        
        # Save additional motion analysis
        # ���������˶�����
        data = self.receiver.get_latest_data(10000)  # Get all data
        if data and data['position']:
            analysis_file = f"motion_analysis_{time.strftime('%Y%m%d_%H%M%S')}.txt"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                f.write("=== �˶��켣�������� ===\n")
                f.write(f"���ʱ��: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"�ܾ���: {self.total_distance:.3f} m\n")
                f.write(f"����ٶ�: {self.max_speed:.3f} m/s\n")
                f.write(f"�˶�ʱ��: {time.time() - self.motion_start_time:.1f} s\n")
                f.write(f"���ݵ���: {len(data['position'])}\n")
                
                if len(data['position']) > 0:
                    pos_data = np.array(data['position'])
                    f.write(f"X�᷶Χ: {pos_data[:, 0].min():.3f} ~ {pos_data[:, 0].max():.3f} m\n")
                    f.write(f"Y�᷶Χ: {pos_data[:, 1].min():.3f} ~ {pos_data[:, 1].max():.3f} m\n")
                    f.write(f"Z�᷶Χ: {pos_data[:, 2].min():.3f} ~ {pos_data[:, 2].max():.3f} m\n")
        
        messagebox.showinfo("��Ϣ", f"�켣�����ѱ���\n��������: {analysis_file}")
    
    def start_animation(self):
        """Start animation / ��ʼ����"""
        self.animation = FuncAnimation(self.fig, self.update_plots, interval=50, blit=False)
    
    def stop_animation(self):
        """Stop animation / ֹͣ����"""
        if hasattr(self, 'animation'):
            self.animation.event_source.stop()
    
    def detect_motion_state(self, linear_acc_data):
        """Detect motion state based on acceleration / ���ڼ��ٶȼ���˶�״̬"""
        if len(linear_acc_data) < 10:
            return "��ֹ"
        
        # Calculate acceleration magnitude
        # ������ٶȷ�ֵ
        acc_magnitude = np.sqrt(np.sum(np.array(linear_acc_data[-10:]) ** 2, axis=1))
        avg_acc = np.mean(acc_magnitude)
        
        if avg_acc > self.motion_threshold:
            return "�˶���"
        elif avg_acc < self.stationary_threshold:
            return "��ֹ"
        else:
            return "�����ƶ�"
    
    def calculate_distance(self, positions):
        """Calculate total distance traveled / �������ƶ�����"""
        if len(positions) < 2:
            return 0.0
        
        pos_array = np.array(positions)
        distances = np.sqrt(np.sum(np.diff(pos_array, axis=0) ** 2, axis=1))
        return np.sum(distances)
    
    def update_info_labels(self):
        """Update information labels / ������Ϣ��ǩ"""
        self.motion_label.config(text=f"�˶�״̬: {self.motion_state}")
        self.distance_label.config(text=f"�ܾ���: {self.total_distance:.3f} m")
        self.speed_label.config(text=f"����ٶ�: {self.max_speed:.3f} m/s")
        
        # Update motion state color
        # �����˶�״̬��ɫ
        if self.motion_state == "�˶���":
            self.motion_label.config(foreground="red")
            self.state_text.set_text("�˶���")
            self.state_text.set_color("red")
        elif self.motion_state == "�����ƶ�":
            self.motion_label.config(foreground="orange")
            self.state_text.set_text("�����ƶ�")
            self.state_text.set_color("orange")
        else:
            self.motion_label.config(foreground="blue")
            self.state_text.set_text("��ֹ")
            self.state_text.set_color("blue")
    
    def update_plots(self, frame):
        """Update all plots / ��������ͼ��"""
        data = self.receiver.get_latest_data(500)
        if not data or not data['timestamps']:
            return
        
        times = np.array(data['timestamps']) / 1000.0  # Convert to seconds
        
        # Update motion state
        # �����˶�״̬
        if data['linear_acceleration']:
            self.motion_state = self.detect_motion_state(data['linear_acceleration'])
        
        # Update 3D trajectory
        # ����3D�켣
        if data['position']:
            pos_data = np.array(data['position'])
            
            # Update trajectory
            # ���¹켣
            self.trajectory_3d.set_data_3d(pos_data[:, 0], pos_data[:, 1], pos_data[:, 2])
            
            # Update current position
            # ���µ�ǰλ��
            if len(pos_data) > 0:
                current_pos = pos_data[-1]
                self.current_pos_3d.set_data_3d([current_pos[0]], [current_pos[1]], [current_pos[2]])
                
                # Update start position
                # ������ʼλ��
                start_pos = pos_data[0]
                self.start_pos_3d.set_data_3d([start_pos[0]], [start_pos[1]], [start_pos[2]])
                
                # Calculate total distance
                # �����ܾ���
                self.total_distance = self.calculate_distance(pos_data)
            
            # Update XY trajectory
            # ����XY�켣
            self.trajectory_xy.set_data(pos_data[:, 0], pos_data[:, 1])
            if len(pos_data) > 0:
                self.current_pos_xy.set_data([current_pos[0]], [current_pos[1]])
                self.start_pos_xy.set_data([start_pos[0]], [start_pos[1]])
        
        # Update speed plot
        # �����ٶ�ͼ
        if data['velocity']:
            vel_data = np.array(data['velocity'])
            speed_data = np.sqrt(np.sum(vel_data ** 2, axis=1))
            self.speed_line.set_data(times, speed_data)
            
            if len(speed_data) > 0:
                self.max_speed = max(self.max_speed, np.max(speed_data))
        
        # Update acceleration plot
        # ���¼��ٶ�ͼ
        if data['linear_acceleration']:
            acc_data = np.array(data['linear_acceleration'])
            acc_magnitude = np.sqrt(np.sum(acc_data ** 2, axis=1))
            self.acc_line.set_data(times, acc_magnitude)
        
        # Auto-scale axes
        # �Զ�����������
        if data['position'] and len(data['position']) > 0:
            pos_data = np.array(data['position'])
            
            # 3D plot limits
            # 3Dͼ����
            margin = 0.1
            self.ax_3d.set_xlim([pos_data[:, 0].min() - margin, pos_data[:, 0].max() + margin])
            self.ax_3d.set_ylim([pos_data[:, 1].min() - margin, pos_data[:, 1].max() + margin])
            self.ax_3d.set_zlim([pos_data[:, 2].min() - margin, pos_data[:, 2].max() + margin])
            
            # XY plot limits
            # XYͼ����
            self.ax_xy.set_xlim([pos_data[:, 0].min() - margin, pos_data[:, 0].max() + margin])
            self.ax_xy.set_ylim([pos_data[:, 1].min() - margin, pos_data[:, 1].max() + margin])
        
        # Auto-scale time-based plots
        # �Զ����Ż���ʱ���ͼ��
        for ax in [self.ax_speed, self.ax_acc]:
            ax.relim()
            ax.autoscale_view()
        
        # Update info labels
        # ������Ϣ��ǩ
        self.update_info_labels()
    
    def run(self):
        """Run the motion tracker / �����˶��켣�����"""
        self.root.mainloop()


if __name__ == "__main__":
    # Create and run the motion tracker
    # �����������˶��켣�����
    tracker = MotionTracker()
    tracker.run() 