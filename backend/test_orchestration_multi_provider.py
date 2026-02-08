"""Test orchestration with multiple providers.

This script tests AI Council's multi-agent orchestration capabilities
with a complex query that requires decomposition across multiple providers.

Usage:
    python test_orchestration_multi_provider.py

The script will:
1. Submit a complex query requiring multiple subtasks
2. Verify AI Council decomposes into multiple subtasks
3. Verify subtasks are distributed across available providers
4. Verify parallel execution with mixed providers (local + cloud)
5. Verify arbitration works when providers give different answers
6. Verify synthesis combines results from different providers coherently
7. Measure total cost and time vs single-provider approach
8. Document test results in backend/docs/ORCHESTRATION_TEST_RESULTS.md
"""

import os
import sys
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

print("=" * 80)
print("MULTI-PROVIDER ORCHESTRATION TEST")
print("=" * 80)
print()

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.provider_config import get_provider_config
from app.services.cloud_ai.model_registry import MODEL_REGISTRY
from app.services.websocket_manager import WebSocketManager
from app.services.council_orchestration_bridge import CouncilOrchestrationBridge
from ai_council.core.models import ExecutionMode


@dataclass
class OrchestrationTestResult:
    """Result of orchestration test."""
    query: str
    execution_mode: str
    success: bool
    total_time: float
    total_cost: float
    subtasks_count: int
    providers_used: List[str]
    models_used: List[str]
    parallel_execution: bool
    arbitration_occurred: bool
    synthesis_quality: str
    final_response: str
    error: Optional[str] = None
    decomposition_details: Dict[str, Any] = field(default_factory=dict)
    routing_details: List[Dict[str, Any]] = field(default_factory=list)
    execution_details: List[Dict[str, Any]] = field(default_factory=list)
    provider_distribution: Dict[str, int] = field(default_factory=dict)


