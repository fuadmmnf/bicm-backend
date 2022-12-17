from django.shortcuts import render
from django.http import JsonResponse
# from lxml import html
# from numpy import indices
import requests
import pandas as pd
from datetime import datetime, timedelta
from  bs4 import BeautifulSoup
from bdshare import get_hist_data
from django.views.decorators.cache import never_cache

# Create your views here.

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


@never_cache
def pe_ratio(request):
    from lxml import html
    import requests
    import pandas as pd
    import math
    url = "https://dsebd.org/latest_PE.php"
    peDataFrame=pd.read_html(url)
    desiredListOfColumns=['#',
    'Trade Code',
    'Close Price',
    'YCP',
    'P/E 1*(Basic)',
    'P/E 2*(Diluted)',
    'P/E 3*(Basic)',
    'P/E 4*(Diluted)',
    'P/E 5*',
    'P/E 6*']
    i=0
    for part in peDataFrame:
        if desiredListOfColumns==list(part.columns):
            peDataFrame=part
            break
        
        

    sizeOfDataFrame=len(peDataFrame.index)
    returnList=list()
    for i in range(sizeOfDataFrame):
        toAppend=peDataFrame.at[i, desiredListOfColumns[4]]
        if not isfloat(toAppend):
            returnList.append(0)
        elif math.isnan(float(toAppend)):
            returnList.append(0)
        else:
            returnList.append(float(toAppend))
# creating companySectorDictionary by reading txt file

    sectorFile=open("companysector.txt", "r")
    sectorFlag=1
    currentSector=""
    companySectorDictionary={}
    for line in sectorFile:
        if line=="\n":
            sectorFlag=1
        else:
            line=line.strip()
            if sectorFlag==1:
                currentSector=line
                sectorFlag=0
            else:
                companySectorDictionary[line]=currentSector
# calculating return of each sector and putting in a dictionary sectorReturnCount

    sectorPECount={}
    size=len(peDataFrame.index)
    for i in range(size):
        if peDataFrame.at[i, 'Trade Code'] in companySectorDictionary:
            sectorOfCompany=companySectorDictionary[peDataFrame.at[i, 'Trade Code']]
        if sectorOfCompany in sectorPECount:
            sectorPECount[sectorOfCompany]+=float(returnList[i])
        else:
            sectorPECount[sectorOfCompany]=float(returnList[i])

    return JsonResponse({'data': sectorPECount})


@never_cache
def sector_wise_volumes(request):  # crawl dse website and calculate sector wise volume data
    from lxml import html
    import requests
    import pandas as pd
    url = "https://www.dsebd.org/latest_share_price_scroll_by_ltp.php"
    dataframe=pd.read_html(url)

    desiredListOfColumns=['#',
    'TRADING CODE',
    'LTP*',
    'HIGH',
    'LOW',
    'CLOSEP*',
    'YCP*',
    'CHANGE',
    'TRADE',
    'VALUE (mn)',
    'VOLUME']

    for part in dataframe:
        if desiredListOfColumns==list(part.columns):
            dataframe=part
            break
    totalVolume=0
    for i in range(384):
        totalVolume=totalVolume+dataframe.iat[i, 10]
    # creating companySectorDictionary by reading txt file

    sectorFile=open("companysector.txt", "r")
    sectorFlag=1
    currentSector=""
    companySectorDictionary={}
    for line in sectorFile:
        if line=="\n":
            sectorFlag=1
        else:
            line=line.strip()
            if sectorFlag==1:
                currentSector=line
                sectorFlag=0
            else:
                companySectorDictionary[line]=currentSector
    # calculating volume of each sector in putting in a dictionary sectorVolumeCount

    sectorVolumeCount={}
    size=len(dataframe.index)
    for i in range(size):
        if dataframe.at[i, 'TRADING CODE'] in companySectorDictionary:
            sectorOfCompany=companySectorDictionary[dataframe.at[i, 'TRADING CODE']]
        if sectorOfCompany in sectorVolumeCount:
            sectorVolumeCount[sectorOfCompany]=sectorVolumeCount[sectorOfCompany]+dataframe.at[i, 'VOLUME']
        else:
            sectorVolumeCount[sectorOfCompany]=dataframe.at[i, 'VOLUME']
    sectorVolumePercentage={}
    for sectorOfCompany in sectorVolumeCount:
        sectorVolumePercentage[sectorOfCompany]=(sectorVolumeCount[sectorOfCompany]*100)/totalVolume


    return JsonResponse({'data': sectorVolumePercentage})


