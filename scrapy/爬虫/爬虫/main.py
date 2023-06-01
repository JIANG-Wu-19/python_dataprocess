import requests,re,json
import bs4
from bs4 import BeautifulSoup
import pandas as pd
import pymysql
# import matplotlib.pyplot as plt
from pyecharts.charts import Bar, Kline, EffectScatter, Line
from pyecharts import options as opts
import wx
import wx.grid
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import webbrowser


# 获取网页HTML代码
from textdistance import Overlap


# def getHtml(stack_code):
#     data = requests.get("https://q.stock.sohu.com/cn/" +
#     stack_code + "/lshq.shtml",
#     headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.58"})
#     # 获得一个请求得到的静态网页
#     return data.text


# 将HTML文本转化成字典列表
# def getData(data):
#     month_data = []
#     soup = BeautifulSoup(data, "lxml")  # data由getHtml()取得
#     # 爬取网页的工具
#     list = soup.find("div", class_="part").find("table", class_="tableQ")
#     # 看html，已经把不需要的都删了，数据在innerbox的table_bg001 border_box limit_sale下面
#     dataList = list.find_all("tr")[1:]
#     # 因为第一个tr后面是一堆th标签，不需要
#     f = open("data.txt", "w", encoding="utf-8")
#     for item in dataList:
#         kv = {}
#         if isinstance(item, bs4.element.Tag):
#             tdList = item.find_all("td")
#             # print(tdList)
#             kv["日期"] = tdList[0].text  # 去掉td和/td，取中间的内容
#             kv["开盘价"] = tdList[1].text
#             kv["最高价"] = tdList[6].text
#             kv["最低价"] = tdList[5].text
#             kv["收盘价"] = tdList[2].text
#             kv["成交量"] = tdList[7].text
#         month_data.append(kv)
#         to_write = json.dumps(kv,ensure_ascii=False)
#         f.write(to_write)
#         # print(kv)
#     f.close()
#     # print(month_data)  # 字典列表
#     return month_data

def getData(stack_code):
    month_data = []
    driver = webdriver.Chrome()
    driver.get('http://q.stock.sohu.com/cn/'+stack_code+'/lshq.shtml')
    time.sleep(5)

    f=open("data.txt","w",encoding="utf-8")

    for i in range(2, 81):
        kv={}
        try:
            kv["日期"] = driver.find_element(By.XPATH,'//*[@id="BIZ_hq_historySearch"]/tbody/tr['+str(i)+']/td[1]').text
            kv["开盘价"] = driver.find_element(By.XPATH,'//*[@id="BIZ_hq_historySearch"]/tbody/tr['+str(i)+']/td[2]').text
            kv["最高价"] = driver.find_element(By.XPATH,'//*[@id="BIZ_hq_historySearch"]/tbody/tr['+str(i)+']/td[7]').text
            kv["最低价"] = driver.find_element(By.XPATH,'//*[@id="BIZ_hq_historySearch"]/tbody/tr['+str(i)+']/td[6]').text
            kv["收盘价"] = driver.find_element(By.XPATH,'//*[@id="BIZ_hq_historySearch"]/tbody/tr['+str(i)+']/td[3]').text
            kv["成交量"] = driver.find_element(By.XPATH,'//*[@id="BIZ_hq_historySearch"]/tbody/tr['+str(i)+']/td[8]').text
            print("complete")
        except:
            print("找不到元素")
            continue
        month_data.append(kv)
        to_write = json.dumps(kv,ensure_ascii=False)
        f.write(to_write)
    f.close()
    # driver.close()
    driver.quit()
    return month_data

