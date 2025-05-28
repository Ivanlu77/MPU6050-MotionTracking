# Pandas 兼容性修复说明

## 问题描述

在新版本的pandas中，`DataFrame.append()`方法已被弃用并移除，导致以下错误：
```
AttributeError: 'DataFrame' object has no attribute 'append'. Did you mean: '_append'?
```

另外还有数据类型不匹配的问题：
```
ValueError: Must pass 2-d input. shape=(1, 1, 3)
```

## 修复内容

### 1. 修复 `functions.py` 中的 DataFrame.append() 问题

#### 修复的函数：
- `norm()` - 第84行
- `get_norm()` - 第163行  
- `integral()` - 第173行
- `integral_vel()` - 第185行

#### 修复方法：
将所有的 `df.append()` 替换为 `pd.concat([df, new_data], ignore_index=True)`

**修复前：**
```python
n = n.append(T, ignore_index=True)
```

**修复后：**
```python
n = pd.concat([n, T], ignore_index=True)
```

### 2. 修复数据类型不匹配问题

#### 问题位置：
- `integral()` 函数中的 `ip` 变量初始化
- `integral_vel()` 函数中的 `ip` 变量初始化和重置

#### 修复方法：
确保 `ip` 变量始终是numpy数组，而不是标量或DataFrame

**修复前：**
```python
def integral_vel(data,time,stationary):
    ip = 0  # 标量初始化
    for i in range(len(data)-1):
        ip += (data.loc[i]+data.loc[i+1])*(time[i+1]-time[i])/2
        if stationary[i]!=0:
            ip = pd.DataFrame([np.array([0,0,0])], columns=data.columns.to_numpy())  # 错误：重置为DataFrame
```

**修复后：**
```python
def integral_vel(data,time,stationary):
    ip = np.array([0,0,0])  # numpy数组初始化
    for i in range(len(data)-1):
        ip += (data.loc[i]+data.loc[i+1])*(time[i+1]-time[i])/2
        if stationary[i]!=0:
            ip = np.array([0,0,0])  # 正确：重置为numpy数组
```

## 测试验证

创建了两个测试脚本来验证修复：

1. **test_pandas_fix.py** - 全面的pandas兼容性测试
2. **test_fix.py** - 快速的函数测试

### 运行测试：
```bash
cd "MPU6050-MotionTracking/Processing data"
python test_fix.py
```

## 兼容性

这些修复确保代码与以下版本兼容：
- pandas >= 2.0.0 (移除了append方法)
- pandas < 2.0.0 (仍然支持旧版本)
- Python 3.8+

## 影响的功能

修复后，以下功能应该正常工作：
- ? 2D动画绘图 (`plot2d_animated()`)
- ? 3D动画绘图 (`plot3d_animate()`)
- ? 速度积分计算 (`integral()`)
- ? 漂移校正速度计算 (`get_vel_drift()`)
- ? 所有依赖这些函数的可视化功能

## 验证步骤

1. 运行测试脚本确认修复成功
2. 尝试运行原始的 `main.py` 程序
3. 测试各种绘图功能

如果仍有问题，请检查pandas版本：
```python
import pandas as pd
print(pd.__version__)
``` 