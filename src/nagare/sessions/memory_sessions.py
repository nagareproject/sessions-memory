# --
# Copyright (c) 2014-2025 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

"""Sessions managed in memory.

These sessions managers keep:
  - the last recently used ``DEFAULT_NB_SESSIONS`` sessions
  - for each session, the last recently used ``DEFAULT_NB_STATES`` states
"""

from nagare.sessions import common, lru_dict
from nagare.sessions.exceptions import ExpirationError

DEFAULT_NB_SESSIONS = 10000
DEFAULT_NB_STATES = 20


class Sessions(common.Sessions):
    """Sessions manager for states kept in memory."""

    CONFIG_SPEC = common.Sessions.CONFIG_SPEC | {
        'nb_sessions': 'integer(default=%d)' % DEFAULT_NB_SESSIONS,
        'nb_states': 'integer(default=%d)' % DEFAULT_NB_STATES,
    }

    def __init__(
        self,
        name,
        dist,
        local_service,
        services_service,
        nb_sessions=DEFAULT_NB_SESSIONS,
        nb_states=DEFAULT_NB_STATES,
        **config,
    ):
        """Initialization.

        In:
          - ``nb_sessions`` -- maximum number of sessions kept in memory
          - ``nb_states`` -- maximum number of states, for each sessions, kept in memory
        """
        services_service(super().__init__, name, dist, **config)

        self.local = local_service
        self.nb_states = nb_states
        self._sessions = lru_dict.ThreadSafeLRUDict(nb_sessions)

    def check_concurrence(self, multi_processes, multi_threads):
        if multi_processes:
            raise TypeError("this <%s> sessions manager can't run in multi-processes" % self.name)

    def check_session_id(self, session_id):
        """Test if a session exist.

        In:
          - ``session_id`` -- id of a session

        Return:
          - is ``session_id`` the id of an existing session?
        """
        return session_id in self._sessions

    def get_lock(self, session_id):
        """Retrieve the lock of a session.

        In:
          - ``session_id`` -- session id

        Return:
          - the lock
        """
        try:
            return self._sessions[session_id][1]
        except KeyError:
            raise ExpirationError('lock not found for session {}'.format(session_id))

    def _create(self, session_id, secure_token):
        """Create a new session.

        In:
          - ``session_id`` -- id of the session
          - ``secure_token`` -- the secure number associated to the session
        """
        lock = self.local.worker.create_lock()
        self._sessions[session_id] = [0, lock, secure_token, None, lru_dict.LRUDict(self.nb_states)]

        return session_id, 0, secure_token, lock

    def delete(self, session_id):
        """Delete a session.

        In:
          - ``session_id`` -- id of the session to delete
        """
        del self._sessions[session_id]

    def _fetch(self, session_id, state_id):
        """Retrieve a state with its associated objects graph.

        In:
          - ``session_id`` -- session id of this state
          - ``state_id`` -- id of this state

        Return:
          - id of the latest state
          - secure number associated to the session
          - data kept into the session
          - data kept into the state
        """
        try:
            last_state_id, _, secure_token, session_data, states = self._sessions[session_id]
            state_data = states[state_id]
        except KeyError:
            raise ExpirationError('invalid session structure')

        return last_state_id, secure_token, session_data, state_data

    def _store(self, session_id, state_id, secure_token, use_same_state, session_data, state_data):
        """Store a state and its associated objects graph.

        In:
          - ``session_id`` -- session id of this state
          - ``state_id`` -- id of this state
          - ``secure_token`` -- the secure number associated to the session
          - ``use_same_state`` -- is this state to be stored in the previous snapshot?
          - ``session_data`` -- data to keep into the session
          - ``state_data`` -- data to keep into the state
        """
        session = self._sessions[session_id]

        if not use_same_state:
            session[0] += 1

        session[2] = secure_token
        session[3] = session_data
        session[4][state_id] = state_data


class SessionsWithPickledStates(Sessions):
    """Sessions manager for states pickled / unpickled in memory."""

    CONFIG_SPEC = Sessions.CONFIG_SPEC | {'serializer': 'string(default="nagare.sessions.serializer:Pickle")'}
