from psyclone import ioloop

def pytest_funcarg__IOloop(request):
    '''Funcarg to create a ioloop that is not the standard ioloop. This allows
    test teardown more easily. It also allows testing of independent
    IOLoops.'''
    return ioloop.IOLoop()
