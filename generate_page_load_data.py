import os
import numpy as np
import pandas as pd

# 创建输出目录
output_dir = "data/page_load_benchmark"
os.makedirs(output_dir, exist_ok=True)

def generate_page_load_data(num_points, seed=None):
    if seed is not None:
        np.random.seed(seed)
    
    # 基础时间序列
    timestamps = np.arange(1, num_points + 1)
    
    # 生成正常范围的加载时间（1-3秒）
    values = np.random.uniform(1.0, 3.0, num_points)
    
    # 添加较小的随机波动（标准差0.2秒）
    values += np.random.normal(0, 0.2, num_points)
    
    # 确保所有值都大于0
    values = np.maximum(values, 0.1)
    
    # 添加异常值标记
    is_anomaly = np.zeros(num_points)
    
    # 随机选择2-4个异常区间
    num_anomaly_periods = np.random.randint(2, 5)
    min_distance = 100  # 异常区间之间的最小距离
    used_positions = set()
    
    # 为每个异常区间预先生成一个基准值，确保同一文件中的异常区间有所不同
    high_anomaly_bases = np.random.uniform(10.0, 20.0, num_anomaly_periods)
    
    for i in range(num_anomaly_periods):
        while True:
            # 随机选择异常开始位置
            anomaly_start = np.random.randint(50, num_points - 20)
            # 检查是否与现有异常区间太近
            if not any(abs(anomaly_start - pos) < min_distance for pos in used_positions):
                break
        
        # 异常持续3-5个时间点
        anomaly_duration = np.random.randint(3, 6)
        
        # 80%概率是高延迟异常，20%概率是超低延迟异常（可能是缓存导致）
        if np.random.random() < 0.8:  # 高延迟异常的概率更大
            # 高延迟异常 (10-20秒)，在基准值附近波动
            base_value = high_anomaly_bases[i]
            values[anomaly_start:anomaly_start + anomaly_duration] = base_value + np.random.uniform(-2, 2, anomaly_duration)
        else:
            # 超低延迟异常 (0.1-0.3秒，可能是缓存命中)
            values[anomaly_start:anomaly_start + anomaly_duration] = np.random.uniform(0.1, 0.3, anomaly_duration)
        
        is_anomaly[anomaly_start:anomaly_start + anomaly_duration] = 1
        used_positions.add(anomaly_start)
    
    return pd.DataFrame({
        'timestamp': timestamps,
        'value': values,
        'is_anomaly': is_anomaly
    })

# 生成多个数据文件
num_files = 50  # 保持与其他数据集一致
for i in range(1, num_files + 1):
    # 随机生成800-1000行数据
    num_points = np.random.randint(800, 1000)
    df = generate_page_load_data(num_points, seed=i)  # 使用文件索引作为随机种子
    
    # 保存为CSV文件
    output_file = os.path.join(output_dir, f'page_load_{i}.csv')
    df.to_csv(output_file, index=False)
    
print(f"Generated {num_files} page load time data files in {output_dir}") 