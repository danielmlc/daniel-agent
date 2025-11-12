import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { InformationEntry } from '../database/entry.entity';
import { GithubService } from './github.service';

@Module({
  imports: [TypeOrmModule.forFeature([InformationEntry])],
  providers: [GithubService],
  exports: [GithubService], // Export GithubService to make it available to other modules
})
export class GithubModule {}
