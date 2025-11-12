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
