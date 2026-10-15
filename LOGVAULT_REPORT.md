# COIMBATORE INSTITUTE OF TECHNOLOGY

## COIMBATORE – 641014

### DEPARTMENT OF INFORMATION TECHNOLOGY

## NoSQL DATABASE PROJECT REPORT

# LogVault — Application Error Tracking & Issue Management System

### Using Python Flask, Apache Cassandra and React

*(Insert CIT college logo here)*

### SUBMITTED BY

**Tanisha D**
**2403717620522055**
**B.Tech IT – III YEAR**

**Course Code: 23IT523**
**Course name: Open Source Systems Laboratory**
**Academic Year: 2024 – 2028**

---

---

# COIMBATORE INSTITUTE OF TECHNOLOGY

*(Government Aided Autonomous Institution Affiliated to Anna University)*

### COIMBATORE – 641014

## BONAFIDE CERTIFICATE

Certified that this project report titled **"LogVault — Application Error Tracking & Issue Management System"** is the Bonafide work of **Tanisha D (2403717620522055)** completed during the academic year 2026-2027 (Semester V) for the project presentation of Open Source System Laboratory (23IT523) under my supervision.

### REVIEW MEMBERS:

1. **Dr. E. Arul**
2. **Dr. S. Devi**

---

---

# COIMBATORE INSTITUTE OF TECHNOLOGY, COIMBATORE-14

## DEPARTMENT OF INFORMATION TECHNOLOGY

### 23IT523 – OPEN SOURCE SYSTEMS LABORATORY

**Course / Sem**: B.Tech / V  **Branch**: Information Technology
**AY**: 2026-2027  **Date**: _______________

### CAT II – Demonstration of Project

**Register Number:** 2403717620522055

**Name of the Student:** Tanisha D

**Title of the Project:** LogVault — Application Error Tracking & Issue Management System

**Objective of the Project:** To build a centralized error-monitoring platform where any application reports its exceptions through a REST API, with automatic duplicate grouping, time-series analytics, spike detection, and webhook delivery, backed by Apache Cassandra for high-throughput write-optimised storage.

**Database used:** Apache Cassandra 4.1 (NoSQL, wide-column store)

### Evaluation criteria:

| Criteria | Marks Allotted | Marks Obtained | Comments |
|---|---|---|---|
| Frontend Design | 25 | | |
| Implementation of the project (Frontend Integration database and CRUD operations) | 40 | | |
| Documentation & Report | 15 | | |
| Presentation | 10 | | |
| Viva | 10 | | |
| **Grand Total** | **100** | | |

**Faculty In-charge:**
Dr. E. Arul
Dr. S. Devi

---

---

## TABLE OF CONTENTS

| S. No. | Contents | Page No. |
|---|---|---|
| 1 | Project Overview | 4 |
| 2 | Objectives | 5 |
| 3 | Technologies Used | 5 |
| 4 | System / Project Description | 6 |
| 5 | System Architecture | 7 |
| 6 | Frontend Implementation | 7 |
| 7 | NoSQL Database Implementation | 8 |
| 8 | CRUD Operations | 10 |
| 9 | Working Screenshots | 11 |
| 10 | Conclusion | 15 |
| 11 | Future Enhancements | 16 |

---

---

## 1. PROJECT OVERVIEW

### 1.1 Introduction

LogVault is a web-based error-monitoring and issue-management platform that allows any application to report its runtime exceptions to a centralized server. The application provides CRUD (Create, Read, Update, Delete) operations through a modern, user-friendly dashboard.

The system is developed using **Python Flask** for the server-side REST API, **React with Vite and Chart.js** for the frontend dashboard, and **Apache Cassandra** as the NoSQL wide-column database. The entire stack is orchestrated through **Docker Compose**, so the full project boots with a single command.

Cassandra stores information as rows inside partitioned tables and uses **counter columns, native TTL, and query-driven denormalization** to serve the dashboard efficiently. Instead of storing each error as an isolated log line, the system groups duplicates through SHA-256 fingerprinting and tracks their frequency, severity, and timeline.