# 从字典列表取出数据存入数据库中
def Storage(data):
    # 连接数据库
    my_database = pymysql.connect(
        host='localhost',
        user='root',
        password='986370165'
    )
    # 生成游标对象
    cursor = my_database.cursor()
    # 创建数据库
    sql_createDataBase = "create database if not exists stockData"
    cursor.execute(sql_createDataBase)
    sql_useDataBase = "USE stockData"
    # 创建表
    cursor.execute(sql_useDataBase)
    sql_createTable = '''create table if not exists data(
                    date DATE,
                    opening_price float,
                    closing_price float,
                    highest float,
                    lowest float)
    '''
    cursor.execute(sql_createTable)
    # 从字典列表中取出数据存入数据库中
    for item in data:
        sql_Insert = '''Insert into data values
        ('{0}',{1},{2},{3},{4})'''.format(item['日期'], item['开盘价'], item['收盘价'], item['最高价'], item['最低价'])
        cursor.execute(sql_Insert)
    cursor.close()
    my_database.commit()
    my_database.close()
    # print(my_database)


date = []
opening_price = []
closing_price = []
highest = []
lowest = []


# 为画K线图做数据处理，将五个数据分别放进五个列表中
def data_Pretreatment(month_data):
    for data in month_data:
        my_date = data.get("日期")
        my_open = data.get("开盘价")
        my_close = data.get("收盘价")
        my_high = data.get("最高价")
        my_low = data.get("最低价")
        date.append(my_date)
        opening_price.append(my_open)
        closing_price.append(my_close)
        highest.append(my_high)
        lowest.append(my_low)


def draw(date,lowest):
    bar1 = Bar()
    bar1.add_xaxis(date)
    bar1.add_yaxis("最低价", lowest)
    bar1.set_series_opts(
        # 是否显示标签
        label_opts=opts.LabelOpts(is_show=False)
        , markpoint_opts=opts.MarkPointOpts(
            data=[opts.MarkPointItem(type_="max", name="max"),
                  opts.MarkPointItem(name="min", type_="min")]
        ),
        markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(name="average", type_="average")]))
    bar1.set_global_opts(
        xaxis_opts=opts.AxisOpts(

            axislabel_opts=opts.LabelOpts(rotate=-60, font_size=10),
        ),
        yaxis_opts=opts.AxisOpts(
            name="价格：(元/股)",
        ),
    )
    bar1.render("最低价.html")


def draw_K():
    kline = Kline().set_global_opts(title_opts=opts.TitleOpts(title="K线图"))
    v1 = []
    size = len(opening_price)  # 有多少条数据（多少天）
    for i in range(size-1, 0, -1):
        tmp = [opening_price[i], closing_price[i], lowest[i], highest[i]]
        v1.append(tmp)  # 整合好一组数据存入v1中
    # print(v1)

    kline.add_yaxis(series_name="日K", y_axis=v1)
    kline.add_xaxis([s for s in date])
    kline.render("K图.html")


def store_in_dataframe(month_data):
    my_list = []
    for item in month_data:
        tmp = list(item.values())
        my_list.append(tmp)
    # print(my_list)
    my_dataframe = pd.DataFrame(my_list,
    columns=["datetime", 'open', 'close', 'low', 'high', "trade_sum"])
    print(my_dataframe)
    my_dataframe.to_excel("数据.xlsx")
    return my_dataframe



def back_testing_plot(table_name, indicator_name_list):
    # data preparation
    da = pd.DataFrame(data=table_name)
    # da['trade_sum'] = da['trade_sum'].apply(lambda vol: vol if vol > 0 else 0)
    date = da["datetime"].apply(lambda x: str(x)).tolist()
    k_plot_value = da.apply(lambda record: [record['open'],
                                            record['close'],
                                            record['low'],
                                            record['high']],
                            axis=1).tolist()

    # K chart
    kline = Kline()
    kline.add("Back_testing Result", date, k_plot_value)

    indicator_lines = Line()
    for indicator_name in indicator_name_list:
        indicator_lines.add(indicator_name,
                            date,
                            da[indicator_name].tolist(),
                            mark_point=["max", "min"],
                            )
    # trading volume bar chart
    bar = Bar()
    print(type(max(da["trade_sum"])))
    bar.add("trade_sum", date, da["trade_sum"],
            tooltip_tragger="axis",
            is_legend_show=False,
            is_yaxis_show=False,
            yaxis_max=5 * max(da["trade_sum"]),
            )
    # buy and sell
    v1 = date[10]
    v2 = da['high'].iloc[10]
    es = EffectScatter("buy")
    es.add("buy", [v1], [v2])
    v1 = date[18]
    v2 = da['high'].iloc[18]
    es.add("sell", [v1], [v2], symbol="pin", )

    overlap = Overlap()
    overlap.add(kline)
    overlap.add(indicator_lines, )
    overlap.add(bar)
    overlap.add(es)
    overlap.render(path='高级图.html')


