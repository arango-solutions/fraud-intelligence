## MCP-first “explore then query” recipes

These are practical sequences an agent can follow when working via the Arango MCP server.

### 1) Explore what’s available (DB → collections → graphs)

- List databases
- Pick the target database
- List collections
- List graphs (if you expect named graphs)

### 2) Always fetch manuals before drafting AQL

Before writing/executing AQL, fetch:
- `aql_ref`
- `optimization`

### 3) Start small: validate shape before scaling

Use `LIMIT 5` or `LIMIT 10`, confirm result shape, then scale.

### 4) Skeleton: list documents with a filter

```aql
FOR d IN @@col
  FILTER d.@field == @value
  LIMIT @limit
  RETURN d
```

Bind vars:
```json
{ "@col": "YourCollection", "field": "status", "value": "active", "limit": 10 }
```

Note: In AQL you can’t parameterize attribute names the same way in all contexts; prefer explicit fields (e.g. `d.status`) unless the manual confirms a safe pattern.

### 5) Skeleton: get a quick sample from a collection

```aql
FOR d IN @@col
  LIMIT @limit
  RETURN d
```

### 6) Skeleton: graph 1-hop neighborhood via edge collections

```aql
FOR v, e IN 1..1 OUTBOUND @start @@edgeCol
  LIMIT @limit
  RETURN {from: e._from, to: e._to, edge: e, vertex: v}
```

### 7) Skeleton: named graph traversal (paths)

```aql
FOR v, e, p IN 1..@depth OUTBOUND @start GRAPH @graphName
  LIMIT @limit
  RETURN {
    vertices: p.vertices[*]._id,
    edges: p.edges[*]._id
  }
```

### 8) Skeleton: “top-N” aggregation

```aql
FOR d IN @@col
  FILTER d.type == @type
  COLLECT key = d.groupKey WITH COUNT INTO n
  SORT n DESC
  LIMIT @limit
  RETURN {key, n}
```

### 9) Checklist when a query is slow

- Add/strengthen FILTERs (more selective).
- Return fewer fields (projection).
- Add LIMIT while iterating.
- Check for existing indexes; if none, propose an index (only if user wants).
- Re-read optimization manual and refactor to a recommended pattern.

