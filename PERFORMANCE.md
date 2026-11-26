# BloomLogic | Performance and QA

## Targets
720p/30 FPS on low-spec hardware and 1080p/60 FPS on capable GPUs are targets, not guarantees. Profile actual physical hardware before expanding the curriculum. Keep simulation deterministic, cache bounded geometry, pool effects and avoid unnecessary draw calls.

## Latest measured release: 1.0.1
Run 45792172356, evidence artifact 15103411879, exact revision 901ef49a1e4b90aae0a30d2d7afea405936a1aca.

Host: Windows Server 2025 Datacenter 64-bit (build 26100), AMD EPYC 9V74, 2 allocated cores / 4 logical CPUs, 17,174,360,064 bytes host RAM, Microsoft Hyper-V Video driver 10.0.26100.1150. Panda3D reported advanced lighting False; renderer/vendor strings empty. No dedicated GPU or actual VRAM measurement. Requested and actual benchmark window resolutions matched. Paused mature plant, VSync disabled, 8 warmup frames and 60 timed task frames per view.

| Resolution / view | Median ms | p95 ms | p99 ms | Approx. median FPS | Frames >50 ms |
|---|---:|---:|---:|---:|---:|
| 1280x720 macro | 29.074 | 29.916 | 30.403 | 34.4 | 0/60 |
| 1280x720 overview | 40.615 | 41.160 | 41.909 | 24.6 | 0/60 |
| 1920x1080 macro | 39.224 | 39.907 | 40.319 | 25.5 | 0/60 |
| 1920x1080 overview | 52.107 | 53.601 | 53.801 | 19.2 | 56/60 |

These rates are derived from median frame times, not sustained GPU measurements. Neither resolution meets every target on this virtual adapter.

| Process check | Elapsed seconds | Sampled peak working set bytes | Exit |
|---|---:|---:|---:|
| Offline self-test | 28.787 | 535453696 | 0 |
| Offline walkthrough | 10.288 | 361533440 | 0 |
| Fresh-process resume | 3.955 | 329465856 | 0 |
| Optional texture failure walkthrough | 10.256 | 361783296 | 0 |
| 720p benchmark | 8.763 | 356286464 | 0 |
| 1080p benchmark | 10.359 | 384520192 | 0 |

Home initialization after Python entry: 0.151s at 720p, 0.172s at 1080p. First scene load: 3.200s and 3.222s respectively. Process memory sampled at 250ms; not exact total system consumption.

## Optimization and limits
41 cached plant mesh stages; 18 pooled droplets; 1024 shadow map on supported graphics. Rhizobox optimized from 172,968 to 8,468 triangles in Phase 3 (actual exported counts). Optional map fallback can reduce visual detail, not a measured speed improvement. Release 1.0 passed hosted tests but failed on a physical device in a shader-enabled path. Hotfix verified fault handling independently of shader support. Physical Windows 10/11 and dedicated GPU profiling remain required. Do not advertise target FPS as achieved.
