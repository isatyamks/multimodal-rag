from datetime import datetime, timezone
from src.simulator.domain.world.models import WorldState
from src.simulator.application.engine.loop import SimulationEngine
from src.simulator.application.engine.runner import SimulationRunner
from src.simulator.application.engine.timing import FixedIntervalStrategy
from src.infra.messaging.file_bus import FileEventBus
from src.simulator.adapters.platforms.slack.adapter import SlackAdapter
from src.simulator.application.generator.topology import DeterministicTopologyGenerator
from src.simulator.domain.actor.engineers import SoftwareEngineerActor

def bootstrap_simulation() -> SimulationEngine:
    """
    Wires the application together and returns a ready-to-run SimulationEngine.
    """
    
    # 2. Adapters (Event Bus + Slack)
    event_bus = FileEventBus(data_dir="data/events")
    slack_adapter = SlackAdapter(event_bus=event_bus, topic="simulator.events.raw")
    observers = [slack_adapter]
    
    # 3. Domain State & Generator
    generator = DeterministicTopologyGenerator(seed=42)
    world = generator.generate_world(tenant_id="tenant-123", company_size="small")
    
    # 4. Initialize Actors based on World Topology
    actors = []
    for team in world.organization.teams:
        for eng in team.engineers:
            actor = SoftwareEngineerActor(
                id=eng.id, 
                name=eng.name,
                # Randomize strictness and fatigue a bit based on seed could go here
                strictness=0.6,
                fatigue_level=0.2 if not eng.is_on_call else 0.8
            )
            actors.append(actor)
            
    print(f"Initialized World with {len(world.organization.teams)} teams, {len(world.services)} services, and {len(actors)} engineers.")
    
    # 5. Application Engine
    engine = SimulationEngine(
        world_state=world,
        actors=actors, 
        observers=observers,
        start_time=datetime.now(timezone.utc)
    )
    
    runner = SimulationRunner(engine, FixedIntervalStrategy(interval_seconds=5.0))
    return runner

if __name__ == "__main__":
    import time
    print("Bootstrapping simulation...")
    runner = bootstrap_simulation()
    
    print("Simulation runner ready. Starting continuous execution...")
    runner.start()
    
    try:
        while True:
            time.sleep(1) # Keep main thread alive
    except KeyboardInterrupt:
        print("\nStopping simulation...")
        runner.stop()
