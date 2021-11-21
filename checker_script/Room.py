class Room:
    def __init__(self, name, availability_thisweek, availability_nextweek):
        self.name = name
        self.availability_thisweek = availability_thisweek
        self.availability_nextweek = availability_nextweek

    def printToConsole(self):
        print(self.name)
        for x in self.availability_thisweek:
            print(x)
        for x in self.availability_nextweek:
            print(x)
