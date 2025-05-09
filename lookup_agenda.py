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
    VALID_COLS = {'date', 'time_start', 'time_end', 'session_title', 'location', 'description', 'speaker'}

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
    
    #
    # Searches the appropriate tables for a specific column and value.
    # Gathers the date, time start, time end, session title, location, and description for the
    # column and value and displays it in a viewable manner.
    #
    # \param column  string  the column that the user wishes to search by
    # \param value   string  the value that the user wishes to search by within the column
    #
    def lookup(self, column, value):
        if column == 'speaker':
            res = self.lookup_speaker(value)
        else:
            res = self.lookup_column(column, value)
        
        for out in res:
            print(f"Date: {out['date']}\t Time start: {out['time_start']}\t Time End: {out['time_end']}")
            print(f"Session Title: {out['session_title']}\t Location: {out['location']}")
            print('Description:\n', out['description'])
            print('='*80, '\n')

        print(f"\nTotal matching sessions: {len(res)}")

    #
    # Searches through the database for a specified column that is not a 'speaker'.
    # Gathers relevant information about sessions relating to the column and value pair
    # and returns an array of all the outputs.
    #
    # \param column  string  the column that the user wishes to search by
    # \param value   string  the value that the user wishes to search by within the column
    #
    # \return List of all the sessions that the value is found in.
    # Example. If the user passes in 'date' as column and '06/16/2018' as the date, the list
    # will contain all sessions where their date is '06/16/2018'.
    #
    def lookup_column(self, column, value):
        out = []
        duplicate = set()
        
        found_ids = self.sessions.select(columns=['id'], where={f"lower({column})": value.lower()})
        for row in found_ids:
            session_id = row['id']
            self.grab_rows(out, duplicate, session_id)
        
        return out

    #
    # Searches through the database for a specific speaker's name and gathers all the
    # sessions the speaker is speaking at.
    #
    # \param speaker_name  string  the name of the speaker to be searched for
    #
    # \return List of all the sessions the speaker is speaking at
    #
    def lookup_speaker(self, speaker_name):
        out = []
        duplicate = set()

        found_ids = self.sessions.select_join(
            other_db='speakers',
            left='id',
            right='session_id',
            columns=['sessions.id'],
            where={'lower(speakers.speaker_name)': speaker_name.lower()}   
        )
        for row in found_ids:
            print(row)
            session_id = row['sessions.id']
            self.grab_rows(out, duplicate, session_id)
        
        return out

    #
    # Gathers all the rows that correspond to the given session id. If the session id
    # has sub-sessions, it will also gather those as well. Note that there will be no
    # duplicate sessions returned.
    #
    # \param out         list     contains all the sessions to be displayed.
    # \param duplicate   set      contains all sessions that were found to prevent
    #                             duplicate sessions from being displayed
    # \param session_id  integer  the session id to be searched for in the database
    #
    def grab_rows(self, out, duplicate, session_id):
        # Check to make sure we don't have duplicate outputs.
        print(type(out))
        if session_id in duplicate:
            return
        
        row = self.sessions.select(where={'id':session_id})[0]

        out.append(row)
        duplicate.add(session_id)

        is_main = row['main_session_id'] == None
        
        # if subsessions exist for this session, recursively find the other sessions
        sub_ids = self.sessions.select(where={'main_session_id': session_id})
        for sub_id in sub_ids:
            self.grab_rows(out, duplicate, sub_id['id'])


    #
    # Close the database connection
    #
    def close_conn(self):
        self.sessions.close()
        self.speakers.close()


def main():
    lookup_agenda = LookupAgenda()
    if len(sys.argv) < 3 and (sys.argv[1].lower() != 'speaker' and len(sys.argv) != 3):
        print('Usage: ./lookup_agenda.py <column|speaker> <value>')
        print(f"Valid column names are: {', '.join(lookup_agenda.VALID_COLS)}")
        print('If using speaker, only input a single speaker\'s name')
        print('If description has special characters, wrap whole description in \' \'.')
        lookup_agenda.close_conn()
        sys.exit(1)

    # '&*_' is utilized as the join so normal '_' can be utilized in the agenda
    col, val = sys.argv[1], ' '.join(sys.argv[2:])
    if col.lower() not in lookup_agenda.VALID_COLS:
        print(f'Error: Column must be one of the following: {lookup_agenda.VALID_COLS}')
        lookup_agenda.close_conn()
        sys.exit(1)

    lookup_agenda.lookup(col.lower(), val)
    lookup_agenda.close_conn()
    

if __name__ == '__main__':
    main()
