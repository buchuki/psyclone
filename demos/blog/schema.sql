-- Copyright 2009 FriendFeed
-- Some Changes Copyright 2010 Dusty Phillips
--
-- Licensed under the Apache License, Version 2.0 (the "License"); you may
-- not use this file except in compliance with the License. You may obtain
-- a copy of the License at
--
--     http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
-- WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
-- License for the specific language governing permissions and limitations
-- under the License.

-- To create the database:
-- $ creatuser psycloneblog
-- $ createdb -U psycloneblog psycloneblog
--
-- To reload the tables:
--   psql -U psycloneblog psycloneblog < schema.sql

DROP TABLE IF EXISTS authors CASCADE;
CREATE TABLE authors (
    id SERIAL NOT NULL PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL
);

DROP TABLE IF EXISTS entries;
CREATE TABLE entries (
    id SERIAL NOT NULL PRIMARY KEY,
    author_id INT NOT NULL REFERENCES authors(id),
    slug VARCHAR(100) NOT NULL UNIQUE,
    title VARCHAR(512) NOT NULL,
    markdown TEXT NOT NULL,
    html TEXT NOT NULL,
    published TIMESTAMP NOT NULL,
    updated TIMESTAMP NOT NULL
);
