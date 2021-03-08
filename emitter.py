
# coding: utf-8

# In[1]:

import numpy as np
import scipy.io.wavfile as sc
import soundfile as sf
import sounddevice as sd
import sys
import Hamming as hm


# In[21]:

Fc0_00 = 1200
Fc0_01 = 1400
Fc0_10 = 1600
Fc0_11 = 1800
Fc1_00 = 2200
Fc1_01 = 2400
Fc1_10 = 2600
Fc1_11 = 2800
Fbit = 10 #bit frequency
Fs = 44100 #sampling frequency
A = 1 #amplitude of the signal

BARKER = [1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1]
BARKER = BARKER + BARKER
TEST = "_t_"


# In[3]:

def encode(text):
    #int_text = int.from_bytes(text.encode(), 'big')
    after_txt = ""
    txt_bytes = bytes(text, 'ascii')
    for i in range(len(txt_bytes)):
        #print("BYTE BFEORE ENCODING: " + str(txt_bytes[i]))
        temp_txt = format(hm.hamming_encode_nibble((txt_bytes[i] & 0xf0) >> 4), '08b')
        #print("tmp: (len, txt) " + str(len(temp_txt)) + "," + temp_txt)
        after_txt += temp_txt #[2:-1]  #take out the b from the binary string, and one extra character for padding"
        temp_txt = format(hm.hamming_encode_nibble(txt_bytes[i] & 0x0f), '08b')
        #print("tmp: (len, txt) " + str(len(temp_txt)) + "," + temp_txt)
        after_txt += temp_txt #[2:-1]

    
    print("text after: (len, txt) " + str(len(after_txt)) + "," + after_txt)

    # #test decoding:
    # print("DECODING")
    
    # binary_int = int(after_txt, 2)
    # byte_number = (binary_int.bit_length() + 7)// 8
    # print('bytes number : ' + str(byte_number))
    # binary_array = binary_int.to_bytes(byte_number, "big")

    # txt_bytes = binary_array
    # after_txt = ""
    # print("num bytes " + str(len(txt_bytes)) )
    # for i in range(len(txt_bytes)):
    #     byte, error, corrected = hm.hamming_decode_byte(txt_bytes[i])
    #     temp_txt = format(byte, '04b')
    #     #print("tmp: (len, txt) " + str(len(temp_txt)) + "," + temp_txt)
    #     after_txt += temp_txt #[2:-1]  #take out the b from the binary string, and one extra character for padding"

    # print("text after: (len, txt) " + str(len(after_txt)) + "," + after_txt)

    # binary_int = int(after_txt, 2)
    # byte_number = (binary_int.bit_length() + 7) // 8
    # binary_array = binary_int.to_bytes(byte_number, "big")
    # ascii_text = binary_array.decode()
    # print("ascii: " + ascii_text)

    return after_txt


# In[4]:

def modulation(choice,bin_text):
    t = np.arange(0,1/float(Fbit),1/float(Fs), dtype=np.float)
    signal = np.ndarray(len(bin_text)//2*len(t),dtype=np.float)

    if(choice==0):
        Fc_00 = Fc0_00
        Fc_01 = Fc0_01
        Fc_10 = Fc0_10
        Fc_11 = Fc0_11
    else:
        Fc_00 = Fc1_00
        Fc_01 = Fc1_01
        Fc_10 = Fc1_10
        Fc_11 = Fc1_11
        
    i=0
    for j in range(0,len(bin_text),2):
        bits = bin_text[j:j+2]
        if bits[0]==0:
            if(bits[1]==1):
                signal[i:i+len(t)]= A * np.cos(2*np.pi*(Fc_01)*t)
            else:
                signal[i:i+len(t)]= A * np.cos(2*np.pi*(Fc_00)*t)
        else:
            if(bits[1]==1):
                signal[i:i+len(t)]= A * np.cos(2*np.pi*(Fc_11)*t)
            else:
                signal[i:i+len(t)]= A * np.cos(2*np.pi*(Fc_10)*t)
        i += len(t)
        
    return signal


# In[5]:

def double_cosinus(bin_text):
    cos0 = modulation(0,bin_text)
    cos1 = modulation(1,bin_text)
    return cos0 + cos1


# In[6]:

def get_sync_signal():
    return double_cosinus(BARKER)


# In[7]:

def get_test_signal():
    return double_cosinus(encode(TEST))


# In[8]:

def emitter_real(text):
    modul = double_cosinus(encode(text))
    sync = get_sync_signal()
    test = get_test_signal()
    return np.append(np.append(np.append(sync,np.append(test,modul)),test), test)


# In[13]:

def emitter(filepath):
    with open(filepath, "r") as data:
        x = emitter_real(data.read())
        sc.write("emitter2b.wav",Fs,x)
        samples, samplerate = sf.read('emitter2b.wav')
        sd.play(samples, samplerate)
        sd.wait()


# In[14]:

def main():
    path = sys.argv[1]
    emitter(path)

if __name__ == "__main__":
    main()
