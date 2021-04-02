import sys


def main():
    if sys.implementation.name in 'micropython' and sys.platform in 'rp2':
        # Raspberry Pi RP2040 Chip
        from machine import Pin
        import utime

        led = Pin(25, Pin.OUT)
        while True:
            led(1)
            utime.sleep_ms(100)
            led(0)
            utime.sleep_ms(900)

    elif sys.implementation._multiarch in 'darwin':
        # MacOS
        print("Hello Mac!")

    elif sys.implementation._multiarch in 'arm-linux-gnueabihf':
        # Raspberry Pi
        print("Hello RPi!")

    else:
        print("Unsupported platform")


if __name__ == '__main__':
    main()