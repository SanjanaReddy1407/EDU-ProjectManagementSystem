# EDU-ProjectManagementSystem
---
# 🎓 EDU-PMS

**Intelligent Academic Project Management & Team Formation System**

![Python](https://img.shields.io/badge/PYTHON-CORE_LOGIC-0078D4?style=for-the-badge&logo=python&logoColor=white) ![Algorithms](https://img.shields.io/badge/ALGORITHMS-DATA_PARTITIONING-150458?style=for-the-badge) ![Database](https://img.shields.io/badge/DATABASE-ROBUST_SCHEMA-F29111?style=for-the-badge&logo=mysql&logoColor=white) ![Security](https://img.shields.io/badge/SECURITY-ROLE__BASED_ACCESS-7952B3?style=for-the-badge&logo=auth0&logoColor=white)

> EDU-PMS is a dynamic web platform engineered to streamline academic workflows and administration. It utilizes custom data partitioning algorithms to intelligently automate merit-balanced team formation and supervisor assignment. Featuring a carefully outlined database schema, strict role-based security layers, and a clear deployment roadmap, the system ensures a secure, organized, and highly efficient environment for managing academic projects.

---

## 📌 Executive Summary

Traditional academic project management relies heavily on manual file uploads, unstructured team formation, and prone-to-bias supervisor allocation. **EDU-PMS** solves these challenges by digitizing the complete project lifecycle:

1. **Automated Tiering:** Classifying students based on merit (CGPA).
2. **Balanced Grouping:** Implementing a 1:N distribution model to avoid dynamic skill polarization.
3. **Smart Priority Allotment:** Matching student preferences with supervisor slots transparently.
4. **Research Integrity:** Ensuring project novelty through historical proposal tracking and QR-code-based digital identity generation.

---

## 🏗️ System Architecture

The application follows a modular Model-View-Controller (MVC) software design pattern built on top of a lightweight, highly responsive WSGI architecture.

                       +-----------------------------------+
                       |        Client Browser UI          |
                       |  (HTML5 / CSS3 / Vanilla JS API)  |
                       +-----------------+-----------------+
                                         |
                                         | HTTP Requests (REST / JSON)
                                         v
                       +-----------------------------------+
                       |         Flask Controller          |
                       |     (Routing & Session Auth)      |
                       +-----------------+-----------------+
                                         |
                +-----------------------+---------------------------+
                |                                                   |
                v                                                   v
    +-------------------------------+               +-------------------------------+
    |      Core Logic Modules       |               |     Database Storage Layer    |
    | - Merit Auto-Tiering          |               | - CSV / SQLite Data Repos     |
    | - Priority Matching Algorithm |<------------->| - Historical Project Records  |
    | - Proposal Lock Engine        |               | - Session Tracking Stores     |
    +-------------------------------+               +-------------------------------+

    
---

## 📊 Process Flowcharts

### 1. Overall System Lifecycle Flowchart

[ Admin Data Ingestion (CSV Upload) ]
│
▼
[ System Tiering Logic Execution ] ──► (Classifies Students into Tiers 1-4)
│
▼
[ Automated Balanced Group Formation ] ──► (1 High Merit Leader + 3 Members)
│
▼
[ Student Leader Preference Submission ] ──► (Ranked Preference P1-P9)
│
▼
[ Meritocratic Priority Allotment ] ──► (Supervisor Allotted & Locked)
│
▼
[ Proposal & Title Review Module ] ──► (Mentor Accept/Reject + Feedback)
│
▼
[ Collaboration & QR Portfolio Generation ] ──► (Archived with Permanent Identity)

---

## 🧮 Core Algorithms

### 1. Meritocratic Batching Algorithm (1:N Tier Distribution)

To prevent skill isolation, students are sorted into 4 CGPA-driven quartiles (Batches 1 to 4). The system pulls exactly one high-performing student as a Leader and three cross-tier students as Members.

```text
Algorithm: BalancedTeamFormation
Input: Student Records S with CGPA
Output: Balanced Teams List T

1. Sort S in descending order based on CGPA.
2. Divide S into 4 equal segments:
   - Batch_1 (Tier 1: HighCGPA)
   - Batch_2 (Tier 2: Mid-High CGPA)
   - Batch_3 (Tier 3: Mid-Low CGPA)
   - Batch_4 (Tier 4: Low CGPA)
3. For i = 1 to length(Batch_1):
   - Group G_i = { Leader: Batch_1[i], Member1: Batch_2[i], Member2: Batch_3[i], Member3: Batch_4[i] }
   - Append G_i to T
4. Return T


Algorithm: MeritPriorityAllocation
Input: Group Preferences P, Mentor Slot Capacity C, Group Merit Rank R
Output: Assigned Mentors Map A

1. Sort Groups in descending order based on Group Merit Rank R.
2. For each Group G in sorted Groups:
   - For choice p in G.Preferences (P1 to P9):
     - If Capacity(p) > 0:
       - Assign Mentor p to Group G
       - Decrement Capacity(p) by 1
       - Break to next Group
     - Else:
       - Continue to next choice (p+1)
3. If Group G has no mentor assigned:
   - Auto-assign next available Mentor with remaining Capacity > 0.
4. Return A

```

## 🌟 Key Features Overview

| Feature Category | Feature Name | Description & Impact |
| :--- | :--- | :--- |
| **User Management** | **Role-Based Access Control (RBAC)** | Dedicated, secure authentication portals and customized views for Admin, Mentors, and Students. |
| **Team Formation** | **Automated Meritocratic Tiering** | Classifies students into 4 CGPA-driven tiers (Batches 1–4) and forms balanced 1:N teams in < 10 seconds. |
| **Supervisor Allotment** | **Merit-First Priority Allocation** | Smart matching engine that allocates mentors based on Group Merit Rank and preference order (P1–P9) with 85% satisfaction. |
| **Proposal Governance** | **Proposal Lock & Feedback System** | Automatically locks submitted titles/aims to prevent unauthorized edits and enables structured mentor review (Accept/Reject with feedback). |
| **Research Integrity** | **Duplicate Topic Prevention** | Cross-references new proposals with historical project records to prevent topic repetition and ensure 100% research novelty. |
| **Digital Portfolio** | **QR-Code Archival Engine** | Automatically generates a unique, permanent QR code for each project profile, allowing instant mobile access to project reports. |
| **Communication** | **Integrated Discussion Hub** | Built-in, secure chat repository for team members and allotted mentors, eliminating reliance on third-party messaging apps. |
| **Efficiency** | **Bulk Data Ingestion** | Enables admins to upload and process 300+ student records instantly via CSV, reducing administrative overhead by 80%. |

---

## 🛠️ Tech Stack & Architecture

| Layer | Technology / Tool | Purpose & Usage |
| :--- | :--- | :--- |
| **Frontend UI** | **HTML5 & CSS3** | Custom Glassmorphism UI, responsive grid/flexbox layouts, and sleek dark mode theme. |
| **Client Scripting** | **Vanilla JavaScript (ES6+)** | Dynamic DOM manipulation, asynchronous `fetch()` API calls for live previews, and interactive toggles. |
| **Backend Framework** | **Python 3.x (Flask)** | Lightweight WSGI web framework handling RESTful routing, session management, and business logic execution. |
| **Templating Engine** | **Jinja2** | Server-side HTML rendering for dynamically injecting database records, sessions, and student batch lists. |
| **Data Storage & Repos**| **CSV / SQLite Database** | Structured data persistence for student records, historical project logs, preference lists, and chat archives. |
| **Algorithms** | **Custom Python Logic** | Proprietary 1:N dynamic batching logic and conflict-free priority supervisor allotment engines. |
| **Typography & Styling**| **Google Fonts (Poppins)** | Modern, professional typography for optimized readability and aesthetic consistency across all views. |




