import {
  useState,
} from "react";


function Approval({
  approval,
  approvalRequired = false,
  onDecision,
  loading = false,
}) {

  const [comment, setComment] =
    useState("");


  if (!approvalRequired) {
    return null;
  }


  if (!approval) {
    return null;
  }


  if (
    approval.status !==
    "pending"
  ) {

    return null;

  }


  const action =
    approval.action ||
    "Sensitive Action";


  const isEmail =
    action === "send_email";


  const isPublish =
    action ===
    "publish_report";


  return (

    <div className="approval-card">

      <div className="approval-icon">
        ⚠️
      </div>


      <div className="approval-content">

        <div className="approval-header">

          <div>

            <h2>
              Human Approval Required
            </h2>

            <p>
              The AI agent is requesting
              permission to perform a
              sensitive action.
            </p>

          </div>

        </div>


        {/* -------------------------------- */}
        {/* Action */}
        {/* -------------------------------- */}

        <div className="approval-action">

          <span>
            Requested Action
          </span>

          <strong>
            {isEmail &&
              "📧 Send Email"}

            {isPublish &&
              "🌐 Publish Report"}

            {!isEmail &&
              !isPublish &&
              action}
          </strong>

        </div>


        {/* -------------------------------- */}
        {/* Reason */}
        {/* -------------------------------- */}

        {approval.reason && (

          <div className="approval-reason">

            <strong>
              Why approval is needed
            </strong>

            <p>
              {approval.reason}
            </p>

          </div>

        )}


        {/* -------------------------------- */}
        {/* Payload preview */}
        {/* -------------------------------- */}

        {approval.payload && (

          <details
            className="approval-details"
          >

            <summary>
              View action details
            </summary>

            <pre>
              {JSON.stringify(
                approval.payload,
                null,
                2
              )}
            </pre>

          </details>

        )}


        {/* -------------------------------- */}
        {/* Comment */}
        {/* -------------------------------- */}

        <textarea
          value={comment}
          onChange={(e) =>
            setComment(
              e.target.value
            )
          }
          placeholder={
            "Optional approval/rejection comment..."
          }
          rows={3}
          disabled={loading}
        />


        {/* -------------------------------- */}
        {/* Buttons */}
        {/* -------------------------------- */}

        <div className="approval-buttons">

          <button
            className="approve-button"
            disabled={loading}
            onClick={() =>
              onDecision(
                true,
                comment.trim()
              )
            }
          >
            {loading
              ? "Processing..."
              : "✓ Approve"}
          </button>


          <button
            className="reject-button"
            disabled={loading}
            onClick={() =>
              onDecision(
                false,
                comment.trim()
              )
            }
          >
            {loading
              ? "Processing..."
              : "✕ Reject"}
          </button>

        </div>

      </div>

    </div>

  );

}


export default Approval;