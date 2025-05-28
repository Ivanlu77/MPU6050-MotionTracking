# ԭʼ�����ռ��������ָ��

## 1. Ӳ������

����README.md������Ҫ��������Ӳ����

### GPIO���ӱ�
| GPIO���� | ��� | ˵�� |
|---------|------|------|
| GPIO 8 (SDA) | MPU6050 SDA | I2C������ |
| GPIO 9 (SCL) | MPU6050 SCL | I2Cʱ���� |
| GPIO 0 | ��ɫLED | ״ָ̬ʾ |
| GPIO 2 | ��ɫLED | ״ָ̬ʾ |
| GPIO 3 | ��ť | ���������ռ� |

### LED״̬˵��
| �̵� | ��� | ״̬ |
|------|------|------|
| 0 | 1 | �ȴ���(25�뵹��ʱ) |
| 1 | 1 | ׼������ |
| 1 | 0 | �����ռ����� |

## 2. �������

### ��װ����
```bash
# ��װ��Ҫ�Ŀ�
sudo apt-get update
sudo apt-get install libgtkmm-3.0-dev
sudo apt-get install wiringpi

# �������ݮ��4����°汾��������Ҫ�ֶ���װwiringPi
# wget https://project-downloads.drogon.net/wiringpi-latest.deb
# sudo dpkg -i wiringpi-latest.deb
```

### ����
```bash
cd "MPU6050-MotionTracking/Collect data"
make clean
make
```

�������������ִ���ļ���
- `collect_data` - ��Ҫ�������ռ�����
- `IMU_zero` - У׼����

## 3. У׼����������ѡ���Ƽ���

```bash
sudo ./IMU_zero
```

�������᣺
1. ����һ��ʱ���ռ�У׼����
2. ���������Сֵ����У׼
3. ����Խ���Щֵ���µ�`collect_data.cpp`�е�ƫ��������

## 4. ���������ռ�����

```bash
sudo ./collect_data
```

### �����������̣�

1. **��ʼ���׶Σ�25�룩**
   - ��������̵�Ϩ��
   - �����ʼ��MPU6050������
   - �ȴ�25���ô������ȶ�

2. **׼���׶�**
   - ��ƺ��̵ƶ�����
   - ���԰���ť��ʼ�����ռ�

3. **�����ռ��׶�**
   - ���°�ť��ʼ�ռ�
   - ���Ϩ���̵�����
   - �ٴΰ���ťֹͣ�ռ�

4. **���⹦��**
   - ������ť5�����ϣ���ݮ�ɹػ�

## 5. ���ݴ洢λ��

���ݻ��Զ������ڣ�
```
MPU6050-MotionTracking/Collect data/Datas/
������ data_0/
��   ������ Data_Quaternions.txt
��   ������ Data_LinearAcc.txt
��   ������ Description.txt
������ data_1/
������ data_2/
������ ...
```

ÿ���ռ��ᴴ��һ���µ�`data_X`�ļ��У�������
- **Data_Quaternions.txt**: ��Ԫ������ (time,qw,qx,qy,qz)
- **Data_LinearAcc.txt**: ���Լ��ٶ����� (time,accx,accy,accz)
- **Description.txt**: �����ļ�

## 6. ���ݸ�ʽ˵��

### Data_Quaternions.txt
```csv
time,qw,qx,qy,qz
5,0.74213,-0.04791,0.01538,0.66833
10,0.74213,-0.04767,0.01550,0.66833
...
```
- time: ʱ���(����)
- qw,qx,qy,qz: ��Ԫ������(������)

### Data_LinearAcc.txt
```csv
time,accx,accy,accz
5,3,-4,59
10,-47,81,146
...
```
- time: ʱ���(����)
- accx,accy,accz: ���Լ��ٶ�(������������ԭʼ��λ)

## 7. ���Բ���

### �������ԣ�
1. ����Ӳ��
2. �������`make`
3. ���У�`sudo ./collect_data`
4. �ȴ�25��ֱ���̵�����
5. ����ť��ʼ�ռ�����
6. �ƶ�������һ��ʱ��
7. �ٰ���ťֹͣ�ռ�
8. ���`Datas/data_X/`�ļ����е�����

### ��֤���ݣ�
```bash
# �鿴�����ռ�������
ls -la Datas/
cd Datas/data_X/  # X�����µ�����
head -10 Data_Quaternions.txt
head -10 Data_LinearAcc.txt
```

## 8. �����ų�

### �������⣺

1. **�������**
   ```bash
   # �������
   pkg-config --exists gtkmm-3.0
   which gpio
   ```

2. **I2C����**
   ```bash
   # ���I2C�豸
   sudo i2cdetect -y 1
   # Ӧ�ÿ���0x68��ַ��MPU6050
   ```

3. **Ȩ�޴���**
   ```bash
   # ȷ����rootȨ������
   sudo ./collect_data
   ```

4. **GPIO����**
   ```bash
   # ���wiringPi��װ
   gpio readall
   ```

## 9. ���ݴ���

�ռ������ݺ󣬽�`Datas`�ļ��и��Ƶ���
```
MPU6050-MotionTracking/Processing data/Datas/
```

Ȼ���������Python�������
```bash
cd "MPU6050-MotionTracking/Processing data"
python main.py
```

## 10. ע������

- ȷ��MPU6050��ȷ���ӵ�I2C����
- ������ҪrootȨ�޷���GPIO
- �����ռ��ڼ䱣�ִ������ȶ�����
- ÿ���ռ����Զ������µ������ļ���
- ������ť��ػ���С�Ĳ��� 