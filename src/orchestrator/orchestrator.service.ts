import { Injectable, Logger } from '@nestjs/common';
import { Cron } from '@nestjs/schedule';
import { GithubService } from '../github/github.service';

@Injectable()
export class OrchestratorService {
  private readonly logger = new Logger(OrchestratorService.name);

  constructor(private readonly githubService: GithubService) {}

  @Cron('0 8 * * *') // Run every day at 8:00 AM
  async handleDailyBriefing() {
    this.logger.log('Starting daily briefing task...');

    // For now, we only have the GitHub service.
    // In the future, we will use Promise.all to run multiple services in parallel.
    await this.githubService.fetchAndStoreUpdates();

    this.logger.log('Daily briefing task finished.');

    // The next steps from plan.md (aggregation, analysis, notification) will be added here later.
  }
}
