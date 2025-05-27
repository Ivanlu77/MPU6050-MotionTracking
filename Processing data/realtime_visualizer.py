#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-time MPU6050 Data Visualizer
ʵʱMPU6050���ݿ��ӻ�����
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
        """Initialize the real-time visualizer / ��ʼ��ʵʱ���ӻ���"""
        self.receiver = MPU6050Receiver()
        self.running = False
        
        # Create main window
        # ����������
        self.root = tk.Tk()
        self.root.title("MPU6050 ʵʱ���ݿ��ӻ�")
        self.root.geometry("1200x800")
        
        # Create GUI elements
        # ����GUIԪ��
        self.create_widgets()
        
        # Animation objects
        # ��������
        self.animations = {}
        
        print("ʵʱ���ӻ�����ʼ�����")
    
    def create_widgets(self):
        """Create GUI widgets / ����GUI���"""
        # Control frame
        # ���ƿ��
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Start/Stop buttons
        # ��ʼ/ֹͣ��ť
        self.start_btn = ttk.Button(control_frame, text="��ʼ����", command=self.start_visualization)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="ֹͣ����", command=self.stop_visualization, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Reset button
        # ���ð�ť
        self.reset_btn = ttk.Button(control_frame, text="���û���", command=self.reset_integration)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Save button
        # ���水ť
        self.save_btn = ttk.Button(control_frame, text="��������", command=self.save_data)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label
        # ״̬��ǩ
        self.status_label = ttk.Label(control_frame, text="״̬: δ����")
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # Create notebook for different views
        # ������ͬ��ͼ��ѡ�
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create different visualization tabs
        # ������ͬ�Ŀ��ӻ�ѡ�
        self.create_acceleration_tab()
        self.create_rotation_tab()
        self.create_position_tab()
        self.create_3d_tab()
    
    def create_acceleration_tab(self):
        """Create acceleration visualization tab / �������ٶȿ��ӻ�ѡ�"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="���ٶ�����")
        
        # Create matplotlib figure
        # ����matplotlibͼ��
        self.acc_fig, self.acc_axes = plt.subplots(2, 2, figsize=(10, 6))
        self.acc_fig.suptitle('���ٶȺ�����������')
        
        # Setup subplots
        # ������ͼ
        self.acc_axes[0, 0].set_title('ԭʼ���ٶ�')
        self.acc_axes[0, 0].set_ylabel('���ٶ� (LSB)')
        self.acc_axes[0, 1].set_title('���Լ��ٶ�')
        self.acc_axes[0, 1].set_ylabel('���ٶ� (LSB)')
        self.acc_axes[1, 0].set_title('����������')
        self.acc_axes[1, 0].set_ylabel('���ٶ� (LSB)')
        self.acc_axes[1, 1].set_title('�ٶ� (����)')
        self.acc_axes[1, 1].set_ylabel('�ٶ� (m/s)')
        
        for ax in self.acc_axes.flat:
            ax.grid(True, alpha=0.3)
            ax.set_xlabel('ʱ�� (ms)')
        
        # Create canvas
        # ��������
        canvas = FigureCanvasTkAgg(self.acc_fig, frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize line objects
        # ��ʼ����������
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
        """Create rotation visualization tab / ������ת���ӻ�ѡ�"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="��ת����")
        
        # Create matplotlib figure
        # ����matplotlibͼ��
        self.rot_fig, self.rot_axes = plt.subplots(2, 2, figsize=(10, 6))
        self.rot_fig.suptitle('��ת����')
        
        # Setup subplots
        # ������ͼ
        self.rot_axes[0, 0].set_title('��Ԫ��')
        self.rot_axes[0, 0].set_ylabel('��Ԫ��ֵ')
        self.rot_axes[0, 1].set_title('ŷ����')
        self.rot_axes[0, 1].set_ylabel('�Ƕ� (����)')
        self.rot_axes[1, 0].set_title('ŷ���� (��)')
        self.rot_axes[1, 0].set_ylabel('�Ƕ� (��)')
        self.rot_axes[1, 1].set_title('���ٶ�')
        self.rot_axes[1, 1].set_ylabel('���ٶ� (��/��)')
        
        for ax in self.rot_axes.flat:
            ax.grid(True, alpha=0.3)
            ax.set_xlabel('ʱ�� (ms)')
        
        # Create canvas
        # ��������
        canvas = FigureCanvasTkAgg(self.rot_fig, frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize line objects
        # ��ʼ����������
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
        """Create position visualization tab / ����λ�ÿ��ӻ�ѡ�"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="λ������")
        
        # Create matplotlib figure
        # ����matplotlibͼ��
        self.pos_fig, self.pos_axes = plt.subplots(2, 2, figsize=(10, 6))
        self.pos_fig.suptitle('λ�ú͹켣����')
        
        # Setup subplots
        # ������ͼ
        self.pos_axes[0, 0].set_title('λ�� (X, Y, Z)')
        self.pos_axes[0, 0].set_ylabel('λ�� (m)')
        self.pos_axes[0, 1].set_title('XYƽ��켣')
        self.pos_axes[0, 1].set_ylabel('Yλ�� (m)')
        self.pos_axes[0, 1].set_xlabel('Xλ�� (m)')
        self.pos_axes[1, 0].set_title('XZƽ��켣')
        self.pos_axes[1, 0].set_ylabel('Zλ�� (m)')
        self.pos_axes[1, 0].set_xlabel('Xλ�� (m)')
        self.pos_axes[1, 1].set_title('YZƽ��켣')
        self.pos_axes[1, 1].set_ylabel('Zλ�� (m)')
        self.pos_axes[1, 1].set_xlabel('Yλ�� (m)')
        
        for ax in self.pos_axes.flat:
            ax.grid(True, alpha=0.3)
        
        self.pos_axes[0, 0].set_xlabel('ʱ�� (ms)')
        
        # Create canvas
        # ��������
        canvas = FigureCanvasTkAgg(self.pos_fig, frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize line objects
        # ��ʼ����������
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
        """Create 3D visualization tab / ����3D���ӻ�ѡ�"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="3D���ӻ�")
        
        # Create matplotlib figure with 3D subplot
        # ������3D��ͼ��matplotlibͼ��
        self.fig_3d = plt.figure(figsize=(10, 8))
        self.ax_3d = self.fig_3d.add_subplot(111, projection='3d')
        self.ax_3d.set_title('3Dλ�úͷ���')
        self.ax_3d.set_xlabel('X (m)')
        self.ax_3d.set_ylabel('Y (m)')
        self.ax_3d.set_zlabel('Z (m)')
        
        # Create canvas
        # ��������
        canvas = FigureCanvasTkAgg(self.fig_3d, frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize 3D objects
        # ��ʼ��3D����
        self.trajectory_3d, = self.ax_3d.plot([], [], [], 'b-', alpha=0.7, label='�켣')
        self.current_pos_3d, = self.ax_3d.plot([], [], [], 'ro', markersize=8, label='��ǰλ��')
        
        # Orientation arrows
        # �����ͷ
        self.orientation_arrows = {
            'x': None,
            'y': None,
            'z': None
        }
        
        self.ax_3d.legend()
    
    def start_visualization(self):
        """Start the visualization / ��ʼ���ӻ�"""
        if self.receiver.start_receiver():
            self.running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="״̬: ���ڽ�������")
            
            # Start animation
            # ��ʼ����
            self.start_animations()
            
            print("���ӻ��ѿ�ʼ")
        else:
            messagebox.showerror("����", "�޷��������ݽ�����")
    
    def stop_visualization(self):
        """Stop the visualization / ֹͣ���ӻ�"""
        self.running = False
        self.receiver.stop_receiver()
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="״̬: ��ֹͣ")
        
        # Stop animations
        # ֹͣ����
        self.stop_animations()
        
        print("���ӻ���ֹͣ")
    
    def reset_integration(self):
        """Reset integration / ���û���"""
        self.receiver.reset_integration()
        messagebox.showinfo("��Ϣ", "����������")
    
    def save_data(self):
        """Save current data / ���浱ǰ����"""
        self.receiver.save_data_to_csv("realtime_data")
        messagebox.showinfo("��Ϣ", "�����ѱ���")
    
    def start_animations(self):
        """Start all animations / ��ʼ���ж���"""
        self.animations['acc'] = FuncAnimation(self.acc_fig, self.update_acceleration_plot, 
                                             interval=50, blit=False)
        self.animations['rot'] = FuncAnimation(self.rot_fig, self.update_rotation_plot, 
                                             interval=50, blit=False)
        self.animations['pos'] = FuncAnimation(self.pos_fig, self.update_position_plot, 
                                             interval=50, blit=False)
        self.animations['3d'] = FuncAnimation(self.fig_3d, self.update_3d_plot, 
                                            interval=100, blit=False)
    
    def stop_animations(self):
        """Stop all animations / ֹͣ���ж���"""
        for anim in self.animations.values():
            if anim:
                anim.event_source.stop()
        self.animations.clear()
    
    def update_acceleration_plot(self, frame):
        """Update acceleration plot / ���¼��ٶ�ͼ"""
        data = self.receiver.get_latest_data(200)
        if not data or not data['timestamps']:
            return
        
        times = np.array(data['timestamps'])
        
        # Update acceleration data
        # ���¼��ٶ�����
        if data['acceleration']:
            acc_data = np.array(data['acceleration'])
            for i, label in enumerate(['X', 'Y', 'Z']):
                self.acc_lines[f'acc_{label}'].set_data(times, acc_data[:, i])
        
        # Update linear acceleration data
        # �������Լ��ٶ�����
        if data['linear_acceleration']:
            linear_acc_data = np.array(data['linear_acceleration'])
            for i, label in enumerate(['X', 'Y', 'Z']):
                self.acc_lines[f'linear_acc_{label}'].set_data(times, linear_acc_data[:, i])
        
        # Update gyroscope data
        # ��������������
        if data['gyroscope']:
            gyr_data = np.array(data['gyroscope'])
            for i, label in enumerate(['X', 'Y', 'Z']):
                self.acc_lines[f'gyr_{label}'].set_data(times, gyr_data[:, i])
        
        # Update velocity data
        # �����ٶ�����
        if data['velocity']:
            vel_data = np.array(data['velocity'])
            for i, label in enumerate(['X', 'Y', 'Z']):
                self.acc_lines[f'vel_{label}'].set_data(times, vel_data[:, i])
        
        # Auto-scale axes
        # �Զ�����������
        for ax in self.acc_axes.flat:
            ax.relim()
            ax.autoscale_view()
    
    def update_rotation_plot(self, frame):
        """Update rotation plot / ������תͼ"""
        data = self.receiver.get_latest_data(200)
        if not data or not data['timestamps']:
            return
        
        times = np.array(data['timestamps'])
        
        # Update quaternion data
        # ������Ԫ����
        if data['quaternion']:
            quat_data = np.array(data['quaternion'])
            for i, label in enumerate(['W', 'X', 'Y', 'Z']):
                self.rot_lines[f'quat_{label}'].set_data(times, quat_data[:, i])
        
        # Update Euler angles
        # ����ŷ����
        if data['euler']:
            euler_data = np.array(data['euler'])
            euler_deg = euler_data * 180 / np.pi
            
            for i, label in enumerate(['Roll', 'Pitch', 'Yaw']):
                self.rot_lines[f'euler_{label}'].set_data(times, euler_data[:, i])
                self.rot_lines[f'euler_deg_{label}'].set_data(times, euler_deg[:, i])
        
        # Calculate angular velocity from gyroscope
        # �������Ǽ�����ٶ�
        if data['gyroscope']:
            gyr_data = np.array(data['gyroscope'])
            gyr_deg = gyr_data / 131.0  # Convert to degrees/second (assuming ��250��/s range)
            
            for i, label in enumerate(['Roll', 'Pitch', 'Yaw']):
                self.rot_lines[f'angular_vel_{label}'].set_data(times, gyr_deg[:, i])
        
        # Auto-scale axes
        # �Զ�����������
        for ax in self.rot_axes.flat:
            ax.relim()
            ax.autoscale_view()
    
    def update_position_plot(self, frame):
        """Update position plot / ����λ��ͼ"""
        data = self.receiver.get_latest_data(200)
        if not data or not data['timestamps']:
            return
        
        times = np.array(data['timestamps'])
        
        # Update position data
        # ����λ������
        if data['position']:
            pos_data = np.array(data['position'])
            
            for i, label in enumerate(['X', 'Y', 'Z']):
                self.pos_lines[f'pos_{label}'].set_data(times, pos_data[:, i])
            
            # Update trajectory plots
            # ���¹켣ͼ
            self.pos_lines['trajectory_xy'].set_data(pos_data[:, 0], pos_data[:, 1])
            self.pos_lines['trajectory_xz'].set_data(pos_data[:, 0], pos_data[:, 2])
            self.pos_lines['trajectory_yz'].set_data(pos_data[:, 1], pos_data[:, 2])
        
        # Auto-scale axes
        # �Զ�����������
        for ax in self.pos_axes.flat:
            ax.relim()
            ax.autoscale_view()
    
    def update_3d_plot(self, frame):
        """Update 3D plot / ����3Dͼ"""
        data = self.receiver.get_latest_data(200)
        if not data or not data['timestamps']:
            return
        
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
                
                # Update orientation arrows (simplified)
                # ���·����ͷ���򻯰棩
                if data['quaternion']:
                    quat = data['quaternion'][-1]
                    # Here you could add orientation visualization
                    # ���������ӷ�����ӻ�
        
        # Auto-scale 3D axes
        # �Զ�����3D������
        if data['position'] and len(data['position']) > 0:
            pos_data = np.array(data['position'])
            if len(pos_data) > 0:
                self.ax_3d.set_xlim([pos_data[:, 0].min() - 0.1, pos_data[:, 0].max() + 0.1])
                self.ax_3d.set_ylim([pos_data[:, 1].min() - 0.1, pos_data[:, 1].max() + 0.1])
                self.ax_3d.set_zlim([pos_data[:, 2].min() - 0.1, pos_data[:, 2].max() + 0.1])
    
    def run(self):
        """Run the visualizer / ���п��ӻ���"""
        self.root.mainloop()


if __name__ == "__main__":
    # Create and run the visualizer
    # ���������п��ӻ���
    visualizer = RealtimeVisualizer()
    visualizer.run() 