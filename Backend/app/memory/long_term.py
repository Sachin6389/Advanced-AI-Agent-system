from app.checkpoints.database import (
    CheckpointDB
)


class LongTermMemory:

    def __init__(
        self,
        db: CheckpointDB
    ):

        self.db = db


    def load(
        self,
        session_id
    ):

        state = self.db.load_state(
            session_id
        )

        if not state:

            return None

        return {

            "memories":
                state.get(
                    "memories",
                    []
                ),

            "previous_queries":
                state.get(
                    "previous_queries",
                    []
                )

        }


    def remember(
        self,
        session_id,
        memory
    ):

        state = (
            self.db.load_state(
                session_id
            )
            or
            {
                "session_id":
                    session_id,

                "memories": [],

                "previous_queries": []
            }
        )

        state.setdefault(
            "memories",
            []
        ).append(
            memory
        )

        self.db.save_state(
            session_id,
            state
        )