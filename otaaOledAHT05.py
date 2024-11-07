import machine
import socket
import time
import ubinascii
import ssd1306
import ahtx0
from network import LoRa
from cayennelpp import CayenneLPP
from ssd1306 import SSD1306_I2C
from machine import Pin, I2C
from time import sleep

#Applications myasr6601 End devices tbeam
led = machine.Pin('P22', machine.Pin.OUT)

pin16 = machine.Pin('P8', machine.Pin.OUT)
pin16.value(1)
i2c = I2C(0, pins=('P3','P4'))   
devices = i2c.scan()
oled=ssd1306.SSD1306_I2C(128,64,i2c)
sensor = ahtx0.AHT10(i2c)

lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.AS923)
app_eui = ubinascii.unhexlify('ABABABABABABABAB')
app_key = ubinascii.unhexlify('45ADB18947EF42ADC36231E01E508461')
dev_eui = ubinascii.unhexlify('70B3D57ED006B08D')
lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0)

oled.text("LoRaWAN Thailand",0,0)
oled.text("Trying to Join",0,20)
oled.show()

while not lora.has_joined():
    oled.text("LoRaWAN Thailand",0,0)
    oled.text("Trying to Join",0,20)
    oled.text("X",15,30)
    oled.show()
    time.sleep(1)
    oled.text("O",15,30)
    oled.show()
    time.sleep(1)
    oled.fill(0)
    print('Not yet joined...')

print('Joined')
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
sensor = ahtx0.AHT10(i2c)
count=0
while True:
    temp=round(sensor.temperature,2)
    hum=round(sensor.relative_humidity,2)
    print( "------------------------------------")
    print( "Packet #{}".format( count) )
    print("AHT10 values:")
    print('temp:', temp, ' Hum:', hum )
    print( "------------------------------------")
    print(lora.stats())
    print("TX Freq:",lora.stats().tx_frequency)
    print("RSSI:",lora.stats().rssi)
    oled.fill(0)
    oled.text("LoRaWAN Thailand",0,0)
    oled.text("Temp: "+str(temp), 0, 10)
    oled.text("Hum: "+str(hum), 0, 20)
    oled.text("Count "+str(count), 0, 30)
    oled.text("Freq : "+str(lora.stats().tx_frequency), 0, 40)
    oled.text("RSSI : "+str(lora.stats().rssi), 0, 50)
    oled.show()    
    c = CayenneLPP()
    c.addTemperature(1, float(temp)) 
    c.addRelativeHumidity(3, float(hum))
    msg=bytes(list(c.getBuffer()))
    s.setblocking(True)
    led.value(1)
    sleep(0.5)
    led.value(0)
    sleep(10)
    s.send(msg)
    s.setblocking(False)
    print(type(lora.stats()))
    print(lora.stats())
    data = s.recv(64)
    print('Downlink:',data)
    count=count+1


