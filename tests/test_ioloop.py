from psyclone import ioloop
import os
import time 

LEGAL_TIMEOUT = 0.5 # If a timeout is late by this many seconds, fail

'''If you're curious about the 'checker' classes in the tests below, they're just a way to save values for delayed assertion. This allows the assertions to take place after the IOLoop has stopped. If we did the assertions inside the callbacks, one of two things would happen: either the assertion would be gobbled up by the main loop (a false pass), or the call inside the callback that stops the loop would never be executed (infinite loop)'''

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
    class checker:
        pass
    def read_callback(fd, events):
        checker.fd = fd
        checker.events = events
        val = reader.read()
        if  val != None:
            checker.val = val
            IOloop.stop()
    def send_val():
        writer.write("ho")
    IOloop.add_handler(fdr, read_callback, IOloop.READ)
    IOloop.add_callback(send_val)
    IOloop.start()
    assert checker.fd == fdr
    assert checker.events & ioloop.IOLoop.READ
    assert checker.val == b"ho"

def test_timeout(IOloop):
    '''Test that adding a timeout to the IOLoop causes an event to occur at
    that time.'''
    end = time.time() + 0.5
    class checker:
        pass
    def check_now():
        checker.ended = time.time()
        IOloop.stop()
    IOloop.add_timeout(end, check_now)
    IOloop.start()
    assert checker.ended > end
    assert checker.ended < end + LEGAL_TIMEOUT

def test_periodic(IOloop):
    '''Ensure periodic callbacks are called repeatedly.'''
    class checker:
        call_count = 0
        checks = []
    def check_period():
        checker.checks.append(time.time())
        checker.call_count += 1
        if checker.call_count > 3:
            IOloop.stop()
    periodic = ioloop.PeriodicCallback(check_period, 200, IOloop)
    periodic.start()
    start = time.time()
    IOloop.start()
    assert checker.call_count == 4
    for count, check in enumerate(checker.checks):
        assert check > start + count * 0.2
        assert check < start + count * 0.2 + LEGAL_TIMEOUT

