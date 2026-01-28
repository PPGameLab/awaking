"""
Генератор карты на основе конфигурации
"""
import math
import json
from typing import Dict, List, Tuple, Optional
import sys
from pathlib import Path

# Добавляем src в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..entities.node import Node
from ..utils.loader import load_json


def v_sub(a: Tuple[float, float], b: Tuple[float, float]) -> Tuple[float, float]:
    """Вычитание векторов"""
    return (a[0] - b[0], a[1] - b[1])


def v_add(a: Tuple[float, float], b: Tuple[float, float]) -> Tuple[float, float]:
    """Сложение векторов"""
    return (a[0] + b[0], a[1] + b[1])


def v_mul(a: Tuple[float, float], k: float) -> Tuple[float, float]:
    """Умножение вектора на число"""
    return (a[0] * k, a[1] * k)


def v_len(a: Tuple[float, float]) -> float:
    """Длина вектора"""
    return math.hypot(a[0], a[1])


def v_norm(a: Tuple[float, float]) -> Tuple[float, float]:
    """Нормализация вектора"""
    l = v_len(a)
    return (0.0, 0.0) if l == 0 else (a[0] / l, a[1] / l)


def lerp(a: Tuple[float, float], b: Tuple[float, float], t: float) -> Tuple[float, float]:
    """Линейная интерполяция"""
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


