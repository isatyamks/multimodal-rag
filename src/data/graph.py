from typing import Any, Dict, List, Set

import networkx as nx

from src.core.entities import Dataset
from src.infra.telemetry import instrument


class GraphService:
    def __init__(self, dataset: Dataset, graph: nx.DiGraph = None):
        self.dataset = dataset
        if graph is not None:
            self.graph = graph
        else:
            self.graph = nx.DiGraph()
            self._build_graph()

    @instrument(span_name="graph_build")
    def _build_graph(self):
        """Builds a NetworkX DiGraph from the entire dataset for causal path finding."""
        for tid, t in self.dataset.tickets.items():
            self.graph.add_node(tid, type="ticket", obj=t)
            if t.requirement_id:
                self.graph.add_edge(
                    tid, f"{t.tenant_id}::{t.requirement_id}", type="implements"
                )
            for sid in t.service_ids:
                self.graph.add_edge(
                    tid, f"{t.tenant_id}::{sid}", type="affects_service"
                )

        for i_id, inc in self.dataset.incidents.items():
            self.graph.add_node(i_id, type="incident", obj=inc)
            for sid in inc.impacted_service_ids:
                self.graph.add_edge(
                    i_id, f"{inc.tenant_id}::{sid}", type="impacts_service"
                )
            for aid in inc.alert_ids:
                self.graph.add_edge(
                    f"{inc.tenant_id}::{aid}", i_id, type="causes_incident"
                )

        for pr_id, pr in self.dataset.pull_requests.items():
            self.graph.add_node(pr_id, type="pull_request", obj=pr)
            for sha in pr.commit_shas:
                self.graph.add_edge(
                    pr_id, f"{pr.tenant_id}::{sha}", type="contains_commit"
                )
                self.graph.add_edge(
                    f"{pr.tenant_id}::{sha}", pr_id, type="belongs_to_pr"
                )

        for d_id, dep in self.dataset.deployments.items():
            self.graph.add_node(d_id, type="deployment", obj=dep)
            self.graph.add_edge(
                d_id, f"{dep.tenant_id}::{dep.service_id}", type="deploys_to"
            )
            if hasattr(dep, "release_id") and dep.release_id:
                self.graph.add_edge(
                    f"{dep.tenant_id}::{dep.release_id}",
                    d_id,
                    type="triggers_deployment",
                )

        for c_id, commit in self.dataset.commits.items():
            self.graph.add_node(c_id, type="commit", obj=commit)

        for s_id, srv in self.dataset.services.items():
            self.graph.add_node(s_id, type="service", obj=srv)
            if srv.team_id:
                self.graph.add_edge(
                    s_id, f"{srv.tenant_id}::{srv.team_id}", type="owned_by_team"
                )
            if hasattr(srv, "depends_on_ids") and srv.depends_on_ids:
                for dep_id in srv.depends_on_ids:
                    if "::" not in dep_id:
                        dep_id = f"{srv.tenant_id}::{dep_id}"
                    self.graph.add_edge(s_id, dep_id, type="depends_on")

        for a_id, api in self.dataset.apis.items():
            self.graph.add_node(a_id, type="api", obj=api)
            if api.service_id:
                self.graph.add_edge(
                    f"{api.tenant_id}::{api.service_id}", a_id, type="exposes_api"
                )

        for e_id, emp in getattr(self.dataset, "employees", {}).items():
            self.graph.add_node(e_id, type="employee", obj=emp)

        for t_id, team in self.dataset.teams.items():
            self.graph.add_node(t_id, type="team", obj=team)
            for member_id in team.members:
                if not str(member_id).startswith(f"{team.tenant_id}::"):
                    member_id = f"{team.tenant_id}::{member_id}"
                self.graph.add_edge(t_id, member_id, type="has_member")

        for r_id, repo in getattr(self.dataset, "repositories", {}).items():
            self.graph.add_node(r_id, type="repository", obj=repo)
            self.graph.add_edge(
                f"{repo.tenant_id}::{repo.service_id}", r_id, type="has_repo"
            )

        for a_id, adr in getattr(self.dataset, "adrs", {}).items():
            self.graph.add_node(a_id, type="adr", obj=adr)
            self.graph.add_edge(
                f"{adr.tenant_id}::{adr.service_id}", a_id, type="has_adr"
            )

        for r_id, rb in getattr(self.dataset, "runbooks", {}).items():
            self.graph.add_node(r_id, type="runbook", obj=rb)
            self.graph.add_edge(
                f"{rb.tenant_id}::{rb.service_id}", r_id, type="has_runbook"
            )

        for rel_id, rel in getattr(self.dataset, "releases", {}).items():
            self.graph.add_node(rel_id, type="release", obj=rel)
            self.graph.add_edge(
                f"{rel.tenant_id}::{rel.repository_id}", rel_id, type="produces"
            )
            for pr_id in rel.pr_ids:
                self.graph.add_edge(
                    f"{rel.tenant_id}::{pr_id}", rel_id, type="included_in"
                )

        # Structural graph excludes logs, metrics, slack messages.

        for a_id, a in getattr(self.dataset, "alerts", {}).items():
            self.graph.add_node(a_id, type="alert", obj=a)
            service_id = a.service.get("id") if isinstance(a.service, dict) else None
            if service_id:
                self.graph.add_edge(
                    f"{a.tenant_id}::{service_id}", a_id, type="emits_alert"
                )

        for pm_id, pm in getattr(self.dataset, "postmortems", {}).items():
            self.graph.add_node(pm_id, type="postmortem", obj=pm)
            self.graph.add_edge(
                f"{pm.tenant_id}::{pm.incident_id}", pm_id, type="analyzes"
            )

    @instrument(span_name="graph_expand_query")
    def expand_query_graph(self, seed_nodes: List[str], node_budget: int = 500) -> nx.DiGraph:
        """Expands a localized subgraph centered around the seed nodes using BFS until budget hit."""
        print(f"  \033[90mExpanding query graph from {len(seed_nodes)} seed nodes (budget={node_budget})...\033[0m")
        
        nodes_to_keep = set()
        queue = list(seed_nodes)
        undirected_g = self.graph.to_undirected()
        
        # Add initial seeds that exist in graph
        for root in seed_nodes:
            if root in undirected_g:
                nodes_to_keep.add(root)
                
        # BFS expansion
        visited = set(nodes_to_keep)
        while queue and len(nodes_to_keep) < node_budget:
            curr = queue.pop(0)
            if curr not in undirected_g:
                continue
                
            for neighbor in undirected_g.neighbors(curr):
                if neighbor not in visited:
                    visited.add(neighbor)
                    nodes_to_keep.add(neighbor)
                    queue.append(neighbor)
                    
                    if len(nodes_to_keep) >= node_budget:
                        break
                        
        query_graph = self.graph.subgraph(nodes_to_keep).copy()
        print(f"  \033[92mQuery graph expanded: {query_graph.number_of_nodes()} nodes, {query_graph.number_of_edges()} edges.\033[0m")
        return query_graph

    @instrument(span_name="graph_iterative_expansion")
    def iterative_expansion(
        self, initial_artifact_ids: List[str], tenant_id: str, max_depth: int = 2
    ) -> Set[str]:
        """Expands using NetworkX BFS."""
        discovered = set(initial_artifact_ids)
        current_layer = set(initial_artifact_ids)

        undirected_g = self.graph.to_undirected()

        for depth in range(max_depth):
            next_layer = set()
            for artifact_id in current_layer:
                if artifact_id in undirected_g:
                    neighbors = list(undirected_g.neighbors(artifact_id))
                    new_neighbors = [
                        n
                        for n in neighbors
                        if n not in discovered and str(n).startswith(f"{tenant_id}::")
                    ]
                    next_layer.update(new_neighbors)
                    discovered.update(new_neighbors)
            if not next_layer:
                break
            current_layer = next_layer

        return discovered

    def get_shortest_path(self, source: str, target: str) -> List[str]:
        """Finds shortest path ignoring edge direction."""
        undirected_g = self.graph.to_undirected()
        if source in undirected_g and target in undirected_g:
            try:
                return nx.shortest_path(undirected_g, source=source, target=target)
            except nx.NetworkXNoPath:
                pass
        return []

    def get_node(self, node_id: str) -> Dict[str, Any]:
        return self.graph.nodes.get(node_id, {})

    def find_causal_paths(self, start_id: str, max_depth: int = 3) -> List[List[Dict[str, Any]]]:
        """Finds paths from a starting node."""
        paths = []
        if start_id not in self.graph:
            return paths
        for neighbor in self.graph.neighbors(start_id):
            paths.append([
                {"id": start_id, "type": self.graph.nodes[start_id].get("type", "unknown")},
                {"id": neighbor, "type": self.graph.nodes[neighbor].get("type", "unknown")}
            ])
        return paths[:5]

