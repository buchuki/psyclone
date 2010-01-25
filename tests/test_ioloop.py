from psyclone import ioloop
import os
def test_class_instance():
    '''Ensure two calls to ioloop.instance create only one object.'''
    assert not hasattr(ioloop.IOLoop, '_instance')
    assert ioloop.IOLoop.instance() == ioloop.IOLoop.instance()
    assert hasattr(ioloop.IOLoop, '_instance')
    assert ioloop.IOLoop.initialized()
    del ioloop.IOLoop._instance

def test_ioloop_funcarg(IOloop):
    '''Ensure the ioloop funcarg isn't from instance'''
    assert isinstance(IOloop, ioloop.IOLoop)
    assert not hasattr(ioloop.IOLoop, '_instance')

def test_run_loop(IOloop):
    '''Test adding a file descriptor to the IOLoop and it receives events.'''
    fdr, fdw = os.pipe()
    reader = os.fdopen(fdr, "rb", 0)
    writer = os.fdopen(fdw, "wb", 0)
    IOloop._set_nonblocking(fdr)
    IOloop._set_nonblocking(fdw)
    read_values = []
    def read_callback(fd, events):
        assert fd == fdr
        assert events & ioloop.IOLoop.READ
        assert IOloop.running()
        val = reader.read()
        if  val != None:
            assert val == b"ho"
            IOloop.stop()
    def send_val():
        writer.write("ho")
    IOloop.add_handler(fdr, read_callback, IOloop.READ)
    IOloop.add_callback(send_val)
    IOloop.start()
