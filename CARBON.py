import time #time to perfrom time dependant functions
from time import sleep
import scipy as sc
import numpy as np



import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
led= 18
laser = 27
fan = 22
GPIO.setup(led, GPIO.OUT)
GPIO.setup(laser, GPIO.OUT)
GPIO.setup(fan, GPIO.OUT)
pwm_led = GPIO.PWM(led, 100)
pwm_laser = GPIO.PWM(laser, 100)
pwm_fan = GPIO.PWM(fan, 100)


import board
import busio

import adafruit_mlx90640 

i2c = busio.I2C(board.SCL, board.SDA, frequency = 800000)
mlx = adafruit_mlx90640.MLX90640(i2c)

off = 0
on = 100

pwm_led.start(off)
pwm_laser.start(off)



mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ
frame = [0] * 768

class carbon():
 start_time = time.monotonic()
 
 def heat(set_T, set_time):

   P, I = 30, 2
   It = I
   max_dc, min_dc = 100., 0.
   T_max = 0.
   start_time = time.monotonic() #initial time
   while (T_max <= set_T):
    
      mlx.getFrame(frame) #we get the frame
      T_data = []
      for h in range (24):
          for w in range (32):
              t = frame[h* 32 + w]
              #print("%0.1f, " % t, end="") #used to print the the T value of all pixels
              T_data.append(t)
              T_max = np.round(np.max(np.array([T_data])), 2)
              error_T = set_T - T_max
              Pt = P * error_T #update the P term
              It = np.sum((I * error_T)) #update the Integral Term
              dc = np.round(Pt + It, 2)
            
              if (dc >= max_dc): #adjust the updated dc boundaries
                  dc = max_dc
              if (dc <= min_dc):
                  dc = min_dc
                  
              pwm_laser.ChangeDutyCycle(dc)
              pwm_led.ChangeDutyCycle(dc)
              if (T_max > set_T+10):
                pwm_laser.ChangeDutyCycle(0) #to ensure the safety
                pwm_led.ChangeDutyCycle(0)
    
      sleep(0.1)
      current_time = np.round(time.monotonic(), 2)
      print (np.array([current_time, T_max, dc]))

    
   hold_time = time.monotonic()
   while (((time.monotonic() - hold_time) <= set_time)):
 
      mlx.getFrame(frame) #we get the frame
      T_data = []
      for h in range (24):
          for w in range (32):
              t = frame[h* 32 + w]
              #print("%0.1f, " % t, end="") #used to print the the T value of all pixels
              T_data.append(t)
              T_max = np.round(np.max(np.array([T_data])), 2)
              error_T = set_T - T_max
              Pt = P * error_T #update the P term
              It = np.sum((I * error_T)) #update the Integral Term
              dc = np.round(Pt + It, 2)
            
              if (dc >= max_dc): #adjust the updated dc boundaries
                  dc = max_dc
              if (dc <= min_dc):
                  dc = min_dc
                  
              pwm_laser.ChangeDutyCycle(dc)
              pwm_led.ChangeDutyCycle(dc)
              if (T_max > set_T+10):
               pwm_laser.ChangeDutyCycle(0) #to ensure the safety
               pwm_led.ChangeDutyCycle(0)
               
      sleep(0.1)
      current_time = np.round(time.monotonic(), 2)
      print (np.array([current_time, T_max, dc]))

 def cool(set_T):
   mlx.getFrame(frame) #we get the frame
   T_data = []
   for h in range (24):
      for w in range (32):
              t = frame[h* 32 + w]
              #print("%0.1f, " % t, end="") #used to print the the T value of all pixels
              T_data.append(t)
              T_max = np.round(np.max(np.array([T_data])), 2)
   T_max = T_max           
#    start_time = time.monotonic()
   while (T_max >= set_T):
             mlx.getFrame(frame) #we get the frame
             T_data = []
             for h in range (24):
                 for w in range (32):
                    t = frame[h* 32 + w]
                    #print("%0.1f, " % t, end="") #used to print the the T value of all pixels
                    T_data.append(t)
                    T_max = np.round(np.max(np.array([T_data])), 2)
                    error_T = T_max - set_T
                    Pt = P * error_T #update the P term
                    It = np.sum((I * error_T)) #update the Integral Term
                    dc = np.round(Pt + It, 2)
                
                    if (dc >= max_dc): #adjust the updated dc boundaries
                       dc = max_dc
                    if (dc <= min_dc):
                       dc = min_dc
                      
                    pwm_laser.ChangeDutyCycle(0)
                    pwm_fan.ChangeDutyCycle(dc)
                    pwm_led.ChangeDutyCycle(0)
              
             sleep(0.1)
             current_time = np.round(time.monotonic(), 2)
             print (np.array([current_time, T_max, 0]))

 def pcr(denat_T, denat_time, extend_T, extend_time, anneal_T, anneal_time, max_cycle):
            
                 cycle = 0
                 while (cycle <= max_cycle):
                  carbon.heat(denat_T, denat_time)
                  carbon.cool(anneal_T)
                  carbon.heat(anneal_T, anneal_time)
                  carbon.heat(extend_T, extend_time)
                 cycle += 1


carbon.pcr(70, 10, 55, 10, 35, 10, 10)

                
