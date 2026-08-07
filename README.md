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
