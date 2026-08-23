# Chapter 3: Extreme Context & Chinese AI Innovation (১০ মিলিয়ন কনটেক্সট ও কুডা-মুক্ত সিলিকন)

---

এক বছর আগেও ১০০k কনটেক্সট উইন্ডোকে মনে হতো এক অবিশ্বাস্য অর্জন।

কিন্তু আজ মুনশট AI (Moonshot AI)-এর **Kimi k3** এবং আলিবাবার **Qwen** মডেলগুলো ২ মিলিয়ন থেকে শুরু করে **১০ মিলিয়ন টোকেন (10M Tokens)** কনটেক্সট উইন্ডোতে নিরবচ্ছিন্নভাবে কাজ করছে!

১০ মিলিয়ন টোকেন মানে কী?

এর মানে হলো শেক্সপিয়ারের সমগ্র রচনাবলী, একটি কোম্পানির ৫০টি বার্ষিক রিপোর্ট অথবা ১ লাখ লাইনের সম্পূর্ণ এন্টারপ্রাইজ কোডবেস একসাথে একটিমাত্র প্রম্পটে দিয়ে দেওয়া!

কীভাবে তারা এই অসম্ভবকে সম্ভব করল? এবং কীভাবে চীনের AI ল্যাবগুলো এনভিডিয়ার CUDA ছাড়াই স্বয়ংসম্পূর্ণ ইকোসিস্টেম গড়ে তুলল?

---

## ১. The 10-Million Token Architecture: Moonshot Kimi

```mermaid
flowchart TD
    subgraph RING["[DISTRIBUTED RINGATTENTION TOPOLOGY (10M+ TOKEN CONTEXT)]"]
        direction TB
        subgraph G0["GPU Node 0 (Tokens: 0 - 2.5M)"]
            N0["<b>Compute: FlashAttention</b><br/>Processes local Q Block &bull; Holds KV Block 0"]
        end
        subgraph G1["GPU Node 1 (Tokens: 2.5M - 5.0M)"]
            N1["<b>Compute: FlashAttention</b><br/>Processes local Q Block &bull; Holds KV Block 1"]
        end
        subgraph G2["GPU Node 2 (Tokens: 5.0M - 7.5M)"]
            N2["<b>Compute: FlashAttention</b><br/>Processes local Q Block &bull; Holds KV Block 2"]
        end
        subgraph G3["GPU Node 3 (Tokens: 7.5M - 10.0M)"]
            N3["<b>Compute: FlashAttention</b><br/>Processes local Q Block &bull; Holds KV Block 3"]
        end

        N0 -->|"Async Overlapped KV Shift"| N1
        N1 -->|"Async Overlapped KV Shift"| N2
        N2 -->|"Async Overlapped KV Shift"| N3
        N3 -->|"Async Overlapped KV Shift"| N0
    end

    classDef gStyle fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#f8fafc,rx:8px,ry:8px;
    classDef subStyle fill:#0b0f19,stroke:#334155,stroke-width:1.5px,color:#94a3b8;

    class N0,N1,N2,N3 gStyle;
    class RING,G0,G1,G2,G3 subStyle;
```

### কোর টেকনোলজি:
1. **RingAttention:** সম্পূর্ণ ১০ মিলিয়ন টোকেনের সিকোয়েন্সকে একাধিক GPU-র মধ্যে সার্কুলার রিং আকারে ভাগ করে দেওয়া হয়। প্রতিটি নোড লোকাল অ্যাটেনশন হিসেব করতে করতেই নেটওয়ার্ক দিয়ে তার পাশের নোডকে KV ব্লক পাঠিয়ে দেয়। ফলে কোনো সিঙ্গেল GPU-তে মেমোরি ক্র্যাশ করে না।
2. **Dynamic YaRN (Yet another RoPE extensioN):** রোটারি পজিশনাল এম্বেডিংয়ের হাই-ফ্রিকোয়েন্সি ডাইমেনশন অক্ষুণ্ণ রেখে স্কেলিং ফ্যাক্টর দিয়ে ১০ মিলিয়ন ডাইমেনশন পর্যন্ত এক্সটেন্ড করা।
3. **100% Needle-in-a-Haystack:** ১০ মিলিয়ন শব্দের সাগরে একটিমাত্র গোপন বাক্য লুকিয়ে রাখলেও কিমি ১০০% নিখুঁতভাবে তা খুঁজে বের করতে পারে।

