#!/usr/bin/env python3
import sys
import xlrd
from db_table import db_table

#
class ImportAgenda:

    def __init__(self):
        
    def import_file(self, file_path):
    
    def close_conn(self):
        self.sessions.close()
        self.speakers.close()
        

def main():
    if len(sys.argv) != 2:
        print("Usage: ./import_agenda.py agenda.xls")
        sys.exit(1)
    # import_agenda(sys.argv[1])
    imported_agenda = ImportAgenda()
    imported_agenda.import_file(sys.argv[1])
    imported_agenda.close_conn()

if __name__ == '__main__':
    main()
    
