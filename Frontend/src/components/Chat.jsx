
import {
  useState,
} from "react";


function Chat({
  onSubmit,
  loading,
}) {

  const [message, setMessage] =
    useState("");

  const [recipient, setRecipient] =
    useState("");


  // ------------------------------------
  // Submit research request
  // ------------------------------------

  const handleSubmit = async (e) => {

    e.preventDefault();


    const trimmedMessage =
      message.trim();

    const trimmedRecipient =
      recipient.trim();


    // --------------------------------
    // Validate message
    // --------------------------------

    if (!trimmedMessage) {
      return;
    }


    // --------------------------------
    // Prevent duplicate request
    // --------------------------------

    if (loading) {
      return;
    }


    try {

      await onSubmit({

        message:
          trimmedMessage,

        recipient:
          trimmedRecipient || null,

      });


      // --------------------------------
      // Clear input only after submit
      // --------------------------------

      setMessage("");

      setRecipient("");


    } catch (error) {

      console.error(
        "Chat submission error:",
        error
      );

    }

  };


  // ------------------------------------
  // Quick prompt
  // ------------------------------------

  const usePrompt = (prompt) => {

    if (loading) {
      return;
    }

    setMessage(prompt);

  };


  return (

    <div className="card">

      {/* -------------------------------- */}
      {/* Header */}
      {/* -------------------------------- */}

      <div className="card-header">

        <h2>
          Research Request
        </h2>

        <p>
          Ask the AI agent to research,
          analyze, fact-check and generate
          a report.
        </p>

      </div>


      {/* -------------------------------- */}
      {/* Quick Prompts */}
      {/* -------------------------------- */}

      <div className="quick-prompts">

        <button
          type="button"
          onClick={() =>
            usePrompt(
              "Research the latest AI agent frameworks, compare their architecture, capabilities, advantages, disadvantages and use cases, fact-check the findings and create a detailed report."
            )
          }
          disabled={loading}
        >
          🔬 Compare AI Frameworks
        </button>


        <button
          type="button"
          onClick={() =>
            usePrompt(
              "Research the latest developments in Generative AI and summarize the major trends, technologies and business applications."
            )
          }
          disabled={loading}
        >
          🤖 GenAI Trends
        </button>


        <button
          type="button"
          onClick={() =>
            usePrompt(
              "Research this topic, verify important claims using reliable sources and create a structured report with citations."
            )
          }
          disabled={loading}
        >
          ✅ Fact Check
        </button>

      </div>


      {/* -------------------------------- */}
      {/* Research Form */}
      {/* -------------------------------- */}

      <form
        onSubmit={handleSubmit}
        className="chat-form"
      >

        {/* -------------------------------- */}
        {/* Research Message */}
        {/* -------------------------------- */}

        <textarea
          value={message}
          onChange={(e) =>
            setMessage(e.target.value)
          }
          placeholder={
            "Example: Research the latest AI " +
            "agent frameworks, compare them, " +
            "fact-check the results and create " +
            "a report."
          }
          rows={8}
          disabled={loading}
        />


        {/* -------------------------------- */}
        {/* Recipient Email */}
        {/* -------------------------------- */}

        <input
          type="email"
          value={recipient}
          onChange={(e) =>
            setRecipient(e.target.value)
          }
          placeholder={
            "Recipient email — required only when requesting email delivery"
          }
          disabled={loading}
        />


        {/* -------------------------------- */}
        {/* Footer */}
        {/* -------------------------------- */}

        <div className="chat-footer">

          <small>
            💡 Tip: Say "send email" or
            "publish report" to trigger
            human approval.
          </small>


          {/* -------------------------------- */}
          {/* Submit Button */}
          {/* -------------------------------- */}

          <button
            type="submit"
            disabled={
              loading ||
              !message.trim()
            }
            className="primary-button"
          >

            {loading
              ? "🤖 Agents Working..."
              : "🚀 Start Research"}

          </button>

        </div>

      </form>

    </div>

  );

}


export default Chat;

