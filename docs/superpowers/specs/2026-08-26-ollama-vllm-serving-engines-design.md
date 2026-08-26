# Design Specification: Ollama, vLLM & Modern LLM Inference Serving Engines

- **Date:** 2026-08-26
- **Target File:** `handbook/frontier_ch6.md`
- **Topic:** In-depth architectural mechanics of Ollama, vLLM, comparative analysis, and related modern inference engines (SGLang, TensorRT-LLM, TGI, ExLlamaV2).

---

## 1. Executive Summary & Goals

This specification defines the content, technical depth, diagrams, mathematical formulas, and comparative frameworks to expand **Chapter 6 in Sector 3 (Frontier AI & Infrastructure)** of the *AI Engineering Handbook*.

The objective is to provide a world-class, production-grade, bilingual (Bengali + English) technical deep-dive into how modern LLM inference engines operate under the hood:
1. **BitNet b1.58:** Maintain and tighten the 1-bit / ternary weight foundation (zero-MAC addition-only matrix engine).
2. **Ollama Architecture:** Deep dive into Go daemon orchestration, `llama.cpp` C++ engine, `ggml` backend, GGUF binary format, `mmap` zero-copy memory mapping, CPU/GPU dynamic layer offloading, and the Modelfile abstraction.
3. **vLLM Architecture:** Root cause of the serving bottleneck (KV-cache fragmentation), PagedAttention virtual memory block tables, Continuous Batching (iteration-level scheduling), Chunked Prefill, Automatic Prefix Caching (APC), Speculative Decoding, and multi-GPU Tensor Parallelism.
4. **Head-to-Head Architectural Matrix:** Direct vector comparison across 8 production dimensions.
5. **Modern Serving Landscape:** Deep dive into SGLang (RadixAttention for agentic multi-turn loops), TensorRT-LLM (NVIDIA custom CUDA kernels), TGI, and ExLlamaV2.
6. **Key Serving Metrics & VRAM Math:** Formal definitions and equations for TTFT, ITL/TPOT, throughput (tok/s/GPU), and exact KV-cache sizing calculations.
7. **Production Flowchart & 3-Tier Flashcards:** A Mermaid decision tree for picking engines, real-world developer perspectives, production realities, common pitfalls, and 3 levels of interview flashcards.

---

## 2. Chapter Structure & Detailed Content Specification

### Section 1: ১. BitNet b1.58: The Addition-Only Neural Network (১-বিট AI)
- Retain the core ternary weights $\{-1, 0, 1\}$ concept and $\log_2(3) \approx 1.58$ bit derivation.
- ASCII / Mermaid flowchart contrasting standard FP16 GEMM with BitNet addition-only accumulator.
- Memory bandwidth savings (10x reduction) and energy efficiency for edge/CPU inference.

### Section 2: ২. How Ollama Works Under the Hood (লোকাল ইঞ্জিনের আর্কিটেকচার)
- **Architecture Layers:**
  - **Client & CLI / REST API:** Endpoints (`/api/generate`, `/api/chat`, OpenAI compatibility layer at `/v1/chat/completions`).
  - **Go Daemon (Orchestrator):** Manages model registry, downloads blobs, loads Modelfiles, and spawns native engine processes.
  - **llama.cpp / libggml (C++ Execution Engine):** Direct hardware acceleration via SIMD (AVX2, AVX-512, ARM NEON), Apple Metal (`MPS`), NVIDIA CUDA, AMD ROCm, and Vulkan.
- **The GGUF Binary Format:**
  - Successor to GGML. Single-file packaging of model metadata, tokenizer vocabulary, quantization quantization scales, and tensor weights.
- **Zero-Copy Memory Mapping (`mmap`):**
  - Why models load in milliseconds: instead of reading 8GB into application memory heap via `fread()`, Ollama maps the file directly into virtual address space.
  - OS page cache handles lazy paging of weights directly to RAM/VRAM.
- **Dynamic Layer Offloading (`--n-gpu-layers`):**
  - Transformer layer splitting: how $L$ transformer layers are split between GPU VRAM and system CPU RAM when model size exceeds VRAM.
  - Latency penalty of PCI-e bus transfer for activation tensors between CPU and GPU.
