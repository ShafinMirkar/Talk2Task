# Talk2Task Frontend Implementation Prompt

## 1. Project Overview

You are working on the frontend of **Talk2Task**, an AI meeting-to-task application.

The core idea:

> Talk2Task turns meeting discussions into actionable tasks, so nothing important gets forgotten.

A typical meeting might contain a statement such as:

> “Shafin will fix the login issue by Friday.”

Normally, someone has to:
1. Remember the commitment
2. Write it down
3. Create a Jira ticket
4. Assign it to the correct person
5. Set the deadline

Talk2Task automates this process:

```text
Meeting
   ↓
Vexa bot joins
   ↓
Meeting transcript
   ↓
Gemini analyzes transcript
   ↓
Action items / Tasks
   ↓
Human approves or rejects
   ↓
Approved tasks
   ↓
Jira via Atlassian MCP
````

Your job is to build the **frontend UI and frontend interaction flow** for this existing backend.

---

# 2. VERY IMPORTANT: Work With the Existing Backend

Do NOT redesign or replace the backend.

Do NOT introduce a new backend architecture.

Do NOT add unnecessary state-management systems, WebSockets, Redux, Zustand, React Query, etc. unless the existing project already uses them or they are genuinely necessary.

First inspect the existing repository and understand:

- existing frontend structure
- existing backend API
- existing authentication
- existing routing
- existing environment variables
- existing components
- existing API calls
- existing CSS setup
- existing dependencies

Reuse what already exists.

The backend is already functional.

The frontend should be a client of the existing backend.

---

# 3. Existing Frontend Stack

The frontend currently uses:

- React
- Vite
- JavaScript / JSX
- Clerk authentication
- React Router
- CSS

Existing frontend environment:

```env
VITE_CLERK_PUBLISHABLE_KEY=...
VITE_API_URL=http://localhost:8000
```

The backend runs on:

```text
http://localhost:8000
```

The frontend normally runs on:

```text
http://localhost:5173
```

Use:

```js
import.meta.env.VITE_API_URL
```

for backend API requests.

Do not hardcode `http://localhost:8000` throughout the application.

---

# 4. Authentication

The application already uses Clerk.

The frontend has:

```jsx
import { ClerkProvider } from "@clerk/react";
```

and authentication utilities such as:

```jsx
useAuth()
UserButton
Show
```

The backend expects the Clerk session token in:

```http
Authorization: Bearer <token>
```

For authenticated requests, use:

```js
const { getToken } = useAuth();

const token = await getToken();

fetch(`${import.meta.env.VITE_API_URL}/...`, {
  headers: {
    Authorization: `Bearer ${token}`,
  },
});
```

Do NOT create a separate authentication system.

Do NOT store Clerk secrets in the frontend.

The frontend only uses:

```env
VITE_CLERK_PUBLISHABLE_KEY
```

The backend handles secret keys.

---

# 5. Product Flow

The complete frontend experience should follow this flow.

## Initial state

The user sees the landing page.

It should communicate:

# Talk2Task

### turns meeting discussions into actionable tasks, so nothing important gets forgotten

Description:

> For example, after a meeting someone might say, “Shafin will fix the login issue by Friday.” Normally, someone has to remember that, write it down, create a Jira ticket, assign it, and set the deadline.
>
> Talk2Task automates that whole process: it listens to the meeting → understands the commitments → turns them into tasks → lets you approve them → creates the Jira tickets.

Then show:

```text
[ Meeting URL input ]

[ Start Meeting ]
```

The user pastes a Google Meet / Teams meeting URL.

---

# 6. Main Application State Machine

The frontend should behave like a simple state machine.

Conceptually:

```text
LANDING
   ↓
MEETING_STARTED
   ↓
BOT_ACTIVE
   ↓
ANALYZING
   ↓
TASK_REVIEW
   ↓
JIRA_PROCESSING
   ↓
LANDING
```

Do not over-engineer this.

Simple React state is sufficient unless the existing project already has another pattern.

---

# 7. State 1: Landing Page

Initial state:

```text
Talk2Task

turns meeting discussions into actionable tasks,
so nothing important gets forgotten

[ explanation ]

[ Paste meeting URL ]

[ Start Meeting ]
```

The landing page should be minimal.

No dashboard clutter.

No unnecessary cards.

