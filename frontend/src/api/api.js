const API_URL = import.meta.env.VITE_API_URL;

export class ApiError extends Error {
  constructor(status, detail) {
    super(detail || `Request failed (${status})`);
    this.status = status; // 0 = could not reach the backend
    this.detail = detail;
  }
}

async function request(path, token, options = {}) {
  let response;

  try {
    response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: {
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        Authorization: `Bearer ${token}`,
      },
    });
  } catch (error) {
    console.error(`[api] ${path} unreachable:`, error);
    throw new ApiError(0, "Could not reach the backend");
  }

  let data = null;
  try {
    data = await response.json();
  } catch {
    // non-JSON body (e.g. a bare 500)
  }

  if (!response.ok) {
    console.error(`[api] ${path} -> ${response.status}`, data);
    throw new ApiError(
      response.status,
      typeof data?.detail === "string" ? data.detail : undefined
    );
  }

  return data;
}

// POST /api/meetings -> { meeting: { _id, status, ... } }
export async function createMeeting(token, meetingUrl) {
  const data = await request("/api/meetings", token, {
    method: "POST",
    body: JSON.stringify({ meeting_url: meetingUrl }),
  });
  return data.meeting;
}

// GET /api/meetings/{id}/status -> { meeting_id, status, ... }
export function getMeetingStatus(token, meetingId) {
  return request(`/api/meetings/${meetingId}/status`, token);
}

// The backend has no per-meeting endpoint, so list the user's items
// and keep the ones from this meeting that have not been reviewed.
export async function getMeetingTasks(token, meetingId) {
  const data = await request("/api/action-items", token);

  return data.action_items
    .filter((item) => item.meeting_id === meetingId && item.status == null)
    .reverse(); // backend returns newest first
}

// POST /api/action-items/review -> { approved, rejected, jira_created: [...] }
export function reviewActionItems(token, approved, rejected) {
  return request("/api/action-items/review", token, {
    method: "POST",
    body: JSON.stringify({ approved, rejected }),
  });
}
