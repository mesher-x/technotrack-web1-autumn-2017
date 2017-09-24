# -*- coding: utf-8 -*-
import socket
import datetime
import os
import re


def parse(request_string):
    lines = request_string.split('\r\n')
    request_line_string = lines[0].strip()
    first_space = request_line_string.find(' ')
    second_space = request_line_string.rfind(' ')
    request_line = {'Method': request_line_string[:first_space],
                    'Uri': request_line_string[first_space + 1:second_space],
                    'HTTP-Version': request_line_string[second_space + 1:]
                    }
    request_headers = {}
    del lines[0]
    for line in lines:
        delimeter = line.find(':')
        request_headers[line[:delimeter]] = line[delimeter + 1:].strip()
    return request_line, request_headers


def get_response(request_string):
    request_line, request_headers = parse(request_string)

    status_line = {'HTTP-Version': 'HTTP/1.1',
                   'Code': '200',
                   'Reason-Phrase': 'OK'
                   }

    response_headers = {'Date': str(datetime.datetime.now()),
                        'Server': 'Macintosh; Intel Mac OS X 10_12_6',
                        'Content-Type': 'text/html',
                        'Content-Length': '0',
                        'Connection': 'close'
                        }

    if request_line['Method'] != 'GET':
        status_line['Code'] = '404'
        status_line['Reason-Phrase'] = 'Not found'
        content = '<html><head></head><body>Page not found</body></html>'
        response_headers['Content-Length'] = str(len(content))

    elif request_line['Uri'] == '/':
        status_line['Code'] = '200'
        status_line['Reason-Phrase'] = 'OK'
        content = '<html><head></head><body>Hello mister!<br>You are: ' \
                  + request_headers['User-Agent'] + '</body></html>'

    elif request_line['Uri'] == '/media/':
        status_line['Code'] = '200'
        status_line['Reason-Phrase'] = 'OK'
        content = '<html><head></head><body>'
        directory_contents = os.listdir('/files/')
        for name in directory_contents:
            content += name + '<br>'
        content += '</body></html>'

    elif request_line['Uri'] == '/test/':
        status_line['Code'] = '200'
        status_line['Reason-Phrase'] = 'OK'
        content = '<html><head></head><body>' + request_string + '</body></html>'

    elif re.search(r'[a-zA-z/]+', request_line['Uri']):
        status_line['Code'] = '200'
        status_line['Reason-Phrase'] = 'OK'
        content = '<html><head></head><body>'
        try:
            path = request_line['Uri']
            file = open('/files' + path[path.find('/', 1):], 'r')
            content += file.read()
        except IOError:
            status_line['Code'] = '404'
            status_line['Reason-Phrase'] = 'Not found'
            content += 'File not found'
        content += '</body></html>'

    response_headers['Content-Length'] = str(len(content))
    return form_response(status_line, response_headers, content)


def form_response(status_line, response_headers, content):
    return (status_line['HTTP-Version'] + ' ' + status_line['Code'] + ' ' + status_line['Reason-Phrase']
            + '\r\n' + 'Date: ' + response_headers['Date']
            + '\r\n' + 'Server ' + response_headers['Server']
            + '\r\n' + 'Content-Type ' + response_headers['Content-Type']
            + '\r\n' + 'Content-Length ' + response_headers['Content-Length']
            + '\r\n' + 'Connection ' + response_headers['Connection']
            + '\r\n\r\n' + content
            )


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('localhost', 8000))  # server_socket привязывается к address = (ip, port)
server_socket.listen(0)  # создает очередь размера 0 на входящие соединения (сколько можно держать not accepted)

print 'Started'

while 1:
    try:
        (client_socket, address) = server_socket.accept()
        print 'Got new client', client_socket.getsockname()  # возвращает адрес клиента (tuple)
        request_string = client_socket.recv(2048) # блокируясь если нечего читать, читает максимум 2048 байт
        client_socket.send(get_response(request_string))  # посылает строку
        client_socket.close()
    except KeyboardInterrupt:  # в случае нажатия ctrl-c
        print 'Stopped'
        server_socket.close()  # закрывает server_socket, если этот сокет более никем не испоьзуется освобождаются ресурсы
        exit()
