# 1. Impliment upvoting on the comment board in app
# 2. Do multithreading for mining server
from hashlib import sha256
import json
import time
import math
import os
import socket
import struct

import base64

from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

global voting_period
voting_period = 120#600#3600 #One Hour

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP
def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)
def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)
def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


#pycryptodome RSA public private keypair functions
def rsa_keypair():
    '''
    Generate a public-private keypair

    Returns:  The private and public keys
    '''
    private_key = RSA.generate(2048)
    return (private_key, private_key.publickey())
def sign(message, private_key):
    '''
    Sign a message(bytes)

    Returns the signature in bytes
    '''
    h = SHA256.new(message.encode('utf-8'))
    signature = base64.b64encode(pkcs1_15.new(private_key).sign(h))
    return signature.decode('utf-8')
def verify(message, signature, public_key):
    h = SHA256.new(message.encode('utf-8'))
    public_key = RSA.import_key(bytes(public_key, 'utf-8'))
    try:
        pkcs1_15.new(public_key).verify(h, base64.b64decode(signature.encode('utf-8')))
        return True
    except (ValueError):
        return False


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()
        #return sha256(json.dumps(self.__dict__, sort_keys=True).encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.difficulty = 2
        self.ccoin_keys()
        self.pcoin_keys()    
        if(os.path.exists("chain.json")):
            self.load()
        else:
            self.create_genesis_block()
    def create_genesis_block(self):
        genesis_transactions = []
        genesis_transactions.append({"Type": "Initial PCoin", "To":self.pcoin_public_key_str, "Amount":"10000"})
        founding_laws = []
        founding_laws.append({"Type": "Founding Law", "Short Text":"Attempting to hack the blockchain is illegal", "Legal Text":"Individuals found attempting to or in the process of hacking or otherwise exploiting vulnerabilities in the blockchain in order to gain monetary or political value will be punished and permanently removed from the blockchain."})
        founding_laws.append({"Type": "Founding Law", "Short Text":"No Bribing Voters", "Legal Text":"Bribing monetarily OR exchanging any goods or services with the expectation of support either through political currency or through voting will result in immediate punishment and expulsion from the blockchain of the individual who initiated the bribery."})
        genesis_transactions = genesis_transactions + founding_laws
        genesis_block = Block(0, genesis_transactions, time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)
    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * self.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash
    def add_block(self, block, proof):
        previous_hash = self.last_block.hash
        if previous_hash != block.previous_hash:
            return False
        if not self.is_valid_proof(block, proof):
            return False
        block.hash = proof
        self.chain.append(block)
        return True
    def is_valid_proof(self, block, block_hash):
        return (block_hash.startswith('0' * self.difficulty) and
                block_hash == block.compute_hash())
    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)
    def ccoin_keys(self):
        '''
        Either load the ccoin private and public keys from memory or create and save them and submit to the chain
        '''
        if(os.path.exists("ccoin_private_key.pem")):
            f = open('ccoin_private_key.pem','r')
            self.ccoin_private_key_str = f.read()
            self.ccoin_private_key = RSA.import_key(bytes(self.ccoin_private_key_str, 'utf-8'))
            f.close()
        
            f = open('ccoin_public_key.pem','r')
            self.ccoin_public_key_str = f.read()
            self.ccoin_public_key = RSA.import_key(bytes(self.ccoin_public_key_str, 'utf-8'))
        
            f.close()
        else: 
            # Otherwise Generate new keys
            self.ccoin_private_key, self.ccoin_public_key = rsa_keypair()
            self.ccoin_private_key_str = self.ccoin_private_key.export_key().decode('utf-8')
            self.ccoin_public_key_str = self.ccoin_public_key.export_key().decode('utf-8')

            f = open('ccoin_private_key.pem','w')
            f.write(self.ccoin_private_key_str)
            f.close()

            f = open('ccoin_public_key.pem','w')
            f.write(self.ccoin_public_key_str)
            f.close()

            self.add_new_transaction({"Type":"CCoin Public Key", "Key":self.ccoin_public_key_str})

        return self.ccoin_private_key, self.ccoin_public_key
    def pcoin_keys(self):
        '''
        Either load saved PCoin keys or create new ones and save and submit to the chain.
        '''
        if(os.path.exists("pcoin_private_key.pem")):
            f = open('pcoin_private_key.pem','r')
            self.pcoin_private_key_str = f.read()
            self.pcoin_private_key = RSA.import_key(bytes(self.pcoin_private_key_str, 'utf-8'))
            f.close()

            f = open('pcoin_public_key.pem','r')
            self.pcoin_public_key_str = f.read()
            self.pcoin_public_key = RSA.import_key(bytes(self.pcoin_public_key_str, 'utf-8'))
            f.close()
        else: 
            # Otherwise Generate new keys
            self.pcoin_private_key, self.pcoin_public_key = rsa_keypair()
            self.pcoin_private_key_str = self.pcoin_private_key.export_key().decode('utf-8')
            self.pcoin_public_key_str = self.pcoin_public_key.export_key().decode('utf-8')

            f = open('pcoin_private_key.pem','w')
            f.write(self.pcoin_private_key_str)
            f.close()

            f = open('pcoin_public_key.pem','w')
            f.write(self.pcoin_public_key_str)
            f.close()

            self.add_new_transaction({"Type":"PCoin Public Key", "Key":self.pcoin_public_key_str})

        return self.pcoin_private_key, self.pcoin_public_key
    def save(self):
        '''
        Saves the blockchain into a json format
        '''
        with open("chain.json", "w") as file:
            json.dump(self.get_chain(), file, indent=4)
    def load(self):
        f = open("chain.json", "r")
        new_chain = json.loads(f.read())
        f.close()
        self.eat_chain(new_chain)
        return True
    def eat_chain(self, chain_dict):
        '''
        Replaces the current chain with the chain contained in chain_dict
        '''
        self.chain = chain_dict["chain"]
        new_chain = []
        for block in chain_dict["chain"]:
            new_block = object.__new__(Block)
            new_block.__dict__ = block
            new_chain.append(new_block)
        self.chain = new_chain
        return True
    def mine(self):
        '''
        Mines the next block of the chain
        When mining is successfully completed the user is able to award themselves
            a set amount of CCoin
        '''
        if not self.unconfirmed_transactions:
            return False
        
        current_time = time.time()

        #Reward the miner with CCoin
        self.add_new_transaction({"Type":"Mining", "Amount":"1", "ID":str(self.ccoin_public_key_str), "Timestamp":str(current_time)})

        #If the voting time period is up with this block then redistribute the PCoin
        last_voting_cycle = self.get_voting_cycle(float(self.get_chain()["chain"][-1]["timestamp"]))
        current_voting_cycle = self.get_voting_cycle(current_time)

        self.check_transactions()
        
        #If we are in a new voting cycle
        if(current_voting_cycle-last_voting_cycle > 0):
            last_law = self.get_current_law(last_voting_cycle)
            #Only try to redistribute pcoin if there was a law to vote on.
            if(last_law != None):
                IDS = []
                for block in self.get_chain()["chain"]:

                    # For the people who voted during the last cycle, redistribute the PCoin
                    if(last_voting_cycle == self.get_voting_cycle(float(block["timestamp"]))):
                        for item in block["transactions"]:
                            if(item["Type"] == "Vote"):
                                IDS.append(item["ID"])

                #Get the pcoin value of the last law to redistribute
                short, legal, pcoin = self.get_current_law_text(last_voting_cycle)
                if(len(IDS) > 0):
                    amount = float(pcoin)/len(IDS)
                    for ID in IDS:
                        self.add_new_transaction({"Type":"PCoin Redist", "Amount":str(amount), "ID":str(ID), "Hash": last_law})

        last_block = self.last_block
        new_block = Block(index=last_block.index + 1,
                        transactions=self.unconfirmed_transactions,
                        timestamp=current_time,
                        previous_hash=last_block.hash)
        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []
        return new_block.index
    
    def get_chain(self):
        '''
        Get the data from the blockchain in a more useable format

        Returns: A Dictionary containing the length of the chain and the chain itself
        '''
        chain_data = []
        for block in self.chain:
            chain_data.append(block.__dict__)
        return {"length": len(chain_data), "chain": chain_data}
    
        # This is possibly useful for transmitting json data over the internet 
        #return json.dumps({"length": len(chain_data), "chain": chain_data})

    def get_yes_comments(self, hash=None):
        '''
        Returns a list of all comments for the law with name==hash who voted yes
        '''
        all_comments = {}
        all_likes = {}
        if(hash == None):
            hash = self.get_current_law()
        for block in self.get_chain()["chain"]:
            for item in block["transactions"]:
                if(item["Type"] == "Vote" and item["Hash"] == hash and str(item["Vote"]) == "1"):
                    all_comments[item["Comment_Hash"]] = item["Comment"]
                    if(item["Like"] not in all_likes.keys()):
                        all_likes[item["Like"]] = 1
                    else:
                        all_likes[item["Like"]] += 1

        #All likes is a dictionary of coment_hash:num_likes - can be used in commented out section below to rank comments        
        # Now that we have all yes comments we need to sort in order of highest voted 
        #sorted_comments = sorted(all_likes.items(), key=lambda x:x[1])
        #highest_comments = []
        #for i in range(len(sorted_comments)):
        #    highest_comments.append(sorted_comments[i][0])
        #return highest_comments
                        
        return all_comments.values()
                        
    def get_no_comments(self, hash=None):
        '''
        Return a list of all comments for the law with name==hash who voted no
        '''
        all_comments = {}
        all_likes = {}
        if(hash == None):
            hash = self.get_current_law()
        for block in self.get_chain()["chain"]:
            for item in block["transactions"]:
                if(item["Type"] == "Vote" and item["Hash"] == hash and str(item["Vote"]) == "-1"):
                    all_comments[item["Comment_Hash"]] = item["Comment"]
                    if(item["Like"] not in all_likes.keys()):
                        all_likes[item["Like"]] = 1
                    else:
                        all_likes[item["Like"]] += 1

        # All likes is a dictionary of coment_hash:num_likes - can be used in commented out section below to rank comments                 
        # Now that we have all yes comments we need to sort in order of highest voted 
        #sorted_comments = sorted(all_likes.items(), key=lambda x:x[1])
        #highest_comments = []
        #for i in range(len(sorted_comments)):
        #    highest_comments.append(sorted_comments[i][0])
        #return highest_comments
                        
        return all_comments.values()
    def draft_law(self, short_text, legal_text):
        '''
        Allows for an individual to submit a law
        A law consists of short text for Advertising and legal text for detail
        '''
        signature=sign(str(short_text)+str(legal_text), self.pcoin_private_key)
        self.add_new_transaction({"Type":"Law", "Short Text":short_text, "Legal Text":legal_text, "ID":str(self.pcoin_public_key_str), "Signature":str(signature), "Hash":sha256((short_text+legal_text+str(self.pcoin_public_key_str)).encode()).hexdigest()})
        return True

    def vote(self, vote, comment="", like=""):
        '''
        Allows for an individual to submit a yes(1) or no(-1) vote to a law based on its hash
        WARNING: The law voted on must be the current law everyone is voting on or else the
            transaction will be rejected.
        '''
        current_time = time.time()
        signature=sign(str(vote)+str(current_time)+str(self.get_current_law())+str(comment)+str(like), self.pcoin_private_key)
        self.add_new_transaction({"Type":"Vote", "Vote":vote, "Hash":self.get_current_law(), "Comment":comment, "Like":like, "ID":str(self.pcoin_public_key_str), "Timestamp":current_time, "Signature":str(signature), "Comment_Hash":sha256((str(vote)+str(current_time)+str(self.get_current_law())+str(comment)+str(like)).encode()).hexdigest()})
    
    def get_passed_laws(self):
        '''
        Get all laws which were voted to become true

        Returns: list of hashes of passed laws
        '''
        votes = {}
        
        #Get all laws with their number of votes
        for block in self.get_chain()["chain"]:
            #Get the founding laws
            if(block["index"] == 0):
                for item in block["transactions"]:
                    if(item["Type"] == "Founding Law"):
                        #Use the short text as the hash
                        votes[item["Short Text"]] = 1.0

            #Dont count the current voting cycle since they are passed yet
            if(self.get_voting_cycle(time.time()) == self.get_voting_cycle(float(block["timestamp"]))):
                break

            #All other laws
            for item in block["transactions"]:
                if(item["Type"] == "Vote"):
                    if(item["Hash"] in votes.keys()):
                        votes[item["Hash"]] += item["Vote"]
                    else:
                        votes[item["Hash"]] = item["Vote"]

        #If yes votes win then append it to the passed law list
        passed_laws = []
        for law, vote in votes.items():
            if(vote > 0):
                passed_laws.append(law)

        return passed_laws
    
    def get_passed_laws_text(self):
        '''
        Get all laws with their short and legal text
        Then return all laws with positive vote sum
        Keys to arrays are the hashes of the short+legal text

        Returns: Short Text(dict), Legal Text(dict)
        '''
        #Get all laws and save their short text
        votes = {}
        short_text = {}
        legal_text = {}

        for block in self.get_chain()["chain"]:
            #Founding Laws
            if(block["index"] == 0):
                for item in block["transactions"]:
                    if(item["Type"] == "Founding Law"):
                        #Use the short text as the hash
                        short_text[item["Short Text"]] = item["Short Text"]
                        legal_text[item["Short Text"]] = item["Legal Text"]
                        votes[item["Short Text"]] = 1.0
            
            #Dont count the current voting cycle since they are passed yet
            if(self.get_voting_cycle(time.time()) == self.get_voting_cycle(float(block["timestamp"]))):
                break

            #All other laws
            for item in block["transactions"]:
                if(item["Type"] == "Vote"):
                    if(item["Hash"] in votes.keys()):
                        votes[item["Hash"]] += item["Vote"]
                    else:
                        votes[item["Hash"]] = item["Vote"]
                if(item["Type"] == "Law"):
                    short_text[item["Hash"]] = item["Short Text"]
                    legal_text[item["Hash"]] = item["Legal Text"]
        
        #Return short text and legal text of all laws with positive vote sum
        passed_short_text = {}
        passed_legal_text = {}
        for law, vote in votes.items():
            if(vote > 0):
                passed_short_text[law] = short_text[law]
                passed_legal_text[law] = legal_text[law]

        return passed_short_text, passed_legal_text

    def get_proposed_laws(self, voting_cycle=None):
        '''
        Get the hashes of all proposed but not yet passed laws
        voting_cycle takes an interger of the voting cycle and can be used for historical analysis

        Returns: list of all proposed laws
        '''
        proposed_laws = []

        #If we dont specify a voting cycle we are interested in, we use the current cycle
        if(voting_cycle == None):
            voting_cycle = self.get_voting_cycle(time.time())

        #Get all law hashes
        for block in self.get_chain()["chain"]:
            if(self.get_voting_cycle(float(block["timestamp"])) > voting_cycle):
                break
            for item in block["transactions"]:
                if(item["Type"] == "Law"):
                    if(not(item["Hash"] in proposed_laws)):
                        proposed_laws.append(item["Hash"])

        #Remove all laws that have been voted on up to the last voting cycle
        for block in self.get_chain()["chain"]:
            if(self.get_voting_cycle(float(block["timestamp"])) < voting_cycle):
                for item in block["transactions"]:
                    if(item["Type"] == "Vote"):
                        if(item["Hash"] in proposed_laws):
                            proposed_laws.remove(item["Hash"])
        return proposed_laws
    
    def get_proposed_laws_text(self, voting_cycle=None):
        '''
        Get the text of all proposed but not yet passed laws 
            as well as their current pcoin values

        Returns: lists of all proposed laws short text, legal text, and pcoin value
        '''
        proposed_laws = []
        short_text = {}
        legal_text = {}
        law_pcoin = {}

        #If we dont specify a voting cycle we are interested in, we use the current cycle
        if(voting_cycle == None):
            voting_cycle = self.get_voting_cycle(time.time())

        #Get all law hashes and text
        for block in self.get_chain()["chain"]:
            if(self.get_voting_cycle(float(block["timestamp"])) > voting_cycle):
                break
            for item in block["transactions"]:
                if(item["Type"] == "Law"):
                    if(not(item["Hash"] in proposed_laws)):
                        proposed_laws.append(item["Hash"])
                        short_text[item["Hash"]] = item["Short Text"]
                        legal_text[item["Hash"]] = item["Legal Text"]
                        law_pcoin[item["Hash"]] = 0.0

        #Count all pcoin values for each law
        for block in self.get_chain()["chain"]:
            if(self.get_voting_cycle(float(block["timestamp"])) > voting_cycle):
                break
            for item in block["transactions"]:
                if(item["Type"] == "PCoin"):
                    law_pcoin[item["Hash"]] += float(item["Amount"])

        #Remove all laws that have been voted on (excluding this cycle)
        for block in self.get_chain()["chain"]:
            if(self.get_voting_cycle(float(block["timestamp"])) >= voting_cycle):
                break
            for item in block["transactions"]:
                if(item["Type"] == "Vote"):
                    if(item["Hash"] in proposed_laws):
                        proposed_laws.remove(item["Hash"])
                        short_text.pop(item["Hash"])
                        legal_text.pop(item["Hash"])
                        law_pcoin.pop(item["Hash"])

        return short_text, legal_text, law_pcoin
    
    def get_voting_cycle(self, timestamp):
        '''
        Takes a timestamp as input and returns the integer voting cycle of that timestamp
        '''
        global voting_period
        voting_start = float(self.get_chain()["chain"][0]["timestamp"])
        return math.floor((float(timestamp) - voting_start)/voting_period)
    
    def get_current_law(self, voting_cycle=None):
        '''
        Get the hash of the current law being voted on

        Gets all proposed laws and sees which has the highest pcoin value
        '''
        if(voting_cycle is None): # If voting cycle isnt specified then assume its the latest cycle
            voting_cycle = self.get_voting_cycle(float(self.get_chain()["chain"][-1]["timestamp"]))

        #Get all proposed laws
        laws_pcoin = {}
        proposed_laws = self.get_proposed_laws(voting_cycle=voting_cycle) 
        
        #Get the pcoin values of all these laws
        for law in proposed_laws:
            laws_pcoin[law] = 0 
        for block in self.get_chain()["chain"]:
            if(self.get_voting_cycle(float(block["timestamp"])) < voting_cycle):
                for item in block["transactions"]:
                    if(item["Type"] == "PCoin"):
                        if(item["Hash"] in proposed_laws):
                            laws_pcoin[item["Hash"]] += float(item["Amount"])
        
        #Get the law with the highest pcoin value
        if(len(laws_pcoin) == 0):
            return None
        return max(zip(laws_pcoin.values(), laws_pcoin.keys()))[1]
    
    def get_current_law_text(self, voting_cycle=None):
        '''
        Get the hash of the current law being voted on then returns the
            short text, legal text, and pcoin value of the law

        Returns: short text, legal text, and pcoin value of the current law being voted on
        '''
        #Get all proposed laws
        laws_pcoin = {}
        short_text = {}
        legal_text = {}
        proposed_laws = self.get_proposed_laws(voting_cycle=voting_cycle) 
        
        #Get the pcoin values of all these laws
        for law in proposed_laws:
            laws_pcoin[law] = 0 
        for block in self.get_chain()["chain"]:
            if(voting_cycle != None and self.get_voting_cycle(float(block["timestamp"])) > voting_cycle):
                break
            else:
                for item in block["transactions"]:
                    if(item["Type"] == "PCoin"):
                        if(item["Hash"] in proposed_laws):
                            laws_pcoin[item["Hash"]] += float(item["Amount"])
                    if(item["Type"] == "Law"):
                        short_text[item["Hash"]] = item["Short Text"]
                        legal_text[item["Hash"]] = item["Legal Text"]
        
        #Get the law with the highest pcoin value
        if(len(laws_pcoin) == 0):
            return "", "", ""
        current_law = max(zip(laws_pcoin.values(), laws_pcoin.keys()))[1]
        return short_text[current_law], legal_text[current_law], laws_pcoin[current_law]
    
    def get_pcoin_balance(self, ID=None):
        '''
        Gets the PCoin Value of the ID from the input

        Returns: PCoin Value of ID (float)
        '''
        if(ID==None):
            ID=self.pcoin_public_key_str
        total = 0.0
        for block in self.get_chain()["chain"]:
            for item in block["transactions"]:
                if(item["Type"]=="Initial PCoin" and item["To"]==ID):
                    total += float(item["Amount"])
                if(item["Type"]=="PCoin Redist" and item["ID"]==ID):
                    total += float(item["Amount"])
                if(item["Type"]=="PCoin" and item["ID"]==ID):
                    total -= float(item["Amount"])
        return total

    def pcoin_transaction(self, hash, amount):
        '''
        Donates pcoin from the user to the law of interest
        The hash value of the law must be used to donate

        Returns: True if successful and False if failed
        '''
        #Remember we also need to write the bit redistributing pcoin after voting in the self.mining function and ensuring this happens in the self.adopt_chain function
        if(self.get_pcoin_balance(str(self.pcoin_public_key_str))-amount < 0):
            print("Not enough PCoin")
            return False
        current_time = time.time()
        signature = sign(str(hash)+str(amount)+str(current_time), self.pcoin_private_key)
        self.add_new_transaction({"Type":"PCoin", "Hash": hash, "ID":str(self.pcoin_public_key_str), "Amount":amount, "Time":current_time, "Signature":str(signature)})
        return True

    def get_ccoin_balance(self, ID=None):
        '''
        Obtain the CCoin balance of any individual by their ID(public key)

        Returns: The total value of CCoin that individual owns
        '''
        if(ID == None):
            ID = self.ccoin_public_key_str
        total = 0.0
        for block in self.get_chain()["chain"]:
            for item in block["transactions"]:
                if(item["Type"]=="Mining" and item["ID"]==ID):
                    total += float(item["Amount"])
                if(item["Type"]=="CCoin" and item["To"]==ID):
                    total += float(item["Amount"])
                if(item["Type"]=="CCoin" and item["From"]==ID):
                    total -= float(item["Amount"])
        return total

    def ccoin_transaction(self, ID, amount):
        '''
        Submits a new CCoin transaction to an individual by their ID(public key)

        Returns: True if successful, False if failed
        '''
        #if(self.get_ccoin_balance(str(self.ccoin_public_key_str))-amount < 0):
        #    print("Not enough Money")
        #    return False
        current_time = time.time()
        signature = sign(str(ID)+str(amount)+str(current_time), self.ccoin_private_key)
        self.add_new_transaction({"Type":"CCoin", "To": ID, "From":str(self.ccoin_public_key_str), "Amount":amount, "Time":current_time, "Signature":str(signature)})
        return True
    
    def check_transactions(self):
        '''
        Checks self.unconfirmed_transactions for invalid transactions
        This function piggybacks off of self.adopt_chain() to allow for patches in the adoption algorithm to automatically be included

        Returns True if all transactions were valid, False if an invalid transaction was found
        '''
        flag = False
        # Get a local copy of the chain to check the validity of the transactions
        base_chain = self.get_chain()
        len_unconfirmed = len(self.unconfirmed_transactions)
        good_transactions = [] #Holds all valid transactions
        for i in range(len_unconfirmed):
            modified_chain = base_chain.copy()
            # Need to copy the chain itself since we will be appending to it
            modified_chain["chain"] = base_chain["chain"].copy()

            # Append the transaction of interest
            modified_chain["chain"].append({"index": modified_chain["length"], "transactions":good_transactions+[self.unconfirmed_transactions[len_unconfirmed-i-1]], "timestamp":time.time(), "previous_hash":'0', "nonce":0, "hash":'0'})
            modified_chain["length"] += 1
            
            # See if we would adopt the transaction
            if(not self.adopt_chain(modified_chain, check_hash=False, keep=False)):
                print(self.unconfirmed_transactions[len_unconfirmed-i-1])
                print("Transactions is BAD!")

                # If the transaction is bad then we remove it
                self.unconfirmed_transactions.pop(len_unconfirmed-i-1)
                flag = True
            else:
                good_transactions.append(self.unconfirmed_transactions[len_unconfirmed-i-1])
        if(flag):
            return False
        else:
            return True
        
    def start_mining_server(self):
        '''
        Start a server in a seperate thread to recieve incoming transactions and then mine them into the chain

        Returns True if the server started successfully and False if the server could not start
        '''

        HOST = get_ip() #Allows for server to function on local network
        #HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
        PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                incoming_data = []
                sent_message = False
                while True:
                    data = conn.recv(1024)
                    data_str = data.decode('utf-8')
                    incoming_data.append(data_str)
                    if not data:
                        all_data = json.loads(all_data)
                        for transaction in all_data["transactions"]:
                            self.unconfirmed_transactions.append(transaction)
                        print(self.unconfirmed_transactions)
                        print("NEW UNCONFIRMED TRANSACTIONS")
                        break
                    
                    #Process the Recieved Data
                    all_data = "".join(incoming_data)
                    print(all_data)
                    # If the communication type is sending transactions
                    
                    if(sent_message == False):
                        send_msg(conn, bytes(str(json.dumps(self.get_chain())),'utf-8'))#chain will be long so we need to use send_msg
                        sent_message = True

                    # If the communication type is asking for the chain
                    #if("get_chain" == all_data):
                    #    send_msg(conn, b"hi")#bytes(str(json.dumps(self.get_chain())),'utf-8'))#chain will be long so we need to use send_msg
                        
        self.mine()

        return True

    def update_with_miner(self, HOST):
        '''
        Sends all unconfirmed transactions to a mining server
        '''
        PORT = 65432  # The port used by the server

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(bytes(str(json.dumps({"transactions": self.unconfirmed_transactions})),'utf-8'))
            chain = json.loads(recv_msg(s).decode('utf-8'))
            
        return self.adopt_chain(chain)
        
    def adopt_chain(self, chain, check_hash=True, keep=True):
        '''
        This Function is very important and does much of the heavy lifting of the network!!!

        This function must check if a given chain is obeying all of the necessary rules and
            conditions of the blockchain

        This includes:
            1. Verifying all signatures
            
            2. Voting:
                All voting must be done on time and be within blocks which are hashed during the voting hours for that law
                No double voting (only a single +1 or -1)

            3. CCoin:
                User must have a public key that was announced earlier
                Amount must be positive (no stealing)
                All users must end up with a positive amount of CCoin

            4. Mining:
                The miner must be compensated at the agreed upon amount
                PCoin must be properly redistributed after a voting cycle

        check_hash = False is used by check_transactions to append transactions to the end of the chain without hashing      
        keep = False is used by check_transactions to see if a block with a given transaction would be valid, without adopting the new transaction immediately  
        
        Returns: True if the chain was adopted, False if the chain was rejected
        '''
        global voting_period
        if(chain["length"] < self.get_chain()["length"]):
            print()
            print("Chain adoption failure 1 - Current Chain is Longer")
            print("My Chain Length: "+str(self.get_chain()["length"]))
            print("Their Chain Length: "+str(chain["length"]))
            return False
        
        # If ccoin key has not yet been announced in this chain or in the transactions then submit it
        #    We also need to check in the chain later
        my_ccoin_public_key = True 
        my_pcoin_public_key = True
        for transaction in self.unconfirmed_transactions:
            if(transaction["Type"] == "CCoin Public Key" and transaction["Key"] == self.ccoin_public_key_str):
                my_ccoin_public_key = False
            if(transaction["Type"] == "PCoin Public Key" and transaction["Key"] == self.pcoin_public_key_str):
                my_pcoin_public_key = False    
        
        #Now we need to check that all signatures are valid, and any other rules necessary for proper functioning
        I_VOTED = []
        CCoin_Accounts = {}
        PCoin_Accounts = {}
        last_time = float(chain["chain"][0]["timestamp"]) #Starts as the initialization time of the blockchain
        last_index = -1
        last_hash = '0'
        all_transactions = []
        for block in chain["chain"]:
            round_mined = False #Flag to ensure that each miner is only compensated once per block
            if(check_hash):
                #Make sure the hash on each chain is valid AND that the last_hash value is correct
                if(block["previous_hash"] != last_hash):
                    print()
                    print("Chain adoption failure 1.5 - Previous hash does not match real value")
                    print("Last Hash: "+str(last_hash))
                    print("Marked Previous Hash: "+str(block["previous_hash"]))
                    return False
                block_copy = block.copy()
                hash_value = block_copy.pop("hash")
                if(hash_value != sha256(json.dumps(block_copy, sort_keys=True).encode()).hexdigest()):#Compute the hash and compare it with the advertised value
                    print()
                    print("Chain adoption failure 1.6 - Advertised block hash value does not match actual hash")
                    print(hash_value)
                last_hash = sha256(json.dumps(block_copy, sort_keys=True).encode()).hexdigest()
            
            #Have to incriment the index each time a block is added
            if(block["index"] != last_index + 1):
                print()
                print("Chain adoption failure 1.8 - Index is wrong")
                print("Last Index: "+str(last_index))
                print("Index: "+str(block["index"]))
                return False
            last_index += 1

            #The Timestamps of each hash have to go forward in time, also no hashes from the future
            if(float(block["timestamp"]) < last_time or float(block["timestamp"]) > time.time()):
                print()
                print("Chain adoption failure 2 - Block timestamps are wrong")
                print("Last Block Time: "+str(last_time))
                print("Block Time: "+str(block["timestamp"]))
                print("Current Clock Time: "+str(time.time()))
                return False
                
            #Next we need to check the transactions inside each block
            for item in block["transactions"]:
                #Check if this transaction is duplicated
                for trans in all_transactions:
                    if(item == trans):#if this item is duplicated
                        print()
                        print("Chain adoption failure 2.5 - duplicated transaction\n")
                        print(item)
                        return False
                all_transactions.append(item)

                #Verify the signature of each law
                if(item["Type"] == "Law"):
                    if(not verify(item["Short Text"]+item["Legal Text"], item["Signature"], item["ID"])):
                        print()
                        print("Chain adoption failure 3 - Law signature forged")
                        print(item)
                        return False
                    
                #Verify the signature of each vote
                if(item["Type"] == "Vote"):
                    if(not verify(str(item["Vote"])+str(item["Timestamp"])+str(item["Hash"])+str(item["Comment"])+str(item["Like"]), item["Signature"], item["ID"])):
                        print()
                        print("Chain adoption failure 5 - Vote signature forged")
                        print(item)
                        return False
                    if(not(item["Vote"] == 1 or item["Vote"] == -1)):#No increasing the vote amount
                        print()
                        print("Chain adoption failure 7 - Vote value is not 1 or -1")
                        print(item)
                        return False
                    if(item["ID"] in I_VOTED): #No Double Voting
                        print()
                        print("Chain adoption failure 8 - Double voting")
                        print(item)
                        return False
                    I_VOTED.append(item["ID"])#If it is a valid vote, add their ID to the voting registration for this round

                if(item["Type"] == "CCoin"):
                    #Verify each CCoin transaction is legitimate
                    if(not verify(str(item["To"])+str(item["Amount"])+str(item["Time"]), item["Signature"], item["From"])):
                        print()
                        print("Chain adoption failure 9 - CCoin transaction forged")
                        print(item)
                        return False
                    
                    #Make sure they are not over-spending
                    if(item["From"] in CCoin_Accounts.keys() and item["To"] in CCoin_Accounts.keys()):
                        CCoin_Accounts[item["From"]] -= float(item["Amount"])
                        CCoin_Accounts[item["To"]] += float(item["Amount"])
                        if(item["Amount"] < 0):#No Stealing
                            print()
                            print("Chain adoption failure 10 - CCoin transaction stealing")
                            print(item)
                            return False
                        if(CCoin_Accounts[item["From"]] < 0):
                            print()
                            print("Chain adoption failure 11 - Individual does not have enough money for CCoin Transaction")
                            print(item)
                            return False
                    else:
                        print()
                        print("Chain adoption failure 12 - Individual has not announced CCoin public key")
                        print(item)
                        return False
                    
                if(item["Type"] == "CCoin Public Key"):
                    CCoin_Accounts[item["Key"]] = 0.0
                    if(item["Key"] == self.ccoin_public_key_str):#Check if your key is in the chain
                        my_ccoin_public_key = False
            
                if(item["Type"] == "PCoin"):
                    #Verify each CCoin transaction is legitimate
                    if(not verify(str(item["Hash"])+str(item["Amount"])+str(item["Time"]), item["Signature"], item["ID"])):
                        print()
                        print("Chain adoption failure 12.1 - PCoin transaction forged")
                        print(item)
                        return False
                    
                    #Make sure they are not over-spending
                    if(item["ID"] in PCoin_Accounts.keys()):
                        PCoin_Accounts[item["ID"]] -= float(item["Amount"])
                        if(item["Amount"] < 0):#No Stealing
                            print()
                            print("Chain adoption failure 12.2 - PCoin transaction stealing")
                            print(item)
                            return False
                        if(PCoin_Accounts[item["ID"]] < 0):
                            print()
                            print("Chain adoption failure 12.3 - Individual does not have enough money for PCoin Transaction")
                            print(item)
                            return False
                    else:
                        print()
                        print("Chain adoption failure 12.4 - Individual has not announced PCoin public key")
                        print(item)
                        return False
                    
                if(item["Type"] == "PCoin Public Key"):
                    if(item["Key"] not in PCoin_Accounts.keys()):#If they are not the PCoin Redist dude
                        PCoin_Accounts[item["Key"]] = 0.
                    if(item["Key"] == self.pcoin_public_key_str):#Check if your key is in the chain
                        my_pcoin_public_key = False    


                if(item["Type"] == "PCoin Redist"):
                    PCoin_Accounts[item["ID"]] += float(item["Amount"])

                if(item["Type"] == "Initial PCoin"):
                    if(str(block["index"]) == "0"):
                        PCoin_Accounts[item["To"]] = float(item["Amount"])
                    else:
                        print()
                        print("Chain adoption failure 12.5 - Initial PCoin found out of place")
                        print(item)
                        return False
                    
                if(item["Type"] == "Mining"):
                    if(round_mined):
                        print()
                        print("Chain adoption failure 13 - miner was rewarded multiple times")
                        print(item)
                        return False
                    else:
                        round_mined = True
                    if(int(item["Amount"]) != 1):
                        print()
                        print("Chain adoption failure 13.1 - Miner is unfairly compenstated")
                        print(item)
                        return False
                
            
            #If a voting round has ended
            if(self.get_voting_cycle(float(block["timestamp"])) > self.get_voting_cycle(last_time)):
                I_VOTED = [] #Clear Voter Registry from last time
                
                # Now we need to check the PCoin has been properly redistributed
                # We start by calculating who should have gotten it ourselves, then compare
                last_law = self.get_current_law(self.get_voting_cycle(last_time))
                IDS = []
                for local_block in chain["chain"]:

                    # For the people who voted during the last cycle, redistribute the PCoin
                    if(self.get_voting_cycle(last_time) == self.get_voting_cycle(float(local_block["timestamp"]))):
                        for local_item in local_block["transactions"]:
                            if(local_item["Type"] == "Vote"):
                                IDS.append(local_item["ID"])

                #Get the pcoin value of the last law to redistribute
                short, legal, pcoin = self.get_current_law_text(self.get_voting_cycle(last_time))
                if(pcoin != "" and len(IDS) > 0):#There was no law to vote on
                    amount = float(pcoin)/len(IDS)
                else:
                    amount = 0
                
                # Now we compare our calculations to the new chain
                for item in block["transactions"]:
                    if(item["Type"] == "PCoin Redist"):
                        if(item["Amount"] == str(amount)):
                            if(item["ID"] in IDS):
                                IDS.remove(item["ID"])
                            else:
                                print()
                                print("Chain adoption failure 13.1.5 - Individual has not announced PCoin public key")
                                print(item)
                                return False
                        else:
                            print()
                            print("Chain adoption failure 13.2 - unequal PCoin redistribution")
                            print(item)
                            return False
                if(len(IDS) > 0 and check_hash):#Needs to be turned off when used in check_transactions() - with check_hash=False
                    print()
                    print("Chain adoption failure 13.3 - Individuals have not been given PCoin after vote")
                    print("Problematic Block Timestamp: "+str(block["timestamp"]))
                    return False
                
            
            # Replace the last block time with the new block time
            last_time = float(block["timestamp"])

        # If ccoin or pcoin public keys have not yet been announced then do so
        if(my_ccoin_public_key):
            self.add_new_transaction({"Type":"CCoin Public Key", "Key":self.ccoin_public_key_str})
        if(my_pcoin_public_key):
            self.add_new_transaction({"Type":"PCoin Public Key", "Key":self.pcoin_public_key_str})
                
        # If it passes all the checks then adopt the chain
        if(keep):
            self.eat_chain(chain)
            # Check all transactions and remove duplicates
            self.check_transactions()
        return True
    
    @property
    def last_block(self):
        return self.chain[-1]

