import math
import heapq
import matplotlib.pyplot as plt

# -----------------------------
# 1) Map data (generated from anchors)
# -----------------------------

CENTER_POS = (500.0, 500.0)

# Capitals as anchors (your current positions kept)
CAPITALS = {
    "Necro":  {"name": "Necropolis",      "pos": (500.0, 1000.0)},
    "Steel":  {"name": "Steelforge",      "pos": (853.0, 853.0)},
    "Body":   {"name": "Temple of Body",  "pos": (1000.0, 500.0)},
    "Fire":   {"name": "Fire Earth",      "pos": (853.0, 146.0)},
    "Demons": {"name": "Demons",          "pos": (500.0, 0.0)},
    "Nature": {"name": "Nature",          "pos": (146.0, 146.0)},
    "Spirit": {"name": "Spirit",          "pos": (0.0, 500.0)},
    "Water":  {"name": "Water Wind",      "pos": (146.0, 853.0)},
}

# Ring order around the world (clockwise)
RING = ["Necro", "Steel", "Body", "Fire", "Demons", "Nature", "Spirit", "Water"]

# MVP layer: 6 outposts per kingdom (can expand later)
OUTPOST_ROLES = ["Farm", "Farm", "Mine", "Lumber", "TradePost", "Ruin"]

# Generation parameters (tweak freely)
GATE_TO_CENTER_DIST = 120.0     # distance from capital towards center for GateToCenter
GATE_TO_NEIGHBOR_T  = 0.35      # interpolation t for gates to neighbors on cap->neighbor line
CITY_OFFSET         = 95.0      # cities offset around capital (perpendicular)
OUTPOST_RADIUS      = 170.0     # outposts circle radius around capital


def v_sub(a, b): return (a[0] - b[0], a[1] - b[1])
def v_add(a, b): return (a[0] + b[0], a[1] + b[1])
def v_mul(a, k): return (a[0] * k, a[1] * k)


def v_len(a):
    return math.hypot(a[0], a[1])


def v_norm(a):
    l = v_len(a)
    return (0.0, 0.0) if l == 0 else (a[0] / l, a[1] / l)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def ring_neighbors(k):
    i = RING.index(k)
    cw = RING[(i + 1) % len(RING)]
    ccw = RING[(i - 1) % len(RING)]
    return cw, ccw


NODES = {
    "Center": {"name": "Center", "pos": CENTER_POS, "type": "Center", "role": "Center"},
}

EDGES = []


def add_edge(a, b):
    EDGES.append((a, b))


# Build nodes + edges
for k, meta in CAPITALS.items():
    cap_id = f"{k}_CAP"
    cap_pos = meta["pos"]

    # Capital
    NODES[cap_id] = {
        "name": meta["name"],
        "pos": cap_pos,
        "type": "Capital",
        "kingdom": k,
        "role": "Capital",
    }

    # Cities (2)
    to_center = v_sub(CENTER_POS, cap_pos)
    u = v_norm(to_center)
    p = (-u[1], u[0])  # perpendicular

    city1_id = f"{k}_CITY1"
    city2_id = f"{k}_CITY2"
    NODES[city1_id] = {"name": f"{k} City I",  "pos": v_add(cap_pos, v_mul(p,  CITY_OFFSET)), "type": "City", "kingdom": k, "role": "City"}
    NODES[city2_id] = {"name": f"{k} City II", "pos": v_add(cap_pos, v_mul(p, -CITY_OFFSET)), "type": "City", "kingdom": k, "role": "City"}

    add_edge(cap_id, city1_id)
    add_edge(cap_id, city2_id)

    # Border castles (3): to center, to CW neighbor, to CCW neighbor
    cw, ccw = ring_neighbors(k)
    cw_pos = CAPITALS[cw]["pos"]
    ccw_pos = CAPITALS[ccw]["pos"]

    gate_ctr_id = f"{k}_GATE_CTR"
    gate_cw_id  = f"{k}_GATE_CW"
    gate_ccw_id = f"{k}_GATE_CCW"

    gate_ctr_pos = v_add(cap_pos, v_mul(v_norm(v_sub(CENTER_POS, cap_pos)), GATE_TO_CENTER_DIST))
    gate_cw_pos  = lerp(cap_pos, cw_pos,  GATE_TO_NEIGHBOR_T)
    gate_ccw_pos = lerp(cap_pos, ccw_pos, GATE_TO_NEIGHBOR_T)

    NODES[gate_ctr_id] = {"name": f"{k} Gate → Center", "pos": gate_ctr_pos, "type": "BorderCastle", "kingdom": k, "role": "GateToCenter"}
    NODES[gate_cw_id]  = {"name": f"{k} Gate → {cw}",    "pos": gate_cw_pos,  "type": "BorderCastle", "kingdom": k, "role": "GateToCW"}
    NODES[gate_ccw_id] = {"name": f"{k} Gate → {ccw}",   "pos": gate_ccw_pos, "type": "BorderCastle", "kingdom": k, "role": "GateToCCW"}

    add_edge(cap_id, gate_ctr_id)
    add_edge(cap_id, gate_cw_id)
    add_edge(cap_id, gate_ccw_id)

    # Center connects ONLY to gates-to-center
    add_edge("Center", gate_ctr_id)

    # Outposts (6) around capital
    for idx, role in enumerate(OUTPOST_ROLES, start=1):
        ang = (idx / len(OUTPOST_ROLES)) * 2.0 * math.pi
        dx = math.cos(ang) * OUTPOST_RADIUS
        dy = math.sin(ang) * OUTPOST_RADIUS

        out_id = f"{k}_OUT{idx}"
        NODES[out_id] = {
            "name": f"{k} {role} {idx}",
            "pos": (cap_pos[0] + dx, cap_pos[1] + dy),
            "type": "Outpost",
            "kingdom": k,
            "role": role,
        }
        add_edge(cap_id, out_id)