### 1.2 Problem Being Addressed

Software applications generate large numbers of error and exception logs, but in small teams these remain scattered across text files and machines, so recurring failures go unnoticed. Teams often learn about bugs from users instead of from their own systems. The same error happening 500 times appears as 500 separate problems. Logs grow without limit and are rarely cleaned. Finally, relational databases slow down under constant, high-volume log writes.

The proposed system addresses these problems by providing a centralized portal where applications can report errors through a REST API, repeated errors are automatically grouped into a single issue, developers can filter and resolve issues, old logs expire automatically through TTL, and live analytics visualise error trends.

### 1.3 Purpose of the Project

The purpose of this project is to develop a practical error-tracking system that demonstrates how Python Flask can integrate with Apache Cassandra as the underlying NoSQL store. It provides a structured way to manage error information while demonstrating query-driven data modelling, counter columns, native TTL retention, and complete CRUD operations.

---

---

## 2. OBJECTIVES

- To develop a web-based portal for managing applications, errors, issues, and their timelines.
- To implement Create, Read, Update, and Delete operations for both the Apps entity and the Issues entity, directly from the dashboard.
- To integrate Python Flask with the Apache Cassandra NoSQL database.
- To represent error data as denormalized, query-driven tables suited to Cassandra's wide-column model.
- To provide a dashboard displaying live counts of events, issues, unresolved issues, and spiking issues.
- To automatically group repeated errors into a single issue using SHA-256 fingerprinting.
- To expire old event rows automatically using Cassandra's native TTL feature.
- To visualize error trends, severity breakdown, and the top noisiest issues using live charts.
- To provide a live benchmark panel showing events-per-second, average, and p99 write latency.
- To deliver webhook notifications when a brand-new issue is detected.
- To demonstrate the practical application of a wide-column NoSQL database in a high-throughput, time-series workload.

---

## 3. TECHNOLOGIES USED

| Technology | Used For |
|---|---|
| React 18 + Vite | Builds the single-page dashboard, with hot-reload during development. |
| Chart.js + react-chartjs-2 | Draws the trend line chart, severity doughnut, and sparklines. |
| HTML5 / CSS3 | Structures and styles the dashboard, sidebar, panels, and tables. |
| Python 3.11 + Flask 3 | Handles REST API routing, request validation, and CRUD business logic. |
| Gunicorn | Production-grade WSGI server that hosts the Flask backend. |
| cassandra-driver (DataStax Python Driver) | Connects Python to the Cassandra cluster and executes CQL prepared statements. |
| Apache Cassandra 4.1 | Stores applications, issues, raw events, and counter aggregates. |
| CQL (Cassandra Query Language) | Declarative query language used for schema and all data operations. |
| Docker + Docker Compose | Containerizes Cassandra, backend, and frontend, orchestrates the full stack with one command. |
| Axios + React Router | Handles HTTP requests from the dashboard and page navigation. |

*Note: The entire system runs locally via Docker Compose — no cloud dependency or paid service is required. The React frontend communicates with the Flask API through a Vite proxy, and the Flask API communicates with Cassandra over the native CQL binary protocol on port 9042.*

---

---

## 4. SYSTEM / PROJECT DESCRIPTION

### 4.1 Main Modules and Features

| Module | Description |
|---|---|
| Application Management | Allows the user to register, view, update, and delete applications. Each application has a name, auto-generated API key, and optional webhook URL. |
| Issue Management | Automatically groups raw events into issues through SHA-256 fingerprinting. Allows developers to view, mark as resolved/unresolved, annotate with developer notes, and delete issues inline from the dashboard. |
| Ingest API | A REST endpoint `POST /api/log` through which any client application can send exceptions. Authenticated via per-app `X-API-Key` header. |
| Analytics Module | Provides three analytics endpoints — trend chart (errors over time, split by severity), severity breakdown (doughnut chart), and top-5 noisiest issues. |
| Live Benchmark Panel | Displays events-per-second, average write latency, p99 write latency, and lifetime event count. Polls every 2 seconds. |
| Spike Detection | Compares the current hour's issue count with the preceding 24-hour average; if 5× higher, the issue is flagged with a SPIKE badge. |
| Webhook Delivery | When a brand-new issue is seen, LogVault POSTs the issue payload to the application's configured webhook URL (demonstrated using webhook.site). |
| TTL-based Retention | Every raw event row is written with `USING TTL 2592000` (30 days), so Cassandra automatically tombstones them during compaction. |

