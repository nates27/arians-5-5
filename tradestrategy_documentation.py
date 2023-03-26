import sys
import pandas as pd
import numpy as np
import joblib

# input_path = sys.argv[1]
# output_path = sys.argv[2]
# symbol_file = "/opt/demos/SampleStocks.csv"



input_path = "test_data/tickdata_20220805.csv"
output_path = "test_data/output_test.csv"
symbol_file = "test_data/SampleStocks.csv"


tick_data = open(input_path, 'r')
order_time = open(output_path, 'w')
symbol = pd.read_csv(symbol_file, index_col=None)['Code'].to_list()
idx_dict = dict(zip(symbol, list(range(len(symbol)))))


# ---------- Initialization ----------

model_file = "pickle_models/model2.pkl"
model = joblib.load(model_file)
target_vol = 100
basic_vol = 2
cum_vol_buy = [0] * len(symbol)  # accumulate buying volume
cum_vol_sell = [0] * len(symbol)  # accumulate selling volume
unfinished_buy = [0] * len(symbol)  # unfinished buying volume in current round
unfinished_sell = [0] * len(symbol)  # unfinished selling volume in current round
last_od_ms = [0] * len(symbol)  # last order time
hist_ms_prc = [[] for i in range(len(symbol))]  # historic time and price


