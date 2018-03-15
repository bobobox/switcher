#!/usr/bin/python3

# Program to run continually and accept socket connections from 'client'
# scripts, either to change relay state, or to return relay status.

from threading import Thread
import socket
import subprocess
import gpiozero

BUTTON_PIN = 24
GREEN_LED_PIN = 27
RED_LED_PIN = 22
RELAY_PIN = 17
SERVER_LISTEN_PORT = 5555

def setup():

    relay = gpiozero.DigitalOutputDevice(RELAY_PIN)
    red_led = gpiozero.PWMLED(RED_LED_PIN, initial_value=True)
    green_led = gpiozero.PWMLED(GREEN_LED_PIN, initial_value=False)

    button = gpiozero.Button(BUTTON_PIN, pull_up=False, hold_time=5)
    # Toggle relay state when pressed
    button.when_pressed = lambda: set_relay('toggle', relay, red_led, green_led)
    # Shut down when held down for 5 seconds
    button.when_held = lambda: shutdown(red_led, green_led)

    return (relay, red_led, green_led, button)

def shutdown(red_led, green_led):

    green_led.off()
    red_led.blink(on_time=0.3, off_time=0.3, fade_in_time=0.1, fade_out_time=0.1, background=True)
    subprocess.check_call(['sudo', 'poweroff'])

def set_relay(state, relay, red_led, green_led):

    if state == 'on':

        if not relay.is_active:
            relay.on()

        red_led.pulse(n=1, fade_out_time=0.5, fade_in_time=0, background=False)
        green_led.pulse(n=2, fade_out_time=0.5, fade_in_time=0.5, background=False)
        green_led.pulse(n=1, fade_out_time=0, fade_in_time=0.5, background=False)
        green_led.on()

    elif state == 'off':

        if relay.is_active:
            relay.off()

        green_led.pulse(n=1, fade_out_time=0.5, fade_in_time=0, background=False)
        red_led.pulse(n=2, fade_out_time=0.5, fade_in_time=0.5, background=False)
        red_led.pulse(n=1, fade_out_time=0, fade_in_time=0.5, background=False)
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

def run_server(relay, red_led, green_led, listen_port):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', listen_port))
    sock.listen(3)

    while True:

        conn, addr = sock.accept()
        print("{} connected".format(addr))

        conn.settimeout(60)

        Thread(target=handle_client, args=(conn, relay, red_led, green_led)).start()


def handle_client(conn, relay, red_led, green_led):

    while True:

        data = conn.recv(1)

        if not data:
            print("Got no data")
            conn.close()
            return
        elif data == b'0':
            print("Got relay off")
            set_relay('off', relay, red_led, green_led)
        elif data == b'1':
            print("Got relay on")
            set_relay('on', relay, red_led, green_led)
        elif data == b'S':
            conn.sendall(b'1' if relay.is_active else b'0')
        else:
            raise ValueError("Unexpected message: '{}'".format(data))



def main():

    (relay, red_led, green_led, button) = setup()

    run_server(relay, red_led, green_led, SERVER_LISTEN_PORT)



if __name__ == '__main__':

    main()