### 4.2 How the Application Works

- The user opens the dashboard in a web browser at `http://localhost:5173`.
- Vite's development server serves the React single-page application.
- The browser calls the Flask REST API through a built-in HTTP proxy.
- Flask receives the request, validates input, and (for ingestion) authenticates the per-app API key.
- The Flask application sends prepared CQL statements to Cassandra through the DataStax Python Driver.
- Cassandra creates, retrieves, updates, or deletes the requested rows across the eight purpose-built tables.
- Counter columns are updated atomically for hourly aggregates and lifetime issue counts.
- The dashboard auto-refreshes every 5 seconds; the live benchmark panel refreshes every 2 seconds.
- When a brand-new issue is created, the Flask backend fires an outbound HTTP POST to the application's webhook URL if one is configured.

---

---

## 5. SYSTEM ARCHITECTURE

The system follows a three-tier containerized architecture:

- **Presentation Layer:** Provides the dashboard, navigation sidebar, forms, charts, tables, and inline action buttons for every CRUD operation.
- **Application Layer:** Processes HTTP requests, validates input, applies authentication, performs error fingerprinting, computes spike detection, delivers webhooks, and executes CQL prepared statements.
- **Data Layer:** Stores partitioned rows, counter aggregates, and TTL-managed event data across eight tables inside Apache Cassandra.

```
┌───────────────────────────────────────────────────────┐
│                 PRESENTATION LAYER                    │
│  React · Vite · Chart.js · Web Browser (port 5173)    │
└───────────────────────┬───────────────────────────────┘
                        │  HTTP / JSON over Vite proxy
                        ▼
┌───────────────────────────────────────────────────────┐
│                 APPLICATION LAYER                     │
│  Python Flask · Gunicorn · DataStax Driver            │
│  Auth · Fingerprint · Spike Detection (port 5000)     │
└───────────────────────┬───────────────────────────────┘
                        │  CQL binary protocol
                        ▼
┌───────────────────────────────────────────────────────┐
│                    DATA LAYER                         │
│       Apache Cassandra 4.1 (port 9042)                │
│       8 tables · Counter columns · 30-day TTL         │
└───────────────────────────────────────────────────────┘
```

*Figure 1: System architecture diagram*

---

## 6. FRONTEND IMPLEMENTATION

The frontend is developed as a React 18 single-page application using Vite as the build tool, with Chart.js providing all data visualizations. The entire dashboard runs inside a Docker container and communicates with the Flask backend through a proxy configured in `vite.config.js`.

### 6.1 Dashboard

The dashboard provides a complete overview of the system. It retrieves live data from Cassandra through the Flask API and displays summary cards (events in window, issues, unresolved, spiking), the live benchmark panel, a trend chart by severity, a severity doughnut, the top-5 noisiest issues panel, and the full issues table with inline Update and Delete actions.

### 6.2 Application Management (Sidebar)

The sidebar lists every registered application and provides a `+ New` button to open a modal form that creates a new application through `POST /api/apps`. Each application also has a 🗑 delete icon that cascades through the related issue tables.

### 6.3 Issue Management (Main Table)

The main issues table displays every grouped issue with severity, exception type, lifetime count, last-seen timestamp, status, and inline actions. The **`✓ Resolve / ↩ Reopen`** button toggles the status, the **🗑** button deletes the issue, and clicking the row navigates to the full issue detail page with stack trace and 24-hour sparkline.

### 6.4 Analytics Panels

The trend chart renders errors per hour broken down by severity using a stacked line chart. The severity breakdown is drawn as a doughnut chart. The top-5 noisiest issues panel lists issues ranked by lifetime count. All charts auto-refresh every 5 seconds.