- **Modelfile Abstraction:**
  - Docker-like syntax: `FROM`, `PARAMETER temperature`, `SYSTEM`, `TEMPLATE`.
- **Mermaid Diagram:** Ollama system architecture from User Request -> Go Server -> `mmap` -> llama.cpp -> Metal/CUDA backend.

### Section 3: ৩. How vLLM Works Under the Hood (এন্টারপ্রাইজ প্রোডাকশন ইঞ্জিন)
- **The Core Problem: The KV-Cache Memory Wall & Fragmentation:**
  - During autoregressive generation, Keys and Values of all prior tokens must be stored in GPU VRAM to avoid recalculating attention.
  - Traditional serving (Hugging Face Transformers): pre-allocates contiguous memory for maximum context length ($L_{\max}$).
  - *Internal Fragmentation:* Pre-allocated slots reserved for tokens that may never be generated.
  - *Reservation Fragmentation:* Unused memory reserved for future generation steps.
  - *External Fragmentation:* Memory fragmentation between requests of different lengths.
  - Result: 60%–80% of GPU VRAM wasted, limiting batch size to 2–4 requests.
- **PagedAttention Mechanism (The Core Breakthrough):**
  - Inspired by Virtual Memory Paging in OS (e.g., Linux page tables).
  - Divides the KV-cache of each sequence into fixed-size **Logical Blocks** (e.g., 16 or 32 tokens).
  - Maps logical blocks to non-contiguous **Physical Blocks** in GPU VRAM via a **Block Table**.
  - No contiguous memory requirement: new physical blocks are allocated dynamically on-demand as tokens are generated.
  - Zero internal fragmentation (except the last block), zero external fragmentation.
  - **Copy-on-Write (CoW) Memory Sharing:** Parallel sampling (generating $N$ candidate responses from 1 prompt) shares identical prefix blocks; forks physical blocks only when outputs diverge.
- **Continuous Batching (Iteration-Level Scheduling):**
  - Static batching vs Continuous batching (Orca-style).
  - Traditional static batching locks an entire batch until the slowest sequence completes, wasting GPU compute cycles on completed sequences.
  - Continuous Batching operates at each single-token iteration step: evicts finished requests immediately and injects waiting requests into the active batch without recomputing existing KV-caches.
- **Chunked Prefill & Latency Balancing:**
  - LLM serving has two phases: **Prefill** (compute-bound, process prompt tokens in parallel) and **Decode** (memory-bandwidth-bound, generates 1 token at a time).
  - A massive 8K prompt in prefill can starve active decoding requests, causing spikes in Inter-Token Latency (ITL).
  - Chunked Prefill chops the prompt into chunks (e.g. 512 tokens) and co-schedules them alongside decode tokens, smoothing TTFT and ITL.
- **Automatic Prefix Caching (APC):**
  - Reuses KV-cache of shared system prompts, multi-turn chat histories, or RAG reference documents across different requests.
- **Distributed Inference (Tensor Parallelism):**
  - Megatron-style tensor parallel matrix splitting across 2, 4, or 8 GPUs (`--tensor-parallel-size`) via NCCL / Ray.
- **Mermaid Diagram:** Detailed PagedAttention Block Table Mapping & Continuous Batching iteration timeline.

### Section 4: ৪. Head-to-Head Architectural Comparison (Ollama বনাম vLLM)
- Comparison Table across:
  1. Primary Design Objective
  2. Execution Engine Core
  3. KV-Cache Memory Management
  4. Batching Paradigm
  5. Target Hardware & Deployment
  6. Optimal Concurrency Range
  7. Quantization Support
  8. Operational Complexity & Observability

### Section 5: ৫. The Extended Serving Landscape: SGLang, TensorRT-LLM, TGI, ExLlamaV2
- **SGLang (Structured Generation Language) & RadixAttention:**
  - Why SGLang is challenging vLLM in 2025–2026.
  - Radix Tree data structure for maintaining and matching KV-cache across complex branching, multi-turn dialogues, agentic loops, and tree-of-thought searches.
  - Native high-speed structured JSON / regex decoding (outlines integration).
