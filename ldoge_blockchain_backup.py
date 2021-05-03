from zipfile import ZipFile
from datetime import datetime
from datetime import timedelta
from datetime import date
from pathlib import Path
import os
import threading, time, signal
import shutil

class ProgramKilled(Exception):
	pass

def backup():
	myHome = Path('/home/YOURUSER/.litedoge')
	now = datetime.now()

	print(now)
	print(myHome)

	os.chdir(str(myHome))

	strZipName = 'LDOGE_Snapshot_' + str(datetime.now().isoformat()) + '.zip'

	webFolder = Path("YOURWEBROOTPATH")

	backFile = webFolder / 'tmp' / strZipName

	print(backFile)

	fileList = [ 'blk0001.dat' , 'peers.dat', 'database', 'txleveldb' ]

	zipObj = ZipFile(backFile, 'w')

	for file in fileList:
		if(os.path.isdir(file)):
			for root, dirs, files in os.walk(file):
				for fcur in files:
					fname = root + '/' + fcur
					zipObj.write(fname)
		elif(os.path.isfile(file)):
			zipObj.write(file)

	finalFolder = webFolder / 'ldoge_snapshots'
	shutil.move(str(backFile), str(finalFolder))

def signal_handler(signum, frame):
	raise ProgramKilled

class Job(threading.Thread):
	def __init__(self, interval, execute, *args, **kwargs):
		threading.Thread.__init__(self)
		self.daemon = False
		self.stopped = threading.Event()
		self.interval = interval
		self.execute = execute
		self.args = args
		self.kwargs = kwargs

	def stop(self):
		self.stopped.set()
		self.join()

	def run(self):
		while not self.stopped.wait(self.interval.total_seconds()):
			print("Execute backup")
			self.execute(*self.args, **self.kwargs)

if __name__ == "__main__":
	signal.signal(signal.SIGTERM, signal_handler)
	signal.signal(signal.SIGINT, signal_handler)
	#job = Job(interval=timedelta(days=1), execute=backup)
	# CHANGE DELAY HERE
	job = Job(interval=timedelta(hours=12), execute=backup)
	job.start()

	while True:
		try:
			time.sleep(1)
		except ProgramKilled:
			print ("LDOGE Backup killed")
			job.stop()
			break
