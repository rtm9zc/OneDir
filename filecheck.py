import os.path
import StringIO

with open('data\data.txt', 'r+') as data:
    output = StringIO.StringIO()
    while True:
        filename = data.readline()
        if filename == '':
            break
        timestr = data.readline()
        time = float(timestr[:(timestr.__len__()-1)])
        newtime = os.path.getmtime(filename[:(filename.__len__()-1)])
        if newtime > time:
            time = str(newtime) +'\n'
        output.write(filename)
        output.write(time)
    data.seek(0)
    data.write(output.getvalue())
    #saddasd