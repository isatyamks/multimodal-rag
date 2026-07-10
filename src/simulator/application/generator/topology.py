import random
from typing import Dict, List
from src.simulator.domain.world.models import (
    Engineer,
    Microservice,
    Organization,
    Repository,
    Team,
    WorldState,
)
from src.simulator.domain.shared.value_objects import (
    EngineerID,
    RepositoryID,
    ServiceID,
    TeamID,
    TenantID,
)

class DeterministicTopologyGenerator:
    """
    Generates a deterministic world topology based on a seed.
    This replaces the 'random noise generator' with a structurally sound
    initial world state.
    """
    def __init__(self, seed: int):
        self.random = random.Random(seed)
        
    def generate_world(self, tenant_id: str, company_size: str) -> WorldState:
        """
        Generates an entire organization topology.
        company_size: "small", "medium", "large"
        """
        # 1. Determine scale based on size
        num_teams = {"small": 3, "medium": 15, "large": 50}[company_size]
        
        org = Organization(
            tenant_id=TenantID(tenant_id),
            name=f"Simulated {company_size.capitalize()} Corp",
            domain=f"sim-{tenant_id}.local"
        )
        
        teams: List[Team] = []
        services: Dict[ServiceID, Microservice] = {}
        
        service_counter = 1
        engineer_counter = 1
        
        # 2. Generate Teams and Engineers
        for t_idx in range(num_teams):
            team_id = TeamID(f"team-{t_idx}")
            num_engineers = self.random.randint(4, 8)
            
            engineers = []
            for _ in range(num_engineers):
                eng = Engineer(
                    id=EngineerID(f"eng-{engineer_counter}"),
                    name=f"Engineer {engineer_counter}",
                    email=f"eng-{engineer_counter}@{org.domain}",
                    roles=["developer"],
                    is_on_call=False
                )
                engineers.append(eng)
                engineer_counter += 1
                
            # Assign one on-call
            if engineers:
                engineers[0] = engineers[0].model_copy(update={"is_on_call": True})
                
            # 3. Generate Services owned by team
            num_services = self.random.randint(1, 4)
            owned_services = []
            for _ in range(num_services):
                svc_id = ServiceID(f"svc-{service_counter}")
                repo_id = RepositoryID(f"repo-{service_counter}")
                
                svc = Microservice(
                    id=svc_id,
                    name=f"service-{service_counter}",
                    repository_id=repo_id,
                    dependencies=[] # We will link dependencies later
                )
                services[svc_id] = svc
                owned_services.append(svc_id)
                service_counter += 1
                
            team = Team(
                id=team_id,
                name=f"Team {t_idx}",
                engineers=engineers,
                owned_services=owned_services
            )
            teams.append(team)
            
        # 4. Link dependencies randomly to form a DAG (roughly)
        service_ids = list(services.keys())
        for idx, svc_id in enumerate(service_ids):
            # A service can only depend on services with a higher index to avoid cycles
            possible_deps = service_ids[idx+1:]
            if possible_deps:
                num_deps = self.random.randint(0, min(3, len(possible_deps)))
                deps = self.random.sample(possible_deps, num_deps)
                services[svc_id] = services[svc_id].model_copy(update={"dependencies": deps})
                
        org = org.model_copy(update={"teams": teams})
        
        return WorldState(
            organization=org,
            services=services,
            infrastructure={}
        )
