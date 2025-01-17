
# coding: utf-8

# In[91]:

import numpy as np
import pyaudio
import struct
import matplotlib.pyplot as plt
import Hamming as hm


# In[92]:

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
FREQ_THRESHOLD = 30 #must be smaller than Fdev

CHUNK = 1024
RECORD_SECONDS = 180
CHANNELS = 1
FORMAT = pyaudio.paInt16

BARKER = [1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1]
BARKER = BARKER + BARKER
TEST = "_t_"
TEST_LEN = len(TEST)*(Fs//Fbit)*4


# In[93]:

def fft(sig):
    return np.abs(np.fft.rfft(sig))


# In[94]:

def index_freq(f) :
    return round(f/Fbit)


# In[95]:

def fft_plot(ns):
    yf = np.abs(np.fft.rfft(ns))
    plt.plot(yf[index_freq(1000):index_freq(2000)])
    plt.grid()
    plt.show()


# In[96]:

def content_at_freq(fft_sample, f, Fbit) :
    lower = f-FREQ_THRESHOLD
    upper = f+FREQ_THRESHOLD
    indexFreqs = [index_freq(f) for f in range(lower,upper, 1)]
    freqSample = max([fft_sample[index] for index in indexFreqs])
    return freqSample


# In[97]:

def filtered(sig, choice,full):
    data = []
    if(full):
        x = len(sig)//(Fs//Fbit)*(Fs//Fbit)
    else :
        x = TEST_LEN
    for i in range(0,x,Fs//Fbit):
        bit = sig[i:i+Fs//Fbit]
        bitfft = fft(bit)
        if(choice == 0) :
            x00 = content_at_freq(bitfft,Fc0_00,Fbit)
            x01 = content_at_freq(bitfft,Fc0_01,Fbit)
            x10 = content_at_freq(bitfft,Fc0_10,Fbit)
            x11 = content_at_freq(bitfft,Fc0_11,Fbit)

            ls = [x00,x01,x10,x11]
            x = np.argmax(ls)
            if(x==0):
                data.append(0)
                data.append(0)
            elif(x==1):
                data.append(0)
                data.append(1)
            elif(x==2):
                data.append(1)
                data.append(0)
            elif(x==3):
                data.append(1)
                data.append(1)
                
        else:
            x00 = content_at_freq(bitfft,Fc1_00,Fbit)
            x01 = content_at_freq(bitfft,Fc1_01,Fbit)
            x10 = content_at_freq(bitfft,Fc1_10,Fbit)
            x11 = content_at_freq(bitfft,Fc1_11,Fbit)

            ls = [x00,x01,x10,x11]
            x = np.argmax(ls)
            if(x==0):
                data.append(0)
                data.append(0)
            elif(x==1):
                data.append(0)
                data.append(1)
            elif(x==2):
                data.append(1)
                data.append(0)
            elif(x==3):
                data.append(1)
                data.append(1)
    return data


# In[98]:

def decode_letter(letter):
    binary = int("0b"+letter,base=2)
    m = ""
    try :
        m = binary.to_bytes((binary.bit_length() + 7) // 8, 'big').decode() #decoding from built-in functions in python
    except (UnicodeDecodeError) :
        m = False
    return m


# In[99]:

def decode(bin_text):
    str_text = "".join([ str(c) for c in bin_text])
    #print("Rec: (len,str)"+ str(len(str_text)) + "," + str_text)
    string = ""
    for i in range(0,len(str_text),8):
        letter = decode_letter(str_text[i:i+8])
        if(letter != False):
            string += letter
        if len(string)>len(TEST) and string[len(string)-len(TEST):]==TEST:
            return string[:len(string)-len(TEST)]
    return string

def decode_hamming(bin_text):
    
    #test decoding:
    
    input_txt = "".join([ str(c) for c in bin_text])
    #print("Decoding hamming: " + input_txt)
    string = ""
    for i in range(0,len(input_txt),8): #find the _t_ and truncate the text
        letter = decode_letter(input_txt[i:i+8])
        if(letter != False and letter in TEST):
            string += letter
        else:
            string = ""
        if (string == TEST):
            input_txt = input_txt[:i-16] #take off the last 2 bits === "_t"
            break

    #print("Decoding hamming2: " + str(len(input_txt)) + "," + input_txt)
    binary_int = int(input_txt, 2)
    byte_number = (binary_int.bit_length() + 7)// 8
    #print('bytes number : ' + str(byte_number))
    binary_array = binary_int.to_bytes(byte_number, "big")

    txt_bytes = binary_array
    after_txt = ""
    #print("num bytes " + str(len(txt_bytes)) )
    total_errors = 0
    total_corrected = 0
    for i in range(len(txt_bytes)):
        byte, error, corrected = hm.hamming_decode_byte(txt_bytes[i])
        total_errors += error
        total_corrected += corrected
        temp_txt = format(byte, '04b')
        #print("tmp: (len, txt) " + str(len(temp_txt)) + "," + temp_txt)
        after_txt += temp_txt #[2:-1]  #take out the b from the binary string, and one extra character for padding"

    #print("text after: (len, txt) " + str(len(after_txt)) + "," + after_txt)

    binary_int = int(after_txt, 2)
    byte_number = (binary_int.bit_length() + 7) // 8
    binary_array = binary_int.to_bytes(byte_number, "big")
    ascii_text = binary_array.decode()
    #print("ascii: " + ascii_text)
    print("Found " + str(total_errors) + " errors!")
    print("Corrected " + str(total_corrected) + " errors!")
    return ascii_text

# In[100]:

def fromstring_buffer(buffer) :
    return struct.unpack('%dh' % (len(buffer)/2), buffer)


# In[101]:

def process_raw(in_data):
    data = np.array(fromstring_buffer(in_data))
    return data


# In[102]:

def listen_to_signal():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,rate=Fs, input=True,frames_per_buffer=CHUNK)
    frames = []
    stream.start_stream()

    for i in range(0, int(Fs / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        data = process_raw(data)
        frames.append(data)
        
    stream.stop_stream()
    stream.close()
    audio.terminate()
    return np.hstack(frames)


# In[103]:

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


# In[104]:

def double_cosinus(bin_text):
    cos0 = modulation(0,bin_text)
    cos1 = modulation(1,bin_text)
    return cos0 + cos1


# In[105]:

def get_sync_signal():
    return double_cosinus(BARKER)


# In[106]:

def try_sync(sig):
    sync_signal = get_sync_signal()
    sync_padded = np.hstack((sync_signal, np.zeros(sig.size-sync_signal.size)))
    correlation = np.abs(np.fft.ifft(np.fft.fft(sig) * np.conj(np.fft.fft(sync_padded))))
    return np.argmax(correlation)


# In[107]:

def sync(sig):
    SYNC = False
    i=0
    x = len(get_sync_signal())
    index = 0
    while not SYNC:
        chunk = sig[i:i+(5*Fs)]
        index = try_sync(chunk)
        if index + x < len(chunk):
             SYNC = True
        i += x
    return sig[index+x:]


# In[108]:

import time
def receiver():
    ls = listen_to_signal()
    x = sync(ls)
    
    t0 = decode(filtered(x,0,False)) #just filters the first data out up to testlen
    t1 = decode(filtered(x,1,False))
    x = x[TEST_LEN:] #removes first testlen
    #print(t0) #should be testlen
    #print(t1)
    #print(filtered(x,0,True))
    #print(filtered(x,1,True))
    #print("reeee")
    if(t0 == TEST):
        return decode_hamming(filtered(x,0,True)) #should be data with testlen removed now
    elif(t1==TEST):
        return decode_hamming(filtered(x,1,True))
    else:
        print("Unable to sync and/or decode!")

# In[20]:

def main():
    x = receiver()
    if (x):
        print("Received: " + x)

if __name__ == "__main__":
    main()