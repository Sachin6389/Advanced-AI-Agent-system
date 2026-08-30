function Sources({
  sources = [],
}) {

  if (
    !Array.isArray(sources) ||
    !sources.length
  ) {
    return null;
  }


  const extractUrl = (
    value
  ) => {

    if (!value) {
      return "";
    }


    const text =
      String(value).trim();


    // Markdown URL
    const markdownMatch =
      text.match(
        /\]\((https?:\/\/[^)]+)\)/
      );


    if (
      markdownMatch
    ) {

      return markdownMatch[1];

    }


    // Normal URL
    const urlMatch =
      text.match(
        /https?:\/\/[^\s)]+/
      );


    return (
      urlMatch?.[0] ||
      ""
    );

  };


  const getDomain = (
    url
  ) => {

    try {

      return new URL(
        url
      ).hostname.replace(
        "www.",
        ""
      );

    } catch {

      return "";

    }

  };


  const getFavicon = (
    url
  ) => {

    try {

      const domain =
        new URL(url)
          .origin;

      return `${domain}/favicon.ico`;

    } catch {

      return "";

    }

  };


  const copyUrl = async (
    url
  ) => {

    try {

      await navigator.clipboard
        .writeText(url);

    } catch (error) {

      console.error(
        "Copy failed:",
        error
      );

    }

  };


  return (

    <div className="card">

      <div className="card-header">

        <h2>
          Sources
        </h2>

        <p>
          Sources collected during research.
        </p>

      </div>


      <div className="sources-list">

        {sources.map(
          (source, index) => {

            const url =
              extractUrl(
                source?.url
              );


            const domain =
              getDomain(url);


            const favicon =
              getFavicon(url);


            return (

              <div
                className="source-item"
                key={
                  url ||
                  index
                }
              >

                <div className="source-number">
                  {index + 1}
                </div>


                <div className="source-icon">

                  {favicon && (

                    <img
                      src={favicon}
                      alt=""
                      onError={(e) => {
                        e.currentTarget.style.display =
                          "none";
                      }}
                    />

                  )}

                  {!favicon && "🔗"}

                </div>


                <div className="source-content">

                  {url ? (

                    <a
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="source-title"
                    >

                      {source?.title ||
                        domain ||
                        url}

                    </a>

                  ) : (

                    <span>
                      No URL available
                    </span>

                  )}


                  {domain && (

                    <div className="source-domain">
                      {domain}
                    </div>

                  )}


                  {url && (

                    <div className="source-actions">

                      <button
                        type="button"
                        onClick={() =>
                          copyUrl(
                            url
                          )
                        }
                      >
                        Copy
                      </button>


                      <a
                        href={url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Open ↗
                      </a>

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


export default Sources;