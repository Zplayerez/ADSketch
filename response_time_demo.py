import os
import json
import logging
import argparse
import numpy as np
import pandas as pd

from dataset_loader import *
from adsketch.motif_operations import *


# Setup the logging file name
seed_everything(seed=1234)
os.makedirs('./logs', exist_ok=True)
init_logging(f'./logs/response_time_demo.log')

parser = argparse.ArgumentParser()
parser.add_argument("--res_dir", type=str, default='./res/response_time/',
                    help="The directory to save experimental figures")
parser.add_argument("--pattern_dir", type=str, default='./offline_metrics/response_time/',
                    help="The directory to save the learned metric patterns and other necessary info")
args = vars(parser.parse_args())

os.makedirs(args['res_dir'], exist_ok=True)
os.makedirs(args['pattern_dir'], exist_ok=True)

with open('params.json', 'r') as json_reader:
    params = json.load(json_reader)


def load_response_time_data():
    """Load response time benchmark data."""
    data_dir = 'data/response_time_benchmark'
    metric_values = []
    metric_labels = []
    
    # 获取所有CSV文件并排序
    files = sorted([f for f in os.listdir(data_dir) if f.endswith('.csv')])
    
    for file in files:
        file_path = os.path.join(data_dir, file)
        df = pd.read_csv(file_path)
        metric_values.append(df['value'].values)
        metric_labels.append(df['is_anomaly'].values)
    
    return metric_values, metric_labels


def response_time_offline():
    logging.info('{}{}{}'.format('^' * 15, ' Offline anomaly detection for Response Time dataset ', '^' * 15))
    response_time_params = params.get('response_time', {})  # 从params.json中获取response_time参数

    metric_values, metric_labels = load_response_time_data()
    train_num = 300  # 使用前300个点作为训练数据（无异常）

    res_lst = []
    all_metrics = []  # 存储所有指标结果
    for metric_id in range(len(metric_values)):
        metric_name = f'response_time_{metric_id + 1}'
        # 如果在params.json中没有特定的参数，使用默认值
        m = response_time_params.get(metric_name, {}).get('m', 5)  # 默认m=5
        p = response_time_params.get(metric_name, {}).get('p', 99)  # 默认p=99

        logging.info('=' * 60)
        logging.info(f'Dataset: response_time (metric {metric_name}), m: {m}, p: {p}')
        fig_dir = os.path.join(args['res_dir'], f'{metric_name}_{m}_{p}.png')
        offline_pattern_dir = os.path.join(args['pattern_dir'], f'{metric_name}_{m}_{p}.pkl')

        train_metric_values = metric_values[metric_id][:train_num]
        test_metric_values = metric_values[metric_id][train_num:]
        test_metric_labels = metric_labels[metric_id][train_num:]
        
        res = offline_anomaly_detection(m, p,
                                    train_metric_values, test_metric_values, test_metric_labels,
                                    offline_pattern_dir, fig_dir)
        
        res_lst.append(res)
        all_metrics.append({
            'metric_name': metric_name,
            'precision': res[0],
            'recall': res[1],
            'f1': res[2]
        })

    res_lst = np.transpose(res_lst).mean(axis=1)

    logging.info('{}{}{}'.format('^' * 15, ' Experimental results of Response Time dataset ', '^' * 15))
    logging.info('precision: {:.3f}, recall: {:.3f}, f1: {:.3f}'.format(res_lst[0], res_lst[1], res_lst[2]))

    # 计算并输出每个指标的平均值
    print("\n" + "=" * 50)
    print("Average Metrics for All Response Time Data:")
    print("-" * 50)
    print(f"Average Precision: {res_lst[0]:.3f}")
    print(f"Average Recall: {res_lst[1]:.3f}")
    print(f"Average F1-Score: {res_lst[2]:.3f}")
    print("=" * 50)

    # 保存详细结果到CSV文件
    results_df = pd.DataFrame(all_metrics)
    results_file = os.path.join(args['res_dir'], 'response_time_results.csv')
    results_df.to_csv(results_file, index=False)
    print(f"\nDetailed results saved to: {results_file}")


if __name__ == '__main__':
    response_time_offline() 