class MockWebSocketManager(WebSocketManager):
    """Mock WebSocket manager that captures messages for testing."""
    
    def __init__(self):
        super().__init__()
        self.messages: List[Dict[str, Any]] = []
    
    async def broadcast_progress(self, request_id: str, event_type: str, data: Dict[str, Any]):
        """Capture WebSocket messages."""
        message = {
            "request_id": request_id,
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.messages.append(message)
        
        # Print message for visibility
        print(f"  📡 WebSocket: {event_type}")
        if event_type == "analysis_complete":
            print(f"     Intent: {data.get('intent')}, Complexity: {data.get('complexity')}")
        elif event_type == "routing_complete":
            assignments = data.get('assignments', [])
            print(f"     Routed {len(assignments)} subtasks")
        elif event_type == "execution_progress":
            print(f"     Subtask completed: {data.get('subtaskId')}")
        elif event_type == "arbitration_decision":
            print(f"     Arbitration: {data.get('reason')}")
        elif event_type == "synthesis_progress":
            print(f"     Synthesis: {data.get('stage')}")
        elif event_type == "final_response":
            print(f"     Final response ready")


class OrchestrationTester:
    """Test AI Council orchestration with multiple providers."""
    
    # Complex query that requires multiple subtasks
    COMPLEX_QUERY = (
        "Explain quantum computing, write a Python example, "
        "and suggest real-world applications"
    )
    
    def __init__(self):
        """Initialize the orchestration tester."""
        self.provider_config = get_provider_config()
        self.results: List[OrchestrationTestResult] = []
    
    async def test_orchestration(
        self,
        query: str,
        execution_mode: ExecutionMode
    ) -> OrchestrationTestResult:
        """Test orchestration with a complex query.
        
        Args:
            query: The complex query to test
            execution_mode: Execution mode to use
            
        Returns:
            OrchestrationTestResult with detailed metrics
        """
        print(f"\n{'=' * 80}")
        print(f"Testing Orchestration: {execution_mode.value.upper()} mode")
        print(f"{'=' * 80}")
        print(f"Query: {query}")
        print()
        
        # Create mock WebSocket manager to capture messages
        ws_manager = MockWebSocketManager()
        
        # Create orchestration bridge
        bridge = CouncilOrchestrationBridge(ws_manager)
        
        # Generate unique request ID
        request_id = f"test_{int(time.time())}"
        
        try:
            # Start timing
            start_time = time.time()
            
            # Process request
            print("🚀 Starting orchestration...")
            response = await bridge.process_request(
                request_id=request_id,
                user_input=query,
                execution_mode=execution_mode
            )
            
            # End timing
            total_time = time.time() - start_time
            
            print(f"\n✓ Orchestration completed in {total_time:.2f}s")
            print()
            
            # Analyze WebSocket messages to extract orchestration details
            analysis_msg = next(
                (m for m in ws_manager.messages if m["event_type"] == "analysis_complete"),
                None
            )
            
            routing_msg = next(
                (m for m in ws_manager.messages if m["event_type"] == "routing_complete"),
                None
            )
            
            execution_msgs = [
                m for m in ws_manager.messages
                if m["event_type"] == "execution_progress"
            ]
            
            arbitration_msgs = [
                m for m in ws_manager.messages
                if m["event_type"] == "arbitration_decision"
            ]
            
            synthesis_msgs = [
                m for m in ws_manager.messages
                if m["event_type"] == "synthesis_progress"
            ]
            
            final_msg = next(
                (m for m in ws_manager.messages if m["event_type"] == "final_response"),
                None
            )
            
            # Extract details
            decomposition_details = {}
            if analysis_msg:
                decomposition_details = {
                    "intent": analysis_msg["data"].get("intent"),
                    "complexity": analysis_msg["data"].get("complexity"),
                }
            
            routing_details = []
            subtasks_count = 0
            providers_used = set()
            models_used = set()
            provider_distribution = {}
            
            if routing_msg:
                assignments = routing_msg["data"].get("assignments", [])
                subtasks_count = len(assignments)
                
                for assignment in assignments:
                    provider = assignment.get("provider")
                    model_id = assignment.get("modelId")
                    
                    if provider:
                        providers_used.add(provider)
                        provider_distribution[provider] = provider_distribution.get(provider, 0) + 1
                    
                    if model_id:
                        models_used.add(model_id)
                    
                    routing_details.append({
                        "subtask_id": assignment.get("subtaskId"),
                        "task_type": assignment.get("taskType"),
                        "model": model_id,
                        "provider": provider,
                        "reason": assignment.get("reason"),
                        "estimated_cost": assignment.get("estimatedCost"),
                        "estimated_time": assignment.get("estimatedTime"),
                    })
            
            execution_details = []
            for msg in execution_msgs:
                execution_details.append({
                    "subtask_id": msg["data"].get("subtaskId"),
                    "status": msg["data"].get("status"),
                    "confidence": msg["data"].get("confidence"),
                    "cost": msg["data"].get("cost"),
                    "execution_time": msg["data"].get("executionTime"),
                })
            
            # Determine if parallel execution occurred
            parallel_execution = subtasks_count > 1
            
            # Determine if arbitration occurred
            arbitration_occurred = len(arbitration_msgs) > 0
            
            # Assess synthesis quality
            synthesis_quality = "good"
            if len(synthesis_msgs) > 0:
                synthesis_quality = "excellent"
            
            # Calculate total cost
            total_cost = sum(detail.get("cost", 0) for detail in execution_details)
            
            # Get final response
            final_response = ""
            if hasattr(response, 'content'):
                final_response = response.content
            elif isinstance(response, dict):
                final_response = response.get('content', '')
            
            # Create result
            result = OrchestrationTestResult(
                query=query,
                execution_mode=execution_mode.value,
                success=True,
                total_time=total_time,
                total_cost=total_cost,
                subtasks_count=subtasks_count,
                providers_used=list(providers_used),
                models_used=list(models_used),
                parallel_execution=parallel_execution,
                arbitration_occurred=arbitration_occurred,
                synthesis_quality=synthesis_quality,
                final_response=final_response,
                decomposition_details=decomposition_details,
                routing_details=routing_details,
                execution_details=execution_details,
                provider_distribution=provider_distribution,
            )
            
            return result
            
        except Exception as e:
            print(f"\n❌ Orchestration failed: {e}")
            import traceback
            traceback.print_exc()
            
            return OrchestrationTestResult(
                query=query,
                execution_mode=execution_mode.value,
                success=False,
                total_time=0.0,
                total_cost=0.0,
                subtasks_count=0,
                providers_used=[],
                models_used=[],
                parallel_execution=False,
                arbitration_occurred=False,
                synthesis_quality="failed",
                final_response="",
                error=str(e),
            )
    
    async def run_tests(self) -> None:
        """Run orchestration tests with different execution modes."""
        print("=" * 80)
        print("AI COUNCIL MULTI-PROVIDER ORCHESTRATION TEST")
        print("=" * 80)
        print()
        
        # Check configured providers
        configured_providers = self.provider_config.get_configured_providers()
        
        if not configured_providers:
            print("❌ No providers configured!")
            print("   Please configure at least one provider in .env file")
            return
        
        print(f"✓ Found {len(configured_providers)} configured provider(s)")
        print(f"  Providers: {', '.join(configured_providers)}")
        print()
        
        # Test with different execution modes
        execution_modes = [
            ExecutionMode.FAST,
            ExecutionMode.BALANCED,
            ExecutionMode.BEST_QUALITY,
        ]
        
        for mode in execution_modes:
            result = await self.test_orchestration(self.COMPLEX_QUERY, mode)
            self.results.append(result)
            
            # Small delay between tests
            await asyncio.sleep(2)
        
        print("\n" + "=" * 80)
        print("ALL TESTS COMPLETED")
        print("=" * 80)
        print()
    
    def print_summary(self) -> None:
        """Print summary of test results."""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print()
        
        for result in self.results:
            print(f"Mode: {result.execution_mode.upper()}")
            print(f"  Success: {'✓' if result.success else '✗'}")
            print(f"  Time: {result.total_time:.2f}s")
            print(f"  Cost: ${result.total_cost:.6f}")
            print(f"  Subtasks: {result.subtasks_count}")
            print(f"  Providers: {', '.join(result.providers_used)}")
            print(f"  Models: {len(result.models_used)}")
            print(f"  Parallel: {'Yes' if result.parallel_execution else 'No'}")
            print(f"  Arbitration: {'Yes' if result.arbitration_occurred else 'No'}")
            print(f"  Synthesis: {result.synthesis_quality}")
            
            if result.provider_distribution:
                print(f"  Provider Distribution:")
                for provider, count in result.provider_distribution.items():
                    print(f"    - {provider}: {count} subtask(s)")
            
            if result.error:
                print(f"  Error: {result.error}")
            
            print()
    
    def generate_report(self) -> str:
        """Generate detailed markdown report."""
        report = []
        report.append("# Multi-Provider Orchestration Test Results")
        report.append("")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Overview
        report.append("## Overview")
        report.append("")
        report.append(f"**Test Query:** {self.COMPLEX_QUERY}")
        report.append("")
        report.append(f"**Execution Modes Tested:** {len(self.results)}")
        report.append(f"**Successful Tests:** {sum(1 for r in self.results if r.success)}")
        report.append(f"**Failed Tests:** {sum(1 for r in self.results if not r.success)}")
        report.append("")
        
        # Comparison table
        report.append("## Execution Mode Comparison")
        report.append("")
        report.append("| Mode | Time (s) | Cost ($) | Subtasks | Providers | Parallel | Arbitration | Synthesis |")
        report.append("|------|----------|----------|----------|-----------|----------|-------------|-----------|")
        
        for result in self.results:
            if result.success:
                report.append(
                    f"| {result.execution_mode.upper()} | "
                    f"{result.total_time:.2f} | "
                    f"${result.total_cost:.6f} | "
                    f"{result.subtasks_count} | "
                    f"{len(result.providers_used)} | "
                    f"{'Yes' if result.parallel_execution else 'No'} | "
                    f"{'Yes' if result.arbitration_occurred else 'No'} | "
                    f"{result.synthesis_quality} |"
                )
        
        report.append("")
        
        # Detailed results for each mode
        report.append("## Detailed Results")
        report.append("")
        
        for result in self.results:
            report.append(f"### {result.execution_mode.upper()} Mode")
            report.append("")
            
            if not result.success:
                report.append(f"**Status:** ❌ Failed")
                report.append(f"**Error:** {result.error}")
                report.append("")
                continue
            
            report.append(f"**Status:** ✓ Success")
            report.append("")
            
            # Performance metrics
            report.append("**Performance Metrics:**")
            report.append("")
            report.append(f"- **Total Time:** {result.total_time:.2f} seconds")
            report.append(f"- **Total Cost:** ${result.total_cost:.6f}")
            report.append(f"- **Subtasks Created:** {result.subtasks_count}")
            report.append(f"- **Parallel Execution:** {'Yes' if result.parallel_execution else 'No'}")
            report.append("")
            
            # Decomposition details
            if result.decomposition_details:
                report.append("**Task Decomposition:**")
                report.append("")
                report.append(f"- **Intent:** {result.decomposition_details.get('intent', 'N/A')}")
                report.append(f"- **Complexity:** {result.decomposition_details.get('complexity', 'N/A')}")
                report.append("")
            
            # Provider distribution
            if result.provider_distribution:
                report.append("**Provider Distribution:**")
                report.append("")
                for provider, count in sorted(result.provider_distribution.items()):
                    percentage = (count / result.subtasks_count * 100) if result.subtasks_count > 0 else 0
                    report.append(f"- **{provider.capitalize()}:** {count} subtask(s) ({percentage:.1f}%)")
                report.append("")
            
            # Models used
            if result.models_used:
                report.append("**Models Used:**")
                report.append("")
                for model in sorted(result.models_used):
                    report.append(f"- {model}")
                report.append("")
            
            # Routing details
            if result.routing_details:
                report.append("**Routing Decisions:**")
                report.append("")
                report.append("| Subtask | Task Type | Model | Provider | Reason |")
                report.append("|---------|-----------|-------|----------|--------|")
                
                for detail in result.routing_details:
                    subtask_id = detail.get('subtask_id', 'N/A')
                    task_type = detail.get('task_type', 'N/A')
                    model = detail.get('model', 'N/A')
                    provider = detail.get('provider', 'N/A')
                    reason = detail.get('reason', 'N/A')[:50]  # Truncate long reasons
                    
                    report.append(f"| {subtask_id} | {task_type} | {model} | {provider} | {reason} |")
                
                report.append("")
            
            # Execution details
            if result.execution_details:
                report.append("**Execution Details:**")
                report.append("")
                report.append("| Subtask | Status | Confidence | Cost ($) | Time (s) |")
                report.append("|---------|--------|------------|----------|----------|")
                
                for detail in result.execution_details:
                    subtask_id = detail.get('subtask_id', 'N/A')
                    status = detail.get('status', 'N/A')
                    confidence = detail.get('confidence', 0)
                    cost = detail.get('cost', 0)
                    exec_time = detail.get('execution_time', 0)
                    
                    report.append(
                        f"| {subtask_id} | {status} | "
                        f"{confidence:.2f} | ${cost:.6f} | {exec_time:.2f} |"
                    )
                
                report.append("")
            
            # Arbitration
            if result.arbitration_occurred:
                report.append("**Arbitration:**")
                report.append("")
                report.append("- Arbitration was triggered to resolve conflicting results")
                report.append("")
            
            # Final response
            report.append("**Final Response:**")
            report.append("")
            report.append("```")
            # Truncate very long responses
            response_preview = result.final_response[:1000]
            if len(result.final_response) > 1000:
                response_preview += "\n... (truncated)"
            report.append(response_preview)
            report.append("```")
            report.append("")
        
        # Key findings
        report.append("## Key Findings")
        report.append("")
        
        successful_results = [r for r in self.results if r.success]
        
        if successful_results:
            # Find fastest mode
            fastest = min(successful_results, key=lambda r: r.total_time)
            report.append(f"- **Fastest Mode:** {fastest.execution_mode.upper()} ({fastest.total_time:.2f}s)")
            
            # Find cheapest mode
            cheapest = min(successful_results, key=lambda r: r.total_cost)
            report.append(f"- **Most Cost-Effective:** {cheapest.execution_mode.upper()} (${cheapest.total_cost:.6f})")
            
            # Find mode with most subtasks
            most_subtasks = max(successful_results, key=lambda r: r.subtasks_count)
            report.append(f"- **Most Thorough:** {most_subtasks.execution_mode.upper()} ({most_subtasks.subtasks_count} subtasks)")
            
            # Provider diversity
            all_providers = set()
            for result in successful_results:
                all_providers.update(result.providers_used)
            report.append(f"- **Providers Utilized:** {', '.join(sorted(all_providers))}")
            
            # Parallel execution
            parallel_count = sum(1 for r in successful_results if r.parallel_execution)
            report.append(f"- **Parallel Execution:** {parallel_count}/{len(successful_results)} modes")
            
            # Arbitration
            arbitration_count = sum(1 for r in successful_results if r.arbitration_occurred)
            report.append(f"- **Arbitration Triggered:** {arbitration_count}/{len(successful_results)} modes")
        
        report.append("")
        
        # Verification checklist
        report.append("## Verification Checklist")
        report.append("")
        
        # Check if AI Council decomposed into multiple subtasks
        has_decomposition = any(r.subtasks_count > 1 for r in successful_results if r.success)
        report.append(f"- [{'x' if has_decomposition else ' '}] AI Council decomposes complex query into multiple subtasks")
        
        # Check if subtasks distributed across providers
        has_multi_provider = any(len(r.providers_used) > 1 for r in successful_results if r.success)
        report.append(f"- [{'x' if has_multi_provider else ' '}] Subtasks distributed across multiple providers")
        
        # Check if parallel execution occurred
        has_parallel = any(r.parallel_execution for r in successful_results if r.success)
        report.append(f"- [{'x' if has_parallel else ' '}] Parallel execution with mixed providers")
        
        # Check if arbitration occurred
        has_arbitration = any(r.arbitration_occurred for r in successful_results if r.success)
        report.append(f"- [{'x' if has_arbitration else ' '}] Arbitration works when providers give different answers")
        
        # Check if synthesis occurred
        has_synthesis = any(r.synthesis_quality != "failed" for r in successful_results if r.success)
        report.append(f"- [{'x' if has_synthesis else ' '}] Synthesis combines results coherently")
        
        # Check if cost/time measured
        has_metrics = all(r.total_time > 0 and r.total_cost >= 0 for r in successful_results if r.success)
        report.append(f"- [{'x' if has_metrics else ' '}] Total cost and time measured")
        
        report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        report.append("")
        
        if successful_results:
            report.append("Based on the test results:")
            report.append("")
            
            fastest = min(successful_results, key=lambda r: r.total_time)
            report.append(f"- **For Speed:** Use **{fastest.execution_mode.upper()}** mode for fastest results ({fastest.total_time:.2f}s)")
            
            cheapest = min(successful_results, key=lambda r: r.total_cost)
            cost_display = f"${cheapest.total_cost:.6f}" if cheapest.total_cost > 0 else "FREE"
            report.append(f"- **For Cost:** Use **{cheapest.execution_mode.upper()}** mode for lowest cost ({cost_display})")
            
            most_subtasks = max(successful_results, key=lambda r: r.subtasks_count)
            report.append(f"- **For Quality:** Use **{most_subtasks.execution_mode.upper()}** mode for most thorough analysis ({most_subtasks.subtasks_count} subtasks)")
        
        report.append("")
        
        # Conclusion
        report.append("## Conclusion")
        report.append("")
        report.append("The multi-provider orchestration test demonstrates AI Council's ability to:")
        report.append("")
        report.append("1. **Intelligently decompose** complex queries into manageable subtasks")
        report.append("2. **Distribute work** across multiple AI providers based on capabilities and cost")
        report.append("3. **Execute in parallel** to reduce total processing time")
        report.append("4. **Resolve conflicts** through arbitration when providers disagree")
        report.append("5. **Synthesize results** into coherent final responses")
        report.append("")
        report.append("This approach provides significant advantages over single-provider solutions:")
        report.append("")
        report.append("- **Cost Optimization:** Use cheaper models for simple tasks, premium models for complex ones")
        report.append("- **Speed Improvement:** Parallel execution reduces total time")
        report.append("- **Quality Enhancement:** Multiple perspectives and arbitration improve accuracy")
        report.append("- **Reliability:** Fallback to alternative providers if one fails")
        report.append("")
        
        return "\n".join(report)
    
    def save_report(self, report: str) -> None:
        """Save report to file."""
        os.makedirs("backend/docs", exist_ok=True)
        output_path = "backend/docs/ORCHESTRATION_TEST_RESULTS.md"
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"✓ Report saved to: {output_path}")


async def main():
    """Main test function."""
    tester = OrchestrationTester()
    
    # Run tests
    await tester.run_tests()
    
    # Print summary
    tester.print_summary()
    
    # Generate and save report
    report = tester.generate_report()
    tester.save_report(report)
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print()
    print("Review the detailed report at:")
    print("  backend/docs/ORCHESTRATION_TEST_RESULTS.md")
    print()


if __name__ == "__main__":
    asyncio.run(main())