- **TensorRT-LLM (NVIDIA Native):**
  - Extreme hardware optimization for NVIDIA Hopper (H100/H200) and Blackwell (B200).
  - Custom fused multi-head attention (FMHA), In-Flight Batching, native FP8 / FP4 tensor core exploitation.
  - Peak throughput, but proprietary to NVIDIA and complex compilation pipeline.
- **TGI (Text Generation Inference by Hugging Face):**
  - Production engine written in Rust (router & web server) + Python/C++ (backends).
  - Watermarking, token streaming, OpenTelemetry metrics.
- **ExLlamaV2 (EXL2):**
  - Custom CUDA kernels for single-GPU gaming/workstation rigs (RTX 3090/4090).
  - Mixed-bit precision quantization (e.g., 3.5 bpw, 4.2 bpw).

### Section 6: ৬. Serving Metrics & Memory Sizing Formulas (গণিত ও ক্যালকুলেশন)
- **Primary Serving Metrics:**
  - **TTFT (Time to First Token):** $T_{\text{prefill}} = \frac{\text{Prompt Tokens}}{\text{Prefill FLOPS / Bandwidth}}$
  - **ITL (Inter-Token Latency) / TPOT (Time Per Output Token):** $T_{\text{decode}} = \frac{2 \times \text{Parameters} + \text{KV-Cache Size}}{\text{Memory Bandwidth (GB/s)}}$
  - **Throughput:** Total tokens generated per second across all active requests.
- **The KV-Cache Sizing Formula:**
  $$\text{KV Cache Size per Token} = 2 \times n_{\text{layers}} \times n_{\text{heads}} \times d_{\text{head}} \times \text{Precision Bytes}$$
  - Step-by-step calculation example for Llama 3 8B (32 layers, 8 KV heads with GQA, 128 head dim, FP16):
    $$\text{Bytes per token} = 2 \times 32 \times 8 \times 128 \times 2 = 131,072 \text{ bytes} \approx 128 \text{ KB/token}$$
  - For 100 concurrent users with 4K context:
    $$100 \times 4096 \times 128 \text{ KB} \approx 52.4 \text{ GB VRAM}$$ (Demonstrating why PagedAttention is mandatory for enterprise concurrency).

### Section 7: ৭. Decision Tree, Production Realities & Interview Flashcards
- **Production Architecture Decision Flowchart (Mermaid):**
  - Clear branch paths: Local dev / single laptop -> Ollama; High concurrency enterprise API -> vLLM or SGLang; Agentic multi-turn with complex schema -> SGLang; Pure NVIDIA peak throughput on H100 -> TensorRT-LLM.
- **Developer Perspective:**
  - Running local models on Apple Silicon Mac Studio via Ollama/Metal vs AWS vLLM instances.
- **Production Reality:**
  - The danger of running Ollama in multi-user production (lack of continuous batching causes severe queue head-of-line blocking).
- **Common Mistake:**
  - Calculating GPU VRAM based only on model weights, forgetting that KV-cache scales with `Concurrency * Context Length`.
- **Interview Flashcards (3 Levels):**
  - Beginner: What is the primary architectural difference between Ollama and vLLM?
  - Intermediate: How does PagedAttention eliminate memory fragmentation, and what role do Block Tables play?
  - Advanced: How does Continuous Batching (Iteration-level scheduling) eliminate GPU bubbles, and how does SGLang's RadixAttention differ from vLLM's PagedAttention?

---

## 3. Verification & Quality Gates

1. **Formatting & Syntax:**
   - Valid Markdown, clean KaTeX formulas (`$$...$$`), standard GitHub alerts, and syntactically correct Mermaid diagrams.
2. **Technical Accuracy:**
   - Accurate representation of PagedAttention equations, GGUF/mmap behavior, Continuous Batching schedules, and SGLang RadixAttention.
3. **Consistency with Handbook:**
   - Follows the design language, tone, and callout standards (`Developer Perspective`, `Production Reality`, `Common Mistake`, `Interview Flashcards`) established across Sectors 1, 2, and 3.