---

## ২. Alibaba Qwen: The Synthetic Data & Coding Engine

আলিবাবার **Qwen 2.5 & Qwen 2.5-Coder** আজ বিশ্বের অন্যতম শীর্ষ কোডিং ও ম্যাথ মডেল।

```mermaid
flowchart TD
    subgraph FLYWHEEL["[SYNTHETIC REASONING DATA & VERIFICATION FLYWHEEL]"]
        direction TB
        S1["<b>1. Seed Problem Bank</b><br/>Olympiad mathematics, competitive code specs, formal logic theorems"]
        S2["<b>2. High-Temperature Generation Engine</b><br/>Generates 10M+ diverse multi-step solution rollouts"]
        S3["<b>3. Automated Formal Ground-Truth Verifier</b><br/>Python Sandbox & Lean 4 Interactive Theorem Prover"]
        S4["<b>4. Formal Verification Filter</b><br/>Extracts 100% mathematically proven trajectories (0% hallucination)"]
        S5["<b>5. Large-Scale RLVR Post-Training</b><br/>Reinforcement Learning with Verifiable Rewards (Qwen / DeepSeek-R1)"]

        S1 --> S2 --> S3 --> S4 --> S5
        S5 -.->|"Self-Distillation of Harder Problems"| S1
    end

    classDef sStyle fill:#78350f,stroke:#fbbf24,stroke-width:2px,color:#f8fafc,rx:8px,ry:8px;
    classDef vStyle fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#f8fafc,rx:8px,ry:8px;
    classDef rlStyle fill:#1e1b4b,stroke:#818cf8,stroke-width:2px,color:#f8fafc,rx:8px,ry:8px;
    classDef subStyle fill:#0b0f19,stroke:#334155,stroke-width:1.5px,color:#94a3b8;

    class S1,S2 sStyle;
    class S3,S4 vStyle;
    class S5 rlStyle;
    class FLYWHEEL subStyle;
```

---

## ৩. Overcoming CUDA: Huawei Ascend 910C & CANN Architecture

আমেরিকার চিপ নিষেধাজ্ঞার পর চীন তৈরি করেছে নিজস্ব চিপ ও সফটওয়্যার স্ট্যাক: **Huawei Ascend 910B/910C NPU** এবং **CANN (Compute Architecture for Neural Networks)**।

```mermaid
flowchart LR
    subgraph NVIDIA["NVIDIA COMPUTE ECOSYSTEM"]
        direction TB
        NV_FRAME["Frameworks: PyTorch / vLLM / SGLang"]
        NV_CUDA["Acceleration: CUDA / cuDNN / TensorRT-LLM"]
        NV_HW["Silicon: Nvidia H100 / B200 SXM5 GPUs"]
        NV_FRAME --> NV_CUDA --> NV_HW
    end

    subgraph HUAWEI["HUAWEI ASCEND ECOSYSTEM"]
        direction TB
        HW_FRAME["Frameworks: PyTorch / vLLM-Ascend"]
        HW_CANN["Acceleration: CANN Architecture Stack"]
        HW_NPU["Silicon: Huawei Ascend 910B / 910C NPUs"]
        HW_FRAME --> HW_CANN --> HW_NPU
    end

    classDef nvStyle fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#f8fafc,rx:6px,ry:6px;
    classDef hwStyle fill:#831843,stroke:#f43f5e,stroke-width:2px,color:#f8fafc,rx:6px,ry:6px;
    classDef subStyle fill:#0b0f19,stroke:#334155,stroke-width:1.5px,color:#94a3b8;

    class NV_FRAME,NV_CUDA,NV_HW nvStyle;
    class HW_FRAME,HW_CANN,HW_NPU hwStyle;
    class NVIDIA,HUAWEI subStyle;
```

