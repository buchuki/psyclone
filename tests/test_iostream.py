from psyclone import iostream
import socket

def pytest_funcarg__server_socket(request):
    '''Funcarg to create a UDP socket that can be communicated with. Why UDP
    when the httpserver we'll be testing is tcp?  So we don't have to set up an
    entire socket server using listen and accept. We're testing iostream now,
    not httpserver.
    
    A better solution is probably to create a mock object.'''
    read_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    read_socket.bind(("localhost", 9562))
    request.addfinalizer(lambda: read_socket.close())
    return read_socket

def pytest_funcarg__bound_socket(request):
    '''Funcarg to create a socket that communicates with the socket above.'''
    write_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    write_socket.connect(("localhost", 9562))
    request.addfinalizer(lambda: write_socket.close())
    return write_socket

def test_read_until(IOloop, server_socket, bound_socket):
    stream = iostream.IOStream(server_socket, IOloop)
    class checker:
        pass
    def onread(data):
        checker.data = data
        IOloop.stop()
    def send_val():
        bound_socket.send(b"This is a line.\na second line")
    stream.read_until('\n', onread)
    IOloop.add_callback(send_val)
    IOloop.start()
    assert checker.data == "This is a line.\n"

def test_read_bytes(IOloop, server_socket, bound_socket):
    stream = iostream.IOStream(server_socket, IOloop)
    class checker:
        pass
    def onread(data):
        checker.data = data
        IOloop.stop()
    def send_val():
        bound_socket.send(b"This is a line.\na second line")
    stream.read_bytes(5, onread)
    IOloop.add_callback(send_val)
    IOloop.start()
    assert checker.data == 'This '

def test_write(IOloop, server_socket, bound_socket):
    rcv_stream = iostream.IOStream(server_socket, IOloop)
    send_stream = iostream.IOStream(bound_socket, IOloop)
    class checker:
        pass
    def onread(data):
        checker.data = data
        IOloop.stop()
    send_stream.write(b'This is a line\n')
    rcv_stream.read_until('\n', onread)
    IOloop.start()
    assert checker.data == 'This is a line\n'