# Inter-kingdom links via gates:
# k Gate CW <-> cw Gate CCW (one per ring pair)
for k in RING:
    cw, _ = ring_neighbors(k)
    a = f"{k}_GATE_CW"
    b = f"{cw}_GATE_CCW"

    # Add each pair only once
    i = RING.index(k)
    j = RING.index(cw)
    if (i < j) or (i == len(RING) - 1 and j == 0):
        add_edge(a, b)


TYPE_STYLE = {
    "Center":       {"marker": "X", "size": 220},
    "Capital":      {"marker": "s", "size": 140},
    "City":         {"marker": "o", "size": 110},
    "BorderCastle": {"marker": "^", "size": 90},
    "Outpost":      {"marker": ".", "size": 70},
}


def dist(a, b):
    ax, ay = NODES[a]["pos"]
    bx, by = NODES[b]["pos"]
    return math.hypot(ax - bx, ay - by)


def build_graph():
    g = {k: [] for k in NODES.keys()}
    for a, b in EDGES:
        w = dist(a, b)
        g[a].append((b, w))
        g[b].append((a, w))
    return g


GRAPH = build_graph()

# -----------------------------
# 2) A* on node graph
# -----------------------------
def astar(start, goal):
    def h(n):
        return dist(n, goal)

    open_heap = []
    heapq.heappush(open_heap, (h(start), start))

    came_from = {}
    gscore = {start: 0.0}
    in_open = {start}

    while open_heap:
        _, cur = heapq.heappop(open_heap)
        in_open.discard(cur)

        if cur == goal:
            path = [cur]
            while cur in came_from:
                cur = came_from[cur]
                path.append(cur)
            path.reverse()
            return path

        for nb, w in GRAPH[cur]:
            tentative = gscore[cur] + w
            if tentative < gscore.get(nb, float("inf")):
                came_from[nb] = cur
                gscore[nb] = tentative
                if nb not in in_open:
                    heapq.heappush(open_heap, (tentative + h(nb), nb))
                    in_open.add(nb)

    return None

# -----------------------------
# 3) Visualization + clicks
# -----------------------------
def draw_map(path=None, start=None, goal=None):
    plt.cla()

    # Edges
    for a, b in EDGES:
        ax, ay = NODES[a]["pos"]
        bx, by = NODES[b]["pos"]
        plt.plot([ax, bx], [ay, by], linewidth=1)

    # Path highlight
    if path and len(path) > 1:
        xs = [NODES[n]["pos"][0] for n in path]
        ys = [NODES[n]["pos"][1] for n in path]
        plt.plot(xs, ys, linewidth=4)

    # Nodes by type
    for t, st in TYPE_STYLE.items():
        xs, ys = [], []
        for nid, data in NODES.items():
            if data["type"] == t:
                xs.append(data["pos"][0])
                ys.append(data["pos"][1])
        if xs:
            plt.scatter(xs, ys, s=st["size"], marker=st["marker"])

    # Labels
    for nid, data in NODES.items():
        x, y = data["pos"]
        t = data["type"]
        # Keep labels readable: show short id + name; role in parentheses
        role = data.get("role", "")
        role_sfx = f" ({role})" if role and role not in ("City", "Capital") else ""
        label = f"{nid}: {data['name']}{role_sfx}"
        plt.text(x + 1, y + 1, label, fontsize=8)

    # Start/goal outline
    if start:
        x, y = NODES[start]["pos"]
        plt.scatter([x], [y], s=260, marker="o", facecolors="none", linewidths=2)
    if goal:
        x, y = NODES[goal]["pos"]
        plt.scatter([x], [y], s=260, marker="s", facecolors="none", linewidths=2)

    plt.title("Node Map (click nodes: 1st=start, 2nd=goal, 3rd=reset)")
    plt.axis("equal")
    plt.grid(True)
    plt.draw()


def nearest_node(x, y, threshold=10.0):
    best = None
    best_d = float("inf")
    for nid, data in NODES.items():
        nx, ny = data["pos"]
        d = math.hypot(nx - x, ny - y)
        if d < best_d:
            best_d = d
            best = nid
    return best if best_d <= threshold else None


start = None
goal = None
current_path = None

fig = plt.figure(figsize=(10, 10))
draw_map()


def on_click(event):
    global start, goal, current_path
    if event.xdata is None or event.ydata is None:
        return

    nid = nearest_node(event.xdata, event.ydata)
    if nid is None:
        return

    if start is None:
        start = nid
    elif goal is None:
        goal = nid
        current_path = astar(start, goal)
    else:
        start = None
        goal = None
        current_path = None

    draw_map(path=current_path, start=start, goal=goal)


fig.canvas.mpl_connect("button_press_event", on_click)
plt.show()
