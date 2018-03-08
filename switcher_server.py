#!/usr/bin/python3

# Program to run continually and accept socket connections from 'client'
# scripts, either to change relay state, or to return relay status.

import time
from threading import Thread
import gpiozero
from subprocess import check_call
from signal import pause

BUTTON_PIN=24
GREEN_LED_PIN=27
RED_LED_PIN=22
RELAY_PIN=17

def setup():

    relay = gpiozero.DigitalOutputDevice(RELAY_PIN)
    red_led = gpiozero.PWMLED(RED_LED_PIN, initial_value=True)
    green_led = gpiozero.PWMLED(GREEN_LED_PIN, initial_value=False)

    button = gpiozero.Button(BUTTON_PIN, pull_up=False, hold_time=5)
    # Toggle relay state when pressed
    button.when_pressed = lambda : set_relay('toggle', relay, red_led, green_led)
    # Shut down when held down for 5 seconds
    button.when_held = lambda : check_call(['sudo', 'poweroff'])

    return (relay, red_led, green_led, button)

def set_relay(state, relay, red_led, green_led):

    if state == 'on':

        if not relay.is_active:
            relay.on()

        red_led.off()
        green_led.pulse(n=1, background=False)
        green_led.on()

    elif state == 'off':

        if relay.is_active:
            relay.off()

        green_led.off()
        red_led.pulse(n=1, background=False)
        red_led.on()

    elif state == 'toggle':

        if relay.is_active:

            set_relay('off', relay, red_led, green_led)

        else:

            set_relay('on', relay, red_led, green_led)

    else:

        raise ValueError("Expected 'on', 'off', or 'toggle'.")


def get_relay_state(relay):

    return relay.is_active

def main():

    (relay, red_led, green_led, button) = setup()
    pause()


if __name__ == '__main__':

    main()
