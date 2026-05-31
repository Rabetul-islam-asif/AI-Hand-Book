# Chapter 22: AI Observability & Monitoring

---

### Chapter Goal
এই চ্যাপ্টারের মূল লক্ষ্য হলো প্রোডাকশন এআই সিস্টেমের প্রতিটি মিলি-সেকেন্ডের কম্পিউটেশন ও ট্র্যাকিং—অর্থাৎ এআই অবজারভেবিলিটি (AI Observability), ট্র্যাকিং (Tracing - LangSmith), কস্ট ও Latency ট্র্যাকিং (Cost & Latency Tracking), এবং রিট্রিভাল Quality পরিমাপের জন্য ইভালুয়েশন ফ্রেমওয়ার্ক (Evaluation Framework - Ragas) এর টেকনিক্যাল Architecture সম্পন্ন করা। চ্যাপ্টারটি শেষ করার পর তুমি নিজেই একটি এডভান্সড অবজারভেবিলিটি ড্যাশবোর্ড ইন্টিগ্রেট করতে পারবে এবং প্রতিটি কাস্টমার কুয়্যারির পেছনের Token খরচ ও Error স্পট সনাক্ত করতে সক্ষম হবে।

### Why Should I Care?
একটি সাধারণ চ্যাট বা আরএজি অ্যাপ ল্যাবে চমৎকার চলে, কিন্তু প্রোডাকশনে যাওয়ার সাথে সাথেই কাস্টমার কমপ্লেইন করা শুরু করে, **"চ্যাটবট লোড হতে ১০ সেকেন্ড সময় নিচ্ছে!"** অথবা তোমার সিএফও (CFO) এসে তোমাকে ডেকে বললে, **"আজকে ব্যাকএন্ডে মাত্র ১০০ কাস্টমার রিকোয়েস্টে ৫০০ ডলারের API বিল কীভাবে আসলো?"** তুমি যদি এজেন্টের প্রতি ইটারেশনের ইনার Loop ট্র্যাক বা ট্রেস (Trace) না করো, তবে কোন টুলে মেমরি লিক হচ্ছে বা কোথায় Loop ইনফিনিট ঘুরছে, তা তুমি কখনোই বের করতে পারবে না।

### Big Picture
আগের চ্যাপ্টারে আমরা নিরাপত্তা ও সংবিধান হারনেস (Harness Engineering) ডিজাইন করা শিখেছি। এই চ্যাপ্টারে আমরা সেই Architecture-এর জন্য একটি হাই-ডেফিনিশন ড্যাশবোর্ড বা ট্র্যাকিং Window তৈরি করব। এখানে শেখা অবজারভেবিলিটি লজিক আমাদের পরবর্তী সিকিউরিটি ও কস্ট অপ্টিমাইজেশন এবং ৪টি কমপ্লিট প্রডাক্ট ব্লুপ্রিন্ট তৈরি করার মূল চালিকাশক্তি।

---

### ১. Hook: ব্ল্যাকবক্স ইঞ্জিনের ভেতরে ফাইবার অপটিক্যাল ক্যামেরা ইনজেক্ট করা

কল্পনা করো, তুমি একটি অন্ধকার গুহা বা ব্ল্যাকবক্সের ভেতর একটি গোলকধাঁধা তৈরি করে একটি ছোট ইঁদুর (এজেন্ট) ছেড়ে দিলে। ইঁদুরটি গুহা থেকে একটি হিরে (Goal) খুঁজে নিয়ে আসলো। 
* **No Observability (অন্ধ প্রোডাকশন):** তুমি গুহার বাইরে বসে আছেন। ইঁদুরটি ভেতরে গিয়ে কী করল, কোথায় হোঁচট খেল, কোন রাস্তা দিয়ে ঘুরল—তার কিছুই তুমি জানো না। শুধু দেখলে সে ৫ মিনিট পর হিরেটি এনেছে। কেন ৫ মিনিট লাগলো? এর উত্তর তোমার কাছে নেই।

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

