"""
Local tools service for ReportAgent when GRAPH_BACKEND=local.

This provides a minimal subset of ZepToolsService capabilities using:
- Neo4j graph for nodes/edges
- Qdrant for semantic search over chunks (optional)

The return types reuse dataclasses from zep_tools.py for compatibility.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..config import Config
from ..utils.logger import get_logger
from .local_graph_store import LocalNeo4jGraphStore
from .local_vector_store import QdrantChunkStore
from .zep_tools import InsightForgeResult, PanoramaResult, SearchResult, NodeInfo, EdgeInfo

logger = get_logger("mirofish.local_tools")


class LocalToolsService:
    def __init__(self):
        self.graph_store = LocalNeo4jGraphStore()
        self.vector_store = None
        if Config.VECTOR_BACKEND == "qdrant":
            try:
                self.vector_store = QdrantChunkStore()
            except Exception as e:
                logger.warning(f"Qdrant init failed, semantic search disabled: {e}")
                self.vector_store = None

    def quick_search(self, graph_id: str, query: str, limit: int = 10) -> SearchResult:
        facts: List[str] = []
        if self.vector_store is not None:
            try:
                items = self.vector_store.search_chunks(
                    project_id=None,
                    graph_id=graph_id,
                    query=query,
                    limit=limit,
                )
                facts = [i.get("text", "") for i in items if i.get("text")]
            except Exception as e:
                logger.warning(f"Local quick_search vector failed: {e}")

        # Fallback: show edge facts from Neo4j
        if not facts:
            graph = self.graph_store.get_graph_data(graph_id)
            for e in (graph.get("edges") or [])[:limit]:
                fact = e.get("fact") or ""
                if fact:
                    facts.append(fact)

        return SearchResult(
            facts=facts[:limit],
            edges=[],
            nodes=[],
            query=query,
            total_count=len(facts[:limit]),
        )

    def search_graph(self, graph_id: str, query: str, limit: int = 10, scope: str = "edges") -> SearchResult:
        # Backward-compatible alias used by debug endpoints and older code.
        _ = scope
        return self.quick_search(graph_id=graph_id, query=query, limit=limit)

    def panorama_search(self, graph_id: str, query: str, include_expired: bool = True) -> PanoramaResult:
        graph = self.graph_store.get_graph_data(graph_id)
        nodes = graph.get("nodes") or []
        edges = graph.get("edges") or []

        # Facts: prefer vector search results if available, else use edge facts
        facts: List[str] = []
        if self.vector_store is not None and query:
            try:
                items = self.vector_store.search_chunks(
                    project_id=None,
                    graph_id=graph_id,
                    query=query,
                    limit=30,
                )
                facts = [i.get("text", "") for i in items if i.get("text")]
            except Exception:
                facts = []

        if not facts:
            facts = [e.get("fact") for e in edges if e.get("fact")]

        node_infos = [
            NodeInfo(
                uuid=n.get("uuid", ""),
                name=n.get("name", ""),
                labels=n.get("labels", []) or ["Entity"],
                summary=n.get("summary", ""),
                attributes=n.get("attributes", {}) or {},
            )
            for n in nodes
        ]

        edge_infos = [
            EdgeInfo(
                uuid=e.get("uuid", ""),
                name=e.get("name", ""),
                fact=e.get("fact", ""),
                source_node_uuid=e.get("source_node_uuid", ""),
                target_node_uuid=e.get("target_node_uuid", ""),
                source_node_name=e.get("source_node_name"),
                target_node_name=e.get("target_node_name"),
                created_at=e.get("created_at"),
                valid_at=e.get("valid_at"),
                invalid_at=e.get("invalid_at"),
                expired_at=e.get("expired_at"),
            )
            for e in edges
        ]

        result = PanoramaResult(query=query)
        result.all_nodes = node_infos
        result.all_edges = edge_infos
        result.total_nodes = len(node_infos)
        result.total_edges = len(edge_infos)
        result.active_facts = facts
        result.historical_facts = [] if not include_expired else []
        result.active_count = len(result.active_facts)
        result.historical_count = len(result.historical_facts)
        return result

    def insight_forge(
        self,
        graph_id: str,
        query: str,
        simulation_requirement: str = "",
        report_context: str = "",
    ) -> InsightForgeResult:
        # Minimal implementation: treat the query as a single sub-query and return semantic facts.
        search = self.quick_search(graph_id=graph_id, query=query, limit=15)

        graph = self.graph_store.get_graph_data(graph_id)
        nodes = graph.get("nodes") or []
        edges = graph.get("edges") or []

        # Pick top entities by occurrence in facts (very rough)
        entity_insights: List[Dict[str, Any]] = []
        for n in nodes[:10]:
            etype = next((l for l in (n.get("labels") or []) if l not in ["Entity", "Node"]), "实体")
            entity_insights.append(
                {
                    "name": n.get("name", ""),
                    "type": etype,
                    "summary": n.get("summary", ""),
                    "related_facts": [],
                }
            )

        relationship_chains = []
        for e in edges[:20]:
            s = e.get("source_node_name") or e.get("source_node_uuid", "")[:8]
            t = e.get("target_node_name") or e.get("target_node_uuid", "")[:8]
            rel = e.get("name") or e.get("fact_type") or "REL"
            relationship_chains.append(f"{s} --[{rel}]--> {t}")

        result = InsightForgeResult(
            query=query,
            simulation_requirement=simulation_requirement or "",
            sub_queries=[query],
        )
        result.semantic_facts = search.facts
        result.entity_insights = entity_insights
        result.relationship_chains = relationship_chains
        result.total_facts = len(result.semantic_facts)
        result.total_entities = len(result.entity_insights)
        result.total_relationships = len(result.relationship_chains)
        return result

    # Backward-compatible helpers used by ReportAgent
    def get_graph_statistics(self, graph_id: str) -> Dict[str, Any]:
        g = self.graph_store.get_graph_data(graph_id)
        return {"graph_id": graph_id, "node_count": g.get("node_count", 0), "edge_count": g.get("edge_count", 0)}

    def get_entities_by_type(self, graph_id: str, entity_type: str) -> List[NodeInfo]:
        g = self.graph_store.get_graph_data(graph_id)
        nodes = g.get("nodes") or []
        out: List[NodeInfo] = []
        for n in nodes:
            labels = n.get("labels") or []
            if entity_type and entity_type not in labels:
                continue
            out.append(
                NodeInfo(
                    uuid=n.get("uuid", ""),
                    name=n.get("name", ""),
                    labels=labels or ["Entity"],
                    summary=n.get("summary", ""),
                    attributes=n.get("attributes", {}) or {},
                )
            )
        return out

    def get_entity_summary(self, graph_id: str, entity_name: str) -> Dict[str, Any]:
        g = self.graph_store.get_graph_data(graph_id)
        for n in g.get("nodes") or []:
            if (n.get("name") or "").strip() == (entity_name or "").strip():
                etype = next((l for l in (n.get("labels") or []) if l not in ["Entity", "Node"]), "实体")
                return {
                    "name": n.get("name", ""),
                    "type": etype,
                    "summary": n.get("summary", ""),
                    "attributes": n.get("attributes", {}) or {},
                }
        return {"name": entity_name, "summary": "", "attributes": {}}

    def get_simulation_context(self, graph_id: str, query: str, limit: int = 20) -> Dict[str, Any]:
        # Compatibility shim: return quick_search facts.
        res = self.quick_search(graph_id=graph_id, query=query, limit=limit)
        return {"query": query, "facts": res.facts, "count": res.total_count}