* **CANN Compiler:** পিওর PyTorch কোডকে কনভার্ট করে হুয়াওয়ের NPU-তে অপ্টিমাইজড ভেক্টর কোড হিসেবে এক্সেকিউট করে।
* আজ চীনের প্রায় ৫০% ক্লাউড ডাটা সেন্টারে কুডার বিকল্প হিসেবে CANN প্ল্যাটফর্মে মডেল ট্রেইনিং ও ইনফারেন্স চলছে।

---
Developer Perspective
১০ মিলিয়ন কনটেক্সট উইন্ডো পাওয়ার মানে এই নয় যে তুমি সব ডেটা এক প্রম্পটে ঢালবে। ইনপুট টোকেন যত বাড়বে, First-Token Latency (TTFT) তত বাড়বে। তাই ১০ মিলিয়ন কনটেক্সট ব্যবহার করার সময় সার্ভারে **Chunked Prefill** এবং **Prompt Caching** অন রাখা বাধ্যতামূলক।

---
Production Reality
প্রোডাকশনে Qwen-2.5-Coder-32B আজ গ্লোবালি শীর্ষ ওপেন-সোর্স কোডিং মডেল। অনেক এন্টারপ্রাইজ কোম্পানি প্রোপাইটরি কোডের গোপনীয়তা রক্ষার জন্য তাদের ইন্টারনাল সার্ভারে Qwen-2.5-Coder সেলফ-হোস্ট করে গিটহ্যাব কোপাইলটের শতভাগ বিকল্প হিসেবে ব্যবহার করছে।

---
Common Mistake
লং কনটেক্সট টেস্ট করার সময় শুধু টেক্সটের শুরুতে বা শেষে ডেটা দেওয়া। মডেলের আসল পরীক্ষা হলো কনটেক্সটের ঠিক মাঝখানে (যেমন ৩.৫ মিলিয়ন নম্বর টোকেনে) ডেটা রেখে টেস্ট করা (Lost in the Middle Test)।

---

## Interview Flashcards

#### Beginner Level
* **প্রশ্ন:** Kimi এবং Qwen মডেলের প্রধান বিশেষত্ব কী?
* **উত্তর:** কিমি তার অসাধারণ লং-কনটেক্সট ইঞ্জিনের জন্য পরিচিত যা ১০ মিলিয়ন টোকেন পর্যন্ত তথ্য প্রসেস করতে পারে। আর Qwen তার ওপেন-সোর্স কোডিং, গণিত এবং মাল্টিমোডাল দক্ষতায় বিশ্বের অন্যতম সেরা।

#### Intermediate Level
* **প্রশ্ন:** RingAttention কীভাবে লং-কনটেক্সটে মেমোরি সমস্যার সমাধান করে?
* **উত্তর:** RingAttention সম্পূর্ণ সিকোয়েন্সকে একাধিক GPU-র মধ্যে ভাগ করে একটি সার্কুলার রিং বাফারে অ্যাসিনক্রোনাসলি KV ব্লক আদান-প্রদান করে। ফলে কোনো একক GPU-র VRAM উপচে পড়ে না।

#### Advanced Level
* **প্রশ্ন:** Huawei CANN কী এবং কেন এটি গুরুত্বপূর্ণ?
* **উত্তর:** CANN হলো হুয়াওয়ের ডিপ লার্নিং সফটওয়্যার স্ট্যাক যা এনভিডিয়ার CUDA-র সমকক্ষ। এটি হুয়াওয়ের Ascend NPU চিপসেটের ওপর PyTorch ও অন্যান্য ফ্রেমওয়ার্কের কোড অপ্টিমাইজডভাবে চালাতে ব্যবহৃত হয়।