* **High-Definition Tracing:** তুমি ইঁদুরের মাথায় একটি ফাইবার অপটিক্যাল লাইভ ক্যামেরা এবং জিপিএস ট্র্যাকার লাগিয়ে দিলে (Tracing Engine)। এবার তুমি তোমার ড্যাশবোর্ড স্ক্রিনে পরিষ্কার দেখতে পাচ্ছেন ইঁদুরটি প্রথমে ২ নম্বর বাঁকে গিয়ে আটকে পড়েছিল, তারপর ৩ নম্বর ড্রয়ার খুলে খাবার খেয়ে সঠিক রাস্তায় লাফ দিয়েছে। 

এআই অবজারভেবিলিটি হলো এআই-এর সেই ড্যাশবোর্ড ক্যামেরা। এটি ব্ল্যাকবক্স চ্যাট API-এর প্রতি ইনার Token ও টুল কলের মেমরি ফ্লো রিয়েল-টাইমে ভিজ্যুয়ালাইজ করে।

---

### ২. Core Concepts: ট্রেসিং, মেট্রিদ ও ইভালুয়েশন

একটি প্রোডাকশন-গ্রেড এআই অবজারভেবিলিটি Architecture মূলত ৩টি উপাদানের সমন্বয়ে কাজ করে:

#### ক. Distributed Tracing (ট্রেসিং - LangSmith)
একটি সিঙ্গেল ইউজার মেসেজ সলভ করতে এআই এজেন্ট ভেতরের লেয়ারে হয়তো ৫টি API কল এবং ৩টি লোকাল টুল রান করেছে। ট্রেসিং এই পুরো সিকোয়েন্সকে একটি প্যারেন্ট-চাইল্ড হাইয়ার্কি **Tree (স্প্যান - Spans)** হিসেবে রেকর্ড করে।
* **LangSmith / Phoenix:** এগুলো বিশেষায়িত ট্রেসিং হাব। এরা তোমার ব্যাকএন্ড Code-এর সাথে ইন্টিগ্রেট হয়ে অটোমেটিক্যালি Input, Output, Token সংখ্যা এবং কাস্টম সিস্টেমের ভেতরের ফ্লো চার্ট ড্যাশবোর্ডে পুশ করে দেয়।

#### খ. Performance Metrics (পারফরম্যান্স মেটেরিক্স)
Developer ও বিজনেসের জন্য ৪টি প্রধান মেটেরিক্স প্রতিনিয়ত মনিটর করতে হয়:
1. **Latency per Step:** কোন স্পেসিফিক টুল বা API কল সবচেয়ে বেশি সময় নিচ্ছে (Bottleneck)।
2. **Token Usage & Cost:** Input ও Output Token-এর অনুপাত ও রিয়েল ডলার কস্ট ট্র্যাক করা।
3. **Tool Accuracy:** সঠিক প্রশ্নের জন্য সঠিক টুল ট্রিগার হচ্ছে কি না।
4. **Token-to-Latency Ratio:** প্রতি সেকেন্ডে Model কত Token জেনারেট করছে (Speed)।

#### গ. Ragas Evaluation Framework (আরএজি ইভ্যালুয়েশন)
আরএজি পাইপলাইনের Quality পরিমাপের জন্য ক্লাসিক্যাল মেথড কাজ করে না। এর জন্য আমরা বিশেষায়িত **Ragas** ফ্রেমওয়ার্ক ব্যবহার করি, যা প্রধান ৪টি Parameter স্কোর করে:

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

🧠 Remember

**Faithfulness = Hallucination Detector!**  
Ragas এর `Faithfulness` স্কোর ০ মানে Model সোর্স ডক ইগনোর করে সম্পূর্ণ নিজের মতো মনগড়া বা হ্যালুসিনেটেড উত্তর জেনারেট করেছে। ১ মানে উত্তর ১০০% সোর্সের তথ্যের ওপর ভিত্তি করে তৈরি।

---

### ৩. Visual Explanation: Loop ও বটলনেক ডিটেকশন

ট্রেসিং ড্যাশবোর্ডে কীভাবে একটি স্লো রিট্রিভাল Error পিনপয়েন্ট করা হয়, তা নিচে ডায়াগ্রামের মাধ্যমে ভিজ্যুয়ালাইজ করো:

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

ড্যাশবোর্ডের এই টাইমলাইন চার্ট স্ক্যান করে Developer সাথে সাথে বুঝতে পারো ল্যাটেন্সির মূল অপরাধী এলএলএম নয়; অপরাধী হলো ইনডেক্সবিহীন স্লো Vector Database Search, যা ৮ সেকেন্ড সময় নষ্ট করেছে।

---

### ৪. Real World Example: Perplexity-র গ্লোবাল অবজারভেবিলিটি ড্যাশবোর্ড

Perplexity.ai বা Cursor যখন লক্ষ কোটি কনকারেন্ট রিকোয়েস্ট মনিটর করে:

1. **Auto Tracing:** প্রতি সেকেন্ডে জেনারেট হওয়া প্রতিটি Code-এর পেছনের কম্পিউটেশন গ্রাফ ওপেন-টেলিমেন্ট্রি (OpenTelemetry) দিয়ে প্রসেস করে ড্যাশবোর্ডে লাইভ স্টিমিং রেকর্ড করা হয়।
2. **Anomaly Alert:** কোনো নির্দিষ্ট ক্লায়েন্টের কস্ট যদি ১ মিনিটে ১০ ডলার ক্রস করে, ড্যাশবোর্ডের এনোমালি ডিটেক্টর (Anomaly Detector) অ্যালার্ট রেইজ করে সেই ক্লায়েন্টের কাস্টম সেশন রেট-লিমিট লক করে দেয়।

---

### ৫. Developer Perspective: PyTorch & Python standard SDK তে কাস্টম লগার Code

💻 Developer View

Developer হিসেবে পাইথনে কোনো পেইড Library ছাড়া একটি কাস্টম ওপেন-সোর্স ট্রেসিং ড্যাশবোর্ড লগার ইমপ্লিমেন্ট করার রিয়েল ও গোল্ড স্ট্যান্ডার্ড প্রোডাকশন Code:

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

---

### ৬. Production Perspective: PII Masking over Trace Logs

🏭 Production Reality

অটোমেটিক ট্রেসিং লাইব্রেরিগুলো (যেমন: LangSmith) যখন Input ও Output Data ড্যাশবোর্ডে পুশ করে, তখন সবচেয়ে বড় কর্পোরেট রেগুলেটরি অডিট রিস্ক হলো **Trace Log PII Leakage**।

* **The Threat:** যদি ইউজার চ্যাটে তার ক্রেডিট কার্ড নম্বর বা পাসওয়ার্ড টাইপ করে এবং তোমার ট্রেসিং লগার হুবহু Input-Output ক্লাউড ড্যাশবোর্ডে পাঠিয়ে দেয়, তবে সম্পূর্ণ Data সিকিউরিটি কমপ্লায়েন্স ভেঙে পড়বে (GDPR / HIPAA violations)।
* **সমাধান:** প্রোডাকশন অবজারভেবিলিটি পাইপলাইনে ক্লাউডে Data পুশ করার আগে একটি কাস্টম **Data Sanitization Filter Middleware** ব্যবহার করা বাধ্যতামূলক, যা সমস্ত সংবেদনশীল Data মাস্ক বা ফিল্টার করে ড্যাশবোর্ডে সেভ করে।

---

### ७. Common Mistakes

🔴 Common Mistake

**ভুল ধারণা:** প্রজেক্টে এআই অবজারভেবিলিটি মডিউল সচল রাখলে অ্যাপ্লিকেশনের স্পিড বা Inference স্পিড বৃদ্ধি পায়।

**বাস্তবতা:** ট্র্যাকিং বা ট্রেসিং লাইব্রেরিগুলো ব্যাকগ্রাউন্ডে নেটওয়ার্ক রিকোয়েস্ট এবং মেমরি বাফার ব্যবহার করে ক্লাউডে Log পাঠায়, যা তোমার অ্যাপ্লিকেশনের ওপর অতিরিক্ত প্রসেসিং প্রেসার তৈরি করে (Latency সামান্য বাড়াতে পারে)। তাই প্রোডাকশনে সর্বদা **Asynchronous Trace Exporter** (যা প্রধান থ্রেডকে ব্লক না করে ব্যাকগ্রাউন্ডে নন-ব্লকিং কোয়েরি করে) ব্যবহার করা ম্যান্ডেটরি।

---

### ৮. Mental Model: এয়ার ট্রাফিক কন্ট্রোল টাওয়ার

এআই অবজারভেবিলিটির মেন্টাল Model:

**"AI Observability = এয়ারপোর্ট রানওয়ের এয়ার ট্রাফিক কন্ট্রোল টাওয়ার (ATC)"**

[VISUAL]
Title: Air Traffic Control Room analogy of Observability
Illustration: Visual radar scanning multiple planes (tasks) landing with flight numbers, coordinates, and delay metrics
Placement: After Mental Model section
Purpose: Ground the intuitive dashboard control space.

```
       [ ATC Radar Observability Dashboard ]
   ✈ Flight 101 (Embedding)  ──► Latency: 45ms  ──► Status: Safe Landing ✓
   ✈ Flight 202 (Vector DB)  ──► Latency: 8.0s ──► Status: ALERT! Ground Hold 🔴
   ✈ Flight 303 (LLM Gener.) ──► Latency: 1.1s  ──► Status: Safe Landing ✓
```

অন্ধকারে আকাশে শয়ে শয়ে প্লেন (ইউজার কুয়্যারি) উড়ছে। তুমি যদি কন্ট্রোল টাওয়ারের রাডার (Tracing) সচল না রাখেন, তবে কোন প্লেন কার সাথে কনফ্লিক্ট করছে বা কোথায় জট লেগে রানওয়ে ব্লক হচ্ছে তা তুমি কখনোই বুঝবে না। রাডার স্ক্রিন তোমাকে রিয়েল-টাইমে প্রতিটি ফ্লাইটের স্পিড, অল্টিটিউড এবং ফুয়েল কস্ট দেখিয়ে নিখুঁত বিমানবন্দর ট্র্যাকিং ম্যানেজ করতে সাহায্য করে।

---

### ৯. Mini Project: পাইথনে কাস্টম ভিক্টরাইজড Ragas ইভ্যালুয়েশন সিমুলেটর

চলো পাইথনে কাস্টম NumPy ব্যবহার করে কোনো এক্সটার্নাল Library ছাড়া একটি আরএজি Faithfulness (হ্যালুসিনেশন ডিটেক্টর) ইভালুয়েশন Engine স্ক্র্যাচ থেকে আর্কিটেক্ট করি।

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
print(f"Answer B Faithfulness Score: {score_B:.4f} (Hallucination Detected! 🔴)")
```

#### Code Breakdown:
* **Input:** ৩-ডাইমেনশন সোর্স এবং প্রেডিক্টেড উত্তরের এম্বেডিংস Vector।
* **Output:** গাণিতিক কোসাইন প্রজেকশন স্কোর যা Faithfulness রিফ্লেক্ট করে।
* **Why it works:** `Answer B` এর জ্যামিতিক ওরিয়েন্টেশন সোর্স Vector-এর সম্পূর্ণ বিপরীত দিকে হওয়ায় এর স্কোর অত্যন্ত নিম্ন ($0.089$) এসেছে, যা হ্যালুসিনেশন ডিটেক্ট করেছে।
* **When to use:** ব্যাকঅ্যান্ডে কাস্টম RAG ইভালুয়েশন পাইপলাইন এবং ট্র্যাকিং Algorithm অটোমেট করার জন্য।

---

### ১০. Interview Questions

#### Beginner
1. **প্রশ্ন:** প্রথাগত লিনিয়ার লগার File-এর (যেমন: Winston/console.log) তুলনায় ডিস্ট্রিবিউটেড ট্রেসিং (Tracing) কেন এআই এজেন্টের জন্য আবশ্যক?
   * **উত্তর:** প্রথাগত লগার শুধুমাত্র ফ্ল্যাট টাইমস্ট্যাম্পে সিঙ্গেল লাইন Log লেখে। কিন্তু এআই এজেন্ট এক ইউজার রিকোয়েস্টে ভেতরের লেয়ারে মাল্টি-স্টেপ কম্পিউটেশন (Embedding, Vector Search, Tool calls) রান করে। ট্রেসিং এই পুরো প্রসেসকে একটি প্যারেন্ট-চাইল্ড গ্রাফ Tree হিসেবে Latency, কস্ট ও Input-আউটপুটসহ ভিজ্যুয়ালাইজ করতে পারে, যা ডিবাগিংয়ের জন্য অপরিহার্য।

#### Intermediate
2. **প্রশ্ন:** Ragas ইভালুয়েশন ফ্রেমওয়ার্কের "Faithfulness" এবং "Answer Relevance" মেটেরিক্স দুটির গাণিতিক ও ফাংশনাল তাৎপর্য ব্যাখ্যা করো।
   * **উত্তর:** `Faithfulness` পরিমাপ করে জেনারেট হওয়া উত্তরটি সোর্স Document-এর তথ্যের ওপর ভিত্তি করে তৈরি কি না (Hallucination check)। আর `Answer Relevance` পরিমাপ করে জেনারেট হওয়া উত্তরটি ইউজারের কোশ্চেনের আসল ও প্রাসঙ্গিক সমাধান দিচ্ছে কি না (কোশ্চেন এলাইন্ড চেক)।

#### Advanced
3. **প্রশ্ন:** প্রোডাকশন গেটওয়েতে এআই অবজারভেবিলিটি মনিটর করার সময় PII Leakage বা Data সিকিউরিটি লিক প্রতিহত করার স্ট্যান্ডার্ড আর্কিটেকচারাল Pattern কী?
   * **উত্তর:** এটি প্রতিহত করতে ব্যাকঅ্যান্ডে **PII Sanitizer Middleware / Log Exporter Interceptor** ইন্টিগ্রেট করতে হয়। এই ফিল্টারটি এআই ট্র্যাকিং Data ক্লাউড ড্যাশবোর্ডে পুশ করার আগেই রিয়েল-টাইমে রেগুলার এক্সপ্রেশন বা কাস্টম নেমড এন্টিটি রিকগনিশন (NER) ব্যবহার করে গ্রাহকের ফোন, ইমেইল বা ক্রেডিট কার্ড নম্বর মাস্ক করে নিরাপদ প্লেসহোল্ডারে রূপান্তর করে।

---

### ১১. Chapter Summary
* **AI Observability** প্রোডাকশন এআই এজেন্টের কার্যকারিতা মনিটর করার একমাত্র স্বচ্ছ ড্যাশবোর্ড।
* **Tracing** প্রতি ইউজার রিকোয়েস্টকে মাল্টি-লেয়ার প্যারেন্ট-চাইল্ড গ্রাফ আকারে ভিজ্যুয়ালাইজ করে।
* **Ragas** রিট্রিভাল Quality পরিমাপের জন্য সিমান্টিক ও ফ্যাট-ভিত্তিক স্কোরিং করে।
* লগার সিকিউরিটি গার্ডে সর্বদা **Trace Log PII Masking** নিশ্চিত করা ম্যান্ডেটরি।

---

### ১২. What's Next
দারুণ! আমরা সফলভাবে প্রোডাকশন অবজারভেবিলিটি ও ডিস্ট্রিবিউটেড ট্র্যাকিং Mechanism জয় করে ফেলেছি। পরবর্তী চ্যাপ্টারে আমরা এই প্রোডাকশন সিস্টেমের সবচেয়ে গুরুত্বপূর্ণ ফাইন্যান্সিয়াল ও সেফটি লেয়ার নিয়ে আলোচনা করব: **Chapter 23: Cost Optimization & Guardrails**। Context কম্প্যাকশন, কাস্টম ক্যাশিং, Prompt ইনজেকশন ব্লক ও Output পিআইআই ভ্যালিডেটর কীভাবে তোমার এআই Project-এর বাজেট ও নিরাপত্তা নিশ্চিত করে, তা আমরা বিস্তারিত শিখব।

---
**Chapter 22 সমাপ্ত।**
