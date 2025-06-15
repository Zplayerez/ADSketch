import os
import numpy as np
import pandas as pd

# 创建输出目录
output_dir = "data/response_time_benchmark"
os.makedirs(output_dir, exist_ok=True)

def generate_response_time_data(num_points, seed=None):
    if seed is not None:
        np.random.seed(seed)
    
    # 基础时间序列
    timestamps = np.arange(1, num_points + 1)
    
    # 生成正常范围的响应时间（200-300ms）
    values = np.random.uniform(200.0, 300.0, num_points)
    
    # 添加较小的随机波动（标准差15ms，因为响应时间通常会有一定波动）
    values += np.random.normal(0, 15, num_points)
    
    # 确保所有值都大于0（响应时间不能为负）
    values = np.maximum(values, 0)
    
    # 添加异常值标记
    is_anomaly = np.zeros(num_points)
    
    # 随机选择2-4个异常区间
    num_anomaly_periods = np.random.randint(2, 5)
    min_distance = 100  # 异常区间之间的最小距离
    used_positions = set()
    
    # 为每个异常区间预先生成一个基准值，确保同一文件中的异常区间有所不同
    high_anomaly_bases = np.random.uniform(600.0, 800.0, num_anomaly_periods)
    
    for i in range(num_anomaly_periods):
        while True:
            # 随机选择异常开始位置
            anomaly_start = np.random.randint(50, num_points - 20)
            # 检查是否与现有异常区间太近
            if not any(abs(anomaly_start - pos) < min_distance for pos in used_positions):
                break
        
        # 异常持续3-5个时间点
        anomaly_duration = np.random.randint(3, 6)
        
        # 生成高响应时间异常 (600-800ms)，在基准值附近波动
        base_value = high_anomaly_bases[i]
        values[anomaly_start:anomaly_start + anomaly_duration] = base_value + np.random.uniform(-40, 40, anomaly_duration)
        
        # 确保所有值都大于0
        values[anomaly_start:anomaly_start + anomaly_duration] = np.maximum(
            values[anomaly_start:anomaly_start + anomaly_duration], 0)
        
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
    df = generate_response_time_data(num_points, seed=i)  # 使用文件索引作为随机种子
    
    # 保存为CSV文件
    output_file = os.path.join(output_dir, f'response_time_{i}.csv')
    df.to_csv(output_file, index=False)
    
print(f"Generated {num_files} response time data files in {output_dir}") 