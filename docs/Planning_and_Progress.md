# Planning & Progress

## 1. High-Level Roadmap

### Phase 1: Core Features
- Set up Flask routes, define data models, and implement a basic TDD structure.
- Provide an initial UI with tag-based filtering for stipends.

### Phase 2: Automation & Admin Tools
- Develop automated bots for stipend tagging, updates, and validations.
- Enhance the admin interface with complete CRUD functionality and robust security.

### Phase 3: Production Readiness
- Integrate and test automated backups, finalize semantic versioning, and implement a structured release process.
- Conduct performance and security reviews before going live.

## 2. Milestone Breakdown

| Milestone                | Tasks                                                          | Status       |
|--------------------------|----------------------------------------------------------------|-------------|
| **M1 – MVP**            | Flask setup, DB models, TDD harness, basic filtering           | In Progress |
| **M2 – Admin Interface** | Complete admin CRUD, add authentication, refine tests          | Planned     |
| **M3 – Automated Bots**  | Implement tagging & validation bots, integrate migrations      | Planned     |
| **M4 – Production**      | Backup management, log archiving, final release packaging      | Planned     |

## 3. Sprint & Task Organization

- **User Stories**
  - “As an admin, I need to create and update stipends quickly so new opportunities are available.”
  - “As a user, I want to filter stipends by tags for relevant opportunities.”

- **Branching Strategy**
  - Create feature branches, e.g., `feature/<short_description>`.
  - Merge via pull requests with tests and clear summaries.

## 4. Risk & Mitigation

- **Risk**: Delays or instability from insufficient testing.  
  **Mitigation**: Enforce TDD, code reviews, and limit pull requests to small, focused changes.

- **Risk**: Data/config issues during production deployment.  
  **Mitigation**: Thoroughly test Alembic migrations in staging, keep frequent backups, follow a structured release process.
