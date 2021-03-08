# Team Members
Chester Hulse, Mortiniera Thevie, Karthigan Sinnathamby, Mohamed Ndoye, Frédéric Myotte

# Summary
Fork the original project from Mortiniera+ and add a digital encoding scheme in order to correct errored bits upon receiving them.

# Requirements 

The projects requires the following python libraries : 

numpy as np
pyaudio
struct
matplotlib
scipy
soundfile
sounddevice

# Running 

The test were executed as follows  :
- Create a 160 characters text file(or use the already create text file "test160.txt")
- Generate the gaussian noise (1-2khz or 2-3khz) . The files are in the folder.
- Run : "python emitter.py test160.txt"
- Run : "receiver.py"

The emitter should encode the text file as sound, while the receiver should recognize by himself the non-blocking frequency range of the generated noise and decode the receiving sound as the output textfile, all in 3 minutes. It prints the decoded text in the console.
