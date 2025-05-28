# 原始数据收集程序测试指南

## 1. 硬件连接

根据README.md，你需要连接以下硬件：

### GPIO连接表
| GPIO引脚 | 组件 | 说明 |
|---------|------|------|
| GPIO 8 (SDA) | MPU6050 SDA | I2C数据线 |
| GPIO 9 (SCL) | MPU6050 SCL | I2C时钟线 |
| GPIO 0 | 绿色LED | 状态指示 |
| GPIO 2 | 红色LED | 状态指示 |
| GPIO 3 | 按钮 | 控制数据收集 |

### LED状态说明
| 绿灯 | 红灯 | 状态 |
|------|------|------|
| 0 | 1 | 等待中(25秒倒计时) |
| 1 | 1 | 准备就绪 |
| 1 | 0 | 正在收集数据 |

## 2. 编译程序

### 安装依赖
```bash
# 安装必要的库
sudo apt-get update
sudo apt-get install libgtkmm-3.0-dev
sudo apt-get install wiringpi

# 如果是树莓派4或更新版本，可能需要手动安装wiringPi
# wget https://project-downloads.drogon.net/wiringpi-latest.deb
# sudo dpkg -i wiringpi-latest.deb
```

### 编译
```bash
cd "MPU6050-MotionTracking/Collect data"
make clean
make
```

这会生成两个可执行文件：
- `collect_data` - 主要的数据收集程序
- `IMU_zero` - 校准程序

## 3. 校准传感器（可选但推荐）

```bash
sudo ./IMU_zero
```

这个程序会：
1. 运行一段时间收集校准数据
2. 输出最大和最小值用于校准
3. 你可以将这些值更新到`collect_data.cpp`中的偏移量设置

## 4. 运行数据收集程序

```bash
sudo ./collect_data
```

### 程序运行流程：

1. **初始化阶段（25秒）**
   - 红灯亮起，绿灯熄灭
   - 程序初始化MPU6050传感器
   - 等待25秒让传感器稳定

2. **准备阶段**
   - 红灯和绿灯都亮起
   - 可以按按钮开始数据收集

3. **数据收集阶段**
   - 按下按钮开始收集
   - 红灯熄灭，绿灯亮起
   - 再次按按钮停止收集

4. **特殊功能**
   - 长按按钮5秒以上：树莓派关机

## 5. 数据存储位置

数据会自动保存在：
```
MPU6050-MotionTracking/Collect data/Datas/
├── data_0/
│   ├── Data_Quaternions.txt
│   ├── Data_LinearAcc.txt
│   └── Description.txt
├── data_1/
├── data_2/
└── ...
```

每次收集会创建一个新的`data_X`文件夹，包含：
- **Data_Quaternions.txt**: 四元数数据 (time,qw,qx,qy,qz)
- **Data_LinearAcc.txt**: 线性加速度数据 (time,accx,accy,accz)
- **Description.txt**: 描述文件

## 6. 数据格式说明

### Data_Quaternions.txt
```csv
time,qw,qx,qy,qz
5,0.74213,-0.04791,0.01538,0.66833
10,0.74213,-0.04767,0.01550,0.66833
...
```
- time: 时间戳(毫秒)
- qw,qx,qy,qz: 四元数分量(浮点数)

### Data_LinearAcc.txt
```csv
time,accx,accy,accz
5,3,-4,59
10,-47,81,146
...
```
- time: 时间戳(毫秒)
- accx,accy,accz: 线性加速度(整数，传感器原始单位)

## 7. 测试步骤

### 基本测试：
1. 连接硬件
2. 编译程序：`make`
3. 运行：`sudo ./collect_data`
4. 等待25秒直到绿灯亮起
5. 按按钮开始收集数据
6. 移动传感器一段时间
7. 再按按钮停止收集
8. 检查`Datas/data_X/`文件夹中的数据

### 验证数据：
```bash
# 查看最新收集的数据
ls -la Datas/
cd Datas/data_X/  # X是最新的数字
head -10 Data_Quaternions.txt
head -10 Data_LinearAcc.txt
```

## 8. 故障排除

### 常见问题：

1. **编译错误**
   ```bash
   # 检查依赖
   pkg-config --exists gtkmm-3.0
   which gpio
   ```

2. **I2C错误**
   ```bash
   # 检查I2C设备
   sudo i2cdetect -y 1
   # 应该看到0x68地址的MPU6050
   ```

3. **权限错误**
   ```bash
   # 确保以root权限运行
   sudo ./collect_data
   ```

4. **GPIO错误**
   ```bash
   # 检查wiringPi安装
   gpio readall
   ```

## 9. 数据处理

收集完数据后，将`Datas`文件夹复制到：
```
MPU6050-MotionTracking/Processing data/Datas/
```

然后可以运行Python处理程序：
```bash
cd "MPU6050-MotionTracking/Processing data"
python main.py
```

## 10. 注意事项

- 确保MPU6050正确连接到I2C总线
- 程序需要root权限访问GPIO
- 数据收集期间保持传感器稳定连接
- 每次收集会自动创建新的数据文件夹
- 长按按钮会关机，小心操作 