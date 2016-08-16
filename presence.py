import subprocess
from time import sleep
from threading import Thread
from ISStreamer.Streamer import Streamer

# Edit these for how many people/devices you want to track
occupant = ["Rachel","Josh"]
# MAC addresses for our phones
address = ["6c:xx:xx:xx:xx:xx","18:xx:xx:xx:xx:xx"]

# Sleep for a minute to wait for internet connection
sleep(60)

# Initialize the Initial State streamer
# Be sure to add your unique access key
streamer = Streamer(bucket_name=":homes:Who's Home?", bucket_key="chip_home", access_key="YOUR_ACCESS_KEY")

# Some arrays to help minimize streaming and account for devices
# disappearing from the network when asleep
firstRun = [1,1]
presentSent = [0,0]
notPresentSent = [0,0]
counter = [0,0]

# Function that checks for device presence
def whosHome(i):
	try:
		# Loop through checking for devices and counting if they're not present
		while True:
			# Assign list of devices on the network to "output"
			output = subprocess.check_output("sudo arp-scan -l", shell=True)
			# If a listed device address is present print and stream
			if address[i] in output:
				print(occupant[i] + "'s device is connected to your network")
				if presentSent[i] == 0:
					# Stream that device is present
					streamer.log(occupant[i],":house_with_garden:")
					streamer.flush()
					print(occupant[i] + " present streamed")
					# Reset counters so another stream isn't sent if the device
					# is still present
					presentSent[i] = 1
					notPresentSent[i] = 0
					counter[i] = 0
				else:
					# If a stream's already been sent, just wait for 5 minutes
					counter[i] = 0
					sleep(300)
			# If a listed device address is not present, print and stream
			else:
				print(occupant[i] + "'s device is not present")
				# Only consider a device offline if it's counter has reached 30
				# This is the same as 15 minutes passing
				if counter[i] == 30 or firstRun[i] == 1:
					firstRun[i] = 0
					if notPresentSent[i] == 0:
						# Stream that device is not present
						streamer.log(occupant[i],":no_entry_sign::house_with_garden:")
						streamer.flush()
						print(occupant[i] + " not present streamed")
						# Reset counters so another stream isn't sent if the device
						# is still present
						notPresentSent[i] = 1
						presentSent[i] = 0
						counter[i] = 0
					else:
						# If a stream's already been sent, wait 30 seconds
						counter[i] = 0
						sleep(30)
				# Count how many 30 second intervals have happened since the device 
				# disappeared from the network
				else:
					counter[i] = counter[i] + 1
					print(occupant[i] + "'s counter at " + str(counter[i]))
					sleep(30)
	# Return on a Keyboard Interrupt
	except KeyboardInterrupt:
		return

# Start the thread
# It will start as many threads as there are values in the occupant array
for i in range(len(occupant)):
	t = Thread(target=whosHome, args=(i,))
	t.start()
