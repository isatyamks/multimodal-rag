import threading
from typing import Optional
from src.simulator.application.engine.loop import SimulationEngine
from src.simulator.application.engine.timing import TickStrategy

class SimulationRunner:
    """
    Lifecycle manager for the SimulationEngine.
    """
    def __init__(self, engine: SimulationEngine, strategy: TickStrategy):
        self.engine = engine
        self.strategy = strategy
        
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._paused = False
        
    def start(self):
        """Starts the continuous simulation loop in a background thread."""
        if self._running:
            return
        
        self._running = True
        self._paused = False
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        print("[Runner] Simulation started.")
        
    def _run_loop(self):
        while self._running:
            if not self._paused:
                self.step()
                self.strategy.wait()
            else:
                import time
                time.sleep(0.5)

    def pause(self):
        """Pauses the background simulation loop."""
        self._paused = True
        print("[Runner] Simulation paused.")
        
    def resume(self):
        """Resumes a paused simulation loop."""
        self._paused = False
        print("[Runner] Simulation resumed.")
        
    def stop(self):
        """Stops the simulation loop permanently."""
        self._running = False
        if self._thread:
            self._thread.join()
        print("[Runner] Simulation stopped.")
        
    def step(self):
        """Executes a single tick synchronously."""
        self.engine.tick()
        
    def reset(self):
        """Resets the simulation to its initial state."""
        # For future implementation if we want to reset world state
        pass