@never_cache
def sector_wise_return(request): # crawl dse website and calculate sector wise return data
    url = "https://dsebd.org/dse_close_price.php"
    closePriceDataFrame=pd.read_html(url)
    desiredListOfColumns=['#', 'TRADING CODE', 'CLOSEP*', 'YCP*']
    i=0
    for part in closePriceDataFrame:
        if desiredListOfColumns==list(part.columns):
            closePriceDataFrame=part
            break
    sizeOfDataFrame = len(closePriceDataFrame.index)
    returnList = list()
    for i in range(sizeOfDataFrame):
        returnList.append(
            closePriceDataFrame.at[i, desiredListOfColumns[3]] - closePriceDataFrame.at[i, desiredListOfColumns[2]])
    totalReturn = 0
    for value in returnList: # calculate total return summation
        totalReturn = totalReturn + value

    sectorFile = open("companysector.txt", "r")
    sectorFlag = 1
    currentSector = ""
    companySectorDictionary = {}
    for line in sectorFile:
        if line == "\n":
            sectorFlag = 1
        else:
            line = line.strip()
            if sectorFlag == 1:
                currentSector = line
                sectorFlag = 0
            else:
                companySectorDictionary[line] = currentSector

    # calculating return of each sector and putting in a dictionary sectorReturnCount
    sectorReturnCount = {}
    size = len(closePriceDataFrame.index)
    for i in range(size): # calculate sector wise return summation
        if closePriceDataFrame.at[i, 'TRADING CODE'] in companySectorDictionary:
            sectorOfCompany = companySectorDictionary[closePriceDataFrame.at[i, 'TRADING CODE']]
        if sectorOfCompany in sectorReturnCount:
            sectorReturnCount[sectorOfCompany] = sectorReturnCount[sectorOfCompany] + returnList[i]
        else:
            sectorReturnCount[sectorOfCompany] = returnList[i]
    sectorReturnPercentage = {}
    for sectorOfCompany in sectorReturnCount: # calculate sector wise return percentage
        sectorReturnPercentage[sectorOfCompany] = (sectorReturnCount[sectorOfCompany] * 100) / totalReturn
        
    return JsonResponse({'data': sectorReturnPercentage})



def extract_date(date):
    new_date = ""
    for i in date:
        if i=='-' or (i<='9' and i>='0'):
            new_date+=i
    return new_date

def extract_data(data):
    new_data = ""
    for i in data:
        if i=='.' or (i<='9' and i>='0'):
            new_data+=i
    return new_data

def extract_time(date):
    # print(date)
    n_date, time = date.split(' ')
    new_time = ""
    return time

def get_monthly_indices_data(market):
    url = "https://dsebd.org/php_graph/monthly_graph_index.php?type="+market+"&duration=1"
    pages = requests.get(url)
    pages.text
    pageData = str(BeautifulSoup(pages.text, 'lxml'))
    flag = False
    datapoints = list()
    for line in pageData.split('\n'):
        if line.find("Date,"+market.upper()+" Index") != -1:
            flag = True
        elif flag:
            for data in line.split('\"+\"'):
                datapoints.append(data)
            break

    tot_datapoints = len(datapoints)
    first_day_data = datapoints[0]
    last_day_data = datapoints[tot_datapoints-1]
    last_day_data = last_day_data[:-2]
    # print(last_day_data)
    first_day, first_data = first_day_data.split(',')
    last_day, last_data = last_day_data.split(',')
    
    first_data, last_data = float(extract_data(first_data)), float(extract_data(last_data))
    indices = [first_data, last_data, last_data-first_data, (last_data-first_data)*100/first_data]
    '''first , last, change, change(%)'''
    return indices

def ret_json_monthly_indices(indices):
    data = {
        "First Day Value": indices[0],
        "Last Day Value": indices[1],
        "Change": indices[2],
        "Change(%)": indices[3]
    }
    return data