No excessive gradients.

No illustrations unless absolutely necessary.

---

# 8. State 2: After Clicking Start Meeting

When the user submits the meeting URL:

```http
POST /api/meetings
```

Request:

```json
{
  "meeting_url": "https://meet.google.com/..."
}
```

The backend may also support:

```json
{
  "meeting_url": "...",
  "passcode": "..."
}
```

but the current UI only needs the meeting URL unless the existing backend requires otherwise.

The request must include:

```http
Authorization: Bearer <clerk_token>
Content-Type: application/json
```

Example:

```js
const response = await fetch(
  `${import.meta.env.VITE_API_URL}/api/meetings`,
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      meeting_url,
    }),
  }
);
```

The backend starts the Vexa bot.

The response contains information similar to:

```json
{
  "id": "...",
  "platform": "google_meet",
  "native_meeting_id": "dwe-kegt-zub",
  "status": "requested"
}
```

The important value for the frontend is the returned application/database meeting ID:

```text
meeting_id
```

Save this in React state.

Do NOT expose Vexa API keys to the frontend.

---

# 9. State 2 UI

Immediately after successfully starting the meeting:

Show a simple state containing ONLY the relevant text:

> **admit the bot in the meet**

Do not show a giant dashboard.

Do not show technical Vexa information.

Do not show the Vexa meeting ID.

Do not show API details.

The user should understand:

> I need to go to the meeting and admit the bot.

---

# 10. Checking Meeting Status

The frontend can poll:

```http
GET /api/meetings/{meeting_id}/status
```

Authenticated request:

```http
Authorization: Bearer <clerk_token>
```

Example:

```js
const response = await fetch(
  `${API_URL}/api/meetings/${meetingId}/status`,
  {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }
);
```

The backend returns information similar to:

```json
{
  "meeting_id": "...",
  "status": "active",
  "completion_reason": null,
  "start_time": "...",
  "end_time": null
}
```

Possible Vexa lifecycle statuses include:

```text
requested
joining
awaiting_admission
needs_help
active
stopping
completed
failed
```

The frontend does NOT need to display every technical state.

Map them to user-facing states.

---

# 11. State: Bot Joining / Waiting For Admission

For statuses such as:

```text
requested
joining
awaiting_admission
```

show:

> **admit the bot in the meet**

This should remain simple.

---

# 12. State: Bot Is Active

When:

```json
{
  "status": "active"
}
```

show ONLY:

> **bot is listening in the meet**

The user does not need to see technical status information.

The frontend should continue polling the meeting status.

Use a reasonable polling interval.

Do not poll every few milliseconds.

Something around 2–5 seconds is sufficient.

Make sure polling is cleaned up when the component unmounts or the state changes.

---

# 13. State: Meeting Completed / AI Processing

When the backend reports:

```text
completed
```

the backend webhook processing is responsible for:

```text
Vexa meeting completed
       ↓
fetch transcript
       ↓
fetch Jira users
       ↓
Gemini analyzes transcript
       ↓
action items generated
       ↓
action items saved to MongoDB
       ↓
meeting becomes processed
```

During this period the frontend should show:

> **AI is analyzing the transcript**

And underneath / around it use a subtle changing animation:

```text
creating action-items
creating action-items.
creating action-items..
creating action-items...
```

Cycle through those states.

Do not make this a complicated animation.

Keep it minimal.

The backend's `meeting.status` should eventually become:

```text
processed
```

At that point, the frontend should fetch the generated tasks.

---

# 14. IMPORTANT: Do Not Assume Gemini Output Exists in Frontend

Gemini runs on the backend.

The frontend does NOT call Gemini.

The frontend does NOT call Vexa directly.

The frontend does NOT call Jira MCP directly.

Architecture:

```text
Frontend
   ↓
Talk2Task Backend
   ↓
Vexa / Gemini / Jira MCP
```

The frontend communicates only with the Talk2Task backend.

---

# 15. Action Items / Tasks

Once the meeting has been processed, display the action items.

In the UI call them:

# Tasks

Do NOT use "Action Items" as the primary user-facing terminology unless needed.

Each task should show:

```text
Fix the login API

Alice Watson

Due: Friday
```

or:

```text
Fix the login API

Alice Watson

No deadline mentioned
```

Each task has:

```text
[ Approve ] [ Reject ]
```

