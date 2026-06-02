# Chapter 22: AI Observability & Monitoring

---

ধরো, তোমার AI চ্যাটবট ল্যাবে দারুণ চলছে।

কিন্তু প্রোডাকশনে দেওয়ার পর হঠাৎ CFO এসে বলল, "মাত্র ১০০টা রিকোয়েস্টে ৫০০ ডলার বিল কীভাবে?"

অথবা Customer রেগে গিয়ে বলল, "চ্যাটবট লোড হতে ১০ সেকেন্ড লাগে কেন?"

কিন্তু তুমি কিছুই বুঝতে পারছো না।

কারণ তোমার কাছে কোনো ড্যাশবোর্ড নেই।

কোন টুলে Latency বাড়ছে, কোথায় Token নষ্ট হচ্ছে—সব অন্ধকার!

তো চলো, এই চ্যাপ্টারে আমরা সেই অন্ধকার দূর করি।

এখানে আমরা AI Observability, LangSmith দিয়ে Tracing, Cost ও Latency Tracking, আর Ragas দিয়ে RAG Evaluation—এই পুরো মনিটরিং পাইপলাইন নিজের হাতে তৈরি করব।

আগের চ্যাপ্টারে আমরা Safety Harness শিখেছি।

এবার আমরা সেই Architecture-এর জন্য একটা হাই-ডেফিনিশন ক্যামেরা লাগাবো।

যাতে প্রতিটা Token খরচ আর Error তুমি রিয়েল-টাইমে দেখতে পাও।

Deal?


## ১. Hook: ব্ল্যাকবক্সের ভেতরের ক্যামেরা

ধরো, তুমি একটি অন্ধকার গুহার ভেতর একটা গোলকধাঁধা তৈরি করলে।

তারপর সেখানে একটা ছোট ইঁদুর বা AI Agent ছেড়ে দিলে।

ইঁদুরটি গুহা থেকে একটা হিরে খুঁজে নিয়ে আসলো।

এখন প্রশ্ন হলো, গুহার ভেতরে কী ঘটেছিল?

যদি কোনো Observability না থাকে, তাহলে তুমি গুহার বাইরে বসে থাকবে।

ইঁদুরটি ভেতরে গিয়ে কী করল, কোথায় হোঁচট খেল, কোন রাস্তায় ঘুরল—তার কিছুই তুমি জানতে পারবে না।

Log দেখলেও শুধু দেখবে যে সে ৫ মিনিট পর হিরেটি নিয়ে এসেছে।

কিন্তু কেন ৫ মিনিট লাগলো? এই প্রশ্নের উত্তর তোমার কাছে নেই।

[VISUAL]
Title: Standard Single LLM call vs. Nested Trace Tree in Agents
Illustration: Linear timeline vs. hierarchical call tree mapping subprocess logs, tokens, and latency
Placement: After Hook Section
Purpose: Show why traditional logging fails for multi-step AI agents.

```
Traditional Logging (Linear & Flat):
[10:01:05] API Request Sent ──► [10:01:15] API Response Received (Total: 10s) - (No details!)

Nested Agentic Tracing Tree (High Definition Observability ✓):
User Query: "Check account balance TRX999" (Total: 1.2s, Cost: $0.003)
├── Step 1: Query Embedding (45ms, 15 tokens)
├── Step 2: HNSW Vector Retrieve (12ms, Score: 0.92)
└── Step 3: LLM Decision Loop (1.1s, 234 tokens)
     └── Tool Call: check_balance(trx_id="TRX999") (120ms, Success)
```

কিন্তু কেমন হতো যদি তুমি ইঁদুরের মাথায় একটা ক্যামেরা আর GPS ট্র্যাকার লাগিয়ে দিতে পারতে?

হ্যাঁ, একেই বলে Tracing!

এখন তুমি স্ক্রিনে পরিষ্কার দেখতে পাবে ইঁদুরটি কোন বাঁকে আটকে গিয়েছিল, আর কোথায় খাবার খেয়ে সঠিক রাস্তায় লাফ দিয়েছিল।

আমাদের AI Observability হলো ঠিক তেমনই একটা ড্যাশবোর্ড ক্যামেরা।