@never_cache
def get_dsex_monthly_indices(request):
    indices = get_monthly_indices_data('dseX')
    data = ret_json_monthly_indices(indices)
    return JsonResponse(data)

@never_cache
def get_dses_monthly_indices(request):
    indices = get_monthly_indices_data('dseS')
    data = ret_json_monthly_indices(indices)
    return JsonResponse(data)
@never_cache
def get_ds30_monthly_indices(request):
    indices = get_monthly_indices_data('ds30')
    data = ret_json_monthly_indices(indices)
    return JsonResponse(data)
@never_cache
def get_cdset_monthly_indices(request):
    indices = get_monthly_indices_data('cdset')
    data = ret_json_monthly_indices(indices)
    return JsonResponse(data)

def get_daily_indices_from_market(pageData, st):
    datapoints = list()
    # print(type(pageData))
    flag = False
    for line in pageData.split('\n'):
        if line.find("var index_value_"+st+" = ") != -1:
            flag = True
            # print(line)
            # continue
        if flag:
            # print('yo')
            for data in line.split('\"+\"'):
                # print(data)
                datapoints.append(data)
            break

    # print(datapoints)
    mydata = list()
    for i in range(1, len(datapoints)):
        time, t_data = datapoints[i].split(',')
        # time = time[:-1]
        time = extract_time(time)
        t_data = float(extract_data(t_data))
        mydata.append([time, t_data])
    return mydata

def daily_indices(market):
    web_url = "https://www.dsebd.org/"
    html = requests.get(web_url).content
    soup = BeautifulSoup(html, "html.parser")
    # print(soup)
    market_data = get_daily_indices_from_market(str(soup), market)

    return market_data
@never_cache
def get_dsex_daily_indices(request):
    indices = daily_indices('dsbi')
    return JsonResponse({'indices':indices})

@never_cache
def get_dses_daily_indices(request):
    indices = daily_indices('dses')
    return JsonResponse({'indices':indices})
@never_cache
def get_ds30_daily_indices(request):
    indices = daily_indices('ds30')
    return JsonResponse({'indices':indices})
@never_cache
def get_cdset_daily_indices(request):
    indices = daily_indices('cdset')
    return JsonResponse({'indices':indices})

def getPrevYearMonth():
    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    prevMonth = currentMonth-1 + (currentMonth==1)*12
    prevYear = currentYear
    if prevMonth == 12: prevYear-=1
    return str(prevMonth), str(prevYear)

