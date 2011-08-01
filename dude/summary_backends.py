# Copyright (c) 2011 Stephan Creutz
# Distributed under the MIT License
# See accompanying file LICENSE

'''
various summary backends
'''

import os
import sqlite3

class FileSumBackend:
    def __init__(self, name):
        self.__file = open(name, 'w')

    def write_header(self, header):
        '''
        write the column names for the summary
        '''

        if type(header) == str:
            self.__file.write(header + '\n')
        elif type(header) == list:
            self.__file.write(' '.join(header) + '\n')

    def write(self, string):
        '''
        behavior to be a "file-like" object (see documention for "print")
        '''

        self.__file.write(string)

    def close(self):
        if self.__file.closed:
            return

        os.fsync(self.__file)
        self.__file.close()

    def __del__(self):
        self.close()

class Sqlite3SumBackend:
    '''
    sqlite3 database backend support

    behaves like a "file-like" object
    '''

    def __init__(self, name):
        self.__name = name
        self.__connection = sqlite3.connect(name + '.sqlite3')
        self.__cursor = self.__connection.cursor()
        self.__closed = False

    def write_header(self, header):
        '''
        write the column names for the summary
        '''

        if type(header) == str:
            cols = header.split()
        else:
            cols = header

        table_name = self.__name.split('/')[-1]

        # check if table already exists
        # SQLite FAQ: http://www.sqlite.org/faq.html#q7
        self.__cursor.execute('''
select count(name) from sqlite_master where type=\'table\' and name=?;''',
                              (table_name,))

        if self.__cursor.fetchone()[0] > 0:
            self.__cursor.execute('delete from %s;' % table_name)
        else:
            self.__cursor.execute('create table %s (%s);' % \
                                      (table_name, ', '.join(cols)))

    def write(self, string):
        '''
        behavior to be a "file-like" object (see documention for "print")
        '''

        args = string.strip().split()
        if len(args) == 0:
            return

        self.__cursor.execute('insert into %s values (%s);' %
                              (self.__name.split('/')[-1],
                               ', '.join(['\'' + str(arg) + '\''
                                          for arg in args])))

    def close(self):
        if self.__closed:
            return

        self.__cursor.close()
        self.__connection.commit()
        self.__connection.close()
        self.__closed = True

    def __del__(self):
        self.close()

registry = { 'file' : FileSumBackend, 'sqlite3' : Sqlite3SumBackend }

def backend_names():
    return registry.keys()

def backend_constructor(backend_name):
    return registry[backend_name]
