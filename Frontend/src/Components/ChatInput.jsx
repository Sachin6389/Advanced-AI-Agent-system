
import { useState } from "react";


export default function ChatInput({
  sendMessage,
  loading = false,
}) {

  const [message, setMessage] =
    useState("");


  // ============================================================
  // SEND MESSAGE
  // ============================================================

  function handleSend() {

    const cleanMessage =
      message.trim();


    // Do not send empty message
    if (!cleanMessage) {
      return;
    }


    // Do not send while loading
    if (loading) {
      return;
    }


    sendMessage(
      cleanMessage
    );

    setMessage("");
  }


  // ============================================================
  // KEYBOARD
  // ============================================================

  function handleKeyDown(event) {

    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {

      event.preventDefault();

      handleSend();
    }
  }


  // ============================================================
  // RENDER
  // ============================================================

  return (

    <div
      className="
        flex
        gap-3
        p-4
        bg-white
        border-t
      "
    >

      {/* ======================================================
          INPUT
      ====================================================== */}

      <input
        type="text"

        className="
          flex-1
          border
          border-gray-300
          rounded-xl
          px-4
          py-3
          outline-none
          focus:ring-2
          focus:ring-green-500
          focus:border-transparent
          disabled:bg-gray-100
          disabled:cursor-not-allowed
        "

        placeholder={
          loading
            ? "Agent is thinking..."
            : "Ask anything..."
        }

        value={message}

        disabled={loading}

        onChange={(event) =>
          setMessage(
            event.target.value
          )
        }

        onKeyDown={
          handleKeyDown
        }
      />


      {/* ======================================================
          SEND BUTTON
      ====================================================== */}

      <button
        type="button"

        onClick={handleSend}

        disabled={
          loading ||
          !message.trim()
        }

        className="
          px-6
          rounded-xl
          text-white
          font-medium
          transition
          bg-green-600
          hover:bg-green-700
          disabled:bg-gray-400
          disabled:cursor-not-allowed
        "
      >

        {loading
          ? "Sending..."
          : "Send"}

      </button>

    </div>

  );
}