### 6.5 Live Benchmark Panel

A dedicated panel polls `GET /api/analytics/throughput` every 2 seconds and displays events-per-second, average write latency (in milliseconds), p99 write latency, and lifetime event count ingested since backend start. This panel provides quantitative evidence of Cassandra's write performance.

### 6.6 Webhook Settings

A settings panel on the dashboard allows the user to edit the webhook URL for the currently selected app. The URL is persisted through `PATCH /api/apps/<name>`.

---

---

## 7. NoSQL DATABASE IMPLEMENTATION

### 7.1 Why Apache Cassandra?

- Cassandra is a wide-column NoSQL database designed for **write-heavy, time-series, and append-mostly workloads**, which exactly matches an error-tracking workload.
- It stores every row by partition key, so queries that stay within one partition are extremely fast and scale horizontally as nodes are added.
- Cassandra uses an **LSM-tree storage engine**, so inserts are O(1) in-memory writes — unlike a B-tree in relational systems, which must update indexes under lock on every insert.
- Native **counter columns** allow lock-free atomic increments, which perfectly fit per-hour aggregates and lifetime issue counts.
- Native **TTL** on inserts allows event rows to auto-expire after a configured retention window, eliminating the need for a cleanup job.
- Cassandra uses **CQL**, a declarative, SQL-like query language, making the data layer approachable.

### 7.2 Table Model

The schema contains **eight tables**, each designed to serve a specific query pattern. This is Cassandra's query-driven data modelling philosophy — one table per query, denormalized intentionally.

| Table | Primary Key | Purpose |
|---|---|---|
| `apps` | `(app_name)` | Registered applications and their API keys. |
| `issues` | `(issue_id)` | Canonical issue record, keyed by fingerprint. |
| `issues_by_app` | `(app, issue_id)` | Per-app issue index for the dashboard. |
| `events_by_issue` | `(issue_id, event_time, event_id)` | Timeline of raw events for an issue, TTL'd. |
| `events_by_app_day` | `((app, day), event_time, event_id)` | Recent events per app per day, bucketed and TTL'd. |
| `event_count_by_issue_hour` | `(issue_id, hour)` | Counter: per-issue sparkline source. |
| `event_count_by_app_hour` | `(app, hour, severity)` | Counter: trend chart and severity source. |
| `issue_total_count` | `(app, issue_id)` | Counter: lifetime count per issue, powers top-N. |

### 7.3 Partitioning and Clustering Strategy

The partition key determines which Cassandra node owns the row. Clustering keys determine the sort order inside the partition.

| Table | Partition Key | Clustering Key | Rationale |
|---|---|---|---|
| `events_by_issue` | `issue_id` | `event_time DESC` | Show the newest events for an issue first. |
| `events_by_app_day` | `(app, day)` | `event_time DESC` | Bounds partition size by day, keeps hot partitions small. |
| `event_count_by_issue_hour` | `issue_id` | `hour DESC` | Enables range queries like "last 24 hours of counts". |
| `event_count_by_app_hour` | `app` | `(hour, severity)` | Range by hour, split by severity for the trend chart. |

**Key design properties:**

- **Writes stay in one partition** per event: each `POST /api/log` writes to `events_by_issue`, `events_by_app_day`, and 3 counter rows — all in different partitions, so writes parallelize across the cluster.
- **Reads stay in one partition** per query: listing issues for an app hits one `issues_by_app` partition; rendering a sparkline hits one `event_count_by_issue_hour` partition.
- **Counter columns handle aggregates:** instead of `SELECT COUNT(*)`, which would scan rows, LogVault increments counters at write time and reads them in O(1) at query time.

### 7.4 Example CQL Queries

**Create an application (Create):**
```cql
INSERT INTO apps (app_name, api_key, webhook_url, created_at)
VALUES ('payments', 'demo-key-payments', '', toTimestamp(now()));
```

**Insert a raw event with TTL (Create):**
```cql
INSERT INTO events_by_issue
    (issue_id, event_time, event_id, app, severity, message, stack)
VALUES
    ('15b3852ae3d297f3', '2026-10-14 13:26:00', uuid(),
     'payments', 'ERROR', "KeyError: 'user_id'", '...')
USING TTL 2592000;
```

