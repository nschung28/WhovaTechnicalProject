#!/usr/bin/env python3
import sys
import xlrd
from db_table import db_table

#
class ImportAgenda:

    def __init__(self):
        # Create the table for sessions:
        # Table will include information such as the PRIMARY KEY session id, another session id (if it is a sub-session),
        # date of the session, starting and ending time of the session, name of the session, session location,
        # and the description for the session.
        # NOTE: Might be useful to add indexing to main_session_id to find sub-sessions of a session a lot faster. Same with
        # date and location since these commonly correspond to larger amounts of data.
        self.sessions = db_table("sessions", 
                            {
                                "id": "integer PRIMARY KEY",
                                "main_session_id": "integer",
                                "date": "text",
                                "time_start": "text",
                                "time_end": "text",
                                "session_title": "text",
                                "location": "text",
                                "description": "text"
                            })
        
        # Create the table for the speakers:
        # Table will include information on the PRIMARY KEY speaker id, the session id that they are speaking at,
        # and the name of the speaker.
        # NOTE: 'id' is utilized for faster lookup and possible joins that might be needed later.
        # NOTE: might go back and add an index for the speaker name and session_id for faster look up later.
        self.speakers = db_table("speakers",
                            {
                                "id": "integer PRIMARY KEY",
                                "session_id": "text",
                                "speaker_name": "text"
                            })


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
    
