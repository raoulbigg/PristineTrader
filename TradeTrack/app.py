from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import pandas as pd
import json
import requests
import glob
from csv import writer


app = Flask(__name__)



@app.route('/')
def screener():
    images = []
    for file in os.listdir('static/screener'):
        if file.endswith('.png'):
            images.append(file)
    meta = open("static/screener/meta1d.json")
    meta_json = json.load(meta)
    print(meta_json)
    return render_template('screener.html', images=images, meta=meta_json, mode="screen", img_src="static")



@app.route('/metrics', methods=['GET', 'POST'])
def metrics(play=None):
    filter_string = False
    #If play selected from playground select play .csv data
    if request.args.get('play'):
        trades_csv_file = "static/playground/"+request.args.get('play')
    else:
        trades_csv_file = "trades.csv"
    # read csv
    csv = pd.read_csv(trades_csv_file, sep=";", encoding='unicode_escape', on_bad_lines='skip', header=0)
    csv = csv.fillna('None')
    columns = csv.columns
    #if POST request get filtered csv
    if request.method == 'POST':
        column = request.form.get('column')
        operator = request.form.get('operator')
        #try to make an integer of value else string
        try:
            value = int(request.form.get('value'))
        except:
            value = str(request.form.get('value'))
        csv = filter(csv, column, operator, value)
        filter_string=str("'"+column+"' "+operator+" "+str(value))

    #calculate statistics
    total_pnl = calculate_pnl(csv)
    win_loss = calculate_win_loss_ratio(csv)
    symbols = all_symbols(csv)
    profit_loss = all_profit_loss(csv)
    days = most_least_active_day(csv)
    #return the values of the csv to metrics.html
    df = list(csv.values)
    return render_template('metrics.html', 
        trades=df,
        columns=columns,
        total_pnl=total_pnl, 
        wins=win_loss[0], 
        losses=win_loss[1],
        symbols=symbols,
        profit_loss=profit_loss[0],
        equity_curve=profit_loss[1],
        total_r=profit_loss[2],
        average_winning_r=profit_loss[3],
        average_losing_r=profit_loss[4],
        days=days,
        filter=filter_string,
        file=trades_csv_file)


@app.route('/add_trade', methods=['POST'])
def add_trade():
    data_to_append = [request.form['trade_number'],request.form['date'], request.form['day'], request.form['timeframe'], 
                      request.form['ticker'],  request.form['buy_sell'],  request.form['size'],
                      request.form['equity_risk'],  request.form['r_r'],  request.form['win_loss'],
                      request.form['pnl'],  request.form['screenshot'],  request.form['duration'],
                      request.form['management_number'],  request.form['reason_to_sell'],  request.form['mistake'],
                      request.form['mentor_feedback'] ]
    with open(request.form['csv_file'], 'a') as f_object:
     
        # Pass this file object to csv.writer()
        # and get a writer object
        writer_object = writer(f_object, delimiter=';')
     
        # Pass the list as an argument into
        # the writerow()
        writer_object.writerow(data_to_append)
     
        # Close the file object
        f_object.close()
    return redirect(url_for('metrics'))

@app.route('/managements', methods=['GET', 'POST'])
def managements():
    #read and load json file containing management iterations
    management_json = open("static/managements/managements.json")
    data = json.load(management_json)
    return render_template('managements.html', data=data)


@app.route('/playground', methods=['GET', 'POST'])
def playground():
    #list all csv files in folder
    playground_files = glob.glob("static/playground/*.csv")
    return render_template('playground.html', playground_files=playground_files)

@app.route('/playground/<play>', methods=['GET' ,'POST'])
def playground_open(play):
    return redirect(url_for('metrics', play=play))

@app.route('/trades_csv')
def trades_csv():
    return send_file('trades.csv')


#Below are functions to calculate metrics

def calculate_pnl(csv):
    pnl = 0
    for i in range(len(csv)):
        pnl = pnl + float(csv.iloc[i]['PnL'])
    return round(pnl,2)

def calculate_win_loss_ratio(csv):
    win = 0
    loss = 0
    for i in range(len(csv)):
        if 'Win' in csv.iloc[i]["Win/Loss"]:
            win = win +1
        elif 'Loss' in csv.iloc[i]["Win/Loss"]:
            loss = loss +1
    return win, loss

def all_symbols(csv):
    symbols = []
    for i in range(len(csv)):
        symbols += csv.iloc[i]['Symbol']
    return symbols

def all_profit_loss(csv):
    profit_loss = []
    equity = []
    s = 0
    average_r = 0
    average_r_loss = 0
    total_r = 0
    winning_count = 0
    losing_count = 0
    #loop over every entry in csv and append pnl results
    for i in range(len(csv)):
        profit_loss.append(csv.iloc[i]['PnL'])
        #iterate over every entry and + it with pnl
        s = s + csv.iloc[i]['PnL']
        equity.append(s)
        #iterate over ebery entry and calc average R and total R
        total_r = total_r + csv.iloc[i]['Realised R:R']
        #calculate average winning R
        if csv.iloc[i]['Realised R:R'] > 0:
            winning_count = winning_count + 1
            average_r = average_r +csv.iloc[i]['Realised R:R']
        #calculate average losing R
        elif csv.iloc[i]['Realised R:R'] < 0:
            losing_count = losing_count + 1
            average_r_loss = average_r_loss + csv.iloc[i]['Realised R:R']

    try:
        average_r = average_r / winning_count
        average_r_loss = average_r_loss / losing_count
    except:
        average_r = 0
        average_r_loss = 0

    return profit_loss, equity, total_r, average_r, average_r_loss

def most_least_active_day(csv):
    return csv['Day of entry'].value_counts().items()


def filter(csv, column, operator, value):
    if operator == "==":
        filtered = csv[csv[column] == value]
    elif operator == ">":
        filtered = csv[csv[column] > value]
    elif operator == "<":
        filtered = csv[csv[column] < value]
    elif operator == "contains":
        filtered = csv[csv[column].str.contains(str(value))]
    elif operator == "not contains":
        filtered = csv[~csv[column].str.contains(value)]
    return filtered


if __name__ == '__main__':
    app.run(host="0.0.0.0")
