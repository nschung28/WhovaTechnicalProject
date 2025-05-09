#!/usr/bin/env python3
import sys
from db_table import db_table

#
# Allows the user to search for specific values in their agenda database.
# Example. User can search up 'date' and specify '06/16/2018' as the date and any row
# in their agenda with that date will be displayed.
# 
# If the user prompts to search by speaker, only one speaker's name can be taken at a time.
#
class LookupAgenda:

    # Set of columns that the user can lookup by.
    VALID_COLS = {"date", "time_start", "time_end", "session_title", "location", "description"}

    #
    # Initializes the sessions and speakers table in order to be searched in later methods.
    #
    def __init__(self):
        
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

    
    def lookup_column(self, column, value):

    def lookup_speaker(self, speaker_name):

    #
    # Close the database connection
    #
    def close_conn(self):
        self.sessions.close()
        self.speakers.close()


def main():
    if len(sys.argv) != 3:
        print("Usage: ./lookup_agenda.py <column|speaker> <value>")
        sys.exit(1)

if __name__ == "__main__":
    main()
