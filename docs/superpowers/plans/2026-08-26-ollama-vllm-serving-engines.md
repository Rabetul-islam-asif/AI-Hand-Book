# Ollama, vLLM & Modern Serving Engines Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand `handbook/frontier_ch6.md` into an exhaustive architectural deep dive covering BitNet b1.58, Ollama, vLLM, PagedAttention, Continuous Batching, SGLang, TensorRT-LLM, serving metrics, and production flashcards.

**Architecture:** Maintain the existing 1-bit foundation, then expand into 7 comprehensive sections with Mermaid diagrams, bilingual explanations (Bengali + English), ASCII architectures, exact formulas for KV-cache sizing, and 3-level interview flashcards. Ensure `index.html` navigation and TOC continue to cleanly render the expanded chapter.

**Tech Stack:** Markdown, Mermaid.js, KaTeX LaTeX math, HTML5/JS (Marked.js, Highlight.js).

## Global Constraints
- Target file: `handbook/frontier_ch6.md`
- Preserve bilingual style (clean Bengali concept explanations with industry-standard English terminology).
- Preserve callouts: `Developer Perspective`, `Production Reality`, `Common Mistake`, and `Interview Flashcards`.
- Mermaid diagrams must use valid syntax with enclosed node strings to prevent parser breakages.
- Math equations must use valid KaTeX delimiters (`$$...$$` or `$..$`).

---

### Task 1: Draft the Comprehensive Chapter 6 Content in `handbook/frontier_ch6.md`

**Files:**
- Modify: `handbook/frontier_ch6.md:1-133`

- [ ] **Step 1: Write the complete expanded content into `handbook/frontier_ch6.md`**
Include:
1. Section 1: BitNet b1.58 (Ternary weights $\{-1, 0, 1\}$, Addition-only matrix math, 10x bandwidth savings).
2. Section 2: Ollama Deep Dive (Go daemon orchestrator, `llama.cpp` C++ engine, `ggml` backend, GGUF binary format, `mmap` zero-copy memory mapping, CPU/GPU layer offloading with `--n-gpu-layers`, Modelfile abstraction, Mermaid architecture diagram).
3. Section 3: vLLM Deep Dive (KV-Cache Memory Wall & Fragmentation, PagedAttention block tables & OS virtual memory analogy, Copy-on-Write sharing, Continuous Batching / Iteration-level scheduling vs static batching, Chunked Prefill, Automatic Prefix Caching, Tensor Parallelism across multi-GPU, Mermaid sequence & memory diagram).
4. Section 4: Head-to-Head Architectural Comparison (Ollama vs vLLM 8-dimension matrix table).
5. Section 5: The Extended Serving Landscape (SGLang & RadixAttention for multi-turn/agents, TensorRT-LLM for peak NVIDIA kernels, TGI, ExLlamaV2).
6. Section 6: Serving Metrics & Memory Sizing Formulas (TTFT, ITL/TPOT, Throughput, exact KV-cache sizing formula: $2 \times n_{\text{layers}} \times n_{\text{heads}} \times d_{\text{head}} \times \text{bytes}$, with concrete Llama 3 8B calculation).
7. Section 7: Production Decision Flowchart (Mermaid), Developer Perspective, Production Reality, Common Mistake, and 3-tier Interview Flashcards.

- [ ] **Step 2: Verify file syntax, equations, and Mermaid diagrams**
Validate that Mermaid blocks have proper formatting and no broken quotes or HTML entities.

- [ ] **Step 3: Commit changes to Git**
Run: `git add handbook/frontier_ch6.md && git commit -m "feat(ch6): expand Ollama and vLLM architecture deep dive in Chapter 6"`

---

### Task 2: Verify Rendering in Web Viewer and PDF Engine

**Files:**
- Test: Local browser preview via `run.py` (or verify markdown parsing via test script)

- [ ] **Step 1: Run Python verification script to check Markdown parsing, KaTeX tokens, and Mermaid validity**
- [ ] **Step 2: Verify `index.html` loads and renders `frontier_ch6.md` without errors**
- [ ] **Step 3: Commit any adjustments if needed**
