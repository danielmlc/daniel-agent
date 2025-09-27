from abc import ABC, abstractmethod
from typing import Dict, List, Any
import logging
import time
from datetime import datetime

class BaseAgent(ABC):
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.logger = logging.getLogger(f"agent.{name}")
        self.performance_metrics = {
            'success_rate': 1.0,  # Start with 100% success
            'avg_response_time': 0.0,
            'error_count': 0,
            'last_execution': None,
            'total_executions': 0
        }

    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务的抽象方法"""
        pass

    async def execute_with_fallback(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """带容错的执行方法"""
        self.performance_metrics['last_execution'] = datetime.now().isoformat()
        self.performance_metrics['total_executions'] += 1

        try:
            start_time = time.time()
            result = await self.execute(task)

            # 更新性能指标
            execution_time = time.time() - start_time
            self.update_metrics(success=True, response_time=execution_time)

            return {
                'status': 'success',
                'data': result,
                'agent': self.name,
                'execution_time': execution_time
            }

        except Exception as e:
            self.logger.error(f"Task execution failed for agent {self.name}: {e}", exc_info=True)
            self.update_metrics(success=False)

            # 执行降级策略
            fallback_result = await self.fallback_strategy(task, e)
            return {
                'status': 'fallback',
                'data': fallback_result,
                'agent': self.name,
                'error': str(e)
            }

    async def fallback_strategy(self, task: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """降级策略 - 子类可覆盖"""
        self.logger.warning(f"Executing fallback for agent {self.name} due to error: {error}")
        return {
            'message': f'Agent {self.name} encountered an error but provided basic fallback.',
            'error_type': type(error).__name__,
            'timestamp': datetime.now().isoformat()
        }

    def update_metrics(self, success: bool, response_time: float = None):
        """更新性能指标"""
        total = self.performance_metrics['total_executions']

        if success:
            if response_time is not None:
                # 使用指数移动平均更新响应时间
                current_avg_time = self.performance_metrics['avg_response_time']
                if total == 1:
                     self.performance_metrics['avg_response_time'] = response_time
                else:
                    self.performance_metrics['avg_response_time'] = 0.9 * current_avg_time + 0.1 * response_time

            # 更新成功率
            current_success_rate = self.performance_metrics['success_rate']
            self.performance_metrics['success_rate'] = (current_success_rate * (total -1) + 1) / total

        else:
            self.performance_metrics['error_count'] += 1
            current_success_rate = self.performance_metrics['success_rate']
            self.performance_metrics['success_rate'] = (current_success_rate * (total -1)) / total