class MyFrame(wx.Frame):
    data = []
    column_names = []
    stock_Code = ""

    def __init__(self, data, column_names):
        super().__init__(parent=None, title="股票数据显示界面", size=(600, 600))
        self.data = data
        self.column_names = column_names
        self.Centre()
        panel = wx.Panel(parent=self)
        # self.message1 = wx.StaticText()
        # self.message1.SetLabelText("请输入股票代码")
        # self.message1.SetPosition((400,370))
        self.number = wx.TextCtrl(panel, pos=(450, 370))
        query_button = wx.Button(parent=panel, id=1, label='查询K图', pos=(450, 400))
        post = wx.Button(parent=panel, id=2, label='更新', pos=(450, 435))
        show = wx.Button(parent=panel, id=3, label='查看表格', pos=(450, 470))
        self.Bind(wx.EVT_BUTTON, self.on_click, query_button)
        self.Bind(wx.EVT_BUTTON, self.on_click, post)
        self.Bind(wx.EVT_BUTTON, self.on_click, show)
        # self.Bind(wx.EVT_TEXT, self.EvtText)
        # 建立表格

    def generate_xlsx(self):
        self.grid = self.CreateGrid(self)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClick)

    def on_click(self, event):
        event_id = event.GetId()
        print(event_id)
        if event_id == 1:
            print("查询K图")
            webbrowser.open('K图.html')
        elif event_id == 2:
            self.stock_Code = self.number.GetValue()
            print(self.number.GetValue())
            update_xlsx(self, self.stock_Code)
        elif event_id == 3:
            self.generate_xlsx()

    def OnLabelLeftClick(self, event):
        print("RowIdx：{0}".format(event.GetRow()))
        print("ColIdx：{0}".format(event.GetCol()))
        print(self.data[event.GetRow()])
        event.Skip()

    def CreateGrid(self, parent):
        grid = wx.grid.Grid(parent)
        grid.CreateGrid(len(self.data), len(self.data[0]))

        for row in range(len(self.data)):
            for col in range(len(self.data[row])):
                grid.SetColLabelValue(col, self.column_names[col])
                grid.SetCellValue(row, col, self.data[row][col])
        # 设置行和列自定调整
        grid.AutoSize()

        return grid


class App(wx.App):
    data = []
    column_names = []

    def show(self):
        frame = MyFrame(self.data, self.column_names)
        frame.Show()
        return True


def update_xlsx(app, stock_code):
    month_data = getData(stock_code)
    Storage(month_data)
    store_in_dataframe(month_data)
    my_list = []
    for item in month_data:
        tmp = list(item.values())
        my_list.append(tmp)
    app.data = my_list
    update(month_data)

def update(month_data):
    date.clear()
    opening_price.clear()
    closing_price.clear()
    highest.clear()
    lowest.clear()
    data_Pretreatment(month_data)
    draw_K()




data=getData("300117")  # 字典列表
date.sort(key=lambda k: k['日期'])
Storage(data)
store_in_dataframe(data)
data_Pretreatment(data)
draw_K()

# print(data)
app = App()
my_list = []
for item in data:
    print(item)
    tmp = list(item.values())
    my_list.append(tmp)
app.data = my_list
app.column_names = ["datetime", 'open', 'close', 'low', 'high', "trade_sum"]
print(app.data)
app.show()
app.MainLoop()