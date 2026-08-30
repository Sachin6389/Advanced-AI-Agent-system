from app.checkpoints.database import (
    CheckpointDB
)


class ApprovalManager:

    def __init__(
        self,
        db: CheckpointDB
    ):

        self.db = db


    def create(

        self,

        session_id,

        action,

        reason,

        payload

    ):

        approval = {

            "action": action,

            "reason": reason,

            "payload": payload,

            "status": "pending"

        }

        self.db.save_approval(
            session_id,
            approval
        )

        return approval


    def get(
        self,
        session_id
    ):

        return self.db.get_approval(
            session_id
        )


    def decide(

        self,

        session_id,

        approved,

        comment=None

    ):

        approval = self.db.get_approval(
            session_id
        )

        if not approval:

            raise ValueError(
                "Approval not found"
            )

        approval["status"] = (
            "approved"
            if approved
            else
            "rejected"
        )

        approval["comment"] = comment

        self.db.save_approval(
            session_id,
            approval
        )

        return approval