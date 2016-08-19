#!/usr/bin/env python

import settings
import sqlite3

def main():
    conn = sqlite3.connect(settings.DB_NAME)
    conn.execute("CREATE TABLE papers (title text)")


if __name__ == '__main__':
    main()
