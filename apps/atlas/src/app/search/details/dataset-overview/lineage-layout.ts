import { DatasetLineage, LineageNode } from './dataset-overview.service';

export const LAYOUT = {
    columnWidth: 150,
    nodeWidth: 124,
    rowHeight: 72,
    datasetHeight: 52,
    processHeight: 40,
    padding: 24,
};

export interface PlacedNode extends LineageNode {
    readonly column: number;
    readonly x: number;
    readonly y: number;
    readonly width: number;
    readonly height: number;
}

export interface PlacedEdge {
    readonly from: string;
    readonly to: string;
    /** SVG path from the right side of `from` to the left side of `to` */
    readonly path: string;
}

export interface LineageLayout {
    readonly nodes: PlacedNode[];
    readonly edges: PlacedEdge[];
    readonly width: number;
    readonly height: number;
}

/**
 * Places the lineage left to right: the base entity in its own column, everything upstream to the left and
 * downstream to the right, one column per step (datasets and processes alternate). Within a column the nodes are
 * ordered by the position of their neighbours closer to the base, which keeps lines from crossing in the usual
 * fan-in / fan-out shapes.
 */
export function layoutLineage(lineage: DatasetLineage): LineageLayout {
    const nodes = new Map(lineage.nodes.map((n) => [n.guid, n]));
    const edges = lineage.edges.filter((e) => nodes.has(e.from) && nodes.has(e.to) && e.from !== e.to);
    const base = nodes.has(lineage.baseEntityGuid) ? lineage.baseEntityGuid : lineage.nodes[0]?.guid;
    const column = new Map<string, number>();
    if (base) {
        column.set(base, 0);
    }

    // breadth first from the base: downstream +1, upstream -1
    let changed = true;
    for (let pass = 0; changed && pass <= nodes.size; pass++) {
        changed = false;
        for (const { from, to } of edges) {
            if (column.has(from) && !column.has(to) && column.get(from) >= 0) {
                column.set(to, column.get(from) + 1);
                changed = true;
            } else if (column.has(to) && !column.has(from) && column.get(to) <= 0) {
                column.set(from, column.get(to) - 1);
                changed = true;
            }
        }
    }
    // longest path: a node goes right of everything that feeds it (downstream) / left of what it feeds (upstream)
    for (let pass = 0; pass < nodes.size; pass++) {
        let moved = false;
        for (const { from, to } of edges) {
            const a = column.get(from);
            const b = column.get(to);
            if (a === undefined || b === undefined || b > a) {
                continue;
            }
            if (b > 0 || (b === 0 && to !== base)) {
                column.set(to, a + 1);
            } else if (from !== base) {
                column.set(from, b - 1);
            } else {
                continue;
            }
            moved = true;
        }
        if (!moved) {
            break;
        }
    }
    // nodes the walk did not reach (not connected to the base): after the rest
    const reached = [...column.values()];
    let spare = reached.length ? Math.max(...reached) + 1 : 0;
    for (const guid of nodes.keys()) {
        if (!column.has(guid)) {
            column.set(guid, spare++);
        }
    }

    const minColumn = Math.min(...column.values());
    const byColumn = new Map<number, string[]>();
    for (const [guid, c] of column) {
        byColumn.set(c, [...(byColumn.get(c) ?? []), guid]);
    }
    const row = new Map<string, number>();
    const neighbours = (guid: string, c: number) =>
        edges
            .filter((e) => (e.from === guid && column.get(e.to) === c) || (e.to === guid && column.get(e.from) === c))
            .map((e) => (e.from === guid ? e.to : e.from));
    const order = (c: number, towardsBase: number) => {
        const guids = byColumn.get(c) ?? [];
        const weight = (guid: string) => {
            const rows = neighbours(guid, towardsBase)
                .map((n) => row.get(n))
                .filter((r) => r !== undefined);
            return rows.length ? rows.reduce((s, r) => s + r, 0) / rows.length : Number.MAX_SAFE_INTEGER;
        };
        guids
            .sort((a, b) => weight(a) - weight(b) || nodes.get(a).name.localeCompare(nodes.get(b).name))
            .forEach((guid, i) => row.set(guid, i));
    };
    order(0, 0);
    const columns = [...byColumn.keys()];
    for (let c = 1; c <= Math.max(...columns); c++) {
        order(c, c - 1);
    }
    for (let c = -1; c >= Math.min(...columns); c--) {
        order(c, c + 1);
    }

    const tallest = Math.max(...[...byColumn.values()].map((g) => g.length), 1);
    const height = LAYOUT.padding * 2 + tallest * LAYOUT.rowHeight;
    const placed = new Map<string, PlacedNode>();
    for (const [guid, node] of nodes) {
        const c = column.get(guid) - minColumn;
        const inColumn = byColumn.get(column.get(guid)).length;
        const h = node.kind === 'process' ? LAYOUT.processHeight : LAYOUT.datasetHeight;
        const centre =
            LAYOUT.padding + ((tallest - inColumn) * LAYOUT.rowHeight) / 2 + (row.get(guid) + 0.5) * LAYOUT.rowHeight;
        placed.set(guid, {
            ...node,
            column: c,
            x: LAYOUT.padding / 2 + c * LAYOUT.columnWidth,
            y: centre - h / 2,
            width: LAYOUT.nodeWidth,
            height: h,
        });
    }
    const width = LAYOUT.padding + (Math.max(...column.values()) - minColumn) * LAYOUT.columnWidth + LAYOUT.nodeWidth;

    const placedEdges = edges.map(({ from, to }) => {
        const a = placed.get(from);
        const b = placed.get(to);
        const x1 = a.x + a.width;
        const y1 = a.y + a.height / 2;
        const x2 = b.x - 4;
        const y2 = b.y + b.height / 2;
        const mx = (x1 + x2) / 2;
        return { from, to, path: `M ${x1} ${y1} C ${mx} ${y1}, ${mx} ${y2}, ${x2} ${y2}` };
    });
    return { nodes: [...placed.values()], edges: placedEdges, width, height };
}
