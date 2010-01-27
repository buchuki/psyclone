#!/usr/bin/env python3
#
# Copyright 2009 Facebook
# Copyright 2010 Dusty Phillips
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

import psyclone.auth
import psyclone.escape
import psyclone.httpserver
import psyclone.ioloop
import psyclone.options
import psyclone.web

from psyclone.options import define, options

define("port", default=8888, help="run on the given port", type=int)


class Application(psyclone.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/auth/login", AuthHandler),
        ]
        settings = dict(
            cookie_secret="32oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/auth/login",
        )
        psyclone.web.Application.__init__(self, handlers, **settings)


class BaseHandler(psyclone.web.RequestHandler):
    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json: return None
        return psyclone.escape.json_decode(user_json)


class MainHandler(BaseHandler):
    @psyclone.web.authenticated
    def get(self):
        name = psyclone.escape.xhtml_escape(self.current_user["name"])
        self.write("Hello, " + name)


class AuthHandler(BaseHandler, psyclone.auth.GoogleMixin):
    @psyclone.web.asynchronous
    def get(self):
        if self.get_argument("openid.mode", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authenticate_redirect()
    
    def _on_auth(self, user):
        if not user:
            raise psyclone.web.HTTPError(500, "Google auth failed")
        self.set_secure_cookie("user", psyclone.escape.json_encode(user))
        self.redirect("/")


def main():
    psyclone.options.parse_command_line()
    http_server = psyclone.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    psyclone.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
