"""
Coordinator - Phase 2.4
Coordinador principal que orquesta la colaboración entre agentes.
Gestiona el flujo completo: Planner → Executor → Validator
"""

import time
import json
import psutil
import os
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
import sys
from pathlib import Path

# Añadir paths necesarios
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.planner_agent import planner_agent
from agents.executor_agent import executor_agent
from agents.validator_agent import validator_agent

# Import feedback system (with fallback if not available)
try:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from phase3.learning.feedback_collector import feedback_collector, ExecutionFeedback
    FEEDBACK_AVAILABLE = True
except ImportError:
    FEEDBACK_AVAILABLE = False
    feedback_collector = None

@dataclass
class MultiAgentResult:
    """Resultado completo del sistema multi-agente"""
    success: bool
    flag: str
    total_time: float
    agents_used: List[str]
    planner_result: Dict[str, Any]
    executor_result: Dict[str, Any]
    validator_result: Dict[str, Any]
    confidence: float
    quality_score: float

class MultiAgentCoordinator:
    """
    Coordinador Multi-Agente - Orquesta la colaboración entre agentes especializados
    """
    
    def __init__(self):
        self.name = "MultiAgentCoordinator"
        self.agents = {
            'planner': planner_agent,
            'executor': executor_agent,
            'validator': validator_agent
        }
        self.execution_history = []
    
    def solve_challenge(
        self, 
        challenge_description: str, 
        files: List[Dict[str, str]],
        max_execution_time: int = 300  # 5 minutos máximo
    ) -> MultiAgentResult:
        """
        Resuelve un challenge CTF usando arquitectura multi-agente
        """
        print("🚀 MULTI-AGENT SYSTEM ACTIVATED")
        print("=" * 60)
        print(f"Challenge: {challenge_description}")
        print(f"Files: {len(files)} file(s)")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # FASE 1: PLANIFICACIÓN
            print(f"\n📋 PHASE 1: STRATEGIC PLANNING")
            print("-" * 40)
            
            planner_start = time.time()
            execution_plan = self.agents['planner'].create_execution_plan(
                challenge_description, files
            )
            planner_time = time.time() - planner_start
            
            print(f"✅ Planning completed in {planner_time:.2f}s")
            
            # FASE 2: EJECUCIÓN
            print(f"\n⚡ PHASE 2: STRATEGY EXECUTION")
            print("-" * 40)
            
            executor_start = time.time()
            execution_result = self.agents['executor'].execute_plan(execution_plan)
            executor_time = time.time() - executor_start
            
            print(f"✅ Execution completed in {executor_time:.2f}s")
            
            # FASE 3: VALIDACIÓN
            print(f"\n🔍 PHASE 3: RESULT VALIDATION")
            print("-" * 40)
            
            validator_start = time.time()
            validation_result = self.agents['validator'].validate_execution_result(execution_result)
            validator_time = time.time() - validator_start
            
            print(f"✅ Validation completed in {validator_time:.2f}s")
            
            # COMPILAR RESULTADO FINAL
            total_time = time.time() - start_time
            
            success = execution_result.get('flag_found', False)
            flag = execution_result.get('final_flag', '')
            confidence = validation_result.get('confidence', 0.0)
            quality_score = validation_result.get('overall_quality', 0.0)
            
            result = MultiAgentResult(
                success=success,
                flag=flag,
                total_time=total_time,
                agents_used=['planner', 'executor', 'validator'],
                planner_result=execution_plan,
                executor_result=execution_result,
                validator_result=validation_result,
                confidence=confidence,
                quality_score=quality_score
            )
            
            # REPORTE FINAL
            self._print_final_report(result)
            
            # Guardar en historial
            self.execution_history.append({
                'timestamp': time.time(),
                'challenge_description': challenge_description,
                'result': result,
                'performance': {
                    'planner_time': planner_time,
                    'executor_time': executor_time,
                    'validator_time': validator_time,
                    'total_time': total_time
                }
            })
            
            # Recolectar feedback para aprendizaje (Phase 3.0)
            if FEEDBACK_AVAILABLE:
                self._collect_execution_feedback(
                    challenge_description, files, result, 
                    execution_plan, execution_result, validation_result
                )
            
            return result
            
        except Exception as e:
            print(f"\n❌ MULTI-AGENT SYSTEM ERROR: {str(e)}")
            
            # Resultado de error
            return MultiAgentResult(
                success=False,
                flag="",
                total_time=time.time() - start_time,
                agents_used=[],
                planner_result={},
                executor_result={},
                validator_result={},
                confidence=0.0,
                quality_score=0.0
            )
    
    def _print_final_report(self, result: MultiAgentResult):
        """
        Imprime reporte final del sistema multi-agente
        """
        print(f"\n" + "=" * 60)
        print(f"🎯 MULTI-AGENT SYSTEM FINAL REPORT")
        print(f"=" * 60)
        
        # Estado general
        status = "✅ SUCCESS" if result.success else "❌ FAILED"
        print(f"Status: {status}")
        print(f"Total Time: {result.total_time:.2f}s")
        print(f"Agents Used: {', '.join(result.agents_used)}")
        
        # Resultados por agente
        print(f"\n📊 AGENT PERFORMANCE:")
        
        # Planner
        planner_strategies = len(result.planner_result.get('strategies', []))
        planner_confidence = result.planner_result.get('confidence', 0.0)
        rag_patterns = result.planner_result.get('rag_patterns_count', 0)
        print(f"   🧠 Planner: {planner_strategies} strategies, {planner_confidence:.2f} confidence, {rag_patterns} RAG patterns")
        
        # Executor
        strategies_tried = result.executor_result.get('total_strategies_tried', 0)
        winning_strategy = result.executor_result.get('winning_strategy', 'none')
        print(f"   ⚡ Executor: {strategies_tried} strategies tried, winner: {winning_strategy}")
        
        # Validator
        validation_confidence = result.validator_result.get('confidence', 0.0)
        quality_score = result.quality_score
        print(f"   🔍 Validator: {validation_confidence:.2f} confidence, {quality_score:.2f} quality")
        
        # Flag encontrada
        if result.success:
            print(f"\n🎉 FLAG FOUND:")
            print(f"   {result.flag}")
            print(f"   Confidence: {result.confidence:.2f}")
            print(f"   Quality: {result.quality_score:.2f}")
        else:
            print(f"\n❌ NO FLAG FOUND")
            recommendations = result.validator_result.get('recommendations', [])
            if recommendations:
                print(f"   Recommendations:")
                for rec in recommendations[:3]:  # Top 3
                    print(f"   - {rec}")
        
        print(f"=" * 60)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de rendimiento del sistema
        """
        if not self.execution_history:
            return {"message": "No execution history available"}
        
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for h in self.execution_history if h['result'].success)
        
        avg_time = sum(h['performance']['total_time'] for h in self.execution_history) / total_executions
        avg_planner_time = sum(h['performance']['planner_time'] for h in self.execution_history) / total_executions
        avg_executor_time = sum(h['performance']['executor_time'] for h in self.execution_history) / total_executions
        avg_validator_time = sum(h['performance']['validator_time'] for h in self.execution_history) / total_executions
        
        avg_confidence = sum(h['result'].confidence for h in self.execution_history) / total_executions
        avg_quality = sum(h['result'].quality_score for h in self.execution_history) / total_executions
        
        return {
            'total_executions': total_executions,
            'success_rate': successful_executions / total_executions,
            'average_times': {
                'total': avg_time,
                'planner': avg_planner_time,
                'executor': avg_executor_time,
                'validator': avg_validator_time
            },
            'average_confidence': avg_confidence,
            'average_quality': avg_quality,
            'agent_usage': {
                'planner': total_executions,  # Siempre se usa
                'executor': total_executions,  # Siempre se usa
                'validator': total_executions   # Siempre se usa
            }
        }
    
    def _collect_execution_feedback(self, challenge_description: str, files: List[Dict[str, str]], 
                                  result: MultiAgentResult, execution_plan: Dict[str, Any],
                                  execution_result: Dict[str, Any], validation_result: Dict[str, Any]):
        """
        Recolecta feedback de la ejecución para el sistema de aprendizaje
        """
        try:
            # Obtener métricas del sistema
            process = psutil.Process(os.getpid())
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            cpu_usage = process.cpu_percent()
            
            # Extraer información de estrategias
            strategies_tried = []
            failed_strategies = []
            winning_strategy = None
            
            if 'strategies_attempted' in execution_result:
                for strategy in execution_result['strategies_attempted']:
                    strategy_info = {
                        'name': strategy.get('name', 'unknown'),
                        'priority': strategy.get('priority', 0),
                        'attempts': strategy.get('attempts', 0),
                        'success': strategy.get('success', False),
                        'time': strategy.get('time', 0.0)
                    }
                    strategies_tried.append(strategy_info)
                    
                    if strategy.get('success', False):
                        winning_strategy = strategy_info
                    else:
                        failed_strategies.append(strategy_info)
            
            # Crear feedback
            feedback = ExecutionFeedback(
                timestamp=datetime.now().isoformat(),
                challenge_id=f"challenge_{int(time.time())}",
                challenge_type=execution_plan.get('challenge_type', 'Unknown'),
                challenge_name=challenge_description[:100],  # Truncar si es muy largo
                success=result.success,
                flag_found=result.flag if result.success else None,
                total_time=result.total_time,
                confidence=result.confidence,
                quality_score=result.quality_score,
                
                # Agent performance
                agents_used=result.agents_used,
                planner_confidence=execution_plan.get('confidence', 0.0),
                planner_strategies=len(execution_plan.get('strategies', [])),
                planner_rag_patterns=execution_plan.get('rag_patterns_count', 0),
                executor_attempts=execution_result.get('total_attempts', 0),
                executor_success_strategy=winning_strategy.get('name') if winning_strategy else None,
                validator_confidence=validation_result.get('confidence', 0.0),
                
                # Strategy details
                strategies_tried=strategies_tried,
                winning_strategy=winning_strategy,
                failed_strategies=failed_strategies,
                
                # Error information
                errors=execution_result.get('errors', []),
                warnings=execution_result.get('warnings', []),
                
                # Context
                rag_context=execution_plan.get('rag_context', []),
                bert_prediction=execution_plan.get('challenge_type', 'Unknown'),
                bert_confidence=execution_plan.get('bert_confidence', 0.0),
                
                # Performance metrics
                memory_usage=memory_usage,
                cpu_usage=cpu_usage
            )
            
            # Enviar feedback al collector
            feedback_collector.collect_feedback(feedback)
            
        except Exception as e:
            print(f"⚠️ Warning: Could not collect feedback: {e}")

# Instancia global
multi_agent_coordinator = MultiAgentCoordinator()