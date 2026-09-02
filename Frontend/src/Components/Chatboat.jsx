
import { useState, useEffect, useRef } from "react";
import axios from "axios";

import Message from "./Message";
import ChatInput from "./ChatInput";


function Chatboat() {

  // ============================================================
  // API
  // ============================================================

  const API = (
    import.meta.env.VITE_BACKEND_URL || ""
  ).replace(/\/$/, "");


  const [userId] = useState(() => {

    const STORAGE_KEY = "medv_user_id";

    // Check whether a user ID already exists
    const existingUserId =
      localStorage.getItem(STORAGE_KEY);

    if (existingUserId) {
      return existingUserId;
    }

    // Generate a new permanent user ID
    const newUserId =
      `user-${crypto.randomUUID()}`;

    // Save permanently in browser localStorage
    localStorage.setItem(
      STORAGE_KEY,
      newUserId
    );

    return newUserId;
  });


  const [sessionId] = useState(() => {

    const STORAGE_KEY = "medv_session_id";

    const existingSession =
      localStorage.getItem(STORAGE_KEY);

    if (existingSession) {
      return existingSession;
    }

    const newSessionId =
      `session-${crypto.randomUUID()}`;

    localStorage.setItem(
      STORAGE_KEY,
      newSessionId
    );

    return newSessionId;
  });


  // ============================================================
  // MESSAGES
  // ============================================================

  const [messages, setMessages] =
    useState([
      {
        sender: "bot",
        text:
          "👋 Hello! I'm your Advanced Research Agent. How can I help you today?",
      },
    ]);


  // ============================================================
  // LOADING
  // ============================================================

  const [loading, setLoading] =
    useState(false);


  // ============================================================
  // APPROVAL
  // ============================================================

  const [approval, setApproval] =
    useState(null);


  // ============================================================
  // SCROLL
  // ============================================================

  const bottomRef =
    useRef(null);


  useEffect(() => {

    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });

  }, [messages]);


  // ============================================================
  // SEND MESSAGE
  // ============================================================

  async function sendMessage(text) {

    const cleanText =
      text?.trim();


    // Do not send empty messages
    if (!cleanText || loading) {
      return;
    }


    // ----------------------------------------------------------
    // Add user message to UI
    // ----------------------------------------------------------

    setMessages((prev) => [
      ...prev,
      {
        sender: "user",
        text: cleanText,
      },
    ]);


    // Start loading
    setLoading(true);


    try {

      // --------------------------------------------------------
      // SEND REQUEST TO BACKEND
      // --------------------------------------------------------

      const response =
        await axios.post(
          `${API}/api/v1/chat`,
          {
            // Permanent user ID
            user_id: userId,

            // Current conversation ID
            session_id: sessionId,

            // User message
            message: cleanText,
          },
          {
            headers: {
              "Content-Type": "application/json",
            },

            timeout: 120000,
          }
        );


      const data =
        response.data;


      console.log(
        "User ID:",
        userId
      );

      console.log(
        "Session ID:",
        sessionId
      );

      console.log(
        "Chat response:",
        data
      );


      // --------------------------------------------------------
      // APPROVAL REQUIRED
      // --------------------------------------------------------

      if (
        data.approval_required === true &&
        data.approval
      ) {

        setApproval(
          data.approval
        );


        setMessages((prev) => [
          ...prev,
          {
            sender: "bot",

            text:
              "⚠️ Human approval is required for this action.",

            approval:
              data,
          },
        ]);


        return;
      }


      // --------------------------------------------------------
      // NORMAL ANSWER
      // --------------------------------------------------------

      if (data.answer) {

        setMessages((prev) => [
          ...prev,
          {
            sender: "bot",
            text: data,
          },
        ]);

      }


      // --------------------------------------------------------
      // WORKFLOW ERRORS
      // --------------------------------------------------------

      if (
        Array.isArray(data.errors) &&
        data.errors.length > 0
      ) {

        setMessages((prev) => [
          ...prev,
          {
            sender: "bot",
            text:
              `⚠️ ${
                data.errors[
                  data.errors.length - 1
                ]
              }`,
          },
        ]);

      }

    } catch (error) {

      // --------------------------------------------------------
      // API ERROR
      // --------------------------------------------------------

      console.error(
        "Chat API error:",
        error
      );


      let errorMessage =
        "❌ Unable to connect to server.";


      // FastAPI HTTPException response
      if (
        error.response?.data?.detail
      ) {

        errorMessage =
          `❌ ${error.response.data.detail}`;

      }


      // Network error
      else if (
        error.request &&
        !error.response
      ) {

        errorMessage =
          "❌ Backend server is not reachable.";

      }


      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: errorMessage,
        },
      ]);

    } finally {

      // Stop loading
      setLoading(false);

    }
  }


  // ============================================================
  // RENDER
  // ============================================================

  return (

    <div
      className="
        bg-white
        shadow-2xl
        rounded-2xl
        w-full
        max-w-3xl
        overflow-hidden
      "
    >

      {/* ======================================================
          HEADER
      ====================================================== */}

      <div
        className="
          bg-blue-900
          text-white
          text-center
          py-5
          text-2xl
          font-bold
        "
      >
        Research Agent
      </div>


      {/* ======================================================
          CHAT AREA
      ====================================================== */}

      <div
        className="
          h-[500px]
          w-full
          overflow-y-auto
          p-6
          bg-gray-50
        "
      >

        {messages.map(
          (message, index) => (

            <Message
              key={index}
              message={message}
              userId={userId}
            />

          )
        )}


        {/* ====================================================
            LOADING
        ==================================================== */}

        {loading && (

          <Message
            message={{
              sender: "bot",
              text: "🤔 Thinking...",
            }}
          />

        )}


        {/* Scroll target */}

        <div
          ref={bottomRef}
        />

      </div>


      {/* ======================================================
          INPUT
      ====================================================== */}

      <ChatInput
        sendMessage={sendMessage}
        loading={loading}
      />

    </div>

  );
}


export default Chatboat;

