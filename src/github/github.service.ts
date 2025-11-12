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
    this.llm = new ChatOpenAI({
      modelName: 'gpt-4o',
      apiKey: this.configService.get('OPENAI_API_KEY'),
    });

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
      owner: this.configService.get('GITHUB_ORG'),
      repo: this.configService.get('GITHUB_REPO'),
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
