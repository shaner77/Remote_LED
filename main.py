from machine import Pin
from machine import PWM
import utime

red = PWM(Pin(2))
green = PWM(Pin(1))
blue = PWM(Pin(0))
inp = Pin(3, Pin.IN)

start = 0
end = 0

global rval
global gval
global bval
rval = [0,0,0,0,0,0,0,0,0,0]
gval = [0,0,0,0,0,0,0,0,0,0]
bval = [0,0,0,0,0,0,0,0,0,0]

global saves
saves = [False]*10

global on
on = True

global slow
global fast


hexdic = {0xFFA25D : "CH-",
          0xFF629D : "CH",
          0xFFE21D : "CH+",
          0xFF22DD : "<<",
          0xFF02FD : ">>",
          0xFFC23D : ">||",
          0xFFE01F : "-",
          0xFFA857 : "+",
          0xFF906F : "EQ",
          0xFF9867 : "100+",
          0xFFB04F : "200+",
          0xFF6897 : "1",
          0xFF30CF : "2",
          0xFF18E7 : "3",
          0xFF10EF : "4",
          0xFF38C7 : "5",
          0xFF5AA5 : "6",
          0xFF42BD : "7",
          0xFF4AB5 : "8",
          0xFF52AD : "9"}

bindic = {111111111010001001011101 : "CH-",
          111111110110001010011101 : "CH",
          111111111110001000011101 : "CH+",
          111111110010001011011101 : "<<",
          111111110000001011111101 : ">>",
          111111111100001000111101 : ">||",
          111111111110000000011111 : "-",
          111111111010100001010111 : "+",
          111111111001000001101111 : "EQ",
          111111110110100010010111 : "0",
          111111111001100001100111 : "100+",
          111111111011000001001111 : "200+",
          111111110011000011001111 : "1",
          111111110001100011100111 : "2",
          111111110111101010000101 : "3",
          111111110001000011101111 : "4",
          111111110011100011000111 : "5",
          111111110101101010100101 : "6",
          111111110100001010111101 : "7",
          111111110100101010110101 : "8",
          111111110101001010101101 : "9"}
def _init_():
    f = open('log.txt', "r")
    f = f.readline().split(',')
    i = 0
    c = 0
    while i < 30:
        if i%3 == 0:
            rval[c] = int(f[i])
        elif (i-1)%3 == 0:
            gval[c] = int(f[i])
        else:
            bval[c] = int(f[i])
            if rval[c] + gval[c] + bval[c] != 0:
                if c != 0: #saves[0] is used for entering save mode, so don't indicate it as True
                    saves[c] = True
            c += 1
        i += 1
    LEDupdate(rval[0], gval[0], bval[0])

def decode():
    code = 0
    val = 0
    while val < 33:
        if inp.value() == 1:
            while inp.value() == 1:
                    utime.sleep_us(1)  
        if inp.value() == 0:
            while inp.value() == 0:
                utime.sleep_us(1)  
        start = utime.ticks_us()
        while inp.value() == 1:
            utime.sleep_us(1)
        
        end = utime.ticks_us()
        diff = end - start
        if val > 8:
            if diff > 1000:
                code = (code*10 + 1)
            else:
                code = (code*10 + 0)
        val += 1
    if code not in bindic:
        return 0 
    else:
        return code
    
def LEDupdate(r,g,b):
    rval[0] = r
    gval[0] = g
    bval[0] = b
    
    red.duty_u16(r*5000)
    green.duty_u16(g*5000)
    blue.duty_u16(b*5000)
    save()

def save():
    f = open('log.txt', "w")
    i=0
    while i < 10:
        f.write(str(rval[i])+",")
        f.write(str(gval[i])+",")
        f.write(str(bval[i])+",")
        i+=1
    f.close()
        
