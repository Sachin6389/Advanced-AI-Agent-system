function Plan({
  plan = [],
}) {

  if (
    !Array.isArray(plan) ||
    !plan.length
  ) {
    return null;
  }


  return (

    <div className="card">

      <div className="card-header">

        <h2>
          Execution Plan
        </h2>

        <p>
          Plan created by the Planning Agent.
        </p>

      </div>


      <div className="plan-list">

        {plan.map(
          (step, index) => {

            const stepNumber =
              step.id ??
              index + 1;


            const dependencies =
              Array.isArray(
                step.depends_on
              )
                ? step.depends_on
                : [];


            return (

              <div
                key={stepNumber}
                className="plan-item"
              >

                {/* -------------------------------- */}
                {/* Number */}
                {/* -------------------------------- */}

                <div className="plan-number">

                  {stepNumber}

                </div>


                <div className="plan-content">

                  {/* -------------------------------- */}
                  {/* Agent */}
                  {/* -------------------------------- */}

                  <div className="plan-agent">

                    <strong>

                      {formatAgentName(
                        step.agent
                      )}

                    </strong>


                    {step.requires_tool && (

                      <span className="tool-badge">
                        🔧 Tool
                      </span>

                    )}

                  </div>


                  {/* -------------------------------- */}
                  {/* Task */}
                  {/* -------------------------------- */}

                  <p>
                    {step.task ||
                      "No task description"}
                  </p>


                  {/* -------------------------------- */}
                  {/* Dependencies */}
                  {/* -------------------------------- */}

                  {dependencies.length >
                    0 && (

                    <div className="dependencies">

                      <span>
                        Depends on:
                      </span>

                      {dependencies.map(
                        (dependency) => (

                          <span
                            key={
                              dependency
                            }
                            className="dependency-badge"
                          >
                            Step{" "}
                            {dependency}
                          </span>

                        )
                      )}

                    </div>

                  )}


                  {/* -------------------------------- */}
                  {/* Agent key */}
                  {/* -------------------------------- */}

                  {step.agent && (

                    <div className="agent-key">

                      Agent:
                      {" "}
                      <code>
                        {step.agent}
                      </code>

                    </div>

                  )}

                </div>

              </div>

            );

          }
        )}

      </div>

    </div>

  );

}


function formatAgentName(
  agent
) {

  if (!agent) {
    return "Unknown Agent";
  }


  const names = {

    planning:
      "Planning Agent",

    researcher:
      "Research Agent",

    analyst:
      "Analysis Agent",

    fact_checker:
      "Fact Checker",

    reporter:
      "Report Agent",

  };


  return (
    names[agent] ||
    agent
      .replaceAll(
        "_",
        " "
      )
      .replace(
        /\b\w/g,
        (char) =>
          char.toUpperCase()
      )
  );

}


export default Plan;