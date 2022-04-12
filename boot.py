
# Written by Daniel Corcoran for Bearcat Solar Car team
# Mail: corcordp@mail.uc.edu
# autostart location: /etc/xdg/autostart/display.desktop

from imutils.video import VideoStream
import cv2
import numpy as np
import RPi.GPIO as GPIO

# GPIO settings
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Hazard switch
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Left turn to pi
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Right turn to pi
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Headlights

L_BRIGHT = 16
R_BRIGHT = 19
RTS = 11
LTS = 13
FRTS = 7
FLTS = 5

GPIO.setup(L_BRIGHT, GPIO.OUT) # Pi to relay 8 - left headlight
GPIO.setup(R_BRIGHT, GPIO.OUT) # Pi to relay 7 - right headlight
GPIO.setup(RTS, GPIO.OUT) # Pi to relay 14 - RTS
GPIO.setup(LTS, GPIO.OUT) # Pi to relay 12 - LTS
GPIO.setup(FRTS, GPIO.OUT) # Pi to relay 15 - FRTS
GPIO.setup(FLTS, GPIO.OUT) # Pi to relay 13 - FLTS
#GPIO.setup3



# Create a VideoCapture object and read from input file
# If the input is the camera, pass 0 instead of the video file name
cap = cv2.VideoCapture(0)

# Check if camera opened successfully
if (cap.isOpened()== False):
  print("Error opening video stream or file")

# Read until video is completed
cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

def get_mph():
    return 30

def get_motor_temp():
    return 100

def get_battery_temp():
    return 60

def get_battery_pct():
    return 75

tick = 0

def read_switches():
    global tick
    hazards_bool = False
    tick_const = 10
    if GPIO.input(12) == GPIO.HIGH:
        # HAZARDS
        hazards_bool = True
        GPIO.output(FLTS, False)
        GPIO.output(FRTS, False)
        tick = tick + 1
        print("Hazards")
        print(tick)
        if tick < tick_const:
            print("ON")
            GPIO.output(RTS, False)
            GPIO.output(LTS, False)
        elif (2 * tick_const) - 1 > tick >- tick_const:
            print("OFF")
            GPIO.output(RTS, True)
            GPIO.output(LTS, True)
        else:
            tick = 0
    else:

        GPIO.output(FLTS, True)
        GPIO.output(FRTS, True)
        GPIO.output(RTS, True)
        GPIO.output(LTS, True)

    if GPIO.input(18) == GPIO.HIGH:
        print("Right turn signal on")
        tick = tick + 1
        print(tick)
        GPIO.output(FRTS, False)
        if tick < tick_const:
            print("ON")
            GPIO.output(RTS, True)
        elif (2 * tick_const) - 1 > tick >= tick_const:
            print("OFF")
            GPIO.output(RTS, False)
        else:
            tick = 0

    elif hazards_bool == False:
        GPIO.output(RTS, True)
        GPIO.output(FRTS, True)

    if GPIO.input(22) == GPIO.HIGH:
        print("Left turn signal on")
        tick = tick + 1
        print(tick)
        GPIO.output(FLTS, False)
        if tick < tick_const:
            print("ON")
            GPIO.output(LTS, True)
        elif (2 * tick_const) - 1 > tick >= tick_const:
            print("OFF")
            GPIO.output(LTS, False)
        else:
            tick = 0

    elif hazards_bool == False:
        GPIO.output(FLTS, True)
        GPIO.output(LTS, True)

    if GPIO.input(21) == GPIO.HIGH:
        print("Headlights On")
        GPIO.output(R_BRIGHT, False)
        GPIO.output(L_BRIGHT, False)
    else:
        GPIO.output(R_BRIGHT, True)
        GPIO.output(L_BRIGHT, True)


def getStatsDisplay(stats_w):
    # Returns image to concatenate with streaming frame
    f = np.zeros((720, stats_w, 3), np.uint8)
    f.fill(255)
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontSize  =1

    largeFontSize = 2

    color = (0, 0, 0)
    thick = 2


    item_height = 170
    stat_offset = 65

    #f = cv2.line(f, (150, 0), (150, 720), (100, 100, 100), 1)

    f = cv2.putText(f, 'MPH', (110, 50), font, fontSize, color, thick, cv2.LINE_AA)
    f = cv2.putText(f, str(get_mph()), (110, 50 + stat_offset), font, largeFontSize, color, thick, cv2.LINE_AA)


    f = cv2.putText(f, 'Motor Temp', (60, 50 + 1 * item_height), font, fontSize, color, thick, cv2.LINE_AA)
    f = cv2.putText(f, str(get_motor_temp()), (90, 50 + 1 * item_height + stat_offset), font, largeFontSize, color, thick, cv2.LINE_AA)


    f = cv2.putText(f, 'Bat Temp', (75, 50 + 2 * item_height), font, fontSize, color, thick, cv2.LINE_AA)
    f = cv2.putText(f, str(get_battery_temp()), (110, 50 + 2 * item_height + stat_offset), font, largeFontSize, color, thick, cv2.LINE_AA)


    f = cv2.putText(f, 'Bat %', (100, 50 + 3 * item_height), font, fontSize, color, thick, cv2.LINE_AA)
    f = cv2.putText(f, str(get_battery_pct()), (110, 50 + 3 * item_height + stat_offset), font, largeFontSize, color, thick, cv2.LINE_AA)


    return f

stats_width = 300
while(cap.isOpened()):

  # Capture frame-by-frame
  ret, frame = cap.read()
  if ret == True:

    # Check buttons
    read_switches()

    # Display the resulting frame
    #cv2.namedWindow("test", cv2.WND_PROP_FULLSCREEN)
    #cv2.setWindowProperty("test", cv2.WND_PROP_FULLSCREEN, 1)

    frame = cv2.resize(frame, (1280 - stats_width, 720))

    stats = getStatsDisplay(stats_width)

    frame = np.hstack((stats, frame))

    cv2.imshow('Frame',frame)
    # Press Q on keyboard to  exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
      break

  # Break the loop
  else:
    break

# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()
