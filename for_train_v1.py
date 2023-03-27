import glob
import pandas as pd
import random
from tqdm import tqdm

tick_path = "./Data/sample"
trainData_file = './Data/trainData.csv'

def get_ms(tm):
    hhmmss = tm // 1000
    ms = (hhmmss // 10000 * 3600 + (hhmmss // 100 % 100) * 60 + hhmmss % 100) * 1000 + tm % 1000
    ms_from_open = ms - 34200000  # millisecond from stock opening
    if tm >= 130000000:
        ms_from_open -= 5400000
    return ms_from_open

tick_files = glob.glob(f'{tick_path}/*.csv')
#sample_files = random.sample(tick_files, k=1)

train_data = []
for f in tqdm(tick_files):
    print(f)
    tick_data = pd.read_csv(f, index_col=None)
    symbol = list(tick_data['COLUMN02'].unique())
    for sym in tqdm(symbol):
      sym_data = tick_data[tick_data['COLUMN02'] == sym]
      ms = sym_data['COLUMN03'].apply(lambda x: get_ms(x)).values
      price = sym_data['COLUMN07'].values
      buy_vol = sym_data['COLUMN50'].values
      sell_vol = sym_data['COLUMN51'].values
      sampling_p = 0  # sampling pointer
      for i in range(len(ms)):
          if ms[i] - ms[sampling_p] < 60000:  # sampling every 1 minute
              continue

          # find the indexes at different time
          idx_5min, idx_10min, idx_15min, idx_20min, idx_25min = 0, 0, 0, 0, 0
          for j in range(i):
              if ms[i] - ms[j] >= 300000:
                  idx_5min = j
              if ms[i] - ms[j] >= 600000:
                  idx_10min = j
              if ms[i] - ms[j] >= 900000:
                  idx_15min = j
              if ms[i] - ms[j] >= 1200000:
                  idx_20min = j
              if ms[i] - ms[j] >= 1500000:
                  idx_25min = j
          idx_fwd_5min = 0
          for j in range(i, len(ms)):
              if ms[j] - ms[i] >= 300000:
                  idx_fwd_5min = j
                  break

          # calculate a target variable and 10 factor variables
          if idx_25min != 0 and idx_fwd_5min != 0:
              train_data.append((
                  (price[idx_fwd_5min] / price[i] - 1) * 10000,  # target y
                  price[i] / price[idx_5min] - 1,  # factor 1
                  price[i] / price[idx_10min] - 1,  # factor 2
                  (buy_vol[idx_5min]+1) / (sell_vol[idx_5min]+1),  # factor 3
                  (buy_vol[idx_10min]+1) / (sell_vol[idx_10min]+1),  # factor 4
                  # sel_vol[i] / sel_vol[idx_5min] - 1,  # factor 5
                  # sel_vol[i] / sel_vol[idx_10min] - 1,
                  # max(price[idx_5min:i]) / min(price[idx_5min:i]) - 1,  # factor 6
                  # max(price[idx_10min:i]) / min(price[idx_10min:i]) - 1,  # factor 7
                  # max(price[idx_15min:i]) / min(price[idx_15min:i]) - 1,  # factor 8
                  # max(price[idx_20min:i]) / min(price[idx_20min:i]) - 1,  # factor 9
                  # max(price[idx_25min:i]) / min(price[idx_25min:i]) - 1,  # factor 10
              ))
              sampling_p = i

train_data = pd.DataFrame(train_data, columns=['y'] + [f'x{i}' for i in range(1, 5)])
train_data.to_csv(trainData_file, index=False)