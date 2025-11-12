
## 个人智能助理 (NestJS + LangChain.js) 技术规划

### 1\. 项目愿景与目标

(与你的文档一致)
旨在开发一个基于 **NestJS 框架**、由 **LangChain.js** 驱动的、个性化的、团队协作式智能助理系统。该系统通过模拟一个由多个职能`Service`（服务）组成的助理团队，主动为用户完成信息整理、工作同步、健康管理和日程规划等任务，最终成为一个高效、智能的个人中枢。

### 2\. 系统整体架构

#### 核心框架 (Core Framework)

  * **后端应用框架: NestJS**

      * 我们将使用 NestJS 作为常驻后台应用的主体。
      * **理由:** 你的技术栈偏好（从历史中得知）与 NestJS 高度契合。其强大的**模块化（Modules）系统和依赖注入（Dependency Injection）特性，使我们能将每一个“智能体”清晰地实现为服务（Providers / Services）**，并能轻松地在“管家”服务中注入和调用它们。

  * **Agent 引擎: LangChain.js (TypeScript)**

      * 我们将使用 `langchain-ts` 来处理所有与 LLM 相关的任务：包括调用模型、构建提示词、数据解析以及**工具使用（Tools）**。
      * **理由:** 它与 TypeScript 和 NestJS 生态无缝集成。我们将用它来为我们的 NestJS 服务赋予“智能”。

#### 运行模式 (Execution Model)

  * **常驻后台应用: NestJS Application**

      * 整个系统将是一个标准的 NestJS `main.ts` 启动的后台服务。

  * **内置调度器: `@nestjs/schedule`**

      * 我们将使用 NestJS 的官方 `schedule` 模块（基于 `node-cron`）来代替 APScheduler。
      * **实现:** 在“个人管家”服务中，我们将使用 `@Cron()` 装饰器来触发（如 `CronJob('0 8 * * *')`）每日简报任务。

#### 数据存储 (Data Storage)

  * **数据库: TypeORM + SQLite**
      * **ORM:** 使用 **TypeORM**，这是 NestJS 生态中最成熟的 ORM。
      * **数据库:** 依旧选用 **SQLite**。TypeORM 对 SQLite 有出色的支持，这使我们既能享受 SQLite 的轻量级，又能获得\*\*实体（Entities）**和**仓库（Repositories）\*\*带来的结构化数据管理能力。
  * **数据格式: 结构化实体 (Entities)**
      * 我们将定义一个核心的 `InformationEntry` 实体，而不是存储为简单文本。
    <!-- end list -->
    ```typescript
    // src/database/entry.entity.ts
    import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn } from 'typeorm';

    @Entity()
    export class InformationEntry {
      @PrimaryGeneratedColumn('uuid')
      id: string;

      @Column('text')
      content: string; // 智能体处理后的摘要内容

      @Column()
      source: string; // 来源, e.g., 'github', 'email', 'rss'

      @Column('simple-array') // 使用 simple-array 存储标签
      tags: string[];

      @CreateDateColumn()
      createdAt: Date;
    }
    ```
  * **数据组织:** 采用 `tags` 字段（如上）来实现你的标签系统。

-----

### 3\. 智能体团队设计 (NestJS 模块化实现)

在 NestJS 架构中，我们将你设计的“智能体角色”映射为**专职的 NestJS 服务（Providers）**。这些服务将被一个总管服务（`OrchestratorService`）所调用。

| 原始角色 (CrewAI) | NestJS 实现 (Provider) | 核心职责 (Responsibilities) | 依赖工具/库 (Tools/Libraries) |
| :--- | :--- | :--- | :--- |
| **个人管家** | `OrchestratorService` | **团队领导。** 被 `@Cron` 触发；负责调用其他服务（`githubService`, `emailService` 等）并收集结果；使用 **LangChain** 对所有结果进行最终汇总和分析；调用 `NotificationService` 推送报告。 | `TypeORM Repository`, `langchain/chains` (Summarization) |
| **信息分析师** | `WebScraperService` | 监控 RSS源 和指定网站。 | `axios` (HTTP), `cheerio` (HTML解析), `rss-parser` |
| **邮件处理器** | `EmailService` | 登录邮箱，抓取、分类和摘要邮件。 | `imap-simple`, `googleapis` (Gmail) |
| **GitHub 助手** | `GithubService` | 从 GitHub API 获取动态，整理 PR 和 Commits。 | `@octokit/rest` (GitHub官方JS库) |
| **健康顾问** | `WellnessService` | (同左) | Apple Health / Google Fit API SDK |
| **任务规划师** | `TaskPlannerService` | (同左) | Google Calendar API |
| (新增) | `NotificationService` | 专门负责发送消息。 | `axios` (用于调用企业微信/Telegram Bot Webhook) |

-----

### 4\. 核心工作流 (NestJS + LangChain.js)

这是一个典型的“每日简报”工作流在 NestJS 架构下的实现：

1.  **触发 (Trigger):**

      * `@nestjs/schedule` 的 `@Cron('0 8 * * *')` 装饰器准时触发 `OrchestratorService` 中的 `handleDailyBriefing()` 方法。