---

# 16. Task Data

Backend action items conceptually look like:

```json
{
  "id": "...",
  "task": "Fix the login API",
  "assignee": "Alice Watson",
  "due_date": "2026-10-02",
  "status": null
}
```

Possible values:

```text
assignee = null
due_date = null
```

The frontend must gracefully handle these.

For example:

```text
Fix the login API

Unassigned

No deadline mentioned
```

Do not render:

```text
null
undefined
N/A
```

unless that is specifically part of the design.

---

# 17. Getting Tasks

The frontend needs the backend action-item GET endpoint.

Inspect the existing backend for the exact route.

It should conceptually be:

```http
GET /api/action-items/{meeting_id}
```

or whatever equivalent GET endpoint already exists.

DO NOT invent a different endpoint if one already exists.

Use the existing backend implementation.

The request must include:

```http
Authorization: Bearer <clerk_token>
```

The response should be mapped into the task UI.

If the backend endpoint does not currently exist, create the smallest frontend-compatible backend endpoint necessary, but only after confirming that it is actually missing.

Do not redesign the action-item backend.

---

# 18. Approve / Reject Interaction

The user reviews all tasks.

Each task can be:

```text
Approved
```

or:

```text
Rejected
```

Do not immediately create a Jira issue when the user clicks Approve.

Approval is a local review decision.

For example:

```text
Task 1   [✓ Approved]
Task 2   [✕ Rejected]
Task 3   [✓ Approved]
```

The user should be able to review the complete list before anything is sent to Jira.

---

# 19. Review Submission

Once ALL tasks have either been approved or rejected, submit the entire review in one batch.

Backend endpoint:

```http
POST /api/action-items/review
```

Request:

```json
{
  "approved": [
    "action-item-id-1",
    "action-item-id-3"
  ],
  "rejected": [
    "action-item-id-2"
  ]
}
```

Authenticated request:

```http
Authorization: Bearer <clerk_token>
Content-Type: application/json
```

The backend then:

```text
approved tasks
      ↓
Jira MCP
      ↓
create Jira issue
      ↓
assign Jira user
      ↓
transition issue to To Do
```

The frontend should NOT call Jira.

---

# 20. Do Not Allow Partial Review Submission

The "Submit" / final review action should only become available when every task has been reviewed.

For example:

```text
Task 1 → Approved
Task 2 → Rejected
Task 3 → Approved

All reviewed ✓
```

Then:

```text
[ Continue ]
```

If one task remains:

```text
Task 1 → Approved
Task 2 → Not reviewed
Task 3 → Rejected
```

do not submit yet.

The UI should make it obvious that the user still needs to review the remaining task.

---

# 21. Jira Processing State

After the review is submitted, the frontend should enter a short processing state.

For example:

> **creating Jira tasks**

or another minimal equivalent.

The backend response contains the Jira-created results.

Example:

```json
{
  "approved": 2,
  "rejected": 1,
  "jira_created": 2,
  "jira_results": [
    {
      "issue_key": "KAN-25",
      "task": "Fix the login API",
      "assignee": "Alice Watson"
    }
  ]
}
```

The frontend should use this response to confirm Jira creation.

---

# 22. Sidebar Notification

When each Jira task is successfully created, show a sidebar notification / toast.

Example:

```text
┌──────────────────────────────┐
│ Jira task created            │
│                              │
│ KAN-25                       │
│ Fix the login API            │
└──────────────────────────────┘
```

If multiple tasks are created:

```text
KAN-25 created in Jira
KAN-26 created in Jira
KAN-27 created in Jira
```

The notification should appear only after backend confirmation.

Do NOT show:

> Jira task created

before the backend confirms it.

The frontend must treat the backend response as the source of truth.

---

# 23. Return to Landing Page

After all approved tasks have been processed and Jira creation has been confirmed:

Return the user to the landing page.

The user should be able to start another meeting.

Do not leave them stuck on the task review screen.

The sidebar notifications can remain visible briefly while returning to the landing state.

---

# 24. Complete Frontend State Flow

Implement this exact conceptual flow:

```text
                    LANDING
                       │
                       │ submit URL
                       ▼
              STARTING MEETING
                       │
                       ▼
             ADMIT THE BOT IN MEET
                       │
                       │ status = active
                       ▼
            BOT IS LISTENING IN MEET
                       │
                       │ status = completed
                       ▼
             AI IS ANALYZING
                       │
                       │ status = processed
                       ▼
                  TASKS
                       │
             ┌─────────┴─────────┐
             │                   │
          APPROVE              REJECT
             │                   │
             └─────────┬─────────┘
                       │
                       │ all reviewed
                       ▼
               SUBMIT REVIEW
                       │
                       ▼
              CREATING JIRA TASKS
                       │
                       ▼
                JIRA CONFIRMED
                       │
                       ▼
                  LANDING
```

---

# 25. Error Handling

Implement basic error handling.

Do not create elaborate error infrastructure.

Handle at least:

## Invalid meeting URL

Backend may return:

```http
400
```

Show a clear message near the input.

Example:

```text
Enter a valid Google Meet or Teams URL.
```

---

## Unauthorized request

If backend returns:

```http
401
```

handle the authentication state appropriately.

Do not expose backend stack traces.

---

## Backend failure

If starting a meeting fails:

```text
Couldn't start the meeting.
Please try again.
```

Allow the user to retry.

---

## Meeting failed

If status becomes:

```text
failed
```

show a simple error state:

```text
We couldn't connect to the meeting.

[ Back ]
```

Do not expose Vexa's raw technical failure information to the user.

Log useful information to the browser console during development.

---

## Task loading failure

If action items cannot be retrieved:

```text
Couldn't load tasks.

[ Try again ]
```

---

## Jira failure

If review submission fails:

Do NOT return to the landing page.

Keep the reviewed tasks/state available if possible.

Show:

```text
We couldn't create the Jira tasks.
Please try again.
```

Do not falsely tell the user that Jira tasks were created.

---

# 26. Design Requirements

The design is intentionally extremely minimal.

## Background

Use an:

```text
off-white / cream
```

background.

Something around:

```css
#F7F3EA
```

is acceptable, but choose the final shade carefully.

Avoid pure white as the dominant background.

---

# 27. Typography

Use:

# Fraunces

This is the primary and defining visual element.

Load it properly, preferably using the existing project setup or Google Fonts if appropriate.

Use Fraunces throughout the application unless there is a strong technical reason not to.

The design should feel typographic rather than UI-heavy.

---

# 28. Overall Visual Direction

Minimal.

Think:

```text
cream background
+
Fraunces
+
large typography
+
simple inputs
+
simple buttons
+
lots of breathing room
```

Do NOT add:

- gradients
- glassmorphism
- excessive shadows
- neon colors
- generic SaaS dashboard styling
- excessive cards
- complicated illustrations
- unnecessary icons everywhere
- huge navigation bars
- sidebars containing unnecessary information
- analytics dashboards
- decorative blobs
- excessive animations

The UI should feel like a focused product, not an admin panel.

---

# 29. Landing Page Layout

Use a centered, spacious composition.

Something conceptually like:

```text
                         Talk2Task

            turns meeting discussions into
             actionable tasks, so nothing
                 important gets forgotten


       For example, after a meeting someone might
       say, “Shafin will fix the login issue by Friday.”
       Normally, someone has to remember that, write it
       down, create a Jira ticket, assign it, and set
       the deadline.

       Talk2Task automates that whole process:
       it listens to the meeting → understands the
       commitments → turns them into tasks → lets
       you approve them → creates the Jira tickets.


             ┌──────────────────────────────┐
             │ Paste meeting URL            │
             └──────────────────────────────┘

                    [ Start Meeting ]


                    How it works

             1. Enter meeting URL
                       ↓
             2. Bot joins and listens
                       ↓
             3. AI analyzes transcript
                       ↓
             4. Approve / reject tasks
                       ↓
             5. Tasks go to Jira
```

This is only a structural reference.

Use your own judgment to make the actual composition visually good.

---

# 30. Application Flow Visualization

The landing page should also communicate the five-step process vertically downward:

```text
Enter the meeting URL
        ↓
Bot joins and listens
        ↓
AI analyzes the transcript
        ↓
Review tasks
        ↓
Tasks pushed to Jira
```

This should be simple typography.

Do not turn this into a giant graphical workflow.

---

# 31. Meeting State UI

For the intermediate states, intentionally keep the screen extremely simple.

Example:

