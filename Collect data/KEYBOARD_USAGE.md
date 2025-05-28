# MPU6050 键盘控制版本使用指南

## 修改说明

这个版本基于原始的`collect_data.cpp`，保持了所有原有功能，只是将按钮控制改为键盘输入控制：

### 主要变化：
- **移除**: 按钮GPIO控制和长按关机功能
- **保持**: LED状态指示、数据格式、校准偏移量、所有算法
- **新增**: 键盘输入控制（'s'开始/停止，'q'退出）

## 编译和运行

### 1. 编译程序
```bash
cd "MPU6050-MotionTracking/Collect data"

# 使用新的Makefile编译
make -f Makefile_keyboard clean
make -f Makefile_keyboard

# 或者手动编译
g++ -Wall -g -O3 -std=c++17 -o collect_data_keyboard collect_data.cpp I2Cdev.cpp MPU6050.cpp -lwiringPi -lm -lpthread
```

### 2. 运行程序
```bash
sudo ./collect_data_keyboard
```

## 使用方法

### 程序启动流程：
1. **初始化阶段（25秒）**
   - 红灯亮起，绿灯熄灭
   - 程序显示初始化信息
   - 等待25秒让传感器稳定

2. **准备阶段**
   - 绿灯亮起（红灯仍亮）
   - 显示控制说明
   - 可以开始使用键盘控制

### 键盘控制：
- **'s' 或 'S'**: 开始/停止数据收集
- **'q' 或 'Q'**: 退出程序

### LED状态指示：
| 红灯 | 绿灯 | 状态 |
|------|------|------|
| 亮 | 灭 | 初始化中（25秒） |
| 亮 | 亮 | 准备就绪 |
| 灭 | 亮 | 正在收集数据 |

## 数据存储

数据存储格式与原版完全相同：

### 存储位置：
```
./Datas/
├── data_0/
│   ├── Data_Accel.txt
│   ├── Data_Gyro.txt
│   ├── Data_Quaternions.txt
│   └── Data_LinearAcc.txt
├── data_1/
└── ...
```

### 数据格式：

#### Data_Quaternions.txt
```csv
time,qw,qx,qy,qz
5,0.74213,-0.04791,0.01538,0.66833
10,0.74213,-0.04767,0.01550,0.66833
```

#### Data_LinearAcc.txt
```csv
time,accx,accy,accz
5,3,-4,59
10,-47,81,146
```

#### Data_Accel.txt
```csv
time,accx,accy,accz
5,1234,5678,9012
10,1235,5679,9013
```

#### Data_Gyro.txt
```csv
time,gyrx,gyry,gyrz
5,123,456,789
10,124,457,790
```

## 校准设置

程序使用与原版相同的校准偏移量：
```cpp
mpu.setXAccelOffset(-2757);
mpu.setYAccelOffset(417);
mpu.setZAccelOffset(1191);
mpu.setXGyroOffset(-609);
mpu.setYGyroOffset(-474);
mpu.setZGyroOffset(415);
```

如需重新校准，可以运行：
```bash
sudo ./IMU_zero
```

## 与原版的兼容性

### 完全兼容：
- ? 数据格式完全相同
- ? 文件结构完全相同
- ? 校准偏移量相同
- ? 算法和处理逻辑相同
- ? 可以直接用原有的Python处理程序

### 主要区别：
- ? 不支持按钮控制
- ? 不支持长按关机
- ? 支持键盘控制
- ? 更好的用户反馈

## 使用示例

```bash
# 1. 编译
make -f Makefile_keyboard

# 2. 运行
sudo ./collect_data_keyboard

# 3. 等待初始化完成（25秒）
# 看到绿灯亮起和"Controls:"提示

# 4. 开始数据收集
# 按 's' 键

# 5. 移动传感器进行数据收集
# 观察实时数据输出

# 6. 停止数据收集
# 再按 's' 键

# 7. 退出程序
# 按 'q' 键
```

## 故障排除

### 常见问题：

1. **编译错误**
   ```bash
   # 检查依赖
   sudo apt-get install libgtkmm-3.0-dev wiringpi
   ```

2. **权限错误**
   ```bash
   # 必须使用sudo运行
   sudo ./collect_data_keyboard
   ```

3. **键盘输入无响应**
   - 确保终端窗口有焦点
   - 不需要按回车，直接按键即可

4. **数据文件夹不存在**
   ```bash
   mkdir -p Datas
   ```

## 数据处理

收集完数据后，可以直接使用原有的Python处理程序：

```bash
# 将数据复制到处理目录（如果需要）
cp -r Datas/* "../Processing data/Datas/"

# 运行Python处理程序
cd "../Processing data"
python main.py
```

数据格式完全兼容，无需任何修改。 