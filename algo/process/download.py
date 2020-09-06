# -*- coding: utf-8 -*-
# @author: Ting-Hao Chen
# @date: 2020/09/06


import sys

sys.path.append("../")

import pandas as pd
import tushare as ts
from datetime import date
from tqdm import tqdm
from config import TUSHARE_TOKEN


def download_ticker_mapping(tushare_token, ticker_path=None):
    ts.set_token(tushare_token)
    pro = ts.pro_api()
    df_ticker = pro.stock_basic(exchange="", list_status="L", fields="")

    if ticker_path is not None:
        df_ticker.to_excel(ticker_path, index=False, encoding="utf_8_sig")

    return df_ticker


def download_price(tushare_token, df_ticker, end_date, price_path=None):
    ts.set_token(tushare_token)
    pro = ts.pro_api()
    ts_code_list = df_ticker["ts_code"].tolist()
    start_date_list = df_ticker["list_date"].tolist()

    df_price_all = pd.DataFrame()
    for ts_code, start_date in zip(tqdm(ts_code_list), start_date_list):
        df_price = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        df_price_all = df_price_all.append(df_price)

    df_price_all["trade_date"] = pd.to_datetime(df_price_all["trade_date"], format="%Y%m%d")
    _sum = df_price_all["close"].sum()
    df_price_all = pd.merge(df_price_all, df_ticker, how="left", on="ts_code")
    assert df_price_all["close"].sum() == _sum

    if price_path is not None:
        df_price_all.to_csv(price_path, index=False, encoding="utf_8_sig")

    return df_price_all


def download_by_tushare(tushare_token, end_date, ticker_path=None, price_path=None):
    df_ticker = download_ticker_mapping(tushare_token, ticker_path)
    df_price = download_price(tushare_token, df_ticker, end_date=end_date, price_path=price_path)

    return df_ticker, df_price


if __name__ == "__main__":
    # Parameter
    today = str(date.today()).replace("-", "")
    ticker_path = "../data/raw_data/tushare_ticker_list_{}.xlsx".format(today)
    price_path = "../data/clean_data/china_stock_price_{}.csv".format(today)

    df_ticker, df_price = download_by_tushare(
        TUSHARE_TOKEN, end_date=today, ticker_path=ticker_path, price_path=price_path)