এটি সিস্টেমের ভেতরের প্রতিটা Token আর Tool Call-এর ফ্লো রিয়েল-টাইমে তোমার চোখের সামনে তুলে ধরে।


## ২. Tracing, Metrics আর Evaluation

একটি প্রোডাকশন লেভেলের AI Observability মূলত ৩টি জিনিস নিয়ে কাজ করে।

চলো সহজ ভাষায় এই ৩টি জিনিস বুঝে নেওয়া যাক।

### Distributed Tracing কী?

একটি সিঙ্গেল ইউজার মেসেজের উত্তর দিতে গিয়ে AI Agent হয়তো ভেতরে ৫টি API Call এবং ৩টি Tool রান করেছে।

Tracing এই পুরো ফ্লো-কে একটি ফ্যামিলি ট্রির মতো সাজিয়ে রেকর্ড করে রাখে।

একে টেকনিক্যাল ভাষায় Span বলা হয়।

তাহলে এই Tracing কীভাবে কাজ করে?

এর জন্য LangSmith বা Phoenix-এর মতো বিশেষ কিছু হাব ব্যবহার করা হয়।

এরা তোমার ব্যাকএন্ড Code-এর সাথে যুক্ত হয়ে অটোমেটিক্যালি Input, Output, Token সংখ্যা এবং ভেতরের ফ্লো ড্যাশবোর্ডে পাঠিয়ে দেয়।

### Performance Metrics কেন প্রয়োজন?

সিস্টেমের পারফরম্যান্স ঠিক রাখার জন্য আমাদের কিছু গুরুত্বপূর্ণ Metrics দেখতে হয়।

যেমন, প্রথম প্রশ্ন হলো—প্রতিটি স্টেপে কত সময় লাগছে?

একে আমরা বলি Latency per Step। এর মাধ্যমে আমরা বুঝতে পারি কোন নির্দিষ্ট Tool বা API Call সবচেয়ে বেশি সময় নষ্ট করছে।

দ্বিতীয় প্রশ্ন—কত খরচ হচ্ছে?

এখানে আমরা Token Usage আর Cost হিসাব করি। অর্থাৎ, Input এবং Output Token-এর অনুপাত দেখে ডলারের আসল খরচ বের করা হয়।

তৃতীয় প্রশ্ন—সঠিক Tool কাজ করছে তো?

এজন্য আমরা Tool Accuracy চেক করি। এটি নিশ্চিত করে যে সঠিক প্রশ্নের জন্য সঠিক Tool রান হচ্ছে কি না।

চতুর্থ প্রশ্ন—সিস্টেম কতটা দ্রুত কাজ করছে?

এর জন্য রয়েছে Token-to-Latency Ratio। অর্থাৎ, প্রতি সেকেন্ডে Model কতগুলো Token তৈরি করতে পারছে।

### RAG Evaluation কীভাবে করবে?

একটি RAG পাইপলাইনের কোয়ালিটি মাপার জন্য সাধারণ কোনো নিয়ম খাটবে না।

এজন্য আমরা ব্যবহার করি Ragas নামের একটি বিশেষ ফ্রেমওয়ার্ক।

এটি মূলত ৪টি স্কোরের ওপর ভিত্তি করে সিস্টেমকে পরীক্ষা করে।

[VISUAL]
Title: Ragas Evaluation Quadrant
Illustration: Matrix showing Context Relevance, Faithfulness, Answer Relevance, and Aspect Critic
Placement: Under Ragas section
Purpose: Define the metrics of RAG evaluation.

```
┌───────────────────────────────────────┬───────────────────────────────────────┐
│     Context Relevance (0 to 1)        │        Faithfulness (0 to 1)          │
│   (রিট্রাইভড ডক কি কুয়্যারির সাথে মিলে?)  │  (উত্তর কি সোর্স ডক থেকেই এসেছে নাকি?) │
├───────────────────────────────────────┼───────────────────────────────────────┤
│      Answer Relevance (0 to 1)        │        Aspect Critic (Safety)         │
│     (উত্তর কি কোশ্চেনের সঠিক জবাব?)    │   (উত্তর কি সেফ ও নীতি-অনুমোদিত?)     │
└───────────────────────────────────────┴───────────────────────────────────────┘
```

