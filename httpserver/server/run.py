# -*- coding: utf-8 -*-
import socket
import datetime
import os


def parse(request_string):
	lines = request_string.split('\n')
	headers = {}
	headers['request-line'] = lines[0]
	del lines[0]
	for line in lines:
		delimeter = line.find(':')
		headers[line[:delimeter]] = line[delimeter + 1:].strip()
	print headers
	return headers


def same_headers():
	headers = {	'response-line': 'HTTP/1.1 ',
				'Date': str(datetime.datetime.now()),
				'Server': 'Macintosh; Intel Mac OS X 10_12_6',
				'User-Agent': 'Macintosh; Intel Mac OS X 10_12_6',
				'Content-Type': 'text/html',
				'Content-Length': '0',
				'Connection': 'close'}
	return headers

def glue(response, content):
	return (response['response-line'] + '\n' + 'Date: ' 
		+ response['Date'] + '\n'+ 'Server: ' + response['Server'] 
		+ '\n' + 'Content-Length: ' + response['Content-Length'] + '\n' 
		+ 'Content-Type: ' + response['Content-Type'] + '\n' + 'Connection: ' 
		+ response['Connection'] + '\n\n' + content)



def get_response(request_string):
	headers = parse(request_string)
	(method, path, protocol) = headers['request-line'].split(' ')
	response = same_headers()
	if method == 'GET':
		if path == '/':
			response['response-line'] += '200 OK'
			content = '<html><head></head><body>Hello mister!<br>You are: ' + headers['User-Agent'] + '</body></html>'
			response['Content-Length'] = str(len(content))
		elif path == '/media/':
			response['response-line'] += '200 OK'
			content = '<html><head></head><body>'
			files = os.listdir('/files/')
			for file in files:
				content += file + '<br>'
			content += '</body></html>'
			response['Content-Length'] = str(len(content))
		elif path.find('/media/') != -1 and len(path) > 7:
			response['response-line'] += '200 OK'
			content = '<html><head></head><body>'
			try:
				file = open('/files' + path[path.find('a/') + 1:], 'r')
				content += file.read()
			except IOError:
				response['response-line'] = 'HTTP/1.1 404 Not found'
				content += 'File not found'
			content += '</body></html>'
			response['Content-Length'] = str(len(content))
		elif path == '/test/':
			response['response-line'] += '200 OK'
			content = '<html><head></head><body>'
			content += request_string + '</body></html>'
			response['Content-Length'] = str(len(content))
		else:
			response['response-line'] = 'HTTP/1.1 404 Not found'
			content = '<html><head></head><body>'
			content += 'Page not found' + '</body></html>'
			response['Content-Length'] = str(len(content))
		return glue(response, content)







server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('localhost', 8000))  #server_socket привязывается к address = (ip, port)
server_socket.listen(1)  #создает очередь размера 0 на входящие соединения(если очередь заполнена, новые соединения не принимаются)

print 'Started'

while 1:
    try:
        (client_socket, address) = server_socket.accept()
        print 'Got new client', client_socket.getsockname()  #возвращает адрес клиента (tuple)
        request_string = client_socket.recv(2048) #блокируясь если нечего читать, читает максимум 2048 байт
        response = get_response(request_string)
        client_socket.send(response)  #посылает строку 
    except KeyboardInterrupt:  #в случае нажатия ctrl-c
        print 'Stopped'
        server_socket.close()  #закрывает server_socket, если этот сокет более никем не испоьзуется освобождаются ресурсы
        exit()