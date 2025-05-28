# WiringPi 安装指南

## 在树莓派上安装 WiringPi

### 方法1：使用包管理器（推荐）
```bash
# 更新包列表
sudo apt update

# 安装wiringPi
sudo apt install wiringpi

# 验证安装
gpio -v
gpio readall
```

### 方法2：手动安装最新版本
```bash
# 下载最新版本
cd /tmp
wget https://project-downloads.drogon.net/wiringpi-latest.deb

# 安装
sudo dpkg -i wiringpi-latest.deb

# 验证安装
gpio -v
```

### 方法3：从源码编译
```bash
# 克隆源码
git clone https://github.com/WiringPi/WiringPi.git
cd WiringPi

# 编译安装
./build

# 验证安装
gpio -v
```

## 在Windows上的解决方案

### 选项1：使用WSL（Windows Subsystem for Linux）
```bash
# 安装WSL2和Ubuntu
# 在WSL中安装wiringPi
sudo apt update
sudo apt install wiringpi

# 注意：WSL中无法直接访问GPIO，仅用于编译测试
```

### 选项2：交叉编译环境
```bash
# 安装交叉编译工具链
sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf

# 下载树莓派的wiringPi库文件
# 设置交叉编译环境
```

### 选项3：创建模拟版本（用于测试）
如果只是想测试代码逻辑，可以创建wiringPi的模拟版本。

## 验证安装

安装完成后，运行以下命令验证：

```bash
# 检查版本
gpio -v

# 读取所有GPIO状态
gpio readall

# 测试GPIO（小心操作）
gpio mode 0 out
gpio write 0 1
gpio write 0 0
```

## 常见问题

### 1. 权限问题
```bash
# 将用户添加到gpio组
sudo usermod -a -G gpio $USER

# 重新登录或重启
```

### 2. 树莓派4兼容性
```bash
# 如果在树莓派4上遇到问题，使用最新版本
wget https://project-downloads.drogon.net/wiringpi-latest.deb
sudo dpkg -i wiringpi-latest.deb
```

### 3. I2C权限
```bash
# 启用I2C
sudo raspi-config
# Interface Options -> I2C -> Enable

# 添加用户到i2c组
sudo usermod -a -G i2c $USER
```

## 编译MPU6050程序

安装wiringPi后，编译程序：

```bash
cd "MPU6050-MotionTracking/Collect data"

# 创建数据目录
mkdir -p Datas

# 编译
make -f Makefile_keyboard

# 运行
sudo ./collect_data_keyboard
``` 