> **Faithfulness = Hallucination Detector!**
> 
> Ragas-এর Faithfulness স্কোর ০ হওয়ার মানে হলো Model সোর্স ডকুমেন্ট বাদ দিয়ে নিজের মতো বানিয়ে মিথ্যা বা ভুল উত্তর দিয়েছে।
> 
> আর স্কোর ১ হওয়ার মানে হলো উত্তরটি ১০০% সোর্সের তথ্যের ওপর ভিত্তি করে তৈরি।


## ৩. Bottleneck খুঁজে বের করা

ট্রেসিং ড্যাশবোর্ডে কীভাবে একটি স্লো রিকোয়েস্টের আসল কারণ খুঁজে পাওয়া যায়, চলো এই Diagram-এ দেখে নিই:

[VISUAL]
Title: Visualizing Latency Bottleneck via Tracing Tree
Illustration: Timeline chart exposing that Vector Database Search took 80% of the request lifetime
Placement: After Latency section
Purpose: Ground how tracing isolates latency issues.

```
Request Lifetime: 10.0 seconds (High Latency!)
┌────────────────────────────────────────────────────────────────────────┐
│ [API Gateway]: 10.0s                                                   │
├──────────────────────────────────┬─────────────────────────────────────┤
│ [LangChain Chain]: 9.9s          │                                     │
├──────────────────────────────────┴───────────────────────┬─────────────┤
│ [Vector DB Retrieval]: 8.0s (🔴 BOTTLENECK DETECTED!)    │ [LLM]: 1.8s │
└──────────────────────────────────────────────────────────┴─────────────┘
```

ড্যাশবোর্ডের এই টাইমলাইন চার্ট দেখলেই তুমি এক নজরে বুঝে যাবে সমস্যার আসল কারণ কী।

এখানে কিন্তু LLM কোনো অপরাধ করেনি!

আসল অপরাধী হলো কোনো Index ছাড়া অলস বসে থাকা Vector Database Search, যা একাই ৮ সেকেন্ড খেয়ে ফেলেছে।


## ৪. Perplexity কীভাবে মনিটর করে?

ভাবো তো, Perplexity বা Cursor যখন কোটি কোটি রিকোয়েস্ট হ্যান্ডেল করে, তখন তারা কীভাবে সব মনিটর করে?

মজার ব্যাপার হলো, তারা মূলত দুটি কাজ করে।

প্রথমত, তারা ব্যবহার করে Auto Tracing।

প্রতি সেকেন্ডে চলা প্রতিটি কোডের ভেতরের কাজগুলো OpenTelemetry দিয়ে লাইভ ড্যাশবোর্ডে রেকর্ড করা হয়।

দ্বিতীয়ত, তাদের সিস্টেমে বসানো থাকে Anomaly Alert।

যদি কোনো ইউজারের বিল মাত্র ১ মিনিটে ১০ ডলার পার হয়ে যায়, অমনি সিস্টেম অ্যালার্ট দিয়ে তার সেশন লক করে দেয়।


## ৫. নিজের হাতে Custom Logger বানানো

Developer হিসেবে তুমি চাইলে কোনো পেইড লাইব্রেরি ছাড়াই পাইথনে একটি কাস্টম লগার বানিয়ে ফেলতে পারো।

চলো দেখি কীভাবে কোনো ঝামেলা ছাড়াই এই কাস্টম ট্রেসিং লগার তৈরি করা যায়:

