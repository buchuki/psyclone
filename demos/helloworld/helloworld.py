#!/usr/bin/env python
#
# Copyright 2009 Facebook
# Some portions Copyright 2010 Dusty Phillips
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import psyclone.httpserver
import psyclone.ioloop
import psyclone.options
import psyclone.web

from psyclone.options import define, options

define("port", default=8888, help="run on the given port", type=int)


class MainHandler(psyclone.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


def main():
    psyclone.options.parse_command_line()
    application = psyclone.web.Application([
        (r"/", MainHandler),
    ])
    http_server = psyclone.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    psyclone.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
