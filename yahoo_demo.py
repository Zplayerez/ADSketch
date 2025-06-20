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
init_logging(f'./logs/yahoo_demo.log')

parser = argparse.ArgumentParser()
parser.add_argument("--res_dir", type=str, default='./res/yahoo/',
                    help="The directory to save experimental figures")
parser.add_argument("--pattern_dir", type=str, default='./offline_metrics/yahoo/',
                    help="The directory to save the learned metric patterns and other necessary info")
args = vars(parser.parse_args())

os.makedirs(args['res_dir'], exist_ok=True)
os.makedirs(args['pattern_dir'], exist_ok=True)

with open('params.json', 'r') as json_reader:
    params = json.load(json_reader)


def yahoo_offline():
    logging.info('{}{}{}'.format('^' * 15, ' Offline anomaly detection for Yahoo dataset ', '^' * 15))
    yahoo_params = params['yahoo']

    benchmark = 'A1Benchmark'  # We only experiment with the real dataset
    metric_values, metric_labels = load_yahoo_data(benchmark)
    train_num = 300  # The anomaly-free metric time series

    res_lst = []
    all_metrics = []  # 存储所有指标结果
    for metric_id in range(len(metric_values)):
        metric_name = f'real_{metric_id}'
        m, p = yahoo_params[metric_name]['m'], yahoo_params[metric_name]['p']

        logging.info('=' * 60)
        logging.info(f'Dataset: yahoo (metric real_{metric_id}), m: {m}, p: {p}')
        fig_dir = os.path.join(args['res_dir'], f'real_{metric_id}_{m}_{p}.png')
        offline_pattern_dir = os.path.join(args['pattern_dir'], f'{metric_name}_{m}_{p}.pkl')

        train_metric_values, test_metric_values = metric_values[metric_id][5:train_num], metric_values[metric_id][train_num:]
        test_metric_labels = metric_labels[metric_id][train_num:]
        res = offline_anomaly_detection(m, p,
                                        train_metric_values, test_metric_values, test_metric_labels,
                                        offline_pattern_dir, fig_dir)
        
        # No predictions, set the results as all 0
        if metric_id in [28, 54] and sum(res) == 0:
            # [28, 54] have no anomalies.
            res = [1.] * 3

        res_lst.append(res)
        all_metrics.append({
            'metric_name': metric_name,
            'precision': res[0],
            'recall': res[1],
            'f1': res[2]
        })

    res_lst = np.transpose(res_lst).mean(axis=1)

    logging.info('{}{}{}'.format('^' * 15, ' Experimental results of Yahoo dataset ', '^' * 15))
    logging.info('precision: {:.3f}, recall: {:.3f}, f1: {:.3f}'.format(res_lst[0], res_lst[1], res_lst[2]))

    # 计算并输出每个指标的平均值
    print("\n" + "=" * 50)
    print("Average Metrics for All Yahoo Data:")
    print("-" * 50)
    print(f"Average Precision: {res_lst[0]:.3f}")
    print(f"Average Recall: {res_lst[1]:.3f}")
    print(f"Average F1-Score: {res_lst[2]:.3f}")
    print("=" * 50)

    # 保存详细结果到CSV文件
    results_df = pd.DataFrame(all_metrics)
    results_file = os.path.join(args['res_dir'], 'yahoo_results.csv')
    results_df.to_csv(results_file, index=False)
    print(f"\nDetailed results saved to: {results_file}")


if __name__ == '__main__':
    yahoo_offline()
