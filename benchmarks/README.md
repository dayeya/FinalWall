# Benchmarking
Blanket includes a file to benchmark the string manipulation methods that are used by the detection algorithm.

```markdown
-----------------------------------
Performence benchmark: Path Segment
Ran 1000 iterations in 0.0018032s
Avg time for one iteration on bench_path_segment - 0ms
-------------------------------------
Performence benchmark: Content-Length
Ran 1000 iterations in 0.0770879s
Avg time for one iteration on bench_get_content_length - 37ms
---------------------------------
Performence benchmark: User-Agent
Ran 1000 iterations in 0.0009473s
Avg time for one iteration on bench_get_agent - 0ms
----------------------------------
Performence benchmark: Deny Access
Ran 1000 iterations in 0.16218s
Avg time for one iteration on bench_deny_access - 77mss
```

See [bench.py](https://github.com/dayeya/Blanket/blob/main/benchmarks/bench.py)
