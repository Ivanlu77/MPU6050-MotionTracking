# MPU6050 ���̿��ư汾ʹ��ָ��

## �޸�˵��

����汾����ԭʼ��`collect_data.cpp`������������ԭ�й��ܣ�ֻ�ǽ���ť���Ƹ�Ϊ����������ƣ�

### ��Ҫ�仯��
- **�Ƴ�**: ��ťGPIO���ƺͳ����ػ�����
- **����**: LED״ָ̬ʾ�����ݸ�ʽ��У׼ƫ�����������㷨
- **����**: ����������ƣ�'s'��ʼ/ֹͣ��'q'�˳���

## ���������

### 1. �������
```bash
cd "MPU6050-MotionTracking/Collect data"

# ʹ���µ�Makefile����
make -f Makefile_keyboard clean
make -f Makefile_keyboard

# �����ֶ�����
g++ -Wall -g -O3 -std=c++17 -o collect_data_keyboard collect_data.cpp I2Cdev.cpp MPU6050.cpp -lwiringPi -lm -lpthread
```

### 2. ���г���
```bash
sudo ./collect_data_keyboard
```

## ʹ�÷���

### �����������̣�
1. **��ʼ���׶Σ�25�룩**
   - ��������̵�Ϩ��
   - ������ʾ��ʼ����Ϣ
   - �ȴ�25���ô������ȶ�

2. **׼���׶�**
   - �̵����𣨺��������
   - ��ʾ����˵��
   - ���Կ�ʼʹ�ü��̿���

### ���̿��ƣ�
- **'s' �� 'S'**: ��ʼ/ֹͣ�����ռ�
- **'q' �� 'Q'**: �˳�����

### LED״ָ̬ʾ��
| ��� | �̵� | ״̬ |
|------|------|------|
| �� | �� | ��ʼ���У�25�룩 |
| �� | �� | ׼������ |
| �� | �� | �����ռ����� |

## ���ݴ洢

���ݴ洢��ʽ��ԭ����ȫ��ͬ��

### �洢λ�ã�
```
./Datas/
������ data_0/
��   ������ Data_Accel.txt
��   ������ Data_Gyro.txt
��   ������ Data_Quaternions.txt
��   ������ Data_LinearAcc.txt
������ data_1/
������ ...
```

### ���ݸ�ʽ��

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

## У׼����

����ʹ����ԭ����ͬ��У׼ƫ������
```cpp
mpu.setXAccelOffset(-2757);
mpu.setYAccelOffset(417);
mpu.setZAccelOffset(1191);
mpu.setXGyroOffset(-609);
mpu.setYGyroOffset(-474);
mpu.setZGyroOffset(415);
```

��������У׼���������У�
```bash
sudo ./IMU_zero
```

## ��ԭ��ļ�����

### ��ȫ���ݣ�
- ? ���ݸ�ʽ��ȫ��ͬ
- ? �ļ��ṹ��ȫ��ͬ
- ? У׼ƫ������ͬ
- ? �㷨�ʹ����߼���ͬ
- ? ����ֱ����ԭ�е�Python�������

### ��Ҫ����
- ? ��֧�ְ�ť����
- ? ��֧�ֳ����ػ�
- ? ֧�ּ��̿���
- ? ���õ��û�����

## ʹ��ʾ��

```bash
# 1. ����
make -f Makefile_keyboard

# 2. ����
sudo ./collect_data_keyboard

# 3. �ȴ���ʼ����ɣ�25�룩
# �����̵������"Controls:"��ʾ

# 4. ��ʼ�����ռ�
# �� 's' ��

# 5. �ƶ����������������ռ�
# �۲�ʵʱ�������

# 6. ֹͣ�����ռ�
# �ٰ� 's' ��

# 7. �˳�����
# �� 'q' ��
```

## �����ų�

### �������⣺

1. **�������**
   ```bash
   # �������
   sudo apt-get install libgtkmm-3.0-dev wiringpi
   ```

2. **Ȩ�޴���**
   ```bash
   # ����ʹ��sudo����
   sudo ./collect_data_keyboard
   ```

3. **������������Ӧ**
   - ȷ���ն˴����н���
   - ����Ҫ���س���ֱ�Ӱ�������

4. **�����ļ��в�����**
   ```bash
   mkdir -p Datas
   ```

## ���ݴ���

�ռ������ݺ󣬿���ֱ��ʹ��ԭ�е�Python�������

```bash
# �����ݸ��Ƶ�����Ŀ¼�������Ҫ��
cp -r Datas/* "../Processing data/Datas/"

# ����Python�������
cd "../Processing data"
python main.py
```

���ݸ�ʽ��ȫ���ݣ������κ��޸ġ� 