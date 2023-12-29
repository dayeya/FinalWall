# Benchmarking
Blanket includes a file to benchmark the string manipulation methods that are used by the detection algorithm.

```ps1
-----------------------------------
Performence benchmark: Path Segment
Ran 1000 iterations in 0.0015354s
Avg time for one iteration on bench_path_segment - 0ms
-------------------------------------
Performence benchmark: Content-Length
Ran 1000 iterations in 0.0810211s
Avg time for one iteration on bench_get_content_length - 43ms
---------------------------------
Performence benchmark: User-Agent
Ran 1000 iterations in 0.0010192s
Avg time for one iteration on bench_get_agent - 0ms
```

See bench.py [docs](https://github.com/dayeya/Blanket/blob/main/benchmarks/bench.py)