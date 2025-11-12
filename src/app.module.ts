import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { ScheduleModule } from '@nestjs/schedule';
import { TypeOrmModule } from '@nestjs/typeorm';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { InformationEntry } from './database/entry.entity';
import { GithubModule } from './github/github.module';
import { OrchestratorModule } from './orchestrator/orchestrator.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true, // Make the config module available globally
    }),
    ScheduleModule.forRoot(), // Initialize the task scheduler
    TypeOrmModule.forRoot({
      type: 'sqlite',
      database: 'assistant.db',
      entities: [InformationEntry],
      synchronize: true, // Auto-create database schema. Don't use in production.
    }),
    GithubModule,
    OrchestratorModule,
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
