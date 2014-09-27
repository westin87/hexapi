#!/usr/bin/python3

import unittest
import time
import socket
import utils.movement
import network.network_handler


class NetworkTestClient:
    def __init__(self, host, port):
        print("NH test client: Client created")
        self.rpiSocket = socket.socket()
        self.host = host
        self.port = port
        self.arg1 = "-1"
        self.arg2 = "-1"
        return

    def connect(self):
        print("NH test client: Client connecting")
        self.rpiSocket.connect((self.host, self.port))
        pass

    def disconnect(self):
        self.rpiSocket.close()
        pass

    def send(self, data):
        self.rpiSocket.send(data)

    def callbackTestFunc(self, arg1, arg2):
        self.arg1 = arg1
        self.arg2 = arg2


class MovementTestCases(unittest.TestCase):
    
    def setUp(self):
        self.move = utils.movement.Movement(50)
        
    def testSetPitch0(self):
        self.move.setPitch(0)
        self.assertEqual(self.move.pwm.stopTick, 307, "Faulty pitch calculation")
        
    def testSetPitch100(self):
        self.move.setPitch(100)
        self.assertEqual(self.move.pwm.stopTick, 409, "Faulty pitch calculation")
        
    def testSetPitchMinus100(self):
        self.move.setPitch(-100)
        self.assertEqual(self.move.pwm.stopTick, 205, "Faulty pitch calculation")
        
class NetworkHandlerTestCases(unittest.TestCase):
    
    def setUp(self):
        port = 12325
        self.nhServer = network.network_handler.NetworkHandler(port)
        self.nhClient = NetworkTestClient("127.0.0.1", port)
        
        self.nhServer.registerCallback(self.nhClient.callbackTestFunc, "makeCallback")
        
        self.nhServer.start()
        time.sleep(1)
        self.nhClient.connect()
        
    def tearDown(self):
        self.nhClient.disconnect()
        time.sleep(1)
        
    def testCallback(self):
        data = "makeCallback 1337 42"
        self.nhClient.send(data.encode(encoding='utf_8', errors='strict'))
        time.sleep(1)
        self.assertEqual(self.nhClient.arg1, "1337", "Callback not working")
        self.assertEqual(self.nhClient.arg2, "42", "Callback not working")
        
    def testInvalidCallback(self):
        data = "makeInvalidCallback 1337 42"
        self.nhClient.send(data.encode(encoding='utf_8', errors='strict'))
        time.sleep(1)
        self.assertEqual(self.nhClient.arg1, "-1", "Callback not working")
        self.assertEqual(self.nhClient.arg2, "-1", "Callback not working")
        
    
if __name__ == '__main__':
    unittest.main()
