#!/bin/bash

rm sql/empty.db database.db 
touch sql/empty.db
sqlite3 sql/empty.db < sql/create.sql
cp sql/empty.db database.db
