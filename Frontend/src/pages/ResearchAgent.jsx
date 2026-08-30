
import {
  useState,
  useEffect,
  useCallback,
} from "react";

import Chat from "../components/Chat";
import Plan from "../components/Plan";
import AgentStatus from "../components/AgentStatus";
import Sources from "../components/Sources";
import Approval from "../components/Approval";
import Report from "../components/Report";

import {
  sendChat,
  decideApproval,
  getApproval,
} from "../services/api";


function ResearchAgent() {

  // ------------------------------------
  // Get authenticated user ID
  // ------------------------------------

  const getAuthenticatedUserId = () => {

    try {

      // --------------------------------
      // Read userdata
      // --------------------------------

      const userdata =
        localStorage.getItem("userdata");


      if (userdata) {

        const user =
          JSON.parse(userdata);


        // --------------------------------
        // Direct user ID
        // --------------------------------

        const directUserId =
          user?.userId ||
          user?.user_id ||
          user?.id ||
          user?._id;


        if (directUserId) {

          return String(
            directUserId
          );

        }


        // --------------------------------
        // Nested user ID
        // --------------------------------

        const nestedUserId =
          user?.user?.userId ||
          user?.user?.user_id ||
          user?.user?.id ||
          user?.user?._id;


        if (nestedUserId) {

          return String(
            nestedUserId
          );

        }

      }


      // --------------------------------
      // Check standalone localStorage
      // --------------------------------

      const standaloneUserId =
        localStorage.getItem("userId") ||
        localStorage.getItem("user_id");


      if (standaloneUserId) {

        return String(
          standaloneUserId
        );

      }


      // --------------------------------
      // Try to get user ID from JWT
      // --------------------------------

      let accessToken = null;


      if (userdata) {

        const user =
          JSON.parse(userdata);

        accessToken =
          user?.accessToken ||
          user?.access_token ||
          user?.token ||
          null;

      }


      // Check standalone token
      accessToken =
        accessToken ||
        localStorage.getItem("accessToken") ||
        localStorage.getItem("access_token") ||
        localStorage.getItem("token");


      if (accessToken) {

        const tokenParts =
          accessToken.split(".");


        if (tokenParts.length === 3) {

          try {

            const base64Payload =
              tokenParts[1]
                .replace(/-/g, "+")
                .replace(/_/g, "/");


            const payload =
              JSON.parse(
                atob(base64Payload)
              );


            const tokenUserId =
              payload?.userId ||
              payload?.user_id ||
              payload?.id ||
              payload?._id ||
              payload?.sub;


            if (tokenUserId) {

              return String(
                tokenUserId
              );

            }

          } catch (tokenError) {

            console.error(
              "Failed to decode access token:",
              tokenError
            );

          }

        }

      }


      return null;

    } catch (error) {

      console.error(
        "Failed to read authenticated user:",
        error
      );

      return null;

    }

  };


  // ------------------------------------
  // State
  // ------------------------------------

  const [userId, setUserId] =
    useState(null);

  const [sessionId, setSessionId] =
    useState("");

  const [result, setResult] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [approvalLoading, setApprovalLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  // ------------------------------------
  // Load authenticated user
  // ------------------------------------

  useEffect(() => {

    const authenticatedUserId =
      getAuthenticatedUserId();


    console.log(
      "Authenticated User ID:",
      authenticatedUserId
    );


    setUserId(
      authenticatedUserId
    );

  }, []);


  // ------------------------------------
  // Create / restore session
  // ------------------------------------

  useEffect(() => {

    const existingSession =
      localStorage.getItem(
        "research_session_id"
      );


    if (existingSession) {

      setSessionId(
        existingSession
      );

    } else {

      const newSession =
        crypto.randomUUID();


      localStorage.setItem(
        "research_session_id",
        newSession
      );


      setSessionId(
        newSession
      );

    }

  }, []);


  // ------------------------------------
  // Restore approval after refresh
  // ------------------------------------

  const restoreApproval =
    useCallback(async () => {

      if (
        !sessionId ||
        !userId
      ) {

        return;

      }


      try {

        const response =
          await getApproval(
            sessionId
          );


        const approval =
          response.data;


        if (
          approval &&
          approval.status !== "none"
        ) {

          setResult(
            (previous) => ({

              ...previous,

              approval,

              approval_required:
                approval.status ===
                "pending",

              status:
                approval.status ===
                "pending"
                  ? "awaiting_approval"
                  : previous?.status,

            })
          );

        }

      } catch (err) {

        console.log(
          "No existing approval:",
          err
        );

      }

    }, [
      sessionId,
      userId,
    ]);


  useEffect(() => {

    restoreApproval();

  }, [
    restoreApproval,
  ]);


  // ------------------------------------
  // Submit research request
  // ------------------------------------

  const handleSubmit = async ({
    message,
    recipient,
  }) => {

    setLoading(true);
    setError("");


    try {

      // --------------------------------
      // Re-read user ID before request
      // --------------------------------

      const currentUserId =
        getAuthenticatedUserId();


      console.log(
        "Current Authenticated User ID:",
        currentUserId
      );


      // --------------------------------
      // Validate user
      // --------------------------------

      if (!currentUserId) {

        setError(
          "Authenticated user ID not found. Please login again."
        );

        return;

      }


      // --------------------------------
      // Keep state synchronized
      // --------------------------------

      if (
        currentUserId !== userId
      ) {

        setUserId(
          currentUserId
        );

      }


      console.log(
        "Sending research request:",
        {
          userId:
            currentUserId,

          sessionId,

          message,

          recipient,
        }
      );


      // --------------------------------
      // Send API request
      // --------------------------------

      const response =
        await sendChat({

          userId:
            currentUserId,

          sessionId,

          message,

          recipient,

        });


      const data =
        response.data;


      console.log(
        "Research API Response:",
        data
      );


      // --------------------------------
      // Save session
      // --------------------------------

      if (
        data?.session_id
      ) {

        setSessionId(
          data.session_id
        );


        localStorage.setItem(
          "research_session_id",
          data.session_id
        );

      }


      // --------------------------------
      // Save result
      // --------------------------------

      setResult(
        data
      );


    } catch (err) {

      console.error(
        "Research error:",
        err
      );


      console.error(
        "Backend response:",
        err.response?.data
      );


      setError(
        err.response?.data?.detail ||
        err.message ||
        "Something went wrong."
      );


    } finally {

      setLoading(false);

    }

  };


  // ------------------------------------
  // Approval decision
  // ------------------------------------

  const handleApproval = async (
    approved,
    comment
  ) => {

    setApprovalLoading(true);
    setError("");


    try {

      const response =
        await decideApproval({

          sessionId,

          approved,

          comment,

        });


      const data =
        response.data;


      console.log(
        "Approval response:",
        data
      );


      setResult(
        (previous) => ({

          ...previous,

          status:
            data.status ||
            previous?.status,

          approval_required:
            false,

          approval: {

            ...previous?.approval,

            status:
              approved
                ? "approved"
                : "rejected",

            comment,

          },

          tool_result:
            data.tool_result ||
            previous?.tool_result,

        })
      );


    } catch (err) {

      console.error(
        "Approval error:",
        err
      );


      console.error(
        "Backend response:",
        err.response?.data
      );


      setError(
        err.response?.data?.detail ||
        err.message ||
        "Approval failed."
      );


    } finally {

      setApprovalLoading(false);

    }

  };


  // ------------------------------------
  // Start new session
  // ------------------------------------

  const startNewSession = () => {

    const newSession =
      crypto.randomUUID();


    localStorage.setItem(
      "research_session_id",
      newSession
    );


    setSessionId(
      newSession
    );


    setResult(null);

    setError("");

  };


  // ------------------------------------
  // Render
  // ------------------------------------

  return (

    <div className="page">

      {/* -------------------------------- */}
      {/* Header */}
      {/* -------------------------------- */}

      <header className="page-header">

        <div>

          <h1>
            AI Multi-Agent Research
          </h1>


          <p>
            Planning • Research • Analysis •
            Fact Checking • MCP • Memory •
            Human Approval
          </p>

        </div>


        <button
          className="secondary-button"
          onClick={startNewSession}
          disabled={
            loading ||
            approvalLoading
          }
        >
          + New Session
        </button>

      </header>


      {/* -------------------------------- */}
      {/* Session */}
      {/* -------------------------------- */}

      {sessionId && (

        <div className="session-info">

          <span>
            Session ID:
          </span>


          <code>
            {sessionId}
          </code>


          <button
            type="button"
            onClick={() =>
              navigator.clipboard.writeText(
                sessionId
              )
            }
          >
            Copy
          </button>

        </div>

      )}


      {/* -------------------------------- */}
      {/* Error */}
      {/* -------------------------------- */}

      {error && (

        <div className="error-box">

          <strong>
            Error:
          </strong>{" "}

          {error}

        </div>

      )}


      {/* -------------------------------- */}
      {/* Main Layout */}
      {/* -------------------------------- */}

      <div className="layout">

        <main>

          {/* -------------------------------- */}
          {/* Chat */}
          {/* -------------------------------- */}

          <Chat
            onSubmit={handleSubmit}
            loading={loading}
          />


          {/* -------------------------------- */}
          {/* Research Result */}
          {/* -------------------------------- */}

          {result && (

            <>

              {/* Plan */}

              <Plan
                plan={result.plan}
              />


              {/* Report */}

              <Report
                report={result.answer}
                status={result.status}
              />


              {/* Sources */}

              <Sources
                sources={result.sources}
              />


              {/* -------------------------------- */}
              {/* Tool Result */}
              {/* -------------------------------- */}

              {result.tool_result && (

                <div className="card">

                  <div className="card-header">

                    <h2>
                      Tool Result
                    </h2>

                  </div>


                  <pre className="tool-result">

                    {
                      typeof result.tool_result ===
                      "string"

                        ? result.tool_result

                        : JSON.stringify(
                            result.tool_result,
                            null,
                            2
                          )
                    }

                  </pre>

                </div>

              )}

            </>

          )}

        </main>


        {/* -------------------------------- */}
        {/* Sidebar */}
        {/* -------------------------------- */}

        <aside>

          <AgentStatus
            status={result?.status}
            plan={result?.plan}
          />


          <Approval
            approval={result?.approval}
            approvalRequired={
              result?.approval_required
            }
            onDecision={
              handleApproval
            }
            loading={
              approvalLoading
            }
          />

        </aside>

      </div>

    </div>

  );

}


export default ResearchAgent;