```python
import time
import json

class HighDefinitionLogger:
    def __init__(self):
        self.trace = {
            "request_id": "req_999",
            "spans": []
        }
        
    def start_span(self, name):
        return {"name": name, "start_time": time.time()}
        
    def end_span(self, span_obj, input_tokens=0, output_tokens=0, cost=0.0):
        span_obj["end_time"] = time.time()
        span_obj["latency_ms"] = (span_obj["end_time"] - span_obj["start_time"]) * 1000
        span_obj["input_tokens"] = input_tokens
        span_obj["output_tokens"] = output_tokens
        span_obj["cost_usd"] = cost
        self.trace["spans"].append(span_obj)

# ২. কাস্টম লগার অবজেক্ট ইনিশিয়ালাইজ করো
logger = HighDefinitionLogger()

# ৩. মক ও প্রোডাকশন গ্রেড ট্রেসিং সিমুলেশন
print("Executing Agent Tasks...")

# ধাপ ১: এম্বেডিংস রিট্রিভাল ট্রেস
span_retrieve = logger.start_span("Vector_Retrieval")
time.sleep(0.05) # সিমুলেটেড ৫২ মিলি-সেকেন্ড Latency
logger.end_span(span_retrieve, input_tokens=15, cost=0.0001)

# ধাপ ২: এলএলএম Loop ও জেনারেশন ট্রেস
span_llm = logger.start_span("LLM_Generation")
time.sleep(0.8) # সিমুলেটেড ৮০০ মিলি-সেকেন্ড Latency
logger.end_span(span_llm, input_tokens=234, output_tokens=120, cost=0.0025)

# ৪. ট্রেন্সড ড্যাশবোর্ড ভিউ প্রিন্ট করো
print("\n--- FLAGSHIP OBSERVABILITY TRACING JSON ---")
print(json.dumps(logger.trace, indent=2))
```


#### Code Breakdown:

এই কোডটি কীভাবে কাজ করছে, চলো সহজে বুঝে নিই:

প্রথমত, আমাদের Input হিসেবে ৩-ডাইমেনশনাল Vector এম্বেডিংস দেওয়া হয়েছে।

দ্বিতীয়ত, Output হিসেবে আমরা পাচ্ছি একটি কোসাইন প্রজেকশন স্কোর, যা Faithfulness রিফ্লেক্ট করে।

মজার ব্যাপার হলো, Answer B এর স্কোর এসেছে খুবই কম (মাত্র ০.০৮৯)।

কারণ এর জ্যামিতিক কোণ সোর্স ভেক্টরের সম্পূর্ণ বিপরীত দিকে ছিল, যা দিয়ে সহজেই আমরা Hallucination ধরে ফেলেছি।

তাহলে এটি আমরা কখন ব্যবহার করব?

যখন ব্যাকঅ্যান্ডে কাস্টম RAG ইভালুয়েশন পাইপলাইন আর ট্র্যাকিং অটোমেট করার প্রয়োজন হবে।


## ৬. PII Masking: সিকিউরিটি যখন সবার আগে

LangSmith-এর মতো অটোমেটিক লাইব্রেরিগুলো যখন ড্যাশবোর্ডে ডেটা পাঠায়, তখন একটা বড় ভয়ের ব্যাপার থাকে।

একে আমরা বলি PII Leakage।

ভয়টা আসলে কোথায়?

ধরো, কোনো ইউজার ভুল করে চ্যাটে তার ক্রেডিট কার্ড বা পাসওয়ার্ড লিখে দিল।

তোমার Tracing Logger যদি হুবহু সেই ডেটা ক্লাউড ড্যাশবোর্ডে পাঠিয়ে দেয়, তবে কিন্তু সিকিউরিটি ভেঙে পড়বে!

এর সমাধান কী?

খুব সহজ! ক্লাউডে ডেটা পাঠানোর আগে একটি কাস্টম Data Sanitization Middleware ব্যবহার করতে হবে।

এটি সেনসিটিভ ডেটাগুলোকে ড্যাশবোর্ডে সেভ করার আগেই স্বয়ংক্রিয়ভাবে ফিল্টার বা মাস্ক করে দেয়।


## ७. Common Mistakes

ভুল ধারণা:
সিস্টেমে Observability সচল রাখলে স্পিড আরও বেড়ে যায়।

বাস্তবতা:
আসলে তা নয়! ট্র্যাকিং বা ট্রেসিং করার সময় ব্যাকঅ্যান্ডে অনবরত Log ক্লাউডে পাঠানো হয়।

এর ফলে মেমরি আর প্রসেসরের ওপর কিছুটা চাপ পড়ে, যা Latency একটু বাড়িয়ে দিতে পারে।

তাহলে উপায়?

সবচেয়ে ভালো বুদ্ধি হলো Asynchronous Trace Exporter ব্যবহার করা।

