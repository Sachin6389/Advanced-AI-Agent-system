import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";


function Report({
  report,
  status,
}) {

  if (!report) {
    return null;
  }


  return (

    <div className="card report-card">

      <div className="card-header">

        <div>

          <h2>
            Generated Report
          </h2>

          <p>
            AI-generated research report
          </p>

        </div>


        {status && (

          <span
            className={
              `report-status status-${status}`
            }
          >
            {formatStatus(status)}
          </span>

        )}

      </div>


      <div className="report-content">

        <ReactMarkdown
          remarkPlugins={[
            remarkGfm,
          ]}
          rehypePlugins={[
            rehypeHighlight,
          ]}
          components={{

            a: ({
              children,
              href,
              ...props
            }) => (

              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                {...props}
              >
                {children}
              </a>

            ),

            table: ({
              children,
            }) => (

              <div className="markdown-table-wrapper">

                <table>
                  {children}
                </table>

              </div>

            ),

            code: ({
              inline,
              className,
              children,
              ...props
            }) => {

              return inline ? (

                <code
                  className="inline-code"
                  {...props}
                >
                  {children}
                </code>

              ) : (

                <pre className="code-block">

                  <code
                    className={
                      className || ""
                    }
                    {...props}
                  >
                    {children}
                  </code>

                </pre>

              );

            },

          }}
        >
          {report}
        </ReactMarkdown>

      </div>

    </div>

  );

}


function formatStatus(status) {

  const names = {

    completed:
      "✓ Completed",

    started:
      "● Running",

    awaiting_approval:
      "⚠ Approval Required",

    failed:
      "✕ Failed",

  };

  return (
    names[status] ||
    status
  );

}


export default Report;