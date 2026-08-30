import json
import sqlite3

from pathlib import Path
from threading import Lock


class CheckpointDB:

    def __init__(
        self,
        path: str
    ):

        self.path = str(
            Path(path)
        )

        self.lock = Lock()

        self.init_db()


    def connect(self):

        connection = sqlite3.connect(
            self.path
        )

        connection.row_factory = (
            sqlite3.Row
        )

        return connection


    def init_db(self):

        with self.connect() as conn:

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS
                checkpoints (
                    session_id TEXT PRIMARY KEY,
                    state_json TEXT NOT NULL,
                    updated_at TEXT
                    DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS
                approvals (
                    session_id TEXT PRIMARY KEY,
                    approval_json TEXT NOT NULL,
                    updated_at TEXT
                    DEFAULT CURRENT_TIMESTAMP
                )
                """
            )


    def save_state(
        self,
        session_id,
        state
    ):

        with self.lock:

            with self.connect() as conn:

                conn.execute(
                    """
                    INSERT INTO checkpoints
                    (
                        session_id,
                        state_json
                    )
                    VALUES (?, ?)

                    ON CONFLICT(session_id)
                    DO UPDATE SET

                    state_json =
                    excluded.state_json,

                    updated_at =
                    CURRENT_TIMESTAMP
                    """,
                    (
                        session_id,
                        json.dumps(
                            state,
                            default=str
                        )
                    )
                )


    def load_state(
        self,
        session_id
    ):

        with self.connect() as conn:

            row = conn.execute(
                """
                SELECT state_json
                FROM checkpoints
                WHERE session_id=?
                """,
                (
                    session_id,
                )
            ).fetchone()

        if not row:

            return None

        return json.loads(
            row["state_json"]
        )


    def save_approval(
        self,
        session_id,
        approval
    ):

        with self.lock:

            with self.connect() as conn:

                conn.execute(
                    """
                    INSERT INTO approvals
                    (
                        session_id,
                        approval_json
                    )
                    VALUES (?, ?)

                    ON CONFLICT(session_id)
                    DO UPDATE SET

                    approval_json =
                    excluded.approval_json,

                    updated_at =
                    CURRENT_TIMESTAMP
                    """,
                    (
                        session_id,
                        json.dumps(
                            approval,
                            default=str
                        )
                    )
                )


    def get_approval(
        self,
        session_id
    ):

        with self.connect() as conn:

            row = conn.execute(
                """
                SELECT approval_json
                FROM approvals
                WHERE session_id=?
                """,
                (
                    session_id,
                )
            ).fetchone()

        if not row:

            return None

        return json.loads(
            row["approval_json"]
        )