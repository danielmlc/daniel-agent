import { Module } from '@nestjs/common';
import { GithubModule } from '../github/github.module';
import { OrchestratorService } from './orchestrator.service';

@Module({
  imports: [GithubModule], // Import GithubModule to use GithubService
  providers: [OrchestratorService],
})
export class OrchestratorModule {}
