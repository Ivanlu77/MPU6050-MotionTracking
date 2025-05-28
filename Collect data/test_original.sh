#!/bin/bash

echo "=== MPU6050 ԭʼ�����ռ�������Խű� ==="
echo

# ��鵱ǰĿ¼
if [ ! -f "collect_data.cpp" ]; then
    echo "����: ���� 'MPU6050-MotionTracking/Collect data' Ŀ¼�����д˽ű�"
    exit 1
fi

echo "1. �������..."

# ���wiringPi
if ! command -v gpio &> /dev/null; then
    echo "����: wiringPi δ��װ��δ��PATH��"
    echo "������: sudo apt-get install wiringpi"
else
    echo "? wiringPi �Ѱ�װ"
fi

# ���gtkmm
if ! pkg-config --exists gtkmm-3.0; then
    echo "����: gtkmm-3.0 δ��װ"
    echo "������: sudo apt-get install libgtkmm-3.0-dev"
else
    echo "? gtkmm-3.0 �Ѱ�װ"
fi

# ���I2C
if [ ! -e "/dev/i2c-1" ]; then
    echo "����: I2C�豸 /dev/i2c-1 ������"
    echo "��ȷ��I2C������: sudo raspi-config -> Interface Options -> I2C"
else
    echo "? I2C�豸����"
fi

echo
echo "2. �������..."

# ������ļ�
make clean 2>/dev/null

# ����
if make; then
    echo "? ����ɹ�"
else
    echo "? ����ʧ��"
    echo "���������Ƿ���ȷ��װ"
    exit 1
fi

echo
echo "3. ����ִ���ļ�..."

if [ -f "collect_data" ]; then
    echo "? collect_data ������"
    ls -la collect_data
else
    echo "? collect_data δ����"
    exit 1
fi

if [ -f "IMU_zero" ]; then
    echo "? IMU_zero ������"
    ls -la IMU_zero
else
    echo "? IMU_zero δ����"
fi

echo
echo "4. �������Ŀ¼..."

if [ ! -d "Datas" ]; then
    echo "���� Datas Ŀ¼..."
    mkdir -p Datas
fi

echo "��ǰ�����ļ���:"
ls -la Datas/ 2>/dev/null || echo "DatasĿ¼Ϊ��"

echo
echo "5. ���I2C�豸..."

if command -v i2cdetect &> /dev/null; then
    echo "ɨ��I2C�豸..."
    sudo i2cdetect -y 1 2>/dev/null || echo "�޷�ɨ��I2C�豸��������ҪrootȨ��"
else
    echo "i2cdetect δ��װ������I2Cɨ��"
fi

echo
echo "=== ������� ==="
echo
echo "������м�鶼ͨ�������������:"
echo "  sudo ./collect_data    # ���������ռ�����"
echo "  sudo ./IMU_zero        # ����У׼����"
echo
echo "��������˵��:"
echo "1. ���к�ȴ�25���ʼ��"
echo "2. �̵��������԰���ť��ʼ�ռ�"
echo "3. �ٴΰ���ťֹͣ�ռ�"
echo "4. ���ݱ����� Datas/data_X/ Ŀ¼��"
echo
echo "LED״̬:"
echo "  ����� = �ȴ���"
echo "  ��+�̵��� = ׼������"
echo "  �̵��� = �����ռ�����" 