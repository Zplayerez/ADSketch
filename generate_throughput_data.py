import os
import numpy as np
import pandas as pd

# 创建输出目录
output_dir = "data/throughput_benchmark"
os.makedirs(output_dir, exist_ok=True)

def generate_throughput_data(num_points, seed=None):
    if seed is not None:
        np.random.seed(seed)
    
    # 基础时间序列
    timestamps = np.arange(1, num_points + 1)
    
    # 直接生成随机值（正常范围950-1050，减小波动范围）
    values = np.random.uniform(950, 1050, num_points)
    
    # 添加较小的随机跳动（减小标准差）
    values += np.random.normal(0, 20, num_points)
    
    # 添加异常值
    is_anomaly = np.zeros(num_points)
    
    # 随机选择2-4个异常区间
    num_anomaly_periods = np.random.randint(2, 5)
    min_distance = 100  # 异常区间之间的最小距离
    used_positions = set()
    
    # 为每个异常区间预先生成一个基准值，确保同一文件中的异常区间有所不同
    high_anomaly_bases = np.random.uniform(1600, 2300, num_anomaly_periods)
    
    for i in range(num_anomaly_periods):
        while True:
            # 随机选择异常开始位置
            anomaly_start = np.random.randint(50, num_points - 20)
            # 检查是否与现有异常区间太近
            if not any(abs(anomaly_start - pos) < min_distance for pos in used_positions):
                break
        
        # 异常持续3-5个时间点
        anomaly_duration = np.random.randint(3, 6)
        
        # 75%概率是高异常，25%概率是低异常
        if np.random.random() < 0.75:  # 高异常的概率更大
            # 高异常 (1600-2300)，在基准值附近波动
            base_value = high_anomaly_bases[i]
            values[anomaly_start:anomaly_start + anomaly_duration] = base_value + np.random.uniform(-100, 100, anomaly_duration)
        else:
            # 低异常 (20-50)
            values[anomaly_start:anomaly_start + anomaly_duration] = np.random.uniform(20, 50, anomaly_duration)
        
        is_anomaly[anomaly_start:anomaly_start + anomaly_duration] = 1
        used_positions.add(anomaly_start)
    
    return pd.DataFrame({
        'timestamp': timestamps,
        'value': values,
        'is_anomaly': is_anomaly
    })

# 生成多个数据文件
num_files = 50  # 与Yahoo数据集文件数量相似
for i in range(1, num_files + 1):
    # 随机生成1400-1500行数据
    num_points = np.random.randint(800, 1000)
    df = generate_throughput_data(num_points, seed=i)  # 使用文件索引作为随机种子
    
    # 保存为CSV文件
    output_file = os.path.join(output_dir, f'throughput_{i}.csv')
    df.to_csv(output_file, index=False)
    
print(f"Generated {num_files} throughput data files in {output_dir}") 