2.  **任务分配 (Delegation/Execution):**

      * `OrchestratorService` 通过依赖注入，并行调用（使用 `Promise.all`）各个职能服务：

    <!-- end list -->

    ```typescript
    // src/orchestrator/orchestrator.service.ts
    @Injectable()
    export class OrchestratorService {
      constructor(
        private readonly githubService: GithubService,
        private readonly webScraperService: WebScraperService,
        private readonly emailService: EmailService,
        // ... 注入其他服务
      ) {}

      @Cron('0 8 * * *')
      async handleDailyBriefing() {
        // 1. 并行执行所有信息抓取任务
        await Promise.all([
          this.githubService.fetchAndStoreUpdates(),
          this.webScraperService.fetchAndStoreRss(),
          this.emailService.fetchAndStoreSummary(),
        ]);

        // ... (下一步：汇总与分析)
      }
    }
    ```

3.  **执行与数据存储 (Execution & Storage):**

      * 以 `GithubService` 为例：
          * `fetchAndStoreUpdates()` 方法被调用。
          * 它使用 `@octokit/rest` 库请求 GitHub API。
          * (可选) 它使用一个简单的 **LangChain.js 链**（`PromptTemplate` + `ChatModel`）来将 API 返回的 JSON 格式化为人类可读的摘要。
          * 它注入 `Repository<InformationEntry>`，并将格式化后的结果存入 SQLite：
        <!-- end list -->
        ```typescript
        // 示例：github.service.ts
        // ...
        await this.entryRepository.save({
          content: "今日代码提交总结...",
          source: 'github',
          tags: ['github', 'work-summary', '2025-11-12']
        });
        ```

4.  **汇总与分析 (Aggregation & Analysis):**

      * 回到 `OrchestratorService`，在 `Promise.all` 完成后，它从数据库中查询当天所有新存入的数据。

    <!-- end list -->

    ```typescript
    // src/orchestrator/orchestrator.service.ts (续)
        // 2. 从数据库汇总所有刚抓取的数据
        const todayEntries = await this.entryRepository.find({ /* ...查询条件... */ });
        const rawContext = todayEntries.map(e => `[${e.source}]: ${e.content}`).join('\n');

        // 3. 使用 LangChain 进行最终汇总
        const finalReport = await this.summarizeWithLangChain(rawContext);

        // 4. 交付
        await this.notificationService.send(finalReport);
    }
    ```

      * `summarizeWithLangChain()` 方法将使用一个专门的 **LangChain 汇总链**（e.g., `loadSummarizationChain`）来生成那份“个人管家”风格的综合报告。

5.  **交付与交互 (Delivery & Interaction):**

      * `OrchestratorService` 调用 `NotificationService`，将最终报告通过 Webhook 推送给用户。

-----

### 5\. 具体工具实现 - 以 `GithubService` (TS) 为例

为了实现 `GitHub 工作助手`，我们不再需要 CrewAI 的 "Tool" 定义，而是将其实现为一个功能内聚的 NestJS 模块。

1.  **创建模块 (`GithubModule`):**

      * 使用 NestJS CLI: `nest g module github`
      * 使用 NestJS CLI: `nest g service github`

2.  **定义服务 (`GithubService`):**

    ```typescript
    // src/github/github.service.ts
    import { Injectable } from '@nestjs/common';
    import { ConfigService } from '@nestjs/config';
    import { InjectRepository } from '@nestjs/typeorm';
    import { Repository } from 'typeorm';
    import { InformationEntry } from '../database/entry.entity';
    import { Octokit } from '@octokit/rest';

    // 导入 LangChain 相关
    import { ChatOpenAI } from '@langchain/openai';
    import { PromptTemplate } from '@langchain/core/prompts';
    import { StringOutputParser } from '@langchain/core/output_parsers';

    @Injectable()
    export class GithubService {
      private octokit: Octokit;
      private llm: ChatOpenAI;
      private summarizationChain: any; // LangChain RunnableSequence

      constructor(
        private readonly configService: ConfigService,
        @InjectRepository(InformationEntry)
        private readonly entryRepository: Repository<InformationEntry>,
      ) {
        this.octokit = new Octokit({ auth: this.configService.get('GITHUB_TOKEN') });
        this.llm = new ChatOpenAI({ modelName: 'gpt-4o' });

        // 2. 定义 LangChain 格式化链
        const prompt = PromptTemplate.fromTemplate(
          "你是一个专业的技术主管。请根据以下 GitHub 活动 JSON 数据，为我生成一份简洁的中文摘要报告，说明谁做了什么。\n数据: {activity_json}"
        );
        this.summarizationChain = prompt.pipe(this.llm).pipe(new StringOutputParser());
      }

      // 3. 核心执行方法 (被 OrchestratorService 调用)
      async fetchAndStoreUpdates() {
        // 1. 使用 Octokit (TS库) 获取数据
        const { data: commits } = await this.octokit.repos.listCommits({
          owner: 'your-org',
          repo: 'your-repo',
          // ... 其他参数
        });

        // (此处省略获取 PRs 和 Issues 的代码)
        const rawActivity = { commits /*, prs, issues */ };

        // 2. 使用 LangChain 链进行总结
        const summary = await this.summarizationChain.invoke({
          activity_json: JSON.stringify(rawActivity),
        });

        // 3. 存入数据库
        await this.entryRepository.save({
          content: summary,
          source: 'github',
          tags: ['github', 'code', 'daily'],
        });
      }
    }
    ```