def count_mkt_aggr():
    num_of_days = [0, 31, 27, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    prevMonth, prevmonthYear = getPrevYearMonth()
    if len(prevMonth) == 1 : prevMonth = '0'+prevMonth
    end_date = prevmonthYear + '-' + prevMonth + '-' + str(num_of_days[int(prevMonth)])
    start_date = prevmonthYear + '-' + prevMonth + '-01'
    url = 'https://dsebd.org/market_summary.php?startDate='+start_date+'&endDate='+end_date+'&archive=data'
    dataFrame = pd.read_html(url)
    print(url)
    # startDate, endDate = extractDays(url)
    # days = int(endDate[8]+endDate[9]) - int(startDate[8]+startDate[9]) + 1
    days = num_of_days[int(prevMonth)]
    tot_market_cap, tot_traded_val, tot_num_of_trades, tot_trade_vol = 0, 0, 0, 0
    
    for tab in dataFrame:
        if list(tab.columns) == [0, 1, 2, 3]:
            tot_num_of_trades += float(tab[3][1])
            tot_traded_val += float(tab[3][2])
            tot_trade_vol += float(tab[3][3])
            tot_market_cap += float(tab[3][4])

    avg_market_cap, avg_traded_val, avg_num_of_trades, avg_trade_vol = tot_market_cap/days, tot_traded_val/days, tot_num_of_trades/days, tot_trade_vol/days
    market_aggr = avg_market_cap, avg_traded_val, avg_num_of_trades, avg_trade_vol
    return market_aggr

@never_cache
def get_avg_market_aggregate(request):
    mkt_aggr = count_mkt_aggr()
    data = {
        'Market Capital': mkt_aggr[0],
        'Traded Value': mkt_aggr[1],
        'Number of Trades': mkt_aggr[2],
        'Trade Volume': mkt_aggr[3]
    }
    return JsonResponse(data)

def count_specific_ad_ratio(cat):
    url = "https://www.dsebd.org/market-statistics.php"
    pages = requests.get(url)
    pages.text
    pageData = str(BeautifulSoup(pages.text, 'lxml'))
    flag = False
    for line in pageData.split('\n'):
        if line.find(cat+' Category') != -1:
            flag = True
        if flag and line.find('ISSUES ADVANCED') != -1:
            ad_issue = line
        elif flag and line.find('ISSUES DECLINED') != -1:
            dc_issue = line
            break
    
    ad_num = [int(s) for s in str.split(ad_issue) if s.isdigit()]
    dc_num = [int(s) for s in str.split(dc_issue) if s.isdigit()]
    print(cat, ad_num, dc_num)
    if dc_num[0]: ad_ratio = ad_num[0]/dc_num[0]
    else: ad_ratio = min(1, ad_num[0])
    return ad_ratio

@never_cache
def get_all_ad_ratio(request):
    ad_ratios = {
        'All Category': count_specific_ad_ratio('All'),
        'A Category': count_specific_ad_ratio('A'),
        'B Category': count_specific_ad_ratio('B'),
        'N Category': count_specific_ad_ratio('N'),
        'Z Category': count_specific_ad_ratio('Z'),
    }
    return JsonResponse(ad_ratios)

def extract_adn_val(lines):
    values = list()
    for line in lines:
        line = line[:-6]
        val = ""
        i = len(line)-1
        while line[i]!='>':
            val = line[i] + val
            i-=1
        values.append(int(val))
    return values

def todays_adn():
    url = "https://www.dsebd.org/"
    pages = requests.get(url)
    pages.text
    pageData = str(BeautifulSoup(pages.text, 'lxml'))
    # print(pageData)
    skipLine = -100
    adn = list()
    for line in pageData.split('\n'):
        if line.find('Issues Advanced') != -1:
            skipLine = 5
        if skipLine <= 0 and skipLine >= -2:
            adn.append(line)
        if skipLine == -3:
            break
        if skipLine != -100:
            skipLine -=1

    advance, decline, nutral = extract_adn_val(adn)
    return advance, decline, nutral

@never_cache
def get_todays_adn(request):
    advance, decline, neutral = todays_adn()
    data = {
        'Advanced': advance,
        'Declined': decline,
        'Neutral': neutral
    }
    return JsonResponse(data)


def extract_tvv_val(line):
    val = ""
    for i in line:
        if i=='.' or (i>='0' and i<='9'):
            val += i
    return val

def todays_tvv():
    url = "https://www.dsebd.org/"
    pages = requests.get(url)
    pages.text
    pageData = str(BeautifulSoup(pages.text, 'lxml'))
    # print(pageData)
    skipLine = -100
    tvt = list()
    for line in pageData.split('\n'):
        if line.find('Total Trade') != -1:
            skipLine = 6
        if skipLine <= 0 and skipLine >= -4:
            if skipLine % 2 == 0:
                tvt.append(line)
        if skipLine == -5:
            break
        if skipLine != -100:
            skipLine -=1

    tot_trade = int(extract_tvv_val(tvt[0]))
    tot_volume = int(extract_tvv_val(tvt[1]))
    tot_value = float(extract_tvv_val(tvt[2]))

    return tot_trade, tot_volume, tot_value

@never_cache
def get_todays_tvv(request):
    trade, volume, value = todays_tvv()
    tvv = {
        'Total Trade': trade,
        'Total Volume': volume,
        'Total Value': value
    }
    return JsonResponse(tvv)

def top_5_turnover():
    '''returns top 5 firms based on last month's last days turover'''
    today_s = datetime.today()
    yesterday_s = today_s - timedelta(days = 1)
    today = today_s.strftime("%Y-%m-%d")
    yesterday = yesterday_s.strftime("%Y-%m-%d")

    try:    
        first_day_data = get_hist_data(today, today)
    except:
        first_day_data = []
    while(len(first_day_data) == 0):
        today_s = yesterday_s
        yesterday_s = today_s - timedelta(days = 1)
        today = today_s.strftime("%Y-%m-%d")
        yesterday = yesterday_s.strftime("%Y-%m-%d")
        try:    
            first_day_data = get_hist_data(today, today)
        except:
            first_day_data = []
    # print(first_day_data)
    try:
        end_day_data = get_hist_data(yesterday, yesterday)
    except:
        end_day_data = []
    while(len(end_day_data)==0):
        yesterday_s = yesterday_s - timedelta(days=1)
        yesterday = yesterday_s.strftime("%Y-%m-%d")
        try:
            end_day_data = get_hist_data(yesterday, yesterday)
        except:
            end_day_data = []

    listOfFirms = list()
    for j in range(len(end_day_data)):
        for i in range(len(first_day_data)):
            if first_day_data.symbol[i] == end_day_data.symbol[j]:
                if float(first_day_data.value[i])!= 0:
                    '''uncomment to get top firm based on latest turnover'''
                    # cur_data = get_hist_data(end_date, end_date, first_day_data.symbol[i])
                    # turnover = (float(cur_data.ycp[j]) - float(cur_data.close[j])) / float(cur_data.close[j])
                    turnover = (float(end_day_data.ycp[j]) - float(end_day_data.close[j])) / float(end_day_data.close[j])
                    change = -1 * (float(end_day_data.value[j]) - float(first_day_data.value[i])) / float(first_day_data.value[i])
                    listOfFirms.append([first_day_data.symbol[i], turnover, change*100, float(first_day_data.value[j])])
                    break

    # print(listOfFirms)
    listOfFirms.sort(reverse = True, key = lambda x: x[2])
    top5Firms = list()
    for i in range(5):
        top5Firms.append([listOfFirms[i][0], listOfFirms[i][3], listOfFirms[i][2]])

    return top5Firms

@never_cache
def get_top_5_turnover(self):
    return JsonResponse(top_5_turnover(), safe=False)

def top_5_gainer():
    '''returns top 5 firms based on price change'''
    today_s = datetime.today()
    today = today_s.strftime("%Y-%m-%d")
    try:    
        first_day_data = get_hist_data(today, today)
        # print('hi')
    except:
        first_day_data = []
    while(len(first_day_data) == 0):
        today_s = today_s - timedelta(days=1)
        today = today_s.strftime("%Y-%m-%d")
        try:    
            first_day_data = get_hist_data(today, today)
        except:
            first_day_data = []

    listOfFirms = list()
    for i in range(len(first_day_data)):
        if float(first_day_data.ltp[i]):
            change =  -1 * (float(first_day_data.ycp[i]) - float(first_day_data.close[i])) / float(first_day_data.close[i])
            listOfFirms.append([first_day_data.symbol[i], first_day_data.value[i], change*100])
    listOfFirms.sort(reverse=True, key = lambda x: x[2])
    return listOfFirms[:5]
@never_cache
def get_top_5_gainer(self):
    return JsonResponse(top_5_gainer(), safe=False)


def top_5_loser():
    '''returns top 5 firms based on price change'''
    today_s = datetime.today()
    today = today_s.strftime("%Y-%m-%d")
    try:    
        first_day_data = get_hist_data(today, today)
        # print('hi')
    except:
        first_day_data = []
    while(len(first_day_data) == 0):
        today_s = today_s - timedelta(days=1)
        today = today_s.strftime("%Y-%m-%d")
        try:    
            first_day_data = get_hist_data(today, today)
        except:
            first_day_data = []

    listOfFirms = list()
    for i in range(len(first_day_data)):
        if float(first_day_data.ltp[i]):
            change = -1 * (float(first_day_data.ycp[i]) - float(first_day_data.close[i])) / float(first_day_data.close[i])
            listOfFirms.append([first_day_data.symbol[i], first_day_data.value[i], change*100])
    listOfFirms.sort(reverse=False, key = lambda x: x[2])
    return listOfFirms[:5]

@never_cache
def get_top_5_loser(self):
    return JsonResponse(top_5_loser(), safe=False)