```text
        admit the bot in the meet
```

Then:

```text
        bot is listening in the meet
```

Then:

```text
        AI is analyzing the transcript

        creating action-items...
```

The application should feel calm while work happens in the background.

Do not display:

```text
Vexa meeting ID
MongoDB ID
webhook status
API response
Gemini model
Jira cloud ID
native meeting ID
```

These are implementation details.

---

# 32. Task Review UI

Once tasks are generated, the UI can become more information-dense.

Example:

```text
Tasks


Fix the login API

Alice Watson
Due Friday

[ Approve ] [ Reject ]


Update the frontend after the API is ready

Patrick Jane
No deadline mentioned

[ Approve ] [ Reject ]
```

The user should immediately understand:

- what needs to be done
- who is responsible
- when it is due
- whether they approved it

---

# 33. Approved / Rejected Visual State

After clicking:

```text
Approve
```

the task should visually indicate:

```text
✓ Approved
```

After clicking:

```text
Reject
```

show:

```text
× Rejected
```

The user should be able to change their decision before final submission if the backend supports this workflow.

Do not immediately send the decision to Jira.

---

# 34. Responsiveness

The frontend must work on:

- desktop
- laptop
- tablet
- mobile

Desktop is the primary target.

Do not create a completely different mobile architecture.

Use responsive CSS.

The landing page should not overflow horizontally.

Task cards/list should stack naturally on smaller screens.

---

# 35. Accessibility

Implement basic accessibility:

- semantic buttons
- proper input labels/placeholders
- keyboard accessibility
- visible focus states
- sufficient contrast
- disabled button states
- meaningful loading states
- avoid relying only on color to communicate Approved / Rejected

---

# 36. API Summary

The frontend should communicate with the backend through these conceptual APIs.

## Start meeting

```http
POST /api/meetings
```

Request:

```json
{
  "meeting_url": "https://meet.google.com/..."
}
```

Auth:

```http
Authorization: Bearer <clerk_token>
```

---

## Meeting status

```http
GET /api/meetings/{meeting_id}/status
```

Auth:

```http
Authorization: Bearer <clerk_token>
```

Response concept:

```json
{
  "meeting_id": "...",
  "status": "active",
  "completion_reason": null,
  "start_time": "...",
  "end_time": null
}
```

---

## Get action items

Use the existing backend GET action-item endpoint.

Inspect the backend to determine the exact route.

Conceptually:

```http
GET /api/action-items/{meeting_id}
```

Auth:

```http
Authorization: Bearer <clerk_token>
```

---

## Review action items

```http
POST /api/action-items/review
```

Request:

```json
{
  "approved": [
    "id1",
    "id2"
  ],
  "rejected": [
    "id3"
  ]
}
```

Auth:

```http
Authorization: Bearer <clerk_token>
```

Response concept:

```json
{
  "approved": 2,
  "rejected": 1,
  "jira_created": 2,
  "jira_results": [
    {
      "issue_key": "KAN-25",
      "task": "Fix the login API",
      "assignee": "Alice Watson"
    }
  ]
}
```

---

# 37. Backend Responsibilities

The frontend should understand that the backend is responsible for:

```text
Authentication
      ↓
Meeting creation
      ↓
Vexa bot
      ↓
Meeting lifecycle
      ↓
Webhook processing
      ↓
Transcript retrieval
      ↓
Gemini analysis
      ↓
Jira user lookup
      ↓
Task extraction
      ↓
MongoDB persistence
      ↓
Human review endpoint
      ↓
Jira MCP
      ↓
Jira issue creation
      ↓
Jira assignment
      ↓
Jira transition
```

The frontend only orchestrates the user experience around these APIs.

---

# 38. Important Backend Details

Current backend integrations include:

### Vexa

Used for:

- joining Google Meet
- joining Teams
- capturing meeting audio
- transcription
- meeting lifecycle
- completion webhook

The frontend must NEVER contain:

```text
VEXA_BOT_API_KEY
VEXA_TX_API_KEY
VEXA_WEBHOOK_SECRET
```

---

### Gemini

Gemini runs entirely on the backend.

The frontend never calls Gemini.

The backend generates structured meeting intelligence:

```text
summary
key points
decisions
action items
assignee
due date
```

---

### Jira MCP

The backend uses Atlassian Rovo MCP.

