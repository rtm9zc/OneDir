
if __name__ == "__main__":
    with open ("log.txt", "r") as myfile:
        data=myfile.read().replace('\n', '')
    print data
