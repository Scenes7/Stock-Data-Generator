from flask import Flask, render_template, request
from bokeh.models import HoverTool
from bokeh.plotting import figure
import yfinance as yf
from bokeh.resources import INLINE
import random
import math
from flask_cors import CORS
import json
from bokeh.embed import json_item
from datetime import datetime, timedelta
import pandas as pd


app = Flask(__name__)
CORS(app)

targetEps = {
    'tech': 1.3,
    'defense': 1.8,
    'hedge': 5,
    'other': 2
}
targetPE = {
    'tech': 150,
    'defense': 100,
    'hedge': 70,
    'other': 120
}

fields = [
    'name',
    'exchange',
    'earnings',
    'price',
    'shares'
]


def generate_datetime_index(num_days):
    current_date = datetime.now().date()
    end_date = current_date + timedelta(days=num_days)
    date_index = pd.date_range(start=current_date, end=end_date, freq='B')
    return date_index


def growth_function(x):
    return ((x-5)**3)/30000 + x/10


def calculate_changes(price, earnings, shares, industry=None, exchange=None, volitility=0, bias1=0):
    mx = 0.1*volitility
    current_price = price
    ret = [price]
    bench_eps, bench_pe = targetEps[industry], targetPE[industry]

    for i in range(66):
        eps = earnings/shares
        pe = current_price/eps

        if (earnings < 0): eps_dif, pe_dif = eps-bench_eps, pe-bench_pe
        else: eps_dif, pe_dif = eps-bench_eps, bench_pe-pe

        # print(i, eps, eps_dif, pe, pe_dif)
        growth = min(1, growth_function(eps_dif)/100)*current_price*mx + min(1, growth_function(pe_dif)/100)*current_price*mx
        current_price += growth + bias1
        current_price = max(1, current_price)
        current_price+=current_price*mx*random.randint(-1, 1)*(1/random.randint(1, 5-min(4, int(volitility*5))))  
        ret.append(current_price)
    
    return ret


def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period='1y')
    return data

@app.route('/')
def index():
    stock_symbol = 'AAPL'
    stock_data = get_stock_data(stock_symbol)

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    return render_template(
        'index.html',
        plot_script="", 
        plot_div="", 
        css_resources=css_resources, 
        js_resources=js_resources
    )

@app.route('/submission', methods=['POST'])
def createGraph():

    #name, exchange, industry, earnings, prices, shares
    actualData = json.loads(request.data)

    for field in fields:
        if not actualData[field]: return "fill out all basic information and at least 1 quarter.", 400

    name = actualData['name']
    exchange = actualData['exchange']
    industry = actualData['industry']
    earnings = actualData['earnings']
    price = actualData['price']
    shares = actualData['shares']
    print(name, earnings, price, shares, exchange, industry)
    # print(request.data)
    quarters = len(shares)

    try:
        price = float(price)
        for i in range(quarters):
            earnings[i] = float(earnings[i])
            shares[i] = int(shares[i])
            if (price < 0 or shares[i] < 0):
                return "prices and shares must not be less than 0", 400
    except ValueError:
        return "earnings, price, and shares must be numeric", 400
    if (len(name) > 100):
        return "name must be shorter than 100 characters (incuding spaces)", 400
    if (industry == "select" or exchange == "select"):
        return "select and industry and an exchange", 400
    
    v = 0
    if (industry == 'NASDAQ'): v+=0.05
    if (industry == "tech"): v+=0.05
    elif (industry == "defense"): v+=0.02
    elif (industry == "hedge"): v+=0.01
    else: v+=0.03

    a = [[], [], [], []]
    for i in range(quarters):
        current_price = price if i == 0 else a[i-1][-1]
        x = current_price/(1e9)
        if (x < 16.65): current_volitility = v+0.6
        else: current_volitility = v+round((math.e **(-x-2))*100 + 10/x, 5)
        a[i] = calculate_changes(current_price, earnings[i], shares[i], industry, exchange, current_volitility, 0)

    stock_symbol = 'AAPL' ##
    stock_data = get_stock_data(stock_symbol) ##

    p = figure(width = 1500, title=f'Stock Price of {name}', x_axis_type="datetime", sizing_mode="scale_width")

    p.line(generate_datetime_index(len(a[0]+a[1]+a[2]+a[3])), a[0]+a[1]+a[2]+a[3], line_width = 3)

    hover_tool = HoverTool(tooltips=[('Date', '@x{%F}'), ('Price', '@y')], formatters={'@x': 'datetime'})
    p.add_tools(hover_tool)
    p.toolbar.active_drag = None
    p.toolbar.active_scroll = None
    p.toolbar.active_tap = None

    return json.dumps(json_item(p, "bokeh-graph"))
    
    #volitility by industry, market cap, and exchange
    #nasdaq: +0.05
    #industries: tech: +0.05
    # defense: +0.02
    #hedge: +0.01
    #other: +0.03
    #market cap: max of 0.25, min of 0. addition of 0 if market cap > 500 B


if __name__ == '__main__':
    app.run(debug=True)
