# Copyright (c) 2011, 2012 Stephan Creutz
# Distributed under the MIT License
# See accompanying file LICENSE

'''
various summary backends
'''

import json
import os
import re
import sqlite3

class FileSumBackend:
    def __init__(self, name, dimensions):
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

class JsonSumBackend:
    def __init__(self, name, dimensions):
        self.__name = name
        self.__dimensions = dimensions
        self.__jsonobj = {}

    def write_header(self, header):
        if type(header) == str:
            self.__header = header.split()
        elif type(header) == list:
            self.__header = header

    def write(self, string):
        subdoc = self.__jsonobj
        values = string.strip().split(None, len(self.__header) - 1)

        if len(values) != len(self.__header):
            return

        if '{' in values[len(values) - 1]:
            values[len(values) - 1] = json.loads(values[len(values) - 1])

        for i in range(len(self.__dimensions)):
            subdoc = subdoc.setdefault(self.__header[i], {})
            subdoc = subdoc.setdefault(values[i], {})

        for j in range(len(self.__header) - len(self.__dimensions)):
            subdoc[self.__header[len(self.__dimensions) + j]] = values[len(self.__dimensions) + j]

    def close(self):
        with open(self.__name + '.json', 'w') as jsonfile:
            json.dump(self.__jsonobj, jsonfile, indent=4)

class Sqlite3SumBackend:
    '''
    sqlite3 database backend support

    behaves like a "file-like" object
    '''

    def __init__(self, name, dimensions):
        self.__name = name
        self.__connection = sqlite3.connect(name + '.sqlite3')
        self.__connection.text_factory = str # don't create unicode strings
        self.__cursor = self.__connection.cursor()
        self.__closed = False

    def _create_table(self, table_name, cols):
        self.__cursor.execute('create table %s (%s);' % \
                                  (table_name, ', '.join(cols)))

    def _drop_table(self, table_name):
        self.__cursor.execute('drop table %s;' % table_name)

    def write_header(self, header):
        '''
        write the column names for the summary
        '''

        if type(header) == str:
            cols = header.split()
        else:
            cols = header

        table_name = self.__name.split(os.path.sep)[-1]

        # check if table already exists
        # SQLite FAQ: http://www.sqlite.org/faq.html#q7
        self.__cursor.execute('''
select name, sql from sqlite_master where type=\'table\' and name=?;''',
                              (table_name,))

        row = self.__cursor.fetchone()
        if row:
            sql_statement = row[1]
            match = re.search(r'\((.*)\)$', sql_statement)
            prev_cols = match.group(1).split(', ')
            if set(prev_cols) != set(cols): # number or names of columns changed
                # there is no choice, the table must be dropped, because "alter"
                # does not work in all cases
                self._drop_table(table_name)
                self._create_table(table_name, cols)
            else:
                # all data in the table is deleted because if the transaction
                # fails, we have at least the previous data
                self.__cursor.execute('delete from %s;' % table_name)
        else:
            self._create_table(table_name, cols)

    def write(self, string):
        '''
        behavior to be a "file-like" object (see documention for "print")
        '''

        args = string.strip().split()
        if len(args) == 0:
            return

        self.__cursor.execute('insert into %s values (%s);' %
                              (self.__name.split(os.path.sep)[-1],
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

registry = { 'file' : FileSumBackend, 'json' : JsonSumBackend, 'sqlite3' : Sqlite3SumBackend }

def backend_names():
    return registry.keys()

def backend_constructor(backend_name):
    return registry[backend_name]
