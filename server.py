from socket_handler import Socket_Handler

s = Socket_Handler('localhost', 30000, 'server')
s.create()
s.listen()