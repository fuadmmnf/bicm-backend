from django.shortcuts import render
from django.http import JsonResponse
from lxml import html
import requests
import pandas as pd
# Create your views here.
def sector_wise_volumes(request):  # crawl dse website and calculate sector wise volume data
    url = "https://www.dsebd.org/latest_share_price_scroll_by_ltp.php"
    df = pd.read_html(url)
    df = df[384]
    totalVolume = 0
    for i in range(384): # calculate total volume summation
        totalVolume = totalVolume + df.iat[i, 10]

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

    sectorVolumeCount = {}
    for i in range(384):  # calculate sector wise volume summation
        if df.at[i, 'TRADING CODE'] in companySectorDictionary:
            sectorOfCompany = companySectorDictionary[df.at[i, 'TRADING CODE']]
        if sectorOfCompany in sectorVolumeCount:
            sectorVolumeCount[sectorOfCompany] = sectorVolumeCount[sectorOfCompany] + df.at[i, 'VOLUME']
        else:
            sectorVolumeCount[sectorOfCompany] = 1

    sectorVolumePercentage = {}
    for sectorOfCompany in sectorVolumeCount: # calculate sector wise volume percentage
        sectorVolumePercentage[sectorOfCompany] = (sectorVolumeCount[sectorOfCompany] * 100) / totalVolume


    return JsonResponse({'data': sectorVolumePercentage})

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