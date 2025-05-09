#!/usr/bin/env python3
import sys
import xlrd
import sqlite3
from db_table import db_table

# 
# Creates a 'sessions' and 'speakers' table and populates them with the data contained in the
# provided .xls file. 
# 
# Any new file passed through will completely override and delete existing data.
#
class ImportAgenda:

    # Set of headers that are expected to be found in the xls sheet prior to importing
    EXPECTED_HEADERS = {'date', 'time_start', 'time_end', 'session_or_sub-session(sub)',
                        'session_title', 'room/location', 'description', 'speakers'}

    REQUIRED_FIELDS = {'date', 'time_start', 'time_end', 'session_or_sub-session(sub)', 'session_title'}

    # Skip first 14 rows NUM_ROWS_TO_SKIP + 1 represents the first row of data
    NUM_ROWS_TO_SKIP = 14

    #
    # Initializes 'sessions' and 'speakers' tables.
    # If these tables already exist, the tables are dropped and recreated to allow new
    # data to take over.
    #
    def __init__(self):

        conn = sqlite3.connect(db_table.DB_NAME)
        conn.execute("DROP TABLE IF EXISTS sessions")
        conn.execute("DROP TABLE IF EXISTS speakers")
        conn.commit()
        conn.close()

        # Create the table for sessions:
        # Table will include information such as the PRIMARY KEY session id, another session id
        # (if it is a sub-session), date of the session, starting and ending time of the session,
        # name of the session, session location, and the description for the session.
        # NOTE: Might be useful to add indexing to main_session_id to find sub-sessions of a
        # session a lot faster. Same with date and location since these commonly correspond to
        # larger amounts of data.
        self.sessions = db_table('sessions', 
                            {
                                'id': 'integer PRIMARY KEY',
                                'main_session_id': 'integer',
                                'date': 'text',
                                'time_start': 'text',
                                'time_end': 'text',
                                'session_title': 'text',
                                'location': 'text',
                                'description': 'text'
                            })
        
        # Create the table for the speakers:
        # Table will include information on the PRIMARY KEY speaker id, the session id that they
        # are speaking at, and the name of the speaker.
        # NOTE: 'id' is utilized for faster lookup and possible joins that might be needed later.
        # NOTE: might go back and add an index for the speaker name and session_id for faster
        # look up later.
        self.speakers = db_table('speakers',
                            {
                                'id': 'integer PRIMARY KEY',
                                'session_id': 'integer',
                                'speaker_name': 'text'
                            })


    #
    # Database import and initialization.
    # Takes in a .xls file and will read and update the appropriate tables to contain data in
    # the file.
    # 
    # \param file_path  string  path to the .xls file to be imported.
    #
    def import_file(self, file_path):
        rows = self.extract_xls(file_path)
        
        # If current row is a sub-session, utilize this to find main session id
        sub_to_main = None
        for row in rows:
            date, time_start, time_end, sesh_type, sesh_title, loc, desc, speaker = row
            sid = None
            if sesh_type.lower() == 'sub':
                sid = self.sessions.insert({
                    'main_session_id': sub_to_main,
                    'date': date.replace("'", "''"),
                    'time_start': time_start.replace("'", "''"),
                    'time_end': time_end.replace("'", "''"),
                    'session_title': sesh_title.replace("'", "''"),
                    'location': loc.replace("'", "''"),
                    'description': desc.replace("'", "''")
                })
            else:
                sid = self.sessions.insert({
                    'main_session_id': None,
                    'date': date.replace("'", "''"),
                    'time_start': time_start.replace("'", "''"),
                    'time_end': time_end.replace("'", "''"),
                    'session_title': sesh_title.replace("'", "''"),
                    'location': loc.replace("'", "''"),
                    'description': desc.replace("'", "''")
                })
                sub_to_main = sid
            
            if speaker:
                for person in speaker.split(';'):
                    person = person.strip()
                    if not person:
                        continue
                    self.speakers.insert({
                        'session_id': sid,
                        'speaker_name': person.replace("'", "''")
                    })
        
        print(f'Successfully imported {len(rows)} rows from {file_path}')


    @classmethod
    #
    # Extracts data from the .xls file according to the file path
    # Requires headers to be 'date', 'time start', 'time end', 'session or sub-session(sub)',
    # 'session title', 'room/location', 'description', and 'speakers'. Headers can be
    # case-insensitive and may contain '*' characters for clarity.
    # Also requires that no rows in the provided agenda are duplicates.
    # 
    # \param file_path  string  path to the .xls file to be imported.
    #
    # \return List containing tuples which then contain the data per row.
    #
    # Example [('06/16/2018', '08:30 AM', '08:45 AM', 'Session', 'Welcome by general and
    #           program chairs','South Pacific Ballroom', '', 'Rajeev Balasubramonian;
    #           Al Davis; Sarita Adve')]
    #
    # \error RuntimeError is thrown if the .xls file is missing an expected header or if
    #                     there is a row.
    #
    def extract_xls(cls, file_path):
        book = xlrd.open_workbook(file_path)
        sh = book.sheet_by_index(0)
        columns = []
        
        # Extract all the headers and replace spaces with underscore,
        # remove trailing whitespace, and remove * char.
        for header in range(sh.ncols):
            columns.append(sh.cell_value(cls.NUM_ROWS_TO_SKIP, header).lower()
                          .strip().replace(' ', '_').replace('\n', '').replace('*', ''))

        # Look for any missing headers in the given file
        missing_headers = cls.EXPECTED_HEADERS - set(columns)
        if missing_headers:
            raise RuntimeError(
                f"Missing required column headers in row {cls.NUM_ROWS_TO_SKIP+1}: {', '.join(sorted(missing_headers))}"
            )
        
        # Iterate over all the rows and extract data as tuples into rows. 
        # Also check for any duplicate rows and raise error if so.
        index = {h: i for i, h in enumerate(columns)}
        rows = []
        duplicate_rows = set()
        for row_num in range(cls.NUM_ROWS_TO_SKIP + 1, sh.nrows):
            row = sh.row(row_num)

            # Ensures that Session Title, Date, Time Start, Time End, Session are provided
            vals = {h: row[index[h]].value for h in cls.REQUIRED_FIELDS}
            missing = [h for h, v in vals.items() if not str(v).strip()]
            if missing:
                missing = [norm.replace('_', ' ') for norm in missing]
                raise RuntimeError(
                    f"Missing required fields {', '.join(missing)} in row {row_num+1}"
                )

            data_row = (
                row[index['date']].value,
                row[index['time_start']].value,
                row[index['time_end']].value,
                row[index['session_or_sub-session(sub)']].value,
                row[index['session_title']].value,
                row[index['room/location']].value,
                row[index['description']].value,
                row[index['speakers']].value,
            )

            if data_row in duplicate_rows:
                raise RuntimeError(
                    f"Duplicate agenda in row {row_num}: {', '.join(data_row)}"
                )
            duplicate_rows.add(data_row)
            rows.append(data_row)
        
        return rows


    #
    # Close the database connection
    #
    def close_conn(self):
        self.sessions.close()
        self.speakers.close()
        

def main():
    if len(sys.argv) != 2:
        print('Usage: ./import_agenda.py <.xls file path>')
        sys.exit(1)

    imported_agenda = ImportAgenda()
    imported_agenda.import_file(sys.argv[1])
    imported_agenda.close_conn()

if __name__ == '__main__':
    main()
    