The frontend never talks directly to Jira MCP.

The backend handles:

```text
createJiraIssue
assign user
transition issue to To Do
```

---

### MongoDB

MongoDB stores:

- meetings
- meeting ownership
- action items
- action item status
- Jira issue keys

The frontend does not connect directly to MongoDB.

---

# 39. Security Requirements

Never expose these in frontend code:

```env
CLERK_SECRET_KEY
CLERK_WEBHOOK_SIGNING_SECRET
VEXA_BOT_API_KEY
VEXA_TX_API_KEY
VEXA_WEBHOOK_SECRET
ATLASSIAN_API_TOKEN
ATLASSIAN_EMAIL
```

Only:

```env
VITE_CLERK_PUBLISHABLE_KEY
VITE_API_URL
```

should be frontend environment variables.

---

# 40. Existing Project Files

Before changing anything, inspect the existing frontend.

Likely existing structure:

```text
frontend/
├── src/
│   ├── App.jsx
│   ├── main.jsx
│   └── ...
├── package.json
├── vite.config.js
└── .env
```

The backend is roughly structured as:

```text
app/
├── main.py
├── config.py
├── database.py
├── models.py
├── processing.py
├── intelligence.py
├── transcript.py
├── vexa.py
├── webhook.py
├── meetings/
│   └── routes.py
├── action_items/
│   └── routes.py
├── jira/
│   ├── client.py
│   ├── users.py
│   ├── issues.py
│   └── transitions.py
└── auth/
    ├── clerk.py
    └── webhook.py
```

Inspect the actual repository before relying on this structure.

---

# 41. Implementation Instructions

Before coding:

1. Inspect the complete frontend.
2. Inspect the backend API routes relevant to:
   - meetings
   - meeting status
   - action items
   - review
   - authentication
3. Inspect `package.json`.
4. Inspect existing CSS.
5. Inspect existing Clerk setup.
6. Inspect existing React Router setup.
7. Determine the exact response formats of the APIs.
8. Reuse existing components where sensible.

Then implement the frontend.

---

# 42. Do Not Invent API Contracts

This is extremely important.

If the backend currently has:

```http
GET /api/action-items
```

instead of:

```http
GET /api/action-items/{meeting_id}
```

use the actual existing endpoint.

If response fields differ, adapt the frontend to the actual backend response.

Do not silently invent a backend contract.

If something is genuinely missing, identify it clearly before modifying the backend.

---

# 43. Polling

The meeting status endpoint should be polled while the meeting is active.

Conceptually:

```text
POST /api/meetings
       ↓
save meeting_id
       ↓
poll status
       ↓
requested / joining / awaiting_admission
       ↓
active
       ↓
continue polling
       ↓
completed
       ↓
show analyzing state
       ↓
continue polling
       ↓
processed
       ↓
fetch tasks
```

Polling should stop when it is no longer needed.

Avoid memory leaks and duplicate polling intervals.

Do not create multiple simultaneous polling loops because of React re-renders.

---

# 44. Handling `completed`

Important:

A Vexa meeting can become:

```text
completed
```

before Gemini processing has finished.

Therefore:

```text
completed != tasks ready
```

The frontend should NOT immediately fetch tasks and assume they exist.

Instead:

```text
completed
    ↓
AI is analyzing
    ↓
wait/poll
    ↓
processed
    ↓
fetch tasks
```

This is important.

---

# 45. Handling `processed`

When:

```text
status === "processed"
```

fetch the tasks.

Then transition to:

```text
TASK_REVIEW
```

---

# 46. Avoid Unnecessary Complexity

This is an MVP/product frontend.

Do NOT add:

- Redux
- Zustand
- MobX
- GraphQL
- WebSockets
- Server-side rendering
- complicated design systems
- unnecessary custom hooks everywhere
- huge component abstractions
- complicated animation libraries

unless the existing repository already uses them or there is a concrete reason.

Simple React state and API calls are enough.

---

# 47. Component Organization

Use reasonable component separation.

For example:

```text
src/
├── components/
│   ├── Landing.jsx
│   ├── MeetingState.jsx
│   ├── TaskReview.jsx
│   ├── TaskCard.jsx
│   └── Notification.jsx
│
├── api/
│   └── api.js
│
├── App.jsx
├── main.jsx
└── index.css
```