**Increment a counter (Update):**
```cql
UPDATE event_count_by_app_hour SET count = count + 1
WHERE app = 'payments' AND hour = '2026-10-14 13:00:00' AND severity = 'ERROR';
```

**List all issues for an app (Read):**
```cql
SELECT app, issue_id, exception_type, message, severity, status, last_seen
FROM issues_by_app WHERE app = 'payments';
```

**Range query for the trend chart (Read):**
```cql
SELECT hour, severity, count
FROM event_count_by_app_hour
WHERE app = 'payments'
  AND hour >= '2026-10-14 00:00:00'
  AND hour <= '2026-10-14 23:00:00';
```

**Mark an issue as resolved (Update):**
```cql
UPDATE issues SET status = 'resolved', note = 'Fixed in PR #42'
WHERE issue_id = '15b3852ae3d297f3';
```

**Delete an issue (Delete):**
```cql
DELETE FROM issues WHERE issue_id = '15b3852ae3d297f3';
```

These examples demonstrate basic CQL operations. The actual application executes its CRUD operations from the Flask backend using prepared statements for safety and performance — 23 prepared statements are compiled at startup and reused across all requests.

---

---

## 8. CRUD OPERATIONS

LogVault implements full CRUD operations on both of its primary entities — **Apps** and **Issues** — accessible entirely from the dashboard without any page navigation.

### 8.1 Apps CRUD

| Operation | API Endpoint | UI Location | Cassandra Statement |
|---|---|---|---|
| CREATE | `POST /api/apps` | `+ New` button in sidebar → modal form | `INSERT INTO apps (...) VALUES (...)` |
| READ | `GET /api/apps` | Sidebar list of applications | `SELECT * FROM apps` |
| UPDATE | `PATCH /api/apps/<name>` | Webhook URL panel on dashboard | `UPDATE apps SET webhook_url = ? WHERE app_name = ?` |
| DELETE | `DELETE /api/apps/<name>` | 🗑 icon next to each app in sidebar | Cascading delete across `apps`, `issues`, `issues_by_app`, `issue_total_count` |

### 8.2 Issues CRUD

| Operation | API Endpoint | UI Location | Cassandra Statement |
|---|---|---|---|
| CREATE | `POST /api/log` | **`⚡ Fire test error`** button on dashboard header | `INSERT INTO events_by_issue (...) USING TTL ?` plus counter increments |
| READ | `GET /api/issues?app=<name>`<br>`GET /api/issues/<id>` | Dashboard table + Issue Detail page | `SELECT ... FROM issues_by_app WHERE app = ?` |
| UPDATE | `PATCH /api/issues/<id>` | Inline **`✓ Resolve / ↩ Reopen`** button in each row | `UPDATE issues SET status = ?, note = ? WHERE issue_id = ?` |
| DELETE | `DELETE /api/issues/<id>` | Inline **🗑** button in each row | `DELETE FROM issues WHERE issue_id = ?` |

### 8.3 Supporting Operations

| Operation | API Endpoint | Purpose |
|---|---|---|
| Health check | `GET /healthz` | Verifies Cassandra connectivity |
| Trend chart | `GET /api/analytics/trend?app=<name>&hours=24` | Returns per-hour counts by severity |
| Severity breakdown | `GET /api/analytics/severity?app=<name>&hours=24` | Returns totals grouped by severity |
| Top noisy issues | `GET /api/analytics/top-issues?app=<name>&n=5` | Returns top-N by lifetime count |
| Live throughput | `GET /api/analytics/throughput` | Returns ev/s, avg + p99 latency, lifetime events |

Every CRUD operation uses parameterized **prepared statements**, protecting against injection and enabling the Cassandra driver to cache the query plan on the server.

---

---

## 9. WORKING SCREENSHOTS

