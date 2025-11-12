import { Test, TestingModule } from '@nestjs/testing';
import { ConfigService } from '@nestjs/config';
import { getRepositoryToken } from '@nestjs/typeorm';
import { GithubService } from './github.service';
import { InformationEntry } from '../database/entry.entity';

describe('GithubService', () => {
  let service: GithubService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        GithubService,
        {
          provide: ConfigService,
          useValue: {
            get: jest.fn((key: string) => {
              if (key === 'GITHUB_TOKEN') {
                return 'test-token';
              }
              return null;
            }),
          },
        },
        {
          provide: getRepositoryToken(InformationEntry),
          useValue: {
            save: jest.fn().mockResolvedValue(new InformationEntry()),
          },
        },
      ],
    }).compile();

    service = module.get<GithubService>(GithubService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });
});
