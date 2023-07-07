import struct
import socket
import time
import logging

_LOGGER = logging.getLogger(__name__)

MAX_BRIGHTNESS = 255

class ArtNet(object):

    def __init__(self, targetIP : str, targetPort : int, universes : list):


        # TODO HARD CODED UNIVERSES
        universes = [Universe(128), Universe(25), Universe(128), Universe(108)]

        self._state = False
        self._brightness = 255
        self._rgb = (255,255,255)

        self._name = "Enttec Bar LEDs"

        self._TargetIP = targetIP
        self._TargetPort = targetPort
        self._Universes = universes

        ID = "Art-Net".encode() + b"\00"
        OpCode = b'\x00\x50' # 0x500 "ArtDMX"
        ProtocolVersion = bytes.fromhex("000e") # Protocol Version 14
        self._ArtHeader = ID + OpCode + ProtocolVersion

        # Create a single socket instance to sent UDP packets on
        self._Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def sendUniverse(self, universe : int):

        data = bytes(self._Universes[universe])
        sequence = self._Universes[universe].getSequenceBytes()
        physical = int(0).to_bytes(1, 'little')
        universe1 = universe.to_bytes(2, 'little')
        length = int(512).to_bytes(2, 'big')

        packetData = self._ArtHeader + sequence + physical + universe1 + length + data
        r = self._Socket.sendto(packetData, (self._TargetIP, self._TargetPort))

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._state

    @property
    def rgb(self) -> tuple[int, int, int]:
        return self._rgb

    def set_rgb(self, rgb):
        self._rgb = rgb

    @property
    def brightness(self):
        return self._brightness

    def set_brightness(self, intensity: int):
        # TODO WRITE ME
        self._brightness = intensity

    def turn_on(self):
        # TODO WRITE ME
        _LOGGER.debug(f"Turning Light On to rgb value of: {self._rgb} and brightness of {self._brightness}")

        red = self._rgb[0] * (self._brightness / MAX_BRIGHTNESS)
        green = self._rgb[1] * (self._brightness / MAX_BRIGHTNESS)
        blue = self._rgb[2] * (self._brightness / MAX_BRIGHTNESS)

        self._Universes[0].setColor(red, green, blue)
        self._Universes[1].setColor(red, green, blue)
        self._Universes[2].setColor(red, green, blue)
        self._Universes[3].setColor(red, green, blue)

        # self._Universes[0].setColor(self._rgb[0], self._rgb[1], self._rgb[2])
        # self._Universes[1].setColor(self._rgb[0], self._rgb[1], self._rgb[2])
        # self._Universes[2].setColor(self._rgb[0], self._rgb[1], self._rgb[2])
        # self._Universes[3].setColor(self._rgb[0], self._rgb[1], self._rgb[2])
        
        self.sendUniverse(0)
        self.sendUniverse(1)
        self.sendUniverse(2)
        self.sendUniverse(3)

        self._state = True

    def turn_off(self):
        _LOGGER.debug("Turning Light Off")
        # TODO WRITE ME
        self._Universes[0].setColor(0, 0, 0)
        self._Universes[1].setColor(0, 0, 0)
        self._Universes[2].setColor(0, 0, 0)
        self._Universes[3].setColor(0, 0, 0)
        
        self.sendUniverse(0)
        self.sendUniverse(1)
        self.sendUniverse(2)
        self.sendUniverse(3)

        self._state = False

#end ArtNet

class Universe(object):
    def __init__(self, leds : int):
        self._Sequence = 0
        self._DMX = []
        for _ in range(leds):
            self._LEDs = leds
            self._DMX.append(DMX512())

    def __bytes__(self) -> bytes:
        retVal = b""
        for i in range(self._LEDs):
            retVal += bytes(self._DMX[i])

        # If the universe does not fill the entire UDP frame, pad it with zero's
        retVal += b'\00\00\00\00' * (128-self._LEDs)
        return retVal

    def getSequenceBytes(self, increment = True):

        retVal = self._Sequence.to_bytes(1, 'little')
        self._Sequence = (self._Sequence + 1 ) % 128

        return retVal

    def setColor(self, red, green, blue):
        for i in range(self._LEDs):
            self._DMX[i].setRGB(red, green, blue)
# end Universe


class DMX512(object):

    def __init__(self):
        self._White = 0
        self._Red = 0
        self._Green = 0
        self._Blue = 0

    def __str__(self):
        raise NotImplementedError

    def __bytes__(self) -> bytes:
        # Return the rgbw bytes value
        retVal = \
            int(self._Red).to_bytes(1, 'little') + \
            int(self._Green).to_bytes(1, 'little') + \
            int(self._Blue).to_bytes(1, 'little') + \
            int(self._White).to_bytes(1, 'little')
        return retVal

    def setRGB(self,
               r : int,
               g : int,
               b : int):
        CORRECTION_R = 255
        CORRECTION_G = 203
        CORRECTION_B = 155
        CORRECTION_W = 255

        #TODO GAMMA CORRECTION
        # p_r = (uint32_t)GAMMA_LUT[STRIP_LEDs[i].r];
        # p_g = (uint32_t)GAMMA_LUT[STRIP_LEDs[i].g];
        # p_b = (uint32_t)GAMMA_LUT[STRIP_LEDs[i].b];

        white = min(r, g, b) # The minimum of the 3 channels is the amount of "whiteness" that can be removed

        # Pull out the Redundant white values from the RGB signals
        red = r - white
        green = g - white
        blue = b - white

        self._White = int(white * CORRECTION_W / 255)
        self._Red = int(red * CORRECTION_R / 255)
        self._Green = int(green * CORRECTION_G / 255)
        self._Blue = int(blue * CORRECTION_B / 255)

    def toNetwork(self) -> bytes:
        retVal = str(self._Red).encode() + \
                 str(self._Green).encode() + \
                 str(self._Blue).encode() + \
                 str(self._WHite).encode()
        return retVal