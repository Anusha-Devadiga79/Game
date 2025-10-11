# **Software Requirements Specification (SRS) – Ad Module**

**Version:** 1.2
**Date:** 2025-10-11
**Author:** Anusha Devadiga

---

## **1. Introduction**

### 1.1 Purpose

The Ad Module enables businesses, recruiters, and community members to create, manage, and display ads on the website. It includes ad creation, moderation, scheduling, payment processing, analytics, targeting, and notifications. This SRS provides a detailed blueprint for developers, QA, and stakeholders to ensure the module is delivered according to business and technical requirements.

### 1.2 Scope

* Frontend ad creation and submission (Angular 16)
* Advertiser dashboard for ad management
* Admin dashboard for moderation, placement, and analytics
* Dynamic ad display system across website sections
* Analytics and reporting
* Payment integration (optional)
* Targeting and scheduling
* Notifications for ad status updates

**Module Architecture:** Standalone microservice integrated into the main Angular 16 application, using Express as the backend and MSSQL as the database.

### 1.3 Definitions, Acronyms, and Abbreviations

| Term       | Definition                                                   |
| ---------- | ------------------------------------------------------------ |
| CTR        | Click-through rate                                           |
| JWT        | JSON Web Token for secure authentication                     |
| Admin      | User with privileges to manage ads, placements, and policies |
| Advertiser | User creating and submitting ads                             |
| CRUD       | Create, Read, Update, Delete                                 |

---

## **2. Overall Description**

### 2.1 Product Perspective

The Ad Module is a microservice integrated with the main platform:

* Interacts with existing authentication and billing systems
* Shares data with user and wallet tables
* Sends notifications via the existing notification system

### 2.2 User Characteristics

| User Role  | Capabilities                                                                                     |
| ---------- | ------------------------------------------------------------------------------------------------ |
| Advertiser | Create, edit, manage ads; view analytics; make payments                                          |
| Admin      | Approve/reject ads; assign placements; monitor flagged content; view analytics; suspend accounts |

### 2.3 Constraints

| Constraint           | Details                           |
| -------------------- | --------------------------------- |
| Maximum image upload | 5 MB (JPG/PNG)                    |
| Ad display           | Must be responsive across devices |
| API response time    | ≤ 200ms                           |
| Paid ads             | Require payment processing        |

### 2.4 Assumptions

| Assumption          | Details                                                         |
| ------------------- | --------------------------------------------------------------- |
| Registered accounts | Users have valid accounts on the platform                       |
| Payment gateway     | Razorpay, Stripe, or PayPal available                           |
| Notifications       | Existing system supports in-app/email alerts                    |
| System resources    | Backend and frontend servers have sufficient storage and memory |

### 2.5 Dependencies

* Authentication Module for user verification
* Notification Service for alerts
* Billing / Payment Module for processing paid campaigns
* Existing wallet tables for payment history

---

## **3. Functional Requirements**

### 3.1 Ad Creation & Submission

* Form fields: Title, Description, Image/Banner, Target URL, Category, Start/End Date, Budget/Plan
* Preview option
* Save as Draft
* Validation: required fields, URL, image type/size

### 3.2 Advertiser Dashboard

* View, Edit, Pause/Resume/Delete ads
* Status tracking: Pending, Approved, Active, Expired, Rejected
* Analytics: Views, Clicks, CTR

### 3.3 Admin Panel

* Filter and view ads by status, category, advertiser, date
* Approve/Reject/Delete ads
* Assign ad placements (homepage, sidebar, footer)
* Monitor flagged/reported ads
* Suspend advertiser accounts
* Edit ad details if required

### 3.4 Ad Display System

* Display ads based on placement, category relevance, and priority
* Types: Banner, Sidebar, Inline, Popup/Modal (optional)
* Responsive and click-tracking enabled

### 3.5 Analytics & Reporting

* Metrics: Total Impressions, Clicks, CTR
* Daily/Weekly/Monthly charts
* Exportable reports (CSV/PDF)
* Top-performing ads dashboard

### 3.6 Payment & Plans (Optional)

* Pricing Plans: Basic, Premium, Sponsored
* Payment gateway integration
* Auto-calculated cost based on duration and placement
* Payment history and invoice generation

### 3.7 Targeting & Scheduling

* Targeting: Location, User Interests
* Scheduling: Start/End Dates, Priority delivery for premium ads

### 3.8 Notifications & Alerts

* Email/In-app notifications: approval, rejection, expiry, low budget
* Reminders before ad expiry

---

## **4. Non-Functional Requirements**

| Requirement Type | Details                                                                                       |
| ---------------- | --------------------------------------------------------------------------------------------- |
| Performance      | API response time ≤ 200ms; Dashboard charts load within 2s                                    |
| Security         | Input validation, file sanitization, JWT auth, CSRF/XSS protection, role-based access control |
| Usability        | Responsive dashboards; Intuitive ad submission form                                           |
| Scalability      | Support 1000+ concurrent advertisers; horizontal scaling supported                            |
| Reliability      | Analytics updates in real-time; Transactions are ACID compliant                               |

---

## **5. Data Requirements**

### 5.1 Database Tables

