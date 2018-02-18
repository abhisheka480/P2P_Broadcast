import pong as pong
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
import json as js
from uuid import uuid4
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from time import time
from twisted.internet.task import LoopingCall
import hashlib as hs
import cryptotools
import os

class hash_broadcast_replicate:

    def __init__(self):#initializing default hashes to all the 4 peers of n/w
        k = hs.sha256(str("2 bitcoins processed at 21/01/2018").encode('utf-8'))  # bytes literal key
        self.peer1_state = k
        self.peer2_state = k
        self.peer3_state = k
        self.peer4_state = k
    def hash_code_generate(self,old_hash,new_key):#hash code generator function which works in accordance with SHA256 protocol
        #new_hashobj = hs.sha256(bytes(str(new_key),encoding='utf-8'))  # bytes literal key
        old_hash.update(new_key)#updating old hash key with the new one
        new_hash = old_hash.hexdigest()  # bytes literal encoded to hexadecimal hashkey
        return new_hash

class MyProtocol(Protocol):
    def __init__(self, factory,peertype):
        self.factory = factory
        self.state = "HELLO"
        self.remote_nodeid = None
        # nodeid = hs.sha256(os.urandom(256/8)).hexdigest()[:10]
        # self.nodeid = self.nodeid
        self.lc_ping = LoopingCall(self.send_ping)
        self.peertype = peertype
        self.lastping = None

    def connectionMade(self):
        remote_ip = self.transport.getPeer()
        host_ip = self.transport.getHost()
        self.remote_ip = remote_ip.host + ":" + str(remote_ip.port)
        self.host_ip = host_ip.host + ":" + str(host_ip.port)
        print "Connection from", self.transport.getPeer()

    def connectionLost(self, reason):
        if self.remote_nodeid in self.factory.peers:
            self.factory.peers.pop(self.remote_nodeid)
            self.lc_ping.stop()
        print self.nodeid, "disconnected"

    def send_ping(self):
        ping = js.puts({'msgtype': 'ping'})
        print "Pinging", self.remote_nodeid
        self.transport.write(ping + "\n")

    def dataReceived(self, data):
        for line in data.splitlines():
            line = line.strip()
            msgtype = js.loads(line)['msgtype']
            if self.state == "HELLO" or msgtype == "hello":
                self.handle_hello(line)
                self.state = "READY"
            elif msgtype == "ping":
                self.handle_ping()
            elif msgtype == "pong":
                self.handle_pong()
            elif msgtype == "getaddr":
                self.handle_getaddr()

    def send_addr(self, mine=False):
        now = time()
        if mine:
            peers = [self.host_ip]
        else:
            peers = [(peer.remote_ip, peer.remote_nodeid)
                     for peer in self.factory.peers
                     if peer.peertype == 1 and peer.lastping > now - 240]
        addr = js.puts({'msgtype': 'addr', 'peers': peers})
        self.transport.write(peers + "\n")


    def handle_addr(self, addr):
        json = js.loads(addr)
        for remote_ip, remote_nodeid in json["peers"]:
            if remote_nodeid not in self.factory.peers:
                host, port = remote_ip.split(":")
                point = TCP4ClientEndpoint(reactor, host, int(port))
                d = connectProtocol(point, MyProtocol(2))
                d.addCallback(gotProtocol)

    def handle_getaddr(self, getaddr):
        self.send_addr()

    def handle_hello(self, hello):
        hello = js.loads(hello)
        self.remote_nodeid = hello["nodeid"]
        if self.remote_nodeid == self.nodeid:
            print "Connected to myself."
            self.transport.loseConnection()
        else:
            self.factory.peers[self.remote_nodeid] = self
            self.lc_ping.start(60)
            ###inform our new peer about us
            self.send_addr(mine=True)
            ###and ask them for more peers
            self.send_getaddr()

def generate_nodeid():
    return hs.sha256(os.urandom(256/8)).hexdigest()


class MyFactory(Factory):
    # def __init__(self):
    #     self.nodeid = hs.sha256(os.urandom(256 / 8)).hexdigest()[:10]
    def startFactory(self):
        self.peers = {}
        self.nodeid = hs.sha256(os.urandom(256/8)).hexdigest()[:10]

    def stopFactory(self):
        pass

    def buildProtocol(self):
        return MyProtocol(self)


def main():
    obj_hash = hash_broadcast_replicate()
    # endpoint = TCP4ServerEndpoint(reactor, 5999)
    # mcx = MyFactory()#peer1 initialization
    # endpoint.listen(mcx)

    PEER_LIST = ["localhost:5999"
        , "localhost:5998"
        , "localhost:5997"
        ,"localhost:5996"]#4 node p2p n/w hosted on local host having different ports

    for peer in PEER_LIST:
        endpoint = TCP4ServerEndpoint(reactor, 5999)
        mcx = MyFactory()  # peers initialization
        endpoint.listen(mcx)
        host, port = peer.split(":")
        point = TCP4ClientEndpoint(reactor, host, int(port))
        d = connectProtocol(point, MyProtocol(mcx,2))
        d.addCallback(gotProtocol)
    reactor.run()



def gotProtocol(p):
    p.send_hello()

if __name__ == "__main__":
    main()
