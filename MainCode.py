from pinpong.board import Board, Pin
import time
import speech_recognition as sr
import cv2
import numpy as np
import tensorflow as tf

Board().begin()

trigger_pin = Pin(Pin.P16, Pin.OUT)
echo_pin = Pin(Pin.P4, Pin.IN)
red_led = Pin(Pin.P11, Pin.OUT)
yellow_led = Pin(Pin.P7, Pin.OUT)
green_led = Pin(Pin.P6, Pin.OUT)
haptic_motor = Pin(Pin.P12, Pin.OUT)
light_sensor = Pin(Pin.P8, Pin.IN)

def measure_distance():
    trigger_pin.write_digital(1)
    time.sleep(0.00001)  
    trigger_pin.write_digital(0)

    pulse_start = time.time()
    while echo_pin.read_digital() == 0:
        pass
    pulse_start = time.time()

    while echo_pin.read_digital() == 1:
        pass
    pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 34300 / 2  
    return distance

def control_leds_and_haptic(distance):
    if distance > 60:
        red_led.write_digital(0)
        yellow_led.write_digital(0)
        green_led.write_digital(1)
        haptic_motor.write_digital(0)
    elif 40 <= distance <= 60:
        red_led.write_digital(0)
        yellow_led.write_digital(1)
        green_led.write_digital(0)
        haptic_motor.write_digital(128)  
    elif distance < 40:
        red_led.write_digital(0)
        yellow_led.write_digital(0)
        green_led.write_digital(1)
        haptic_motor.write_digital(255)  

def listen_for_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        print("You said: " + text)
        return text
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))

def take_picture():
    cap = cv2.VideoCapture(0)  
    ret, frame = cap.read()
    cap.release()
    cv2.imwrite("captured_image.jpg", frame)
    return frame

def recognize_object(image):
    model = tf.keras.applications.MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

    image = cv2.resize(image, (224, 224))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = np.expand_dims(image, axis=0)

    prediction = model.predict(image)
    object_name = decode_predictions(prediction, top=1)[0][0][1]
    return object_name

def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

while True:
    distance = measure_distance()
    control_leds_and_haptic(distance)

    if listen_for_command() == "what's that?":
        image = take_picture()
        object_name = recognize_object(image)
        speak_text("That is " + object_name)