def Custom(n, saves):

    if saves[0] == True:
        rval[n] = rval[0]
        gval[n] = gval[0]
        bval[n] = bval[0]
        saves[0] = False
        saves[n] = True
        save()
    else:
        if saves[n] == True:
            LEDupdate(rval[n], gval[n], bval[n])
        else:
            return
                        
def main():
    global on
    slow = False
    fast = False
    
    while True:
        if inp.value() == 0: #IR is high when not in use
            code = decode()
            if code in bindic: 
                if bindic[code] == "CH-":
                    save = False
                    slow = False
                    fast = False
                    LEDupdate(13,0,0)
                elif bindic[code] == "CH":
                    saves[0] = False
                    LEDupdate(0,13,0)
                elif bindic[code] == "CH+":
                    saves[0] = False
                    LEDupdate(0,0,13)
                elif bindic[code] == "<<":
                    saves[0] = False
                    if rval[0] <= 12:
                        rval[0] = rval[0] + 1
                        red.duty_u16(rval[0]*5000)
                        save()
                elif bindic[code] == ">>":
                    saves[0] = False
                    if gval[0] <= 12:
                        gval[0] = gval[0] + 1
                        green.duty_u16(gval[0]*5000)
                        save()
                elif bindic[code] == ">||":
                    saves[0] = False
                    if bval[0] <= 12:
                        bval[0] = bval[0] + 1
                        blue.duty_u16(bval[0]*5000)
                        save()
                elif bindic[code] == "-":
                    saves[0] = False
                    if rval[0] >= 1:
                        rval[0] = rval[0] - 1
                        red.duty_u16(rval[0]*5000)
                        save()
                elif bindic[code] == "+":
                    saves[0] = False
                    if gval[0] >= 1:
                        gval[0] = gval[0] - 1
                        green.duty_u16(gval[0]*5000)
                        save()
                elif bindic[code] == "EQ":
                    saves[0] = False
                    if bval[0] >= 1:
                        bval[0] = bval[0] - 1
                        blue.duty_u16(bval[0]*5000)
                        save()
                elif bindic[code] == "0":
                    saves[0] = True
                elif bindic[code] == "100+":
                    saves[0] = False #set colour
                    if on == False:
                        red.duty_u16(rval[0]*5000)
                        green.duty_u16(gval[0]*5000)
                        blue.duty_u16(bval[0]*5000)
                        on = True
                    else:
                        red.duty_u16(0)
                        green.duty_u16(0)
                        blue.duty_u16(0)
                        on = False
                elif bindic[code] == "200+":
                    saves[0] = False
                    rval[0], gval[0], bval[0] = 13,13,13
                    red.duty_u16(rval[0]*5000)
                    green.duty_u16(gval[0]*5000)
                    blue.duty_u16(bval[0]*5000)
                
                elif bindic[code] == "1":
                    Custom(1, saves)
                elif bindic[code] == "2":
                    Custom(2, saves)
                elif bindic[code] == "3":
                    Custom(3, saves)
                elif bindic[code] == "4":
                    Custom(4, saves)
                elif bindic[code] == "5":
                    Custom(5, saves)
                elif bindic[code] == "6":
                    Custom(6, saves)
                elif bindic[code] == "7":
                    Custom(7, saves)
                elif bindic[code] == "8":
                    Custom(8, saves)
                elif bindic[code] == "9":
                    Custom(9, saves)
            else: # INDICATE MISREAD IR SIGNAL
                red.duty_u16(0)
                green.duty_u16(0)
                blue.duty_u16(0)
                utime.sleep_ms(100)
                red.duty_u16(65000)
                green.duty_u16(65000)
                blue.duty_u16(65000)
                utime.sleep_ms(200)
                red.duty_u16(0)
                green.duty_u16(0)
                blue.duty_u16(0)
                utime.sleep_ms(100)
                red.duty_u16(rval[0]*5000)
                green.duty_u16(gval[0]*5000)
                blue.duty_u16(bval[0]*5000)
            utime.sleep_ms(200)

 
_init_()
main()