> **[Student Note: Replace each placeholder below with a screenshot captured from your running project. Open the dashboard at http://localhost:5173 and capture each view.]**

### 9.1 Dashboard — Main View
*(Insert screenshot of the main dashboard showing the sidebar with apps, 4 summary cards, benchmark panel, charts, and issues table.)*

### 9.2 Create a New Application
*(Insert screenshot of the `+ New` modal with the app name, API key, and webhook URL fields filled in.)*

### 9.3 Fire Test Error — Issue Creation
*(Insert screenshot showing the dashboard immediately after clicking `⚡ Fire test error`, with the success message "New issue created" visible under the button.)*

### 9.4 Issue Table with Inline CRUD Actions
*(Insert screenshot focused on the "All issues" table showing the `✓ Resolve` and 🗑 buttons in the Actions column.)*

### 9.5 Issue Detail Page — Stack Trace and Sparkline
*(Insert screenshot of an individual issue page showing the exception type, severity badge, 24-hour sparkline, stack trace, and recent events.)*

### 9.6 Live Benchmark Panel
*(Insert screenshot of the "Live ingest performance" panel showing events-per-second, average + p99 latency, and lifetime event count during active ingestion.)*

### 9.7 Trend and Severity Charts
*(Insert screenshot of the trend line chart and severity doughnut chart filled with real data.)*

### 9.8 Webhook Settings and Webhook.site Delivery
*(Insert screenshot showing LogVault's webhook settings panel on the left and the webhook.site browser tab receiving the live POST on the right.)*

### 9.9 Cassandra Database — Table List
*(Insert screenshot of a terminal running `docker exec logvault-cassandra cqlsh -e "USE logvault; DESCRIBE TABLES;"` showing all 8 tables.)*

### 9.10 Cassandra Database — Sample Rows
*(Insert screenshot of `SELECT * FROM logvault.apps;` or `SELECT * FROM logvault.event_count_by_app_hour WHERE app='payments';` showing real data.)*

---

---

## 10. CONCLUSION

The LogVault project demonstrates the integration of Python Flask with the Apache Cassandra NoSQL database to build a complete, production-style error-tracking and issue-management system. The application provides a centralized interface for performing full CRUD operations on applications and issues, backed by eight purpose-built Cassandra tables designed around specific query patterns.

By representing error data in a wide-column, denormalized, write-optimized schema, the project demonstrates how Cassandra efficiently handles high-volume, time-series workloads that would overwhelm a relational database. Features such as SHA-256 fingerprint-based error grouping, counter columns, TTL-based retention, and live spike detection show how NoSQL design choices translate directly into application behaviour.

The project also provides practical experience in Python Flask API development, React component design, Chart.js visualization, Docker Compose orchestration, prepared statements, and Cassandra data modelling. The complete stack boots with a single `docker compose up` command and demonstrates every CRUD operation inline on the dashboard, satisfying both the technical and user-experience requirements of an open-source NoSQL laboratory project.

---

---

## 11. FUTURE ENHANCEMENTS

1. **Multi-node Cassandra with replication:** Run three Cassandra nodes with replication factor 3 and demonstrate fault tolerance by stopping a node during a live demo.
2. **Prometheus and Grafana integration:** Export application metrics to Prometheus and build Grafana dashboards for operational monitoring.
3. **User authentication and role-based access:** Introduce secure login and permissions for administrators and developer users.
4. **Full-text stack-trace search:** Add Elasticsearch integration so developers can search across stack traces by keyword.
5. **Slack and email webhook templates:** Pre-built delivery formats for Slack and SMTP so notifications land in team workflows.
6. **Mute-until-next-spike feature:** Let developers temporarily mute a chatty issue until its rate meaningfully changes.
7. **Issue assignment and ownership:** Assign issues to team members and track ownership over time.
8. **Daily digest and CSV export:** Email a daily summary of top issues and allow full CSV export of filtered issues.
9. **Mobile-responsive dashboard:** Optimize the React dashboard for mobile viewing with touch-friendly actions.
10. **Rate-limited and signed ingest:** Add HMAC-signed payloads and per-app rate limits to protect against abuse.

These are proposed enhancements and should be described as future work unless they have actually been implemented.
