

class PWM:
    def __init__(self, data, debug):
        self.freq = -1
        self.channel = -1
        self.startTick = -1
        self.stopTick = -1

        pass

    def setPWMFreq(self, freq):
        print "ST: Frequency set to: " + str(freq)
        self.freq = freq

    def setPWM(self, channel, startTick, stopTick):
        print "ST: PWM set for channel: " + str(channel) +\
            " with start: " + str(startTick) + " and stop: " +\
            str(stopTick)

        self.channel = channel
        self.startTick = startTick
        self.stopTick = stopTick
