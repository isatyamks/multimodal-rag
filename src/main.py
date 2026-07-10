import argparse
from typing import List, Union
from dotenv import load_dotenv

from src.infra.telemetry import setup_telemetry
from src.application.container import ApplicationContainer
from src.application.app import CodentirApplication
from src.core.llm import AgentMessage
from src.engine.triage.models import InvestigationRequest
from src.config.prompt import TRIAGE_AGENT_PROMPT

from rich.console import Console

console = Console()

def run_cli_triage(app: CodentirApplication) -> InvestigationRequest:
    """
    Handles the interactive CLI loop for refining an investigation query.
    """
    messages: List[AgentMessage] = [
        AgentMessage(role="system", content=TRIAGE_AGENT_PROMPT)
    ]
    
    initial_query = console.input("\n[bold cyan]What is the incident or query you want to investigate? [/bold cyan]\n> ")
    messages.append(AgentMessage(role="user", content=initial_query))
    
    # Use the context's triage agent to process the conversation
    agent = app.context.triage_agent
    
    while True:
        with console.status("[cyan]Triage Agent is thinking...[/cyan]", spinner="dots"):
            result: Union[InvestigationRequest, str] = agent.refine_query(messages, initial_query)
            
        if isinstance(result, InvestigationRequest):
            console.print(f"\n[bold green]✔ Triage complete! Finalized Query:[/bold green] {result.refined_query}\n")
            return result
            
        # If result is a string, the agent needs clarification
        console.print(f"\n[bold magenta]Triage Agent:[/bold magenta] {result}")
        user_reply = console.input("\n[bold cyan]You:[/bold cyan]\n> ")
        
        messages.append(AgentMessage(role="assistant", content=result))
        messages.append(AgentMessage(role="user", content=user_reply))


def main():
    parser = argparse.ArgumentParser(description="Codentir Investigation Engine CLI")
    parser.add_argument(
        "--tenant-id",
        type=str,
        default="tenant_default",
        help="Tenant ID for multi-tenant isolation",
    )
    args = parser.parse_args()

    load_dotenv()
    setup_telemetry()
    
    # 1. Dependency Composition
    console.print("[cyan]Building Application Context...[/cyan]")
    container = ApplicationContainer(settings={"tenant_id": args.tenant_id, "data_path": "data"})
    context = container.build()
    
    # 2. Application Initialization
    app = CodentirApplication(context)
    app.initialize()
    app.start()
    
    try:
        # 3. Presentation Layer: Triage
        request = run_cli_triage(app)
        
        # 4. Runtime Orchestration
        app.run(request)
        
    except KeyboardInterrupt:
        console.print("\n[bold red]Investigation aborted by user.[/bold red]")
    finally:
        # 5. Teardown
        app.stop()
        app.shutdown()

if __name__ == "__main__":
    main()
