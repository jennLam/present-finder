import datetime

def hello():
    with open('date.txt', 'a') as outFile:
        outFile.write('\n' + str(datetime.datetime.now()))

hello()
