
import axios from "axios";


// ------------------------------------
// Axios API instance
// ------------------------------------

const API = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL,
  headers: {
    "Content-Type": "application/json",
  },
});


// ------------------------------------
// Get authenticated user data
// ------------------------------------

const getUserData = () => {
  try {
    const userdata = localStorage.getItem("userdata");

    if (!userdata) {
      return null;
    }

    return JSON.parse(userdata);

  } catch (error) {
    console.error(
      "Failed to read userdata:",
      error
    );

    return null;
  }
};


// ------------------------------------
// Get user ID
// ------------------------------------

const getUserId = () => {
  const userdata = getUserData();

  if (!userdata) {
    return null;
  }

  return (
    userdata.userId ||
    userdata.user_id ||
    userdata.id ||
    userdata.user?.id ||
    userdata.user?.userId ||
    userdata.user?.user_id ||
    null
  );
};


// ------------------------------------
// Get access token
// ------------------------------------

const getAccessToken = () => {
  const userdata = getUserData();

  if (!userdata) {
    return null;
  }

  return (
    userdata.accessToken ||
    userdata.access_token ||
    null
  );
};


// ------------------------------------
// Authentication interceptor
// ------------------------------------

API.interceptors.request.use(
  (config) => {

    const accessToken =
      getAccessToken();

    const userId =
      getUserId();


    // --------------------------------
    // Access Token
    // --------------------------------

    if (accessToken) {
      config.headers.Authorization =
        `Bearer ${accessToken}`;
    }


    // --------------------------------
    // User ID
    // --------------------------------

    if (userId) {
      config.headers["X-User-Id"] =
        String(userId);
    }


    console.log(
      "API Request:",
      {
        url: config.url,
        method: config.method,
        userId: userId,
        hasToken: Boolean(accessToken),
      }
    );


    return config;

  },

  (error) => {
    return Promise.reject(error);
  }
);


// ------------------------------------
// Send research/chat request
// ------------------------------------

export const sendChat = ({
  userId,
  sessionId,
  message,
  recipient = null,
}) => {

  // Prefer explicitly supplied userId.
  // Otherwise get it from localStorage.
  const authenticatedUserId =
    userId || getUserId();


  if (!authenticatedUserId) {
    return Promise.reject(
      new Error(
        "User ID not found. Please login again."
      )
    );
  }


  return API.post(
    "/chat",
    {
      user_id: authenticatedUserId,
      session_id: sessionId,
      message,
      recipient,
    },
    {
      headers: {
        "X-User-Id":
          String(authenticatedUserId),
      },
    }
  );
};


// ------------------------------------
// Get approval status
// ------------------------------------

export const getApproval = (
  sessionId
) => {

  return API.get(
    `/approval/${sessionId}`
  );
};


// ------------------------------------
// Approve / Reject
// ------------------------------------

export const decideApproval = ({
  sessionId,
  approved,
  comment = "",
}) => {

  return API.post(
    `/approval/${sessionId}`,
    {
      approved,
      comment,
    }
  );
};


export default API;

