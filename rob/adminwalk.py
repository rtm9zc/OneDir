import os

def adminFiles(path): #returns a string with all
                      #subdirectories, files, and sizes under path
    outstring = ''
    totalsize = 0
    for dirname, dirnames, filenames in os.walk(path):
        # print path to all subdirectories first.
        outstring = outstring + "Subdirectories: \n"
        for subdirname in dirnames:
            outstring = outstring + os.path.join(dirname, subdirname) + '\n'
        outstring = outstring + "\nFiles: \n"
        # print path to all filenames.
        for filename in filenames:
            outstring = outstring + os.path.join(dirname, filename) + '\n'
            outstring = outstring + "Size (bytes): " + str(os.path.getsize(filename)) +'\n'
            totalsize += os.path.getsize(filename)
    outstring = outstring + "\nTotal size (bytes): " + str(totalsize)
    return outstring