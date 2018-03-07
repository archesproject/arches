import os, json
import hashlib
import binascii
from Crypto import Random
from Crypto.Cipher import AES

class Crypter(object):
    
    BLOCK_SIZE = 16
    def __init__(cls, key): 
        
        cls.KEY = hashlib.sha256(key.encode()).hexdigest()
    
    @classmethod
    def _pad_string(cls, in_string):
		'''Pad an input string according to PKCS#7'''
		in_len = len(in_string)
		pad_size = cls.BLOCK_SIZE - (in_len % cls.BLOCK_SIZE)
		return in_string.ljust(in_len + pad_size, chr(pad_size))

    @classmethod
    def generate_iv(cls, size=16):
		return Random.get_random_bytes(size)   
    
    @classmethod
    def encrypt(cls, in_string, in_key, in_iv=None):
		'''
		Return encrypted string.
		@in_string: Simple str to be encrypted
		@key: hexified key
		@iv: hexified iv
		'''
		key = binascii.a2b_hex(in_key)
		
		if in_iv is None:
			iv = cls.generate_iv()
			in_iv = binascii.b2a_hex(iv)
		else:
			iv = binascii.a2b_hex(in_iv)
		
		aes = AES.new(key, AES.MODE_CFB, iv, segment_size=128)
		return in_iv, aes.encrypt(cls._pad_string(in_string))