__author__ = 'Beast'

import serial
import sys

ser = serial.Serial(port='COM3', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0, rtscts=0)

# command = b"\x89\x45\x56"

CMD_PWR_ON      = '7E3030303020310D'
CMD_PWR_OFF     = '7E3030303020300D'

cmd = "ON"
if len(sys.argv) > 1:
	cmd = sys.argv[1]

def send(command):
	ser.write(command.decode("hex"))
	# ser.write("~00001\r")
	s = ser.read(1)       # read up to one hundred bytes or as much is in the buffer
	return s

if cmd.upper() == "ON":
	print("Turning projector ON")
	send(CMD_PWR_ON)
elif cmd.upper() == "OFF":
	print("Turning projector OFF")
	result = send(CMD_PWR_OFF)

# getopt.getopt(args, options, [long_options])