class MapGenerator:
    """Генератор карты на основе конфигурации"""
    
    def __init__(self, config_path: str = "game_data/map_config.mvp.json"):
        """Инициализация генератора"""
        base_path = Path(__file__).parent.parent.parent
        data_path = base_path / config_path
        
        if not data_path.exists():
            raise FileNotFoundError(f"Файл {config_path} не найден")
        
        with open(data_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.node_structure = self.config["node_structure"]
        self.params = self.config["generation_params"]
        self.connection_rules = self.config["connection_rules"]
    
    def generate_map(
        self,
        capitals: Dict[str, Dict],
        center_pos: Tuple[float, float],
        ring_order: List[str]
    ) -> Tuple[Dict[str, Node], List[Tuple[str, str]]]:
        """
        Генерирует карту на основе конфигурации
        
        Args:
            capitals: Словарь столиц {kingdom_id: {"name": str, "pos": (x, y)}}
            center_pos: Позиция центра
            ring_order: Порядок королевств по кругу
        
        Returns:
            Tuple[Dict[str, Node], List[Tuple[str, str]]]: (узлы, рёбра)
        """
        nodes: Dict[str, Node] = {}
        edges: List[Tuple[str, str]] = []
        
        # Создаём центр
        center_node = Node(
            id="Center",
            name="Center",
            pos=center_pos,
            node_type="Center",
            kingdom=None,
            role="Center"
        )
        nodes["Center"] = center_node
        
        # Генерируем узлы для каждого королевства
        for kingdom_id in ring_order:
            if kingdom_id not in capitals:
                continue
            
            capital_meta = capitals[kingdom_id]
            capital_pos = capital_meta["pos"]
            
            # Получаем соседей для ворот
            cw_neighbor, ccw_neighbor = self._get_ring_neighbors(kingdom_id, ring_order)
            
            # Генерируем узлы королевства
            kingdom_nodes, kingdom_edges = self._generate_kingdom_nodes(
                kingdom_id,
                capital_pos,
                center_pos,
                capitals[cw_neighbor]["pos"] if cw_neighbor in capitals else None,
                capitals[ccw_neighbor]["pos"] if ccw_neighbor in capitals else None,
                cw_neighbor,
                ccw_neighbor
            )
            
            nodes.update(kingdom_nodes)
            edges.extend(kingdom_edges)
        
        # Создаём межкоролевские связи (ворота)
        if self.connection_rules["border_gates"]["enabled"]:
            inter_kingdom_edges = self._generate_inter_kingdom_edges(ring_order, nodes)
            edges.extend(inter_kingdom_edges)
        
        return nodes, edges
    
    def _get_ring_neighbors(self, kingdom_id: str, ring_order: List[str]) -> Tuple[str, str]:
        """Получает соседей королевства по кольцу"""
        i = ring_order.index(kingdom_id)
        cw = ring_order[(i + 1) % len(ring_order)]
        ccw = ring_order[(i - 1) % len(ring_order)]
        return cw, ccw
    
    def _generate_kingdom_nodes(
        self,
        kingdom_id: str,
        capital_pos: Tuple[float, float],
        center_pos: Tuple[float, float],
        cw_pos: Optional[Tuple[float, float]],
        ccw_pos: Optional[Tuple[float, float]],
        cw_id: str,
        ccw_id: str
    ) -> Tuple[Dict[str, Node], List[Tuple[str, str]]]:
        """Генерирует узлы для одного королевства"""
        nodes: Dict[str, Node] = {}
        edges: List[Tuple[str, str]] = []
        
        # Столица
        capital_node = Node(
            id=f"{kingdom_id}_CAP",
            name=capital_pos[1] if isinstance(capital_pos, dict) else f"{kingdom_id} Capital",
            pos=capital_pos if isinstance(capital_pos, tuple) else capital_pos["pos"],
            node_type="Capital",
            kingdom=kingdom_id,
            role="Capital"
        )
        nodes[capital_node.id] = capital_node
        
        # Генерируем узлы по конфигурации
        structure = self.node_structure["per_kingdom"]
        
        # Cities
        if "City" in structure:
            city_nodes, city_edges = self._generate_cities(
                kingdom_id, capital_pos, center_pos, structure["City"]
            )
            nodes.update(city_nodes)
            edges.extend(city_edges)
            if self.connection_rules["hub_structure"]["enabled"]:
                for city_id in city_nodes:
                    edges.append((capital_node.id, city_id))
        
        # BorderCastles
        if "BorderCastle" in structure:
            border_nodes, border_edges = self._generate_border_castles(
                kingdom_id, capital_pos, center_pos, cw_pos, ccw_pos,
                cw_id, ccw_id, structure["BorderCastle"]
            )
            nodes.update(border_nodes)
            edges.extend(border_edges)
            if self.connection_rules["hub_structure"]["enabled"]:
                for border_id in border_nodes:
                    edges.append((capital_node.id, border_id))
            
            # Связь центра с воротами к центру
            if self.connection_rules["center_connection"]["enabled"]:
                gate_to_center_id = f"{kingdom_id}_GATE_CTR"
                if gate_to_center_id in border_nodes:
                    edges.append(("Center", gate_to_center_id))
        
        # Outposts
        if "Outpost" in structure:
            outpost_nodes, outpost_edges = self._generate_outposts(
                kingdom_id, capital_pos, structure["Outpost"]
            )
            nodes.update(outpost_nodes)
            edges.extend(outpost_edges)
            if self.connection_rules["hub_structure"]["enabled"]:
                for outpost_id in outpost_nodes:
                    edges.append((capital_node.id, outpost_id))
        
        return nodes, edges
    
    def _generate_cities(
        self,
        kingdom_id: str,
        capital_pos: Tuple[float, float],
        center_pos: Tuple[float, float],
        city_config: Dict
    ) -> Tuple[Dict[str, Node], List[Tuple[str, str]]]:
        """Генерирует города"""
        nodes = {}
        edges = []
        
        to_center = v_sub(center_pos, capital_pos)
        u = v_norm(to_center)
        p = (-u[1], u[0])  # Перпендикуляр
        
        count = city_config.get("count", 2)
        offset = self.params.get("city_offset", 95.0)
        
        for i in range(count):
            city_id = f"{kingdom_id}_CITY{i+1}"
            # Располагаем по разные стороны от линии столица-центр
            pos = v_add(capital_pos, v_mul(p, offset * (1 if i == 0 else -1)))
            
            node = Node(
                id=city_id,
                name=f"{kingdom_id} City {i+1}",
                pos=pos,
                node_type="City",
                kingdom=kingdom_id,
                role="City"
            )
            nodes[city_id] = node
        
        return nodes, edges
    
    def _generate_border_castles(
        self,
        kingdom_id: str,
        capital_pos: Tuple[float, float],
        center_pos: Tuple[float, float],
        cw_pos: Optional[Tuple[float, float]],
        ccw_pos: Optional[Tuple[float, float]],
        cw_id: str,
        ccw_id: str,
        border_config: Dict
    ) -> Tuple[Dict[str, Node], List[Tuple[str, str]]]:
        """Генерирует пограничные замки"""
        nodes = {}
        edges = []
        
        roles = border_config.get("roles", [])
        count = border_config.get("count", len(roles))
        
        # Gate to Center
        if "GateToCenter" in roles:
            gate_ctr_id = f"{kingdom_id}_GATE_CTR"
            dist = self.params.get("gate_to_center_dist", 120.0)
            pos = v_add(capital_pos, v_mul(v_norm(v_sub(center_pos, capital_pos)), dist))
            
            node = Node(
                id=gate_ctr_id,
                name=f"{kingdom_id} Gate → Center",
                pos=pos,
                node_type="BorderCastle",
                kingdom=kingdom_id,
                role="GateToCenter"
            )
            nodes[gate_ctr_id] = node
        
        # Gate to CW neighbor
        if "GateToCW" in roles and cw_pos:
            gate_cw_id = f"{kingdom_id}_GATE_CW"
            t = self.params.get("gate_to_neighbor_t", 0.35)
            pos = lerp(capital_pos, cw_pos, t)
            
            node = Node(
                id=gate_cw_id,
                name=f"{kingdom_id} Gate → {cw_id}",
                pos=pos,
                node_type="BorderCastle",
                kingdom=kingdom_id,
                role="GateToCW"
            )
            nodes[gate_cw_id] = node
        
        # Gate to CCW neighbor
        if "GateToCCW" in roles and ccw_pos:
            gate_ccw_id = f"{kingdom_id}_GATE_CCW"
            t = self.params.get("gate_to_neighbor_t", 0.35)
            pos = lerp(capital_pos, ccw_pos, t)
            
            node = Node(
                id=gate_ccw_id,
                name=f"{kingdom_id} Gate → {ccw_id}",
                pos=pos,
                node_type="BorderCastle",
                kingdom=kingdom_id,
                role="GateToCCW"
            )
            nodes[gate_ccw_id] = node
        
        return nodes, edges
    
    def _generate_outposts(
        self,
        kingdom_id: str,
        capital_pos: Tuple[float, float],
        outpost_config: Dict
    ) -> Tuple[Dict[str, Node], List[Tuple[str, str]]]:
        """Генерирует аванпосты"""
        nodes = {}
        edges = []
        
        roles = outpost_config.get("roles", [])
        count = outpost_config.get("count", len(roles))
        radius = self.params.get("outpost_radius", 170.0)
        
        for idx, role in enumerate(roles[:count], start=1):
            ang = (idx / len(roles)) * 2.0 * math.pi
            dx = math.cos(ang) * radius
            dy = math.sin(ang) * radius
            
            outpost_id = f"{kingdom_id}_OUT{idx}"
            pos = (capital_pos[0] + dx, capital_pos[1] + dy)
            
            node = Node(
                id=outpost_id,
                name=f"{kingdom_id} {role} {idx}",
                pos=pos,
                node_type="Outpost",
                kingdom=kingdom_id,
                role=role
            )
            nodes[outpost_id] = node
        
        return nodes, edges
    
    def _generate_inter_kingdom_edges(
        self,
        ring_order: List[str],
        all_nodes: Dict[str, Node]
    ) -> List[Tuple[str, str]]:
        """Генерирует рёбра между королевствами (ворота)"""
        edges = []
        
        for i, kingdom_id in enumerate(ring_order):
            cw_id = ring_order[(i + 1) % len(ring_order)]
            
            gate_cw = f"{kingdom_id}_GATE_CW"
            gate_ccw = f"{cw_id}_GATE_CCW"
            
            # Добавляем каждую пару только один раз
            if gate_cw in all_nodes and gate_ccw in all_nodes:
                if i < ring_order.index(cw_id) or (i == len(ring_order) - 1 and ring_order.index(cw_id) == 0):
                    edges.append((gate_cw, gate_ccw))
        
        return edges
