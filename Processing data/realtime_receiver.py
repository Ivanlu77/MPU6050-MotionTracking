#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-time MPU6050 Data Receiver and Processor
ʵʱMPU6050���ݽ��պʹ������
"""

import socket
import struct
import threading
import time
import numpy as np
import pandas as pd
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for better compatibility

class MPU6050Receiver:
    def __init__(self, port=8888, buffer_size=1000):
        """
        Initialize the MPU6050 data receiver
        ��ʼ��MPU6050���ݽ�����
        
        Args:
            port: UDP port to listen on / ������UDP�˿�
            buffer_size: Maximum number of data points to keep in memory / �ڴ��б��ֵ�������ݵ���
        """
        self.port = port
        self.buffer_size = buffer_size
        self.running = False
        self.socket = None
        
        # Data buffers using deque for efficient append/pop operations
        # ʹ��deque���и�Ч�����ݻ������
        self.timestamps = deque(maxlen=buffer_size)
        self.acc_data = deque(maxlen=buffer_size)
        self.gyr_data = deque(maxlen=buffer_size)
        self.quat_data = deque(maxlen=buffer_size)
        self.linear_acc_data = deque(maxlen=buffer_size)
        
        # Processed data buffers
        # ���������ݻ���
        self.velocity_data = deque(maxlen=buffer_size)
        self.position_data = deque(maxlen=buffer_size)
        self.euler_data = deque(maxlen=buffer_size)
        
        # Data processing parameters
        # ���ݴ������
        self.last_timestamp = 0
        self.velocity = np.array([0.0, 0.0, 0.0])
        self.position = np.array([0.0, 0.0, 0.0])
        
        # Thread lock for data synchronization
        # ����ͬ�����߳���
        self.data_lock = threading.Lock()
        
        print("MPU6050��������ʼ�����")
    
    def start_receiver(self):
        """Start the UDP receiver thread / ����UDP�����߳�"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind(('', self.port))
            self.socket.settimeout(1.0)  # 1 second timeout
            self.running = True
            
            print(f"��ʼ�����˿� {self.port}...")
            
            # Start receiver thread
            # ���������߳�
            self.receiver_thread = threading.Thread(target=self._receive_data)
            self.receiver_thread.daemon = True
            self.receiver_thread.start()
            
            return True
            
        except Exception as e:
            print(f"����������ʧ��: {e}")
            return False
    
    def stop_receiver(self):
        """Stop the UDP receiver / ֹͣUDP������"""
        self.running = False
        if self.socket:
            self.socket.close()
        print("��������ֹͣ")
    
    def _receive_data(self):
        """Internal method to receive UDP data / ����UDP���ݵ��ڲ�����"""
        # Data packet structure: timestamp(8) + acc(6) + gyr(6) + quat(16) + linear_acc(6) = 42 bytes
        # ���ݰ��ṹ��ʱ���(8) + ���ٶ�(6) + ������(6) + ��Ԫ��(16) + ���Լ��ٶ�(6) = 42�ֽ�
        packet_format = 'l3h3h4f3h'  # long + 3*short + 3*short + 4*float + 3*short
        packet_size = struct.calcsize(packet_format)
        
        while self.running:
            try:
                data, addr = self.socket.recvfrom(1024)
                
                if len(data) == packet_size:
                    # Unpack the data packet
                    # �������
                    unpacked = struct.unpack(packet_format, data)
                    
                    timestamp = unpacked[0]
                    acc = np.array(unpacked[1:4], dtype=np.float32)
                    gyr = np.array(unpacked[4:7], dtype=np.float32)
                    quat = np.array(unpacked[7:11], dtype=np.float32)
                    linear_acc = np.array(unpacked[11:14], dtype=np.float32)
                    
                    # Process and store data
                    # �����洢����
                    self._process_data(timestamp, acc, gyr, quat, linear_acc)
                    
                else:
                    print(f"���յ������С�����ݰ�: {len(data)} bytes")
                    
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"��������ʱ����: {e}")
    
    def _process_data(self, timestamp, acc, gyr, quat, linear_acc):
        """Process incoming sensor data / ������Ĵ���������"""
        with self.data_lock:
            # Store raw data
            # �洢ԭʼ����
            self.timestamps.append(timestamp)
            self.acc_data.append(acc)
            self.gyr_data.append(gyr)
            self.quat_data.append(quat)
            self.linear_acc_data.append(linear_acc)
            
            # Calculate time delta
            # ����ʱ���
            if self.last_timestamp > 0:
                dt = (timestamp - self.last_timestamp) / 1000.0  # Convert to seconds
                
                if dt > 0 and dt < 1.0:  # Sanity check for reasonable time delta
                    # Convert linear acceleration from sensor units to m/s?
                    # �����Լ��ٶȴӴ�������λת��Ϊm/s?
                    linear_acc_ms2 = linear_acc / 4096.0 * 9.81  # Assuming ��8g range
                    
                    # Integrate acceleration to get velocity
                    # ���ּ��ٶȵõ��ٶ�
                    self.velocity += linear_acc_ms2 * dt
                    
                    # Integrate velocity to get position
                    # �����ٶȵõ�λ��
                    self.position += self.velocity * dt
                    
                    # Store processed data
                    # �洢����������
                    self.velocity_data.append(self.velocity.copy())
                    self.position_data.append(self.position.copy())
                    
                    # Convert quaternion to Euler angles
                    # ����Ԫ��ת��Ϊŷ����
                    euler = self._quaternion_to_euler(quat)
                    self.euler_data.append(euler)
            
            self.last_timestamp = timestamp
    
    def _quaternion_to_euler(self, q):
        """Convert quaternion to Euler angles / ����Ԫ��ת��Ϊŷ����"""
        w, x, y, z = q
        
        # Roll (x-axis rotation)
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = np.arctan2(sinr_cosp, cosr_cosp)
        
        # Pitch (y-axis rotation)
        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            pitch = np.copysign(np.pi / 2, sinp)
        else:
            pitch = np.arcsin(sinp)
        
        # Yaw (z-axis rotation)
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = np.arctan2(siny_cosp, cosy_cosp)
        
        return np.array([roll, pitch, yaw])
    
    def get_latest_data(self, num_points=100):
        """Get the latest data points / ��ȡ���µ����ݵ�"""
        with self.data_lock:
            if len(self.timestamps) == 0:
                return None
            
            # Get the last num_points data points
            # ��ȡ���num_points�����ݵ�
            n = min(num_points, len(self.timestamps))
            
            data = {
                'timestamps': list(self.timestamps)[-n:],
                'acceleration': list(self.acc_data)[-n:],
                'gyroscope': list(self.gyr_data)[-n:],
                'quaternion': list(self.quat_data)[-n:],
                'linear_acceleration': list(self.linear_acc_data)[-n:],
                'velocity': list(self.velocity_data)[-n:] if self.velocity_data else [],
                'position': list(self.position_data)[-n:] if self.position_data else [],
                'euler': list(self.euler_data)[-n:] if self.euler_data else []
            }
            
            return data
    
    def reset_integration(self):
        """Reset velocity and position integration / �����ٶȺ�λ�û���"""
        with self.data_lock:
            self.velocity = np.array([0.0, 0.0, 0.0])
            self.position = np.array([0.0, 0.0, 0.0])
            self.velocity_data.clear()
            self.position_data.clear()
            print("�����������")
    
    def save_data_to_csv(self, filename_prefix="mpu6050_data"):
        """Save current data to CSV files / ����ǰ���ݱ��浽CSV�ļ�"""
        with self.data_lock:
            if len(self.timestamps) == 0:
                print("û�����ݿɱ���")
                return
            
            # Create DataFrames
            # ����DataFrame
            df_acc = pd.DataFrame({
                'time': list(self.timestamps),
                'accx': [d[0] for d in self.acc_data],
                'accy': [d[1] for d in self.acc_data],
                'accz': [d[2] for d in self.acc_data]
            })
            
            df_gyr = pd.DataFrame({
                'time': list(self.timestamps),
                'gyrx': [d[0] for d in self.gyr_data],
                'gyry': [d[1] for d in self.gyr_data],
                'gyrz': [d[2] for d in self.gyr_data]
            })
            
            df_quat = pd.DataFrame({
                'time': list(self.timestamps),
                'qw': [d[0] for d in self.quat_data],
                'qx': [d[1] for d in self.quat_data],
                'qy': [d[2] for d in self.quat_data],
                'qz': [d[3] for d in self.quat_data]
            })
            
            # Save to CSV files
            # ���浽CSV�ļ�
            timestamp_str = time.strftime("%Y%m%d_%H%M%S")
            df_acc.to_csv(f"{filename_prefix}_acc_{timestamp_str}.csv", index=False)
            df_gyr.to_csv(f"{filename_prefix}_gyr_{timestamp_str}.csv", index=False)
            df_quat.to_csv(f"{filename_prefix}_quat_{timestamp_str}.csv", index=False)
            
            print(f"�����ѱ��浽 {filename_prefix}_*_{timestamp_str}.csv")


if __name__ == "__main__":
    # Test the receiver
    # ���Խ�����
    receiver = MPU6050Receiver()
    
    if receiver.start_receiver():
        try:
            print("������������... ��Ctrl+Cֹͣ")
            while True:
                time.sleep(1)
                data = receiver.get_latest_data(10)
                if data and data['timestamps']:
                    latest_time = data['timestamps'][-1]
                    print(f"��������ʱ���: {latest_time}ms")
                
        except KeyboardInterrupt:
            print("\n����ֹͣ������...")
            receiver.stop_receiver()
    else:
        print("�޷�����������") 