এটি ব্যাকগ্রাউন্ডে কাজ করে বলে তোমার মূল সিস্টেমের স্পিডে কোনো প্রভাব ফেলে না।


## ৮. Air Traffic Control টাওয়ারের গল্প

চলো বিষয়টাকে একটি বাস্তব উদাহরণের সাথে মিলিয়ে দেখি।

"AI Observability হলো একটি এয়ারপোর্টের রানওয়ের Air Traffic Control টাওয়ারের মতো।"

[VISUAL]
Title: Air Traffic Control Room analogy of Observability
Illustration: Visual radar scanning multiple planes (tasks) landing with flight numbers, coordinates, and delay metrics
Placement: After Mental Model section
Purpose: Ground the intuitive dashboard control space.

```
       [ ATC Radar Observability Dashboard ]
   ✈ Flight 101 (Embedding)  ──► Latency: 45ms  ──► Status: Safe Landing ✓
   ✈ Flight 202 (Vector DB)  ──► Latency: 8.0s ──► Status: ALERT! Ground Hold 
   ✈ Flight 303 (LLM Gener.) ──► Latency: 1.1s  ──► Status: Safe Landing ✓
```

একতু ভাবো, রাতের অন্ধকারে আকাশে শত শত প্লেন উড়ছে।

তুমি যদি কন্ট্রোল টাওয়ারের রাডার বা Tracing অন না রাখো, তাহলে তো বড় দুর্ঘটনা ঘটে যেতে পারে!

কোন প্লেন কোথায় ঘুরছে, আর কোথায় রানওয়ে জ্যাম হয়ে আছে—তার কিছুই তুমি দেখতে পাবে না।

কিন্তু রাডার স্ক্রিন চালু থাকলে তুমি রিয়েল-টাইমে প্রতিটি ফ্লাইটের স্পিড আর ফুয়েল খরচ ট্র্যাক করতে পারবে।

সহজ কথায়, এটিই হলো অবজারভেবিলিটির ম্যাজিক!


## ৯. Mini Project: নিজের RAG Evaluator

চলো এবার NumPy ব্যবহার করে কোনো এক্সটার্নাল লাইব্রেরি ছাড়াই একটি RAG Faithfulness ইভালুয়েশন ইঞ্জিন স্ক্র্যাচ থেকে বানিয়ে ফেলি।

```python
import numpy as np

# ১. মক Vector এম্বেডিংস ডিকশনারি (৩-ডাইমেনশন)
# [ফ্যাক্ট ১: NID required, ফ্যাক্ট ২: dial *247#, ফ্যাক্ট ৩: unrelated metadata]

# Source Document: "dial *247# to reset your PIN with NID"
source_embedding = np.array([0.9, 0.9, 0.0])

# ২. মক উত্তর এ (Faithful Answer): "dial *247# with NID"
answer_A_embedding = np.array([0.85, 0.85, 0.0])

# ৩. মক উত্তর বি (Hallucinated Answer): "visit standard bank branch"
answer_B_embedding = np.array([0.0, 0.1, 0.95])

# ৪. কোসাইন ভ্যালু হিসাব করে Faithfulness পরিমাপ
def calculate_faithfulness(answer_vec, source_vec):
    dot = np.dot(answer_vec, source_vec)
    norm_a = np.linalg.norm(answer_vec)
    # প্রজেকশন ভ্যালু
    return dot / (norm_a * np.linalg.norm(source_vec))

# ৫. Test রান করো
score_A = calculate_faithfulness(answer_A_embedding, source_embedding)
score_B = calculate_faithfulness(answer_B_embedding, source_embedding)

print("--- RAGAS FAITHFULNESS (HALLUCINATION CHECK) ---")
print(f"Answer A Faithfulness Score: {score_A:.4f} (100% Faithful / Correct ✓)")
print(f"Answer B Faithfulness Score: {score_B:.4f} (Hallucination Detected! )")
```


#### Code Breakdown:

এই কোডটি কীভাবে কাজ করছে, চলো সহজে বুঝে নিই:

প্রথমত, আমাদের Input হিসেবে ৩-ডাইমেনশনাল Vector এম্বেডিংস দেওয়া হয়েছে।

