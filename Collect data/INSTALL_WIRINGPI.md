# WiringPi ��װָ��

## ����ݮ���ϰ�װ WiringPi

### ����1��ʹ�ð����������Ƽ���
```bash
# ���°��б�
sudo apt update

# ��װwiringPi
sudo apt install wiringpi

# ��֤��װ
gpio -v
gpio readall
```

### ����2���ֶ���װ���°汾
```bash
# �������°汾
cd /tmp
wget https://project-downloads.drogon.net/wiringpi-latest.deb

# ��װ
sudo dpkg -i wiringpi-latest.deb

# ��֤��װ
gpio -v
```

### ����3����Դ�����
```bash
# ��¡Դ��
git clone https://github.com/WiringPi/WiringPi.git
cd WiringPi

# ���밲װ
./build

# ��֤��װ
gpio -v
```

## ��Windows�ϵĽ������

### ѡ��1��ʹ��WSL��Windows Subsystem for Linux��
```bash
# ��װWSL2��Ubuntu
# ��WSL�а�װwiringPi
sudo apt update
sudo apt install wiringpi

# ע�⣺WSL���޷�ֱ�ӷ���GPIO�������ڱ������
```

### ѡ��2��������뻷��
```bash
# ��װ������빤����
sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf

# ������ݮ�ɵ�wiringPi���ļ�
# ���ý�����뻷��
```

### ѡ��3������ģ��汾�����ڲ��ԣ�
���ֻ������Դ����߼������Դ���wiringPi��ģ��汾��

## ��֤��װ

��װ��ɺ���������������֤��

```bash
# ���汾
gpio -v

# ��ȡ����GPIO״̬
gpio readall

# ����GPIO��С�Ĳ�����
gpio mode 0 out
gpio write 0 1
gpio write 0 0
```

## ��������

### 1. Ȩ������
```bash
# ���û���ӵ�gpio��
sudo usermod -a -G gpio $USER

# ���µ�¼������
```

### 2. ��ݮ��4������
```bash
# �������ݮ��4���������⣬ʹ�����°汾
wget https://project-downloads.drogon.net/wiringpi-latest.deb
sudo dpkg -i wiringpi-latest.deb
```

### 3. I2CȨ��
```bash
# ����I2C
sudo raspi-config
# Interface Options -> I2C -> Enable

# ����û���i2c��
sudo usermod -a -G i2c $USER
```

## ����MPU6050����

��װwiringPi�󣬱������

```bash
cd "MPU6050-MotionTracking/Collect data"

# ��������Ŀ¼
mkdir -p Datas

# ����
make -f Makefile_keyboard

# ����
sudo ./collect_data_keyboard
``` 