def get_ms(tm): #tm is time
    hhmmss = tm // 1000 
    
    #divide and floor result (convert milliseconds to seconds)
    
    
    ms = (hhmmss // 10000 * 3600 + (hhmmss // 100 % 100) * 60 + hhmmss % 100) * 1000 + tm % 1000
    
    # hhmmss // 10000 gets the number of hours and hhmmss // 10000 * 3600 gives the number of seconds in the number of hours
    # hhmmss // 100 % 100 gets the number of minutes and (hhmmss // 100 % 100) * 60 gives the number of seconds in the number of minutes
    # (hhmmss // 10000 * 3600 + (hhmmss // 100 % 100) * 60 + hhmmss % 100) * 1000 gives the number of milliseconds in the number of hours and minutes
    # tm % 1000 gives the number of milliseconds
    # ms adds everything to get tm in milliseconds
    
    
    ms_from_open = ms - 34200000  
    
    # milliseconds counted from stock opening 
    #(34200000 is 9:30:00 am in morning)
    
    
    if tm >= 130000000:
        ms_from_open -= 5400000 
        
        # as the stock market is from 9.30am to 11.30am and 1pm to 3pm, 
        # there is a 1 h 30 mins (5400000 milliseconds) break, so if time is after 1.30pm, will minus the break time (take stock time as continuous without breaks)
        
    return ms_from_open


# --------------- Loop ---------------
# recursively read all tick lines from tickdata file,
# do decision with your strategy and write order to the ordertime file

tick_data.readline()  # header
order_time.writelines('symbol,BSflag,dataIdx,volume\n') #write the 4 columns headers
order_time.flush()

while True:
    tick_line = tick_data.readline()  # read one tick line 
    if tick_line.strip() == 'stop' or len(tick_line) == 0:
        break #stop running as end of tick file
    row = tick_line.split(',')
    nTick = row[0] #index number in tick data
    sym = row[1] #stock name
    tm = int(row[2]) #time
    if sym not in symbol:
        order_time.writelines(f'{sym},N,{nTick},0\n') #write stock name, N, index number in tick data, 0 into file if stock name is not found in sample stocks
        order_time.flush()
        continue #skip code below and go to next iteration

    # -------- Your Strategy Code Begin --------

    idx = idx_dict[sym] #find index of stock in symbol_file (symbol[idx] = stock name)
    tm_ms = get_ms(tm) #get the number of milliseconds passed since the 9.30am (ignore the break between 11.30am and 1pm)
    prc = int(row[6]) #get latest transaction price of the stock at that tick
    hist_ms_prc[idx].append((tm_ms, prc)) #appending the tuple (number of milliseconds since 9.30am, latest transaction price of the stock at that tick) to the stock array
    order = ('N', 0)
    
    if tm_ms < 13800000:  # before 14:50:00 (13800000 is output of getms(145000000))
        if tm_ms - last_od_ms[idx] < 300000:  # execute the order every 5 minutes
        
        #if time passed between previous order and current is less than 5 minutes, do nothing and go to next iteration
        
            order_time.writelines(f'{sym},N,{nTick},0\n') 
            order_time.flush()
            continue

        # find the indexes at different time
        ms_temp, prc_temp = zip(*(hist_ms_prc[idx])) #unzip file to get all records in history for the stock
        idx_5min, idx_10min, idx_15min, idx_20min, idx_25min = 0, 0, 0, 0, 0
        for i, m in enumerate(ms_temp): #i will be counter, m is each element of ms_temp
            if tm_ms - m >= 300000: #if (current time - time recorded) is more than 5 mins, set idx_5min to be counter
                idx_5min = i
            if tm_ms - m >= 600000: #if (current time - time recorded) is more than 10 mins, set idx_10min to be counter
                idx_10min = i
            if tm_ms - m >= 900000: #if (current time - time recorded) is more than 15 mins, set idx_15min to be counter
                idx_15min = i
            if tm_ms - m >= 1200000: #if (current time - time recorded) is more than 20 mins, set idx_20min to be counter
                idx_20min = i
            if tm_ms - m >= 1500000: #if (current time - time recorded) is more than 25 mins, set idx_25min to be counter
                idx_25min = i
                
            # set the idx_(x)min to be the index of record in hist_ms_prc where record is more than x mins ago
            
            # eg if idx_25min = 3, then hist_ms_prc[idx][3] was the most recent record measured more than 25 mins ago 
            # and hist_ms_prc[idx][4] onwards is recorded less than 25 mins ago

        # calculate the 10 factor variables and make prediction
        if idx_25min != 0: 
            
        # if there is a record recorded more than 25 mins ago for a particular stock
        # all idx_(x)min will be non zero at this point as well
            
            x = np.array([
                prc / prc_temp[idx_5min] - 1, #get (ratio of current price with price at the most recent record measured more than 5 mins ago) - 1
                prc / prc_temp[idx_10min] - 1, #get (ratio of current price with price at the most recent record measured more than 10 mins ago) - 1
                prc / prc_temp[idx_15min] - 1, #get (ratio of current price with price at the most recent record measured more than 15 mins ago) - 1
                prc / prc_temp[idx_20min] - 1, #get (ratio of current price with price at the most recent record measured more than 20 mins ago) - 1
                prc / prc_temp[idx_25min] - 1, #get (ratio of current price with price at the most recent record measured more than 25 mins ago) - 1
                max(prc_temp[idx_5min:]) / min(prc_temp[idx_5min:]) - 1, #get (ratio of largest price from list K1 with lowest price from list K1) - 1 where K1 is the list of prices occuring from most recent record measured more than 5 mins ago till the current record
                max(prc_temp[idx_10min:]) / min(prc_temp[idx_10min:]) - 1, #get (ratio of largest price from list K2 with lowest price from list K2) - 1 where K2 is the list of prices occuring from most recent record measured more than 10 mins ago till the current record
                max(prc_temp[idx_15min:]) / min(prc_temp[idx_15min:]) - 1, #get (ratio of largest price from list K3 with lowest price from list K3) - 1 where K3 is the list of prices occuring from most recent record measured more than 15 mins ago till the current record
                max(prc_temp[idx_20min:]) / min(prc_temp[idx_20min:]) - 1, #get (ratio of largest price from list K4 with lowest price from list K4) - 1 where K4 is the list of prices occuring from most recent record measured more than 20 mins ago till the current record
                max(prc_temp[idx_25min:]) / min(prc_temp[idx_25min:]) - 1, #get (ratio of largest price from list K5 with lowest price from list K5) - 1 where K5 is the list of prices occuring from most recent record measured more than 25 mins ago till the current record
            ]).reshape(1, -1) #convert array to (1, 10)
            y = model.predict(x)[0] #predict a value for y (price) based on x

            if y >= 0:
                od_vol = basic_vol + unfinished_buy[idx]
                
                #if price is predicted to increased, order volume to buy is set to basic_vol (2) + unfinished_buy for the specified stock
                
                if target_vol - cum_vol_buy[idx] >= od_vol: #to check if we still have not bought 100 stocks, will execute if statement
                    order = ('B', od_vol)
                    cum_vol_buy[idx] += od_vol #add order volume to cumulative buy order volume 
                else:
                    order = ('B', target_vol - cum_vol_buy[idx]) #buy remaining stocks
                    cum_vol_buy[idx] = target_vol #cannot buy anymore stocks
                unfinished_buy[idx] = 0 #bought the unfinished buy stock
                unfinished_sell[idx] += basic_vol #have to sell the stocks you buy
            else:
                od_vol = basic_vol + unfinished_sell[idx]
                
                #if price is predicted to decrease, order volume to sell is set to basic_vol (2) + unfinished_sell for the specified stock
                
                if target_vol - cum_vol_sell[idx] >= od_vol: #to check if we still have not sold 100 stocks, will execute if statement
                    order = ('S', od_vol)
                    cum_vol_sell[idx] += od_vol #add order volume to cumulative sold order volume 
                else:
                    order = ('S', target_vol - cum_vol_sell[idx]) #sell remaining stocks
                    cum_vol_sell[idx] = target_vol #cannot sell anymore stocks
                unfinished_sell[idx] = 0 #sold the unfinished sell stock
                unfinished_buy[idx] += basic_vol #have to buy the stocks you sell
                
    else:  # force complete before market closes (only execute after 14:50pm)
        if tm_ms - last_od_ms[idx] >= 60000: #if at least 1 min (60000 milliseconds) has passed between any orders for that specific stock, then execute if statement
            if target_vol - cum_vol_buy[idx] > 0: #if still have unbought stocks (bought less than 100), buy everything
                order = ('B', target_vol - cum_vol_buy[idx])
                cum_vol_buy[idx] = target_vol
            elif target_vol - cum_vol_sell[idx] > 0: #if still have unbought stocks (sold less than 100), sell everything
                order = ('S', target_vol - cum_vol_sell[idx])
                cum_vol_sell[idx] = target_vol
    
    # write order
    if order[0] == 'N':
        order_time.writelines(f'{sym},N,{nTick},0\n') #do nothing for the tick
        order_time.flush()
    else:
        last_od_ms[idx] = tm_ms
        order_time.writelines(f'{sym},{order[0]},{nTick},{order[1]}\n') #perform order
        order_time.flush()

    # -------- Your Strategy Code End --------

# ---------- Post Processing ----------

tick_data.close()
order_time.close()

    
    