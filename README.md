# Personal AI Assistant (NestJS + LangChain.js)

## Project Vision

This project aims to develop a personalized, team-based intelligent assistant system powered by **NestJS** and **LangChain.js**. The system simulates a team of specialized AI agents (services) that proactively handle tasks like information gathering, work synchronization, and task planning for the user, ultimately becoming an efficient and intelligent personal hub.

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/personal-assistant.git
    cd personal-assistant
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Set up environment variables:**

    Create a `.env` file in the project root by copying the example file:
    ```bash
    cp .env.example .env
    ```

    Now, edit the `.env` file and provide your actual credentials:
    ```
    GITHUB_TOKEN=your_github_personal_access_token
    GITHUB_ORG=your_target_github_organization
    GITHUB_REPO=your_target_github_repository
    OPENAI_API_KEY=your_openai_api_key
    ```

### Running the Application

```bash
# development
npm run start

# watch mode
npm run start:dev

# production mode
npm run start:prod
```

## Core Technologies

- **Backend Framework:** [NestJS](https://nestjs.com/)
- **AI Engine:** [LangChain.js](https://js.langchain.com/)
- **Database:** [TypeORM](https://typeorm.io/) with SQLite
- **Task Scheduling:** `@nestjs/schedule`
