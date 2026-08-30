function AgentStatus({
  status,
  plan = [],
}) {

  const agents = [

    {
      name: "Planning Agent",
      key: "planning",
    },

    {
      name: "Research Agent",
      key: "researcher",
    },

    {
      name: "Analysis Agent",
      key: "analyst",
    },

    {
      name: "Fact Checker",
      key: "fact_checker",
    },

    {
      name: "Report Agent",
      key: "reporter",
    },

  ];


  const usedAgents =
    Array.isArray(plan)
      ? plan.map(
          (step) => step.agent
        )
      : [];


  const uniqueUsedAgents =
    [...new Set(usedAgents)];


  const completed =
    status === "completed";


  const failed =
    status === "failed";


  const awaitingApproval =
    status ===
    "awaiting_approval";


  const running =
    status === "started";


  const totalAgents =
    uniqueUsedAgents.length;


  const completedCount =
    completed
      ? totalAgents
      : 0;


  const progress =
    totalAgents === 0
      ? 0
      : Math.round(
          (completedCount /
            totalAgents) *
            100
        );


  return (

    <div className="card agent-status-card">

      <div className="card-header">

        <div>

          <h2>
            Agent Status
          </h2>

          <p>
            Multi-agent workflow execution
          </p>

        </div>


        {status && (

          <span
            className={
              `workflow-badge ${getStatusClass(
                status
              )}`
            }
          >
            {getStatusLabel(status)}
          </span>

        )}

      </div>


      {/* -------------------------------- */}
      {/* Progress */}
      {/* -------------------------------- */}

      {totalAgents > 0 && (

        <div className="agent-progress">

          <div className="progress-header">

            <span>
              Workflow Progress
            </span>

            <strong>
              {progress}%
            </strong>

          </div>


          <div className="progress-bar">

            <div
              className="progress-fill"
              style={{
                width:
                  `${progress}%`,
              }}
            />

          </div>

        </div>

      )}


      {/* -------------------------------- */}
      {/* Agents */}
      {/* -------------------------------- */}

      <div className="agent-list">

        {agents.map(
          (agent) => {

            const isUsed =
              uniqueUsedAgents.includes(
                agent.key
              );


            let state =
              "pending";


            if (failed && isUsed) {

              state =
                "failed";

            } else if (
              awaitingApproval &&
              isUsed
            ) {

              state =
                "waiting";

            } else if (
              completed &&
              isUsed
            ) {

              state =
                "completed";

            } else if (
              running &&
              isUsed
            ) {

              state =
                "active";

            }


            return (

              <div
                key={agent.key}
                className={
                  `agent-item agent-${state}`
                }
              >

                <div className="agent-icon">

                  {state ===
                    "completed" && "✓"}

                  {state ===
                    "active" && "●"}

                  {state ===
                    "waiting" && "⚠"}

                  {state ===
                    "failed" && "✕"}

                  {state ===
                    "pending" && "○"}

                </div>


                <div className="agent-info">

                  <strong>
                    {agent.name}
                  </strong>

                  <span>
                    {getAgentStateLabel(
                      state
                    )}
                  </span>

                </div>

              </div>

            );

          }
        )}

      </div>


      {/* -------------------------------- */}
      {/* Summary */}
      {/* -------------------------------- */}

      {totalAgents > 0 && (

        <div className="agent-summary">

          <span>
            {totalAgents} agents involved
          </span>

          <span>
            {plan.length} steps
          </span>

        </div>

      )}

    </div>

  );

}


function getStatusClass(status) {

  if (
    status === "completed"
  ) {
    return "status-completed";
  }

  if (
    status === "failed"
  ) {
    return "status-failed";
  }

  if (
    status === "awaiting_approval"
  ) {
    return "status-waiting";
  }

  return "status-running";

}


function getStatusLabel(status) {

  const labels = {

    completed:
      "✓ Completed",

    started:
      "● Running",

    awaiting_approval:
      "⚠ Waiting for Approval",

    failed:
      "✕ Failed",

  };

  return (
    labels[status] ||
    status
  );

}


function getAgentStateLabel(
  state
) {

  const labels = {

    completed:
      "Completed",

    active:
      "Working...",

    waiting:
      "Waiting for approval",

    failed:
      "Failed",

    pending:
      "Not used",

  };

  return (
    labels[state] ||
    state
  );

}


export default AgentStatus;