#"""

#'''
if __name__ == "__main__":

    """Now mine the blockchain in browser with Flask
    from flask import Flask, request
    import requests
    app =  Flask(__name__)
    blockchain = Blockchain()

    @app.route('/mine', methods=['GET'])
    def mine_chain():
        blockchain.add_new_transaction("AHHHHHH")
        return str(blockchain.mine())
        return blockchain.get_chain()

    @app.route('/chain', methods=['GET'])
    def get_chain():
        return blockchain.get_chain()

    app.run(debug=True, port=5000)
    #"""

    #Testing!!!
    for file in ["ccoin_private_key.pem", "ccoin_public_key.pem", "pcoin_private_key.pem", "pcoin_public_key.pem", "chain.json"]:
        if(os.path.exists(file)):
            os.remove(file)

    blockchain = Blockchain()
    
    if(not blockchain.adopt_chain(blockchain.get_chain())):
        input("Chain Adoption FAILED!!! - 0")


    #"""Draft a law and mine the chain
    output=False
    if(output):
        print()
        input("Draft a law and mine the chain")

    #Test Law drafting function
    blockchain.draft_law("Turtles are our new overlords", "Turtles have never caused a recession and therefore should be in control of the taxes.")
    blockchain.mine()

    # Test if chain can still be adopted
    if(not blockchain.adopt_chain(blockchain.get_chain())):
        input("Chain Adoption FAILED!!! - 1")

    if(output):
        input(blockchain.get_chain())
    #"""



    #"""Get all proposed Laws and give a pcoin
    time.sleep(0.1)
    output=False
    if(output):
        print()
        input("Get all proposed laws and donate some pcoin")

    # Check Proposed Laws functions
    proposed_laws = blockchain.get_proposed_laws()
    proposed_laws_text = blockchain.get_proposed_laws_text()
    if(output):
        input(proposed_laws)
        input(proposed_laws_text)

    # Test PCoin balance function
    pcoin_balance = blockchain.get_pcoin_balance(blockchain.pcoin_public_key_str)
    if(output):
        input("My PCoin Balance: "+str(pcoin_balance))

    # Test ability to submit a PCoin transaction
    blockchain.pcoin_transaction(proposed_laws[0], 1)
    blockchain.mine()

    # Test PCoin balance function
    pcoin_balance = blockchain.get_pcoin_balance(blockchain.pcoin_public_key_str)
    if(output):
        input("My PCoin Balance: "+str(pcoin_balance))

    #Test if chain can stil be adopted
    if(not blockchain.adopt_chain(blockchain.get_chain())):
        input("Chain Adoption FAILED!!! - 2")

    if(output):
        input(blockchain.get_chain())
    #"""



    #"""Vote on a law
    time.sleep(0.1)
    output=False
    if(output):
        print()
        input("Vote on a law")

    # Test the Get Commands
    current_law = blockchain.get_current_law()
    current_law_text = blockchain.get_current_law_text()
    if(output):
        input(current_law)
        input(current_law_text)

    # Test the voting functions
    blockchain.vote(1, comment="This is RAD", like="some hash")
    blockchain.mine()
    
    yes_comments = blockchain.get_yes_comments()
    if(output):
        print(yes_comments)
    
    # Test the passed law functions
    passed_laws = blockchain.get_passed_laws()
    passed_laws_text = blockchain.get_passed_laws_text()
    if(output):
        input(passed_laws)
        input(passed_laws_text)

    # Check if the chain can still be adopted
    if(not blockchain.adopt_chain(blockchain.get_chain())):
        input("Chain Adoption FAILED!!! - 3")

    if(output):
        input(blockchain.get_chain())
    #"""
        


    """Redistribute PCoin after a vote
    output=False
    if(output):
        print()
        print("Redistributing PCoin After Vote")

    # Add transaction, wait, and mine chain to test pcoin redistrib
    blockchain.ccoin_transaction(blockchain.ccoin_public_key_str, 1)#Trade ccoin with myself
    time.sleep(voting_period+1)
    blockchain.mine()

    #Test if PCoin was redistributed properly
    pcoin_balance = blockchain.get_pcoin_balance(blockchain.pcoin_public_key_str)
    if(output):
        input("My PCoin Balance: "+str(pcoin_balance))

    #Check if the chain can still be adopted
    if(not blockchain.adopt_chain(blockchain.get_chain())):
        input("Chain Adoption FAILED!!! - 4")

    if(output):
        input(blockchain.get_chain())
    #"""



    """Test Saving and Loading the chain
    output=False
    if(output):
        input(blockchain.get_chain())

    #blockchain.save()
    blockchain.load()

    if(output):
        input(blockchain.get_chain())
    #"""


    #"""Make a CCoin Transaction
    time.sleep(0.1)
    blockchain.mine()
    output=False
    if(output):
        input("Balance Before: "+str(blockchain.get_ccoin_balance(str(blockchain.ccoin_public_key_str))))
    blockchain.ccoin_transaction(blockchain.ccoin_public_key_str, 1)#Trade ccoin with myself
    time.sleep(0.1)
    blockchain.mine()

    new_balance = blockchain.get_ccoin_balance(str(blockchain.ccoin_public_key_str))
    if(output):
        input("Balance After (mining as well): "+str(new_balance))

    # Make sure chain can still be adopted
    if(not blockchain.adopt_chain(blockchain.get_chain())):
        input("Chain Adoption FAILED!!! - 5")

    if(output):
        input(blockchain.get_chain())
    #"""

    #""" Submit a CCoin transaction and Check Transactions
    output=False
    time.sleep(0.1)
    blockchain.mine()
    if(output):
        input(blockchain.get_chain())
    
    #THIS IS A BAD TRANSACTION
    #blockchain.ccoin_transaction("0", 0) #Try to give away CCoin to an individual that does not exist
    
    blockchain.ccoin_transaction(blockchain.ccoin_public_key_str, 1) #A valid transaction
    time.sleep(0.1)
    if(output):
        input("Transactions Before: "+str(blockchain.unconfirmed_transactions))
    blockchain.check_transactions()#Check transactions and throw away this one
    if(output):
        input("Transactions After: "+str(blockchain.unconfirmed_transactions))
        print()
        print("Chain")
        input(blockchain.get_chain())
        time.sleep(0.1)
        input(blockchain.mine())
        input(blockchain.get_chain())
    #"""

    """Check start_mining_server
    print("Starting Mining Server...")
    blockchain.start_mining_server()
    #"""
        
    """Send Transactions and Update Chain from miner server
    print("Sending Transactions to Miner and Updating Chain...")
    blockchain.ccoin_transaction("0", 0) #Try to give away CCoin to an individual that does not exist
    blockchain.update_with_miner()
    blockchain.save()
    #"""

    for file in ["ccoin_private_key.pem", "ccoin_public_key.pem", "pcoin_private_key.pem", "pcoin_public_key.pem", "chain.json"]:
        if(os.path.exists(file)):
            os.remove(file)
#'''