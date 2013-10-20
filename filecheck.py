import os.path
import StringIO

with open('data\data.txt', 'r+') as data: #Database file,
                                        # alternating lines of directory, update time of file
    output = StringIO.StringIO()
    while True:
        filename = data.readline()
        if filename == '' or filename == '\n':
            break
        timestr = data.readline()
        time = float(timestr[:(timestr.__len__()-1)]) #-1's done in slice to get rid of \n
        newtime = os.path.getmtime(filename[:(filename.__len__()-1)])
        if newtime > time: #updatates if observed file time above recorded
            time = str(newtime) +'\n'
            #file uploaded to server
        elif newtime < time: #update client side file update if server has newer version
            i = 1
            #file dow2nloaded to client
        output.write(filename) #updating data file
        output.write(time)
    data.seek(0)
    data.write(output.getvalue())
    
