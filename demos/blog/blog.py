#!/usr/bin/env python3
#
# Copyright 2009 Facebook
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

import markdown
import os.path
import re
import datetime
import psyclone.auth
import psyclone.httpserver
import psyclone.ioloop
import psyclone.options
import psyclone.web
import unicodedata

from psyclone.options import define, options
import postgresql

define("port", default=8888, help="run on the given port", type=int)
define("db_host", default="localhost", help="blog database host")
define("db_database", default="psycloneblog", help="blog database name")
define("db_user", default="psycloneblog", help="blog database user")
define("db_password", default="", help="blog database password")

class Application(psyclone.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/archive", ArchiveHandler),
            (r"/feed", FeedHandler),
            (r"/entry/([^/]+)", EntryHandler),
            (r"/compose", ComposeHandler),
            (r"/auth/login", AuthLoginHandler),
            (r"/auth/logout", AuthLogoutHandler),
        ]
        settings = dict(
            blog_title="Psyclone Blog",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            ui_modules={"Entry": EntryModule},
            xsrf_cookies=True,
            cookie_secret=b"11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/auth/login",
            debug=True
        )
        psyclone.web.Application.__init__(self, handlers, **settings)

        # Have one global connection to the blog DB across all handlers
        self.db = postgresql.open(
            host=options.db_host, database=options.db_database,
            user=options.db_user, password=options.db_password)


class BaseHandler(psyclone.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        user_id = self.get_secure_cookie("user")
        if not user_id: return None
        row = self.db.prepare("SELECT * FROM authors WHERE id = $1").first(int(user_id))
        return row

class HomeHandler(BaseHandler):
    def get(self):
        entries = self.db.prepare("SELECT * FROM entries ORDER BY published "
                                "DESC LIMIT 5")()
        if not entries:
            self.redirect("/compose")
            return
        self.render("home.html", entries=entries)


class EntryHandler(BaseHandler):
    def get(self, slug):
        entry = self.db.prepare("SELECT * FROM entries WHERE slug = $1"
                ).first(slug)
        if not entry: raise psyclone.web.HTTPError(404)
        self.render("entry.html", entry=entry)


class ArchiveHandler(BaseHandler):
    def get(self):
        entries = self.db.prepare("SELECT * FROM entries ORDER BY published "
                                "DESC")()
        self.render("archive.html", entries=entries)


class FeedHandler(BaseHandler):
    def get(self):
        entries = self.db.prepare("SELECT * FROM entries ORDER BY published "
                                "DESC LIMIT 10")()
        self.set_header("Content-Type", "application/atom+xml")
        self.render("feed.xml", entries=entries)


class ComposeHandler(BaseHandler):
    @psyclone.web.authenticated
    def get(self):
        id = self.get_argument("id", None)
        entry = None
        if id:
            entry = self.db.prepare("SELECT * FROM entries WHERE id = $1"
                    ).first(int(id))
        self.render("compose.html", entry=entry)

    @psyclone.web.authenticated
    def post(self):
        id = self.get_argument("id", None)
        title = self.get_argument("title")
        text = self.get_argument("markdown")
        html = markdown.markdown(text)
        if id:
            entry = self.db.prepare("SELECT * FROM entries WHERE id = $1"
                    ).first(int(id))
            if not entry: raise psyclone.web.HTTPError(404)
            slug = entry['slug']
            self.db.prepare(
                "UPDATE entries SET title = $1, markdown = $2, html = $3 "
                "WHERE id = $4")(title, text, html, int(id))
        else:
            slug = unicodedata.normalize("NFKD", title)
            slug = re.sub(r"[^\w]+", " ", slug)
            slug = "-".join(slug.lower().strip().split())
            if not slug: slug = "entry"
            while True:
                e = self.db.prepare("SELECT * FROM entries WHERE slug = $1").first(slug)
                if not e: break
                slug += "-2"
            self.db.prepare(
                "INSERT INTO entries (author_id,title,slug,markdown,html,"
                "published,updated) VALUES ($1,$2,$3,$4,$5,$6,$7)")(
                        self.current_user['id'], title, slug, text, html,
                        datetime.datetime.now(), datetime.datetime.now())
        self.redirect("/entry/" + slug)


class AuthLoginHandler(BaseHandler, psyclone.auth.GoogleMixin):
    @psyclone.web.asynchronous
    def get(self):
        if self.get_argument("openid.mode", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authenticate_redirect()
    
    def _on_auth(self, user):
        if not user:
            raise psyclone.web.HTTPError(500, "Google auth failed")
        author =self.db.prepare("SELECT * FROM authors WHERE email = $1"
                ).first(user["email"])
        if not author:
            # Auto-create first author
            any_author = self.db.prepare("SELECT * FROM authors LIMIT 1"
                    ).first()
            if not any_author:
                author_id = self.db.prepare(
                        "INSERT INTO authors (email,name) VALUES ($1,$2) "
                        "RETURNING id"
                        )(user["email"], user["name"])
            else:
                self.redirect("/")
                return
        else:
            author_id = author["id"]
        self.set_secure_cookie("user", str(author_id))
        self.redirect(self.get_argument("next", "/"))


class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))


class EntryModule(psyclone.web.UIModule):
    def render(self, entry):
        return self.render_string("modules/entry.html", entry=entry)


def main():
    psyclone.options.parse_command_line()
    http_server = psyclone.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    psyclone.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
