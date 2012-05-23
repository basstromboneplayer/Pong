import socket
import pickle
import os

class Socket_Handler(object):
	def __init__( self, host, port, type ):
		self.host = host
		self.port = port
		self.type = type
		self.buffer_size = 10240	# 10KB max
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.dir = 'server_assets/'
		self.asset_list = [ 'ball.png', 'paddle.png' ]

	def create(self):		 
		if self.type == 'server':
			self.s.bind((self.host, self.port))
		else:
			self.s.connect((self.host, self.port))

	def destroy(self):
		self.s.close()
		
	def encode_data(self, data):
		tmp = 'temp.txt'
		f = open(tmp, 'wb')
		pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
		f.close()
		f = open (tmp, 'rb')
		data = f.read()
		f.close()
		if os.path.isfile(tmp):
			os.remove(tmp)
		return data
	
	def decode_packet(self ,packet):
		tmp = 'temp.txt'
		f = open(tmp, 'wb')
		f.write(packet)
		f.close()
		f = open(tmp, 'rb')
		data = pickle.load(f)
		f.close()
		if os.path.isfile(tmp):
			os.remove(tmp)
		return data

	def send_packet(self, packet):
		self.s.send(packet)

	def receive_packet( self ):
		while 1:
			data = self.s.recv(self.buffer_size)
			if not data: break
			return data
		
	# server function only
	def listen(self):
		print 'Press CTRL + C to quit.\nListening on PORT: ', self.port
		self.s.listen(1)
		while 1:
			conn, addr = self.s.accept()
			print 'Connected by', addr
			while 1:
				request = conn.recv(self.buffer_size)
				if not request: break
				
				command = request[0:4]
				if command == 'FILE':
					# conn.send("Getting file: " + request[5:])
					filename = self.dir + request[5:]
					try:
						f = open(filename, 'rb')
						data = f.read()
						f.close()
					
						conn.send(data)
					except IOError as e:
						conn.send('ERROR: File not found!')

				elif command == 'DATA':
					# conn.send("Getting packet info")
					conn.send(request[5:])
					
				elif command == 'LIST':
					conn.send(self.encode_data(self.asset_list))
				
				else:
					conn.send('ERROR: Ignoring invalid request ' + request[0:4])
			conn.close()