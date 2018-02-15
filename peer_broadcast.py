#code for peer2peer hash broadcast and replication
#Assuming a 4 P2P n/w having an initial default hash
import hashlib as hs

class hash_broadcast_replicate:

    def __init__(self):#initializing default hashes to all the 4 peers of n/w
        k = hs.sha256(str("2 bitcoins processed at 21/01/2018").encode('utf-8'))  # bytes literal key
        self.peer1_state = k
        self.peer2_state = k
        self.peer3_state = k
        self.peer4_state = k


    def peer1(self,val):#first node of p2p n/w
        updated_hash = self.hash_code_generate(self.peer1_state,val)
        self.replication(updated_hash)

    def peer2(self,val):#second node of p2p n/w
        updated_hash = self.hash_code_generate(self.peer2_state,val)
        self.replication(updated_hash)

    def peer3(self,val):#third node of p2p n/w
        updated_hash = self.hash_code_generate(self.peer3_state,val)
        self.replication(updated_hash)

    def peer4(self,val):#fourth node of p2p n/w
        updated_hash = self.hash_code_generate(self.peer4_state,val)
        self.replication(updated_hash)

    def replication(self,val):#updating same hash to all peer states
        self.peer1_state = val
        self.peer2_state = val
        self.peer3_state = val
        self.peer4_state = val

    def hash_code_generate(self,old_hash,new_key):#hash code generator function which works in accordance with SHA256 protocol
        #new_hashobj = hs.sha256(bytes(str(new_key),encoding='utf-8'))  # bytes literal key
        old_hash.update(new_key)#updating old hash key with the new one
        new_hash = old_hash.hexdigest()  # bytes literal encoded to hexadecimal hashkey
        return new_hash

    def process(self,peer_val,hash_val):
        value = hash_val
        self.switch_peers(peer_val)

    def switch_peers(self,peer_val,hash_val):#switching to the broadcaster peer
        method_name = 'peer'+str(peer_val)
        method = getattr(self, method_name, lambda: "No such peer exists")
        method(hash_val)
        # switcher = {
        #     1:self.peer1(),
        #     2:self.peer2(),
        #     3:self.peer3(self.value),
        #     4:self.peer4(self.value)
        # }
        # print("kkkk")
        #peer_func = switcher.get(peer_val,hash_val,lambda: "No such peer exists")



def main():
    x = input("Enter peer no. to broadcast message:")#numerical input
    y1 = input("Enter new transaction info:")#string input
    p1 = hash_broadcast_replicate()
    y = str(y1).encode("utf-8")
    print("hash before broadcast:",p1.peer1_state.hexdigest())
    p1.switch_peers(x,y)
    print("hash after broadcast:",p1.peer1_state)

if __name__ == "__main__":
    main()



