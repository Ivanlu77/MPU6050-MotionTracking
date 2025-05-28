# Pandas �������޸�˵��

## ��������

���°汾��pandas�У�`DataFrame.append()`�����ѱ����ò��Ƴ����������´���
```
AttributeError: 'DataFrame' object has no attribute 'append'. Did you mean: '_append'?
```

���⻹���������Ͳ�ƥ������⣺
```
ValueError: Must pass 2-d input. shape=(1, 1, 3)
```

## �޸�����

### 1. �޸� `functions.py` �е� DataFrame.append() ����

#### �޸��ĺ�����
- `norm()` - ��84��
- `get_norm()` - ��163��  
- `integral()` - ��173��
- `integral_vel()` - ��185��

#### �޸�������
�����е� `df.append()` �滻Ϊ `pd.concat([df, new_data], ignore_index=True)`

**�޸�ǰ��**
```python
n = n.append(T, ignore_index=True)
```

**�޸���**
```python
n = pd.concat([n, T], ignore_index=True)
```

### 2. �޸��������Ͳ�ƥ������

#### ����λ�ã�
- `integral()` �����е� `ip` ������ʼ��
- `integral_vel()` �����е� `ip` ������ʼ��������

#### �޸�������
ȷ�� `ip` ����ʼ����numpy���飬�����Ǳ�����DataFrame

**�޸�ǰ��**
```python
def integral_vel(data,time,stationary):
    ip = 0  # ������ʼ��
    for i in range(len(data)-1):
        ip += (data.loc[i]+data.loc[i+1])*(time[i+1]-time[i])/2
        if stationary[i]!=0:
            ip = pd.DataFrame([np.array([0,0,0])], columns=data.columns.to_numpy())  # ��������ΪDataFrame
```

**�޸���**
```python
def integral_vel(data,time,stationary):
    ip = np.array([0,0,0])  # numpy�����ʼ��
    for i in range(len(data)-1):
        ip += (data.loc[i]+data.loc[i+1])*(time[i+1]-time[i])/2
        if stationary[i]!=0:
            ip = np.array([0,0,0])  # ��ȷ������Ϊnumpy����
```

## ������֤

�������������Խű�����֤�޸���

1. **test_pandas_fix.py** - ȫ���pandas�����Բ���
2. **test_fix.py** - ���ٵĺ�������

### ���в��ԣ�
```bash
cd "MPU6050-MotionTracking/Processing data"
python test_fix.py
```

## ������

��Щ�޸�ȷ�����������°汾���ݣ�
- pandas >= 2.0.0 (�Ƴ���append����)
- pandas < 2.0.0 (��Ȼ֧�־ɰ汾)
- Python 3.8+

## Ӱ��Ĺ���

�޸������¹���Ӧ������������
- ? 2D������ͼ (`plot2d_animated()`)
- ? 3D������ͼ (`plot3d_animate()`)
- ? �ٶȻ��ּ��� (`integral()`)
- ? Ư��У���ٶȼ��� (`get_vel_drift()`)
- ? ����������Щ�����Ŀ��ӻ�����

## ��֤����

1. ���в��Խű�ȷ���޸��ɹ�
2. ��������ԭʼ�� `main.py` ����
3. ���Ը��ֻ�ͼ����

����������⣬����pandas�汾��
```python
import pandas as pd
print(pd.__version__)
``` 