দ্বিতীয়ত, Output হিসেবে আমরা পাচ্ছি একটি কোসাইন প্রজেকশন স্কোর, যা Faithfulness রিф্লেক্ট করে।

মজার ব্যাপার হলো, Answer B এর স্কোর এসেছে খুবই কম (মাত্র ০.০৮৯)।

কারণ এর জ্যামিতিক কোণ সোর্স ভেক্টরের সম্পূর্ণ বিপরীত দিকে ছিল, যা দিয়ে সহজেই আমরা Hallucination ধরে ফেলেছি।

তাহলে এটি আমরা কখন ব্যবহার করব?

যখন ব্যাকঅ্যান্ডে কাস্টম RAG ইভালুয়েশন পাইপলাইন আর ট্র্যাকিং অটোমেট করার প্রয়োজন হবে।


## ১০. Interview Questions

### Beginner Level

**প্রশ্ন:** প্রথাগত লিনিয়ার লগার ফাইলের চেয়ে Distributed Tracing কেন AI এজেন্টের জন্য বেশি জরুরি?

**উত্তর:** সাধারণ লগার শুধু এক লাইনে ফ্ল্যাট মেসেজ লেখে।

কিন্তু AI Agent একটা রিকোয়েস্টের পেছনে ভেতরে অনেকগুলো কাজ করে। যেমন Embedding তৈরি, Vector Search বা Tool Run করা।

Distributed Tracing এই পুরো ফ্যামিলি ট্রি-কে কস্ট আর Latency সহ চোখের সামনে তুলে ধরে, যা ডিবাগিংয়ের জন্য অত্যন্ত দরকারি।

---

### Intermediate Level

**প্রশ্ন:** Ragas ইভালুয়েশনে Faithfulness আর Answer Relevance-এর মধ্যে পার্থক্য কী?

**উত্তর:** Faithfulness দেখে উত্তরটি সোর্স ডকুমেন্টের তথ্যের ওপর ভিত্তি করে তৈরি কি না। অর্থাৎ এটি Hallucination চেক করে।

আর Answer Relevance দেখে উত্তরটি ইউজারের মূল প্রশ্নের সঠিক জবাব দিচ্ছে কি না।

---

### Advanced Level

**প্রশ্ন:** প্রোডাকশনে অবজারভেবিলিটি মনিটর করার সময় PII Leakage ঠেকানোর উপায় কী?

**উত্তর:** এজন্য আমাদের ব্যাকঅ্যান্ডে PII Sanitizer Middleware ব্যবহার করতে হয়।

এটি ড্যাশবোর্ডে লগ পাঠানোর ঠিক আগেই ফোন নম্বর, ইমেইল বা ক্রেডিট কার্ডের মতো ব্যক্তিগত তথ্যগুলো মাস্ক বা হাইড করে দেয়।


## ১১. Chapter Summary

এই চ্যাপ্টারে আমরা কী কী শিখলাম?

প্রথমত, AI Observability হলো প্রোডাকশন AI এজেন্টের কাজ মনিটর করার একটি ম্যাজিক ড্যাশবোর্ড।

দ্বিতীয়ত, Tracing-এর মাধ্যমে প্রতিটি রিকোয়েস্টকে ফ্যামিলি ট্রির মতো সুন্দর গ্রাফ আকারে দেখা যায়।

তৃতীয়ত, Ragas দিয়ে আমরা উত্তর কতটা সঠিক বা প্রাসঙ্গিক তা স্কোরিং করে মেপে ফেলি।

সবশেষে, সুরক্ষার জন্য Trace লগে সর্বদা PII Masking নিশ্চিত করা জরুরি।


## ১২. What's Next?

দারুণ! আমরা মনিটরিং আর Tracing ভালোভাবে শিখে ফেলেছি।

পরের চ্যাপ্টারে আমরা কথা বলব সবচেয়ে বড় দুটি বিষয় নিয়ে: বাজেট আর সিকিউরিটি!

হ্যাঁ, Chapter 23-এ থাকছে Cost Optimization ও Guardrails।

কীভাবে AI প্রজেক্টের খরচ বাঁচাবে আর একে সুরক্ষিত রাখবে, চলো পরের চ্যাপ্টারে তা দেখে নিই!

**Chapter 22 শেষ।**
