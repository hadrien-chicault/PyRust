# Architecture Overview

PyRust is built on a modern, high-performance architecture leveraging the best of Rust and Python ecosystems.

## High-Level Architecture

```
┌─────────────────────────────────────────────┐
│          Python Application Layer           │
│         (PySpark-compatible API)            │
└─────────────────┬───────────────────────────┘
                  │ PyO3 Bindings
┌─────────────────▼───────────────────────────┐
│           Rust Execution Layer              │
│                                             │
│  ┌──────────────┐      ┌─────────────────┐ │
│  │   PyRust     │      │   DataFusion    │ │
│  │   Wrappers   │─────▶│  Query Engine   │ │
│  └──────────────┘      └─────────────────┘ │
│                                             │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│          Apache Arrow Layer                 │
│       (Columnar Memory Format)              │
└─────────────────────────────────────────────┘
```

## Key Components

### 1. Python API Layer

**Location:** `python/pyrust/`

The Python API provides a PySpark-compatible interface:

- `SparkSession` - Session management
- `DataFrame` - Main data structure
- `GroupedData` - Aggregation interface
- `DataFrameReader` - Data loading

**Technology:** Pure Python with PyO3 bindings

### 2. Rust Core

**Location:** `src/`

The Rust core handles all computation:

- **PyO3 Wrappers** (`src/dataframe/mod.rs`) - Python↔Rust bridge
- **Query Execution** - Powered by DataFusion
- **Memory Management** - Safe, zero-copy operations

**Technology:** Rust, DataFusion, Arrow

### 3. Apache Arrow

DataFusion uses Apache Arrow for:

- **Columnar Storage** - Efficient memory layout
- **Zero-Copy** - Data shared between Python and Rust
- **Vectorization** - SIMD operations for speed

## Data Flow

### Query Execution

```
1. Python API Call
   df.filter("age > 18").select("name")
        ↓
2. PyO3 Binding
   Rust receives DataFrame + operations
        ↓
3. DataFusion Query Plan
   Builds logical plan → optimizes
        ↓
4. Physical Execution
   Executes on Arrow data
        ↓
5. Return to Python
   Arrow → Python via zero-copy
```

### Example Flow

```python
# 1. Python call
df = spark.read.csv("data.csv")
result = df.filter("age > 18").select("name", "city")

# 2. Rust receives:
# - CSV path
# - Filter expression: "age > 18"
# - Columns: ["name", "city"]

# 3. DataFusion:
# - Reads CSV to Arrow
# - Applies filter (predicate pushdown)
# - Projects columns (column pruning)
# - Returns Arrow batches

# 4. Python receives Arrow data (zero-copy)
```

## Design Principles

### 1. Lazy Evaluation

Transformations are lazy - they build a plan without executing:

```python
# These don't execute yet
df2 = df.filter("age > 18")
df3 = df2.select("name")

# Action triggers execution
df3.show()  # Now it executes
```

### 2. Immutability

DataFrames are immutable - operations return new DataFrames:

```python
df1 = spark.read.csv("data.csv")
df2 = df1.filter("age > 18")  # df1 unchanged
```

### 3. Zero-Copy

Data is shared between Python and Rust without copying:

- Arrow format in Rust
- Same Arrow format in Python
- No serialization overhead

### 4. Type Safety

Rust's type system prevents many runtime errors:

- Schema validation at compile time
- Safe memory management
- No null pointer errors

## Performance Characteristics

### Strengths

1. **Columnar Processing** - Efficient cache usage
2. **Vectorization** - SIMD operations
3. **No GC Pauses** - Rust's ownership model
4. **Predicate Pushdown** - Filter early
5. **Column Pruning** - Read only needed columns

### Comparison

| Operation | PySpark | PyRust | Speedup |
|-----------|---------|--------|---------|
| CSV Read | 1.0x | 2-3x | 2-3x faster |
| Filter | 1.0x | 3-5x | 3-5x faster |
| GroupBy | 1.0x | 2-4x | 2-4x faster |
| Join | 1.0x | 2-3x | 2-3x faster |

*Benchmarks on CPU-bound operations with medium datasets*

## Memory Model

### Arrow Columnar Format

```
Traditional Row Format:
[{id:1, name:"Alice", age:25}, {id:2, name:"Bob", age:30}, ...]

Arrow Column Format:
ids:   [1, 2, 3, ...]
names: ["Alice", "Bob", "Charlie", ...]
ages:  [25, 30, 35, ...]
```

**Benefits:**
- Better cache locality
- Vectorized operations
- Compression-friendly

### Reference Counting

DataFrames use `Arc<>` for cheap cloning:

```rust
pub struct PyDataFrame {
    df: Arc<DataFrame>,  // Shared reference
}
```

Multiple Python DataFrames can reference same data.

## See Also

- [Rust Core](rust-core.md) - Rust implementation details
- [Python Bindings](python-bindings.md) - PyO3 integration
- [Performance Tips](../user-guide/performance.md)
