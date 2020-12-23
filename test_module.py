# import RPi.GPIO as GPIO
# from time import sleep
# import keyboard

# Motor Status
STOP = 0
MOVE = 1

# GPIO PIN
PIN1 = 17
PIN2 = 22
PIN3 = 27

DC = 0
HZ = 1

def setting():
    print("setting")
    return None
    # GPIO.setmode(GPIO.BCM)
    # GPIO.setup(PIN1, GPIO.OUT)
    # GPIO.setup(PIN2, GPIO.OUT)
    # GPIO.setup(PIN3, GPIO.OUT)
    # pwm = GPIO.PWM(PIN1, HZ)
    # return pwm

def move(direction, pwm=None):
    if direction == "forward":
        print("\tforward")
        # GPIO.output(PIN2, MOVE)
        # GPIO.output(PIN3, MOVE)
    elif direction == "right":
        print("\tright")
        # GPIO.output(PIN2, STOP)
        # GPIO.output(PIN3, MOVE)
    elif direction == "left":
        print("\tleft")
        # GPIO.output(PIN2, MOVE)
        # GPIO.output(PIN3, STOP)
    else:
        print(direction)
        # print("Wrong Direction")
        # exit(1)
    # pwm.start(DC)

def stop(pwm):
    print("\tstop")
    # GPIO.output(PIN2, STOP)
    # GPIO.output(PIN3, STOP)
    # pwm.start(DC)

def cleanup():
    print("cleanup")
    # GPIO.cleanup()