This is only a suggestion.

Follow the existing project structure if it is already organized differently.

Do not create dozens of tiny components.

---

# 48. API Helper

Centralize the API base URL:

```js
const API_URL = import.meta.env.VITE_API_URL;
```

If useful, create small helpers such as:

```js
getMeetingStatus()
createMeeting()
getActionItems()
reviewActionItems()
```

Keep them simple.

---

# 49. Loading States

Every network operation should have an appropriate loading state.

Examples:

Start meeting:

```text
Starting...
```

Task loading:

```text
Loading tasks...
```

Review submission:

```text
Creating Jira tasks...
```

But do not overdo spinners.

The primary application states themselves should communicate progress.

---

# 50. Final UX Goal

The user experience should feel like:

```text
Paste meeting URL
        ↓
"admit the bot in the meet"
        ↓
"bot is listening in the meet"
        ↓
"AI is analyzing the transcript"
        ↓
Tasks appear
        ↓
Approve / Reject
        ↓
Jira tasks created
        ↓
Small confirmation notifications
        ↓
Back to Talk2Task landing page
```

The application should feel almost invisible while the automation happens.

The user should not need to understand:

- Vexa
- Gemini
- MCP
- MongoDB
- webhooks
- Jira APIs
- meeting lifecycle APIs

Those are implementation details.

---

# 51. Final Acceptance Criteria

The frontend is complete when this exact scenario works:

### Step 1

User opens Talk2Task.

They see:

```text
Talk2Task

turns meeting discussions into actionable tasks,
so nothing important gets forgotten
```

plus the description and meeting URL input.

---

### Step 2

User enters:

```text
https://meet.google.com/...
```

and clicks Start Meeting.

Backend receives:

```http
POST /api/meetings
```

---

### Step 3

Frontend receives the meeting ID.

UI changes to:

```text
admit the bot in the meet
```

---

### Step 4

User admits Vexa bot.

Backend status becomes:

```text
active
```

Frontend changes to:

```text
bot is listening in the meet
```

---

### Step 5

Meeting ends.

Backend begins:

```text
transcript
→ Gemini
→ action items
```

Frontend shows:

```text
AI is analyzing the transcript

creating action-items...
```

with the subtle changing dots animation.

---

### Step 6

Backend reaches:

```text
processed
```

Frontend fetches the tasks.

Example:

```text
Tasks

Fix the login API
Alice Watson
Due: Friday

[ Approve ] [ Reject ]


Update the frontend
Patrick Jane
No deadline mentioned

[ Approve ] [ Reject ]
```

---

### Step 7

User approves/rejects every task.

Example:

```text
Fix login API
✓ Approved

Update frontend
× Rejected
```

---

### Step 8

Once every task has been reviewed:

```text
POST /api/action-items/review
```

with:

```json
{
  "approved": ["..."],
  "rejected": ["..."]
}
```

---

### Step 9

Backend creates Jira tasks.

Frontend receives:

```json
{
  "jira_results": [
    {
      "issue_key": "KAN-25",
      "task": "Fix login API"
    }
  ]
}
```

---

### Step 10

Show notification:

```text
Jira task created

KAN-25
Fix login API
```

---

### Step 11

Return to landing page.

The application is ready for another meeting.

---

# 52. Most Important Instruction

Build the frontend around the **actual existing backend**.

Do not redesign the backend.

Do not invent API endpoints.

Do not expose backend credentials.

Do not introduce unnecessary libraries.

Do not turn this into a generic SaaS dashboard.

Keep the visual design extremely minimal:

```text
OFF-WHITE / CREAM
+
FRAUNCES
+
TYPOGRAPHY
+
SPACE
+
MINIMAL UI
```

The core product experience is the workflow, not the amount of UI.

First inspect the repository and existing API implementation, then implement the complete frontend flow above.

````

## IMPORTANT WORKING MODE

Do not start by writing code.

First inspect the repository and give me a concise report containing:

1. Current frontend structure
2. Current frontend dependencies
3. Existing routes
4. Existing Clerk integration
5. Existing backend API endpoints relevant to the frontend
6. Exact request/response schemas you found
7. Any mismatch between the frontend requirements below and the existing backend
8. Files you plan to modify

Then implement the frontend.

Do not make backend changes unless something required by this frontend genuinely does not exist.