| Table Name    | Purpose                                                                |
| ------------- | ---------------------------------------------------------------------- |
| users         | Advertiser & admin details                                             |
| ads           | Ad information (title, description, image, URL, status, dates, budget) |
| ad_analytics  | Views, clicks, CTR, timestamps                                         |
| ad_payments   | Payment transactions                                                   |
| ad_targets    | Targeting preferences (location, interest)                             |
| ad_placements | Ad placement locations                                                 |

### 5.2 Data Flow

1. Advertiser submits ad → saved in `ads` table
2. Approved ads → displayed dynamically → impressions/clicks logged in `ad_analytics`
3. Paid ads → payment recorded in `ad_payments` → update ad priority
4. Analytics dashboard pulls data from `ad_analytics`
5. Notifications triggered based on ad events

---

## **6. Interface Requirements**

### 6.1 UI/UX

* Advertiser Dashboard: create/edit/delete ads, analytics charts
* Admin Dashboard: approve/reject, assign placements, view analytics
* Reusable Ad Display Components: Banner, Sidebar, Inline

### 6.2 API Endpoints (Express Backend)

| Endpoint         | Method | Description     | Request Body                                                      | Response                |
| ---------------- | ------ | --------------- | ----------------------------------------------------------------- | ----------------------- |
| /ads             | POST   | Create ad       | JSON: title, desc, image_url, target_url, category, dates, budget | 201 Created + Ad ID     |
| /ads             | GET    | Fetch ads       | Query params: status, category, advertiser                        | 200 OK + List of ads    |
| /ads/:id         | PUT    | Update ad       | JSON fields to update                                             | 200 OK + Updated ad     |
| /ads/:id         | DELETE | Delete ad       | N/A                                                               | 200 OK + message        |
| /analytics/:adId | GET    | Fetch analytics | adId param                                                        | 200 OK + metrics        |
| /payments        | POST   | Process payment | JSON: adId, amount, userId                                        | 200 OK + payment status |

### 6.3 Integration Points

* Authentication Module (JWT-based)
* Billing / Payment Gateway
* Notification Service

---

## **7. Traceability Matrix**

| Requirement ID | Functional Requirement   | Business Objective                               |
| -------------- | ------------------------ | ------------------------------------------------ |
| FR-1           | Ad Creation & Submission | Allow advertisers to submit ads efficiently      |
| FR-2           | Advertiser Dashboard     | Manage ads & track performance                   |
| FR-3           | Admin Panel              | Ensure content compliance and policy enforcement |
| FR-4           | Ad Display System        | Show ads dynamically to users                    |
| FR-5           | Analytics & Reporting    | Provide insights & performance metrics           |
| FR-6           | Payment & Plans          | Monetize ad campaigns                            |
| FR-7           | Targeting & Scheduling   | Deliver ads to relevant audience                 |
| FR-8           | Notifications & Alerts   | Keep advertisers informed of ad status           |

---

## **8. Appendices**

### 8.1 Glossary

* CTR: Click-through rate
* Admin: User managing ads and placements
* Advertiser: User creating ads

### 8.2 Revision History

| Version | Date       | Author          | Description                                                           |
| ------- | ---------- | --------------- | --------------------------------------------------------------------- |
| 1.0     | 2025-10-11 | Anusha Devadiga | Initial Draft                                                         |
| 1.1     | 2025-10-11 | Anusha Devadiga | Added ER diagram, data flow, and API details                          |
| 1.2     | 2025-10-11 | Anusha Devadiga | Added traceability matrix, assumptions, dependencies, quantified NFRs |

### 8.3 Mockups / Diagrams

* ER Diagram (Users, Ads, Payments, Analytics)
* Data Flow Diagram: Ad submission → Display → Analytics → Notifications

---

## **9. Review and Approval Checklist**

| Item                                     | Status |
| ---------------------------------------- | ------ |
| Functional requirements clearly defined  | ✅      |
| Non-functional requirements documented   | ✅      |
| Database tables and ER diagrams included | ✅      |
| API endpoints listed with examples       | ✅      |
| Payment handling described               | ✅      |
| Traceability matrix included             | ✅      |
| Version control maintained               | ✅      |
| Stakeholder review completed             | ✅      |

---
erDiagram
    USERS {
        int user_id PK
        string name
        string email
        string role
    }

    ADS {
        int ad_id PK
        int user_id FK
        string title
        string description
        string image_url
        string target_url
        string category
        date start_date
        date end_date
        string status
        float budget
    }

    AD_ANALYTICS {
        int analytics_id PK
        int ad_id FK
        int views
        int clicks
        float ctr
        datetime timestamp
    }

    AD_PAYMENTS {
        int payment_id PK
        int ad_id FK
        int user_id FK
        float amount
        string payment_method
        datetime payment_date
        string status
    }

    AD_TARGETS {
        int target_id PK
        int ad_id FK
        string location
        string interest
    }

    AD_PLACEMENTS {
        int placement_id PK
        int ad_id FK
        string placement_type
        string page_section
    }

    USERS ||--o{ ADS : "creates"
    ADS ||--o{ AD_ANALYTICS : "logs"
    ADS ||--o{ AD_PAYMENTS : "paid via"
    ADS ||--o{ AD_TARGETS : "targeted by"
    ADS ||--o{ AD_PLACEMENTS : "placed at"
---
