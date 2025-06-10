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
init_logging(f'./logs/error_rate_demo.log')

parser = argparse.ArgumentParser()
parser.add_argument("--res_dir", type=str, default='./res/error_rate/',
                    help="The directory to save experimental figures")
parser.add_argument("--pattern_dir", type=str, default='./offline_metrics/error_rate/',
                    help="The directory to save the learned metric patterns and other necessary info")
args = vars(parser.parse_args())

os.makedirs(args['res_dir'], exist_ok=True)
os.makedirs(args['pattern_dir'], exist_ok=True)

with open('params.json', 'r') as json_reader:
    params = json.load(json_reader)


def load_error_rate_data():
    """Load error rate benchmark data."""
    data_dir = 'data/error_rate_benchmark'
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


def error_rate_offline():
    logging.info('{}{}{}'.format('^' * 15, ' Offline anomaly detection for Error Rate dataset ', '^' * 15))
    error_rate_params = params.get('error_rate', {})  # 从params.json中获取error_rate参数

    metric_values, metric_labels = load_error_rate_data()
    train_num = 300  # 使用前300个点作为训练数据（无异常）

    res_lst = []
    all_metrics = []  # 存储所有指标结果
    for metric_id in range(len(metric_values)):
        metric_name = f'error_rate_{metric_id + 1}'
        # 如果在params.json中没有特定的参数，使用默认值
        m = error_rate_params.get(metric_name, {}).get('m', 50)  # 默认m=50
        p = error_rate_params.get(metric_name, {}).get('p', 10)  # 默认p=10

        logging.info('=' * 60)
        logging.info(f'Dataset: error_rate (metric {metric_name}), m: {m}, p: {p}')
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

    logging.info('{}{}{}'.format('^' * 15, ' Experimental results of Error Rate dataset ', '^' * 15))
    logging.info('precision: {:.3f}, recall: {:.3f}, f1: {:.3f}'.format(res_lst[0], res_lst[1], res_lst[2]))

    # 计算并输出每个指标的平均值
    print("\n" + "=" * 50)
    print("Average Metrics for All Error Rate Data:")
    print("-" * 50)
    print(f"Average Precision: {res_lst[0]:.3f}")
    print(f"Average Recall: {res_lst[1]:.3f}")
    print(f"Average F1-Score: {res_lst[2]:.3f}")
    print("=" * 50)

    # 保存详细结果到CSV文件
    results_df = pd.DataFrame(all_metrics)
    results_file = os.path.join(args['res_dir'], 'error_rate_results.csv')
    results_df.to_csv(results_file, index=False)
    print(f"\nDetailed results saved to: {results_file}")


if __name__ == '__main__':
    error_rate_offline() 