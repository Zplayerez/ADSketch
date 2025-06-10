import os
import numpy as np
import pandas as pd

# 创建输出目录
output_dir = "data/memory_usage_benchmark"
os.makedirs(output_dir, exist_ok=True)

def generate_memory_usage_data(num_points, seed=None):
    if seed is not None:
        np.random.seed(seed)
    
    # 基础时间序列
    timestamps = np.arange(1, num_points + 1)
    
    # 生成正常范围的内存使用率（20-30%）
    values = np.random.uniform(20.0, 30.0, num_points)
    
    # 添加较小的随机波动（标准差2%，因为内存使用率波动通常比较平缓）
    values += np.random.normal(0, 2, num_points)
    
    # 确保所有值都在0-100之间（内存使用率的有效范围）
    values = np.clip(values, 0, 100)
    
    # 添加异常值标记
    is_anomaly = np.zeros(num_points)
    
    # 随机选择2-4个异常区间
    num_anomaly_periods = np.random.randint(2, 5)
    min_distance = 100  # 异常区间之间的最小距离
    used_positions = set()
    
    # 为每个异常区间预先生成一个基准值，确保同一文件中的异常区间有所不同
    high_anomaly_bases = np.random.uniform(50.0, 70.0, num_anomaly_periods)
    
    for i in range(num_anomaly_periods):
        while True:
            # 随机选择异常开始位置
            anomaly_start = np.random.randint(50, num_points - 20)
            # 检查是否与现有异常区间太近
            if not any(abs(anomaly_start - pos) < min_distance for pos in used_positions):
                break
        
        # 异常持续3-5个时间点
        anomaly_duration = np.random.randint(3, 6)
        
        # 95%概率是高内存使用率异常，5%概率是内存泄露（持续增长）
        if np.random.random() < 0.95:  # 高内存使用率异常的概率更大
            # 高内存使用率异常 (50-70%)，在基准值附近波动
            base_value = high_anomaly_bases[i]
            values[anomaly_start:anomaly_start + anomaly_duration] = base_value + np.random.uniform(-3, 3, anomaly_duration)
        else:
            # 内存泄露异常（从当前值开始持续增长）
            start_value = values[anomaly_start - 1]
            growth_rate = np.random.uniform(5, 10)  # 每个时间点增长5-10%
            for j in range(anomaly_duration):
                values[anomaly_start + j] = min(start_value + growth_rate * (j + 1), 100)
        
        # 确保所有值都在0-100之间
        values[anomaly_start:anomaly_start + anomaly_duration] = np.clip(
            values[anomaly_start:anomaly_start + anomaly_duration], 0, 100)
        
        is_anomaly[anomaly_start:anomaly_start + anomaly_duration] = 1
        used_positions.add(anomaly_start)
    
    # 保留一位小数
    values = np.round(values, 1)
    
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
    df = generate_memory_usage_data(num_points, seed=i)  # 使用文件索引作为随机种子
    
    # 保存为CSV文件
    output_file = os.path.join(output_dir, f'memory_usage_{i}.csv')
    df.to_csv(output_file, index=False)
    
print(f"Generated {num_files} memory usage data files in {output_dir}") 