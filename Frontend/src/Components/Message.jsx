
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import axios from "axios";

export default function Message({
  message,
  onApprovalComplete,
  userId,
  
}) {
  // =========================================================
  // MESSAGE TYPE
  // =========================================================
  

  const isUser =
    message?.sender === "user";

  // =========================================================
  // USER MESSAGE
  // =========================================================

  const userText =
    typeof message?.text === "string"
      ? message.text
      : "";



  const rawAnswer =
    message?.answer ??
    message?.text ??
    "";

  const normalizeAnswer = (value) => {
    if (typeof value === "string") {
      return value;
    }

    if (value === null || value === undefined) {
      return "";
    }

    /*
     * If answer is an object containing the actual answer
     */
    if (
      typeof value === "object" &&
      !Array.isArray(value)
    ) {
      if (typeof value.answer === "string") {
        return value.answer;
      }

      if (typeof value.content === "string") {
        return value.content;
      }

      if (typeof value.text === "string") {
        return value.text;
      }

      /*
       * Last fallback.
       *
       * This guarantees ReactMarkdown always
       * receives a string.
       */
      try {
        return JSON.stringify(
          value,
          null,
          2
        );
      } catch {
        return String(value);
      }
    }

    /*
     * If answer is an array
     */
    if (Array.isArray(value)) {
      return value
        .map((item) => {
          if (typeof item === "string") {
            return item;
          }

          if (
            item &&
            typeof item === "object"
          ) {
            if (
              typeof item.text ===
              "string"
            ) {
              return item.text;
            }

            if (
              typeof item.content ===
              "string"
            ) {
              return item.content;
            }

            if (
              typeof item.answer ===
              "string"
            ) {
              return item.answer;
            }

            try {
              return JSON.stringify(
                item
              );
            } catch {
              return "";
            }
          }

          return String(item);
        })
        .join("\n\n");
    }

    return String(value);
  };

  const answer =
    normalizeAnswer(rawAnswer);

  // =========================================================
  // SESSION
  // =========================================================

  const sessionId =
    message?.approval?.session_id ||
    null;



  // =========================================================
  // APPROVAL
  // =========================================================

  const approval =
    message?.approval?.approval ||
    null;

  const approvalRequired =
    message?.approval?.approval_required === true;

  // =========================================================
  // SOURCES
  // =========================================================

  const sources =
    Array.isArray(message?.text?.sources)
      ? message.text.sources
      : [];

  // =========================================================
  // PLAN
  // =========================================================

  const plan =
    Array.isArray(message?.text?.plan)
      ? message.text.plan
      : [];

  // =========================================================
  // WORKFLOW STATUS
  // =========================================================

  const workflowStatus =
    typeof message?.approval?.status === "string"
      ? message.approval.status
      : "unknown";

  // =========================================================
  // ERRORS
  // =========================================================

  const errors =
    Array.isArray(message?.approval?.errors)
      ? message.approval.errors
      : [];

  // =========================================================
  // APPROVAL STATE
  // =========================================================

  const [
    approvalLoading,
    setApprovalLoading,
  ] = useState(false);

  const [
    approvalError,
    setApprovalError,
  ] = useState("");

  const [
    approvalResult,
    setApprovalResult,
  ] = useState(null);

  // =========================================================
  // API URL
  // =========================================================

  const API = (
    import.meta.env.VITE_BACKEND_URL ||
    ""
  ).replace(/\/$/, "");

  // =========================================================
  // GET ACCESS TOKEN
  // =========================================================

  const getAccessToken = () => {
    try {
      const userdata =
        JSON.parse(
          localStorage.getItem(
            "userdata"
          ) || "null"
        );

      return (
        userdata?.accessToken ||
        userdata?.access_token ||
        null
      );
    } catch (error) {
      console.error(
        "Failed to read authentication data:",
        error
      );

      return null;
    }
  };

  // =========================================================
  // APPROVAL API
  // =========================================================

  const handleApproval = async (
    decision
  ) => {
    // -------------------------------------------------------
    // Prevent duplicate requests
    // -------------------------------------------------------

    if (approvalLoading) {
      return;
    }

    // -------------------------------------------------------
    // Validate session
    // -------------------------------------------------------
    console.log("sessionId is ",sessionId)
    if (!sessionId) {
      
      setApprovalError(
        "Session ID is missing."
      );

      return;
    }

    // -------------------------------------------------------
    // Validate decision
    // -------------------------------------------------------

    if (
      decision !== "accept" &&
      decision !== "reject"
    ) {
      setApprovalError(
        "Invalid approval decision."
      );

      return;
    }

    try {
      setApprovalLoading(true);
      setApprovalError("");
      setApprovalResult(null);

      // =====================================================
      // AUTH TOKEN
      // =====================================================

      const token =
        getAccessToken();

      // =====================================================
      // REQUEST HEADERS
      // =====================================================

      const headers = {
        "Content-Type":
          "application/json",
      };

      if (token) {
        headers.Authorization =
          `Bearer ${token}`;
      }

      // =====================================================
      // API REQUEST
      // =====================================================

      const response =
        await axios.post(
          `${API}/api/v1/approval`,
          {
            user_id: userId,

            session_id:
              sessionId,

            decision:
              decision,
          },
          {
            headers: {
          "X-User-Id": userId,
           "X-User-Role": "user",
           },
          }
        );

      // =====================================================
      // AXIOS RESPONSE
      // =====================================================

      const data =
        response.data;

      console.log(
        "Approval API response:",
        data
      );

      // =====================================================
      // SAVE RESULT
      // =====================================================

      setApprovalResult(
        data
      );

      // =====================================================
      // NOTIFY PARENT
      // =====================================================

      if (
        typeof onApprovalComplete ===
        "function"
      ) {
        onApprovalComplete(
          data
        );
      }

    } catch (error) {
      console.error(
        "Approval API error:",
        error
      );

      // =====================================================
      // FASTAPI ERROR
      // =====================================================

      const backendMessage =
        error?.response?.data?.detail ||
        error?.response?.data?.message ||
        error?.message ||
        "Failed to process approval.";

      setApprovalError(
        typeof backendMessage ===
          "string"
          ? backendMessage
          : JSON.stringify(
              backendMessage
            )
      );

    } finally {
      setApprovalLoading(
        false
      );
    }
  };

  // =========================================================
  // CURRENT APPROVAL
  // =========================================================

  const currentApproval =
    approvalResult?.approval ||
    approval;

  // =========================================================
  // CURRENT STATUS
  // =========================================================

  const currentStatus =
    approvalResult?.status ||
    currentApproval?.status ||
    "pending";

  // =========================================================
  // USER MESSAGE
  // =========================================================

  if (isUser) {
    return (
      <div
        className="
          flex
          mb-4
          justify-end
        "
      >
        <div
          className="
            max-w-[80%]
            rounded-2xl
            rounded-br-sm
            bg-blue-600
            text-white
            px-4
            py-3
            shadow
            whitespace-pre-wrap
            break-words
          "
        >
          {userText}
        </div>
      </div>
    );
  }

  // =========================================================
  // BOT MESSAGE
  // =========================================================

  return (
    <div
      className="
        flex
        mb-4
        justify-start
      "
    >
      <div
        className="
          max-w-[90%]
          rounded-2xl
          rounded-bl-sm
          border
          bg-white
          px-4
          py-4
          shadow
          break-words
        "
      >

        {/* ===================================================
            WORKFLOW STATUS
        =================================================== */}

        {workflowStatus !==
          "unknown" && (
          <div
            className="
              mb-3
              text-xs
              text-gray-500
            "
          >
            Workflow status:{" "}
            <span
              className="
                font-medium
                capitalize
              "
            >
              {workflowStatus}
            </span>
          </div>
        )}

        {/* ===================================================
            ANSWER / REPORT
        =================================================== */}

        {answer.trim() && (
          <article
            className="
              prose
              prose-sm
              max-w-none

              prose-headings:font-bold
              prose-headings:text-gray-900

              prose-p:my-2
              prose-p:text-gray-700

              prose-ul:my-2
              prose-ol:my-2

              prose-li:my-1

              prose-table:w-full
              prose-table:border-collapse

              prose-th:border
              prose-th:border-gray-300
              prose-th:bg-gray-100
              prose-th:px-3
              prose-th:py-2

              prose-td:border
              prose-td:border-gray-300
              prose-td:px-3
              prose-td:py-2

              prose-pre:overflow-x-auto
              prose-code:break-words
            "
          >
            <ReactMarkdown
              remarkPlugins={[
                remarkGfm,
              ]}
            >
              {answer}
            </ReactMarkdown>
          </article>
        )}

        {/* ===================================================
            PLAN
        =================================================== */}

        {plan.length > 0 && (
          <details
            className="
              mt-5
              rounded-xl
              border
              border-blue-200
              bg-blue-50
              p-4
            "
          >
            <summary
              className="
                cursor-pointer
                font-semibold
                text-blue-800
              "
            >
              📋 Research Plan (
              {plan.length} tasks)
            </summary>

            <div
              className="
                mt-4
                space-y-3
              "
            >
              {plan.map(
                (
                  task,
                  index
                ) => (
                  <div
                    key={
                      task?.id ||
                      index
                    }
                    className="
                      rounded-lg
                      border
                      border-blue-100
                      bg-white
                      p-3
                    "
                  >
                    <div
                      className="
                        flex
                        items-start
                        gap-3
                      "
                    >
                      <span
                        className="
                          flex
                          h-7
                          w-7
                          shrink-0
                          items-center
                          justify-center
                          rounded-full
                          bg-blue-600
                          text-xs
                          font-bold
                          text-white
                        "
                      >
                        {task?.id ||
                          index + 1}
                      </span>

                      <div
                        className="
                          min-w-0
                        "
                      >
                        <p
                          className="
                            text-sm
                            font-medium
                            text-gray-800
                          "
                        >
                          {typeof task?.task ===
                          "string"
                            ? task.task
                            : "Task"}
                        </p>

                        {task?.agent && (
                          <p
                            className="
                              mt-1
                              text-xs
                              text-gray-500
                            "
                          >
                            Agent:{" "}
                            <span
                              className="
                                font-medium
                              "
                            >
                              {String(
                                task.agent
                              )}
                            </span>
                          </p>
                        )}

                        {task?.requires_tool !==
                          undefined && (
                          <p
                            className="
                              text-xs
                              text-gray-500
                            "
                          >
                            Tool required:{" "}
                            {task.requires_tool
                              ? "Yes"
                              : "No"}
                          </p>
                        )}

                        {Array.isArray(
                          task?.depends_on
                        ) && (
                          <p
                            className="
                              text-xs
                              text-gray-500
                            "
                          >
                            Dependencies:{" "}
                            {task.depends_on.length >
                            0
                              ? task.depends_on.join(
                                  ", "
                                )
                              : "None"}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                )
              )}
            </div>
          </details>
        )}

        {/* ===================================================
            SOURCES
        =================================================== */}

        {sources.length > 0 && (
          <details
            className="
              mt-5
              rounded-xl
              border
              border-gray-200
              bg-gray-50
              p-4
            "
            open
          >
            <summary
              className="
                cursor-pointer
                font-semibold
                text-gray-800
              "
            >
              🔗 Sources (
              {sources.length})
            </summary>

            <div
              className="
                mt-3
                space-y-2
              "
            >
              {sources.map(
                (
                  source,
                  index
                ) => {
                  const title =
                    typeof source?.title ===
                    "string"
                      ? source.title
                      : `Source ${
                          index + 1
                        }`;

                  const url =
                    typeof source?.url ===
                    "string"
                      ? source.url
                      : "";

                  return (
                    <div
                      key={`${url}-${index}`}
                      className="
                        rounded-lg
                        border
                        bg-white
                        p-3
                      "
                    >
                      <div
                        className="
                          text-sm
                          font-medium
                          text-gray-800
                        "
                      >
                        {index + 1}.{" "}

                        {url ? (
                          <a
                            href={url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="
                              text-blue-600
                              hover:underline
                            "
                          >
                            {title}
                          </a>
                        ) : (
                          title
                        )}
                      </div>

                      {url && (
                        <div
                          className="
                            mt-1
                            break-all
                            text-xs
                            text-gray-500
                          "
                        >
                          {url}
                        </div>
                      )}
                    </div>
                  );
                }
              )}
            </div>
          </details>
        )}

        {/* ===================================================
            ERRORS
        =================================================== */}

        {errors.length > 0 && (
          <div
            className="
              mt-4
              rounded-lg
              border
              border-red-300
              bg-red-50
              p-3
              text-sm
              text-red-700
            "
          >
            <div
              className="
                mb-2
                font-semibold
              "
            >
              ⚠️ Workflow Errors
            </div>

            {errors.map(
              (
                error,
                index
              ) => (
                <div
                  key={index}
                  className="mb-1"
                >
                  {typeof error ===
                  "string"
                    ? error
                    : JSON.stringify(
                        error
                      )}
                </div>
              )
            )}
          </div>
        )}

        {/* ===================================================
            APPROVAL CARD
        =================================================== */}

        {(approval ||
          approvalRequired) && (
          <div
            className={`
              mt-5
              rounded-xl
              border
              p-4

              ${
                currentStatus ===
                "pending"
                  ? "border-yellow-300 bg-yellow-50"
                  : currentStatus ===
                    "rejected"
                    ? "border-red-300 bg-red-50"
                    : currentStatus ===
                      "email_sent"
                      ? "border-green-300 bg-green-50"
                      : "border-gray-300 bg-gray-50"
              }
            `}
          >
            {/* =============================================
                APPROVAL HEADER
            ============================================= */}

            <div
              className={`
                mb-3
                font-semibold

                ${
                  currentStatus ===
                  "pending"
                    ? "text-yellow-800"
                    : currentStatus ===
                      "rejected"
                      ? "text-red-800"
                      : currentStatus ===
                        "email_sent"
                        ? "text-green-800"
                        : "text-gray-800"
                }
              `}
            >
              {currentStatus ===
              "pending"
                ? "⚠️ Approval Required"
                : currentStatus ===
                  "email_sent"
                  ? "✅ Email Sent"
                  : currentStatus ===
                    "rejected"
                    ? "❌ Email Rejected"
                    : "Approval Processed"}
            </div>

            {/* =============================================
                ACTION
            ============================================= */}

            {currentApproval?.action && (
              <div className="mb-2">
                <span className="font-medium">
                  Action:
                </span>

                <span className="ml-2">
                  {String(
                    currentApproval.action
                  )}
                </span>
              </div>
            )}
             {currentApproval?.payload
                                   && (
              <div className="mb-2 border-1 border-gray-300 p-2 rounded-lg bg-gray-100">
                <h1 className="text-lg font-bold mb-2">Email Draft</h1>
                <div className="mb-1">
                <span className="font-medium">
                  Recipient:
                </span>

                <span className="ml-2">
                  {String(
                    currentApproval.payload.recipient
                  )}
                </span>
                </div>
                <div className="mb-1">
                 <span className="font-medium">
                  Subject:
                </span>

                <span className="ml-2">
                  {String(
                    currentApproval.payload.subject
                  )}
                </span>
                </div>
                <div className="mb-1">
                 <span className="font-medium">
                  Body:
                </span>

                <span className="ml-2">
                  {String(
                    currentApproval.payload.body
                  )}
                </span>
                </div>
              </div>
            )}

            {/* =============================================
                REASON
            ============================================= */}

            {currentApproval?.reason && (
              <div className="mb-2">
                <span className="font-medium">
                  Reason:
                </span>

                <span className="ml-2">
                  {String(
                    currentApproval.reason
                  )}
                </span>
              </div>
            )}

            {/* =============================================
                STATUS
            ============================================= */}

            <div className="mb-3">
              <span className="font-medium">
                Status:
              </span>

              <span
                className="
                  ml-2
                  capitalize
                "
              >
                {String(
                  currentStatus
                )}
              </span>
            </div>

            {/* =============================================
                API RESPONSE
            ============================================= */}

            {approvalResult && (
              <div
                className="
                  mt-3
                  rounded-lg
                  border
                  border-black
                  bg-green-500
                  px-3
                  py-2
                  text-1xl
                  text-gray-800
                "
              >
                {approvalResult.message
                  ? String(
                      approvalResult.message
                    )
                  : currentStatus ===
                    "email_sent"
                    ? " ✅ Email sent successfully."
                    : currentStatus ===
                      "rejected"
                      ? "Email was rejected."
                      : "Approval processed successfully."}
              </div>
            )}

            {/* =============================================
                APPROVAL ERROR
            ============================================= */}

            {approvalError && (
              <div
                className="
                  mt-3
                  rounded-lg
                  border
                  border-red-300
                  bg-red-100
                  px-3
                  py-2
                  text-sm
                  text-red-700
                "
              >
                {approvalError}
              </div>
            )}

            {/* =============================================
                BUTTONS
            ============================================= */}

            {currentStatus ===
              "pending" && (
              <div
                className="
                  mt-4
                  flex
                  gap-3
                "
              >
                {/* APPROVE */}

                <button
                  type="button"
                  disabled={
                    approvalLoading
                  }
                  onClick={() =>
                    handleApproval(
                      "accept"
                    )
                  }
                  className="
                    flex-1
                    rounded-lg
                    bg-green-600
                    px-4
                    py-2
                    font-medium
                    text-white
                    transition
                    hover:bg-green-700
                    disabled:cursor-not-allowed
                    disabled:opacity-50
                  "
                >
                  {approvalLoading
                    ? "Processing..."
                    : "✓ Approve"}
                </button>

                {/* REJECT */}

                <button
                  type="button"
                  disabled={
                    approvalLoading
                  }
                  onClick={() =>
                    handleApproval(
                      "reject"
                    )
                  }
                  className="
                    flex-1
                    rounded-lg
                    bg-red-600
                    px-4
                    py-2
                    font-medium
                    text-white
                    transition
                    hover:bg-red-700
                    disabled:cursor-not-allowed
                    disabled:opacity-50
                  "
                >
                  {approvalLoading
                    ? "Processing..."
                    : "✕ Reject"}
                </button>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}

