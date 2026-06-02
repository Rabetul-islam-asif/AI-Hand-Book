# Chapter 14: Advanced Retrieval, Hybrid Search & Re-ranking

---

তুমি কি কখনো ভেবেছ — শুধু সাধারণ `Cosine Similarity` বা `Vector Search` ব্যবহার করলে `RAG` পাইপলাইনের `Accuracy` কেন অনেক সময় কমে যায়?

ধরো, কোনো কাস্টমার বানানে ভুল করল।

কিংবা কোনো স্পেশাল আইডি বা পার্ট নাম্বার লিখে সার্চ করল (যেমন: `bKash-1234`)।

তখন `Vector Search` কিন্তু এর আসল অর্থ বুঝতে না পেরে গুলিয়ে ফেলবে।

আর তার ফল কী হবে?

কাস্টমার ভুল তথ্য পাবে, আর তোমার সাধের প্রজেক্ট একদম মুখ থুবড়ে পড়বে!

তো চলো, এই চ্যাপ্টারে আমরা `Search` এর `Accuracy` ৯০% থেকে একলাফে ৯৯%-এ নিয়ে যাওয়ার চমৎকার কিছু উপায় শিখে ফেলি।

আমরা দেখব কীভাবে `Hybrid Search` আর `Re-ranking` কাজ করে।

সেই সাথে `Parent-Document Retrieval` আর `HyDE` এর মতো সব আধুনিক টেকনিকগুলোও সহজ করে বুঝব।

তাহলে আর দেরি কেন?

চলো, লাইব্রেরিয়ান আর একটি বইয়ের দারুণ গল্প দিয়ে শুরু করা যাক!


## ১. Hook: লাইব্রেরিয়ান আর পুরো বইয়ের গল্প

কল্পনা করো, তুমি লাইব্রেরিতে গিয়ে লাইব্রেরিয়ানকে জিজ্ঞেস করলে, **"বিকাশের Dynamic পিন ব্লক কেন হয়?"**

এখানে দুইভাবে খোঁজাখুঁজি হতে পারে।

প্রথমটা হলো **Basic RAG** বা সাধারণ **Vector Search**।

এতে লাইব্রেরিয়ান বই ঘেঁটে এমন একটা লাইন বা প্যারাগ্রাফ খুঁজে বের করলেন, যেটা তোমার প্রশ্নের সাথে মিলে যায়।

কিন্তু মুশকিল হলো, সেই প্যারাগ্রাফে লেখা আছে: *"অনুচ্ছেদ ৪ এর নিয়ম অনুসারে এটি লক হবে।"*

এখন এই "অনুচ্ছেদ ৪" জিনিসটা কী?

সেটা কিন্তু লাইব্রেরিয়ান জানেন না!

এর ফলে AI মডেল অর্ধেক বা ভুল উত্তর দিয়ে বসে থাকবে।

[VISUAL]
Title: Basic RAG vs. Parent-Document Retrieval
Illustration: Small chunk vector matching to index vs. fetching the larger parent document context
Placement: After Hook Section
Purpose: Show how advanced retrieval solves the context bottleneck.

```
Basic Vector RAG (Incomplete Context):
[Query] ──► [Matches Small Chunk A] ──► "According to rule 4, lock PIN" (Confused LLM: What is rule 4?)

Parent-Document Retrieval (Complete Context ✓):
[Query] ──► [Matches Small Chunk A] ──► [Fetch Parent Doc of Chunk A] ──► "Rule 4: If 3 wrong PINs are typed, lock PIN"
```

আর দ্বিতীয় পদ্ধতিটা হলো **Parent-Document Retrieval**।

এখানে লাইব্রেরিয়ান আগের মতোই প্রথমে ছোট একটা অংশ খুঁজে নিলেন।

কিন্তু তিনি সেটা সরাসরি তোমাকে না দিয়ে, তার আসল উৎস বা পুরো "অনুচ্ছেদ ৪" এর সবটুকু লেখা একসাথে নিয়ে আসলেন।

একে আমরা বলি `Parent Document`।

এর ফলে AI মডেল পুরো ব্যাকগ্রাউন্ড জানতে পারে এবং একদম সঠিক উত্তর দেয়।

আমাদের `Advanced Retrieval` ঠিক এই স্মার্ট লাইব্রেরিয়ানের মতোই কাজ করে।

এটি সার্চ করার জন্য ছোট `Vector` ব্যবহার করে গতি বাড়ায়।

আবার `Decoder`-এ পাঠানোর সময় পুরো চ্যাপ্টারটি পাঠিয়ে কাজের মানও দারুণ করে তোলে।


## ২. Hybrid Search আর Re-ranking

অনেক বড় বড় সার্চ সিস্টেমে একদম নিখুঁত রেজাল্ট পাওয়ার জন্য ৩টি আধুনিক টেকনিক ব্যবহার করা হয়।

চলো এগুলো একে একে জেনে নিই।

### Hybrid Search

**প্রশ্ন:** Hybrid Search আসলে কী?

**উত্তর:** এটি হলো কিওয়ার্ড ম্যাচিং আর অর্থভিত্তিক সার্চের এক দারুণ কম্বিনেশন।

এতে দুই ধরনের সার্চ ইঞ্জিন একসাথে কাজ করে।

[VISUAL]
Title: Hybrid Search (Sparse + Dense) Pipeline
Illustration: Block diagram showing Sparse (BM25) and Dense (Vectors) results merging via RRF
Placement: After Core Concepts section
Purpose: Visually demonstrate the dual-engine integration of Hybrid Search.

```
                  ┌───────────────────────────────┐
                  │          User Query           │
                  └──────────────┬────────────────┘
                                 │
                   ┌─────────────┴─────────────┐
         ┌─────────▼─────────┐       ┌─────────▼─────────┐
         │   Sparse Search   │       │   Dense Search    │
         │ (BM25 Keywords)   │       │(Semantic Vectors) │
         └─────────┬─────────┘       └─────────┬─────────┘
                   │                               │
                   └─────────────┬─────────────────┘
                                 ▼
                  ┌───────────────────────────────┐
                  │    Reciprocal Rank Fusion     │
                  │         (RRF Merge)           │
                  └──────────────┬────────────────┘
                                 ▼
                  ┌───────────────────────────────┐
                  │     Reranker Model (BGE)      │
                  └──────────────┬────────────────┘
                                 ▼
                       [ Top 3 Perfect Docs ]
```

**প্রশ্ন:** Sparse Search বা BM25 কী?

**উত্তর:** এটি খুব দ্রুত শব্দের বানান বা কিওয়ার্ড খুঁজে বের করে।

যেমন, কাস্টমার যদি কোনো পার্ট নাম্বার `"bKash-1234"` লিখে সার্চ করে, তবে ভেক্টর সার্চ হয়তো এর মানে বুঝতে না পেরে ভুল করতে পারে।

কিন্তু `BM25` হুবহু কিওয়ার্ড মিলিয়ে সঠিক তথ্যটি বের করে আনে।

**প্রশ্ন:** Dense Search বা Vector Search কী?

**উত্তর:** এটি শব্দের অর্থ বা ভাবার্থ দেখে সার্চ করে।

যেমন, "টাকা পাঠানো" আর "মানি ট্রান্সফার" যে একই কথা, সেটা এই সার্চ সহজেই ধরে ফেলে।

**প্রশ্ন:** RRF কী?

**উত্তর:** এর পুরো নাম হলো Reciprocal Rank Fusion।

এটি একটি বিশেষ অ্যালগরিদম।

এর কাজ হলো `Sparse Search` আর `Dense Search` এর ফলাফলগুলোকে মিলিয়ে একটি একক স্কোর তৈরি করা।

### Re-ranking

**প্রশ্ন:** Re-ranking আসলে কেন লাগে?

**উত্তর:** ভেক্টর ডাটাবেস থেকে আমরা হয়তো প্রথম ধাপে সেরা ১০টি ডকুমেন্ট খুঁজে পাই।

কিন্তু তাদের সিরিয়াল বা র‌্যাঙ্কিং সবসময় নিখুঁত হয় না।

তাই একে আরও নির্ভুল করতে আমরা একটি বিশেষ মডেল ব্যবহার করি, যাকে বলা হয় `Cross-Encoder Reranker`।

যেমন, `Cohere Rerank` বা `BGE-Reranker`।

এটি ইউজারের প্রশ্ন এবং ওই ১০টি ডকুমেন্টের প্রতিটি জোড়া আলাদাভাবে খুব গভীরভাবে স্ক্যান করে।

তারপর একদম নিখুঁত স্কোর দিয়ে সেরা ৩টি ডকুমেন্টকে বাছাই করে আমাদের প্রম্পটে পাঠায়।

এতে ভুল উত্তর দেওয়ার বা `Hallucination` এর ভয় প্রায় ৯০% কমে যায়।

### HyDE

**প্রশ্ন:** HyDE কী আর এটি কীভাবে সাহায্য করে?

**উত্তর:** অনেক সময় ইউজাররা খুব ছোট বা ভাঙা ভাষায় প্রশ্ন লেখে, যেমন: `"PIN blocked bKash"`।

এমন ছোট প্রশ্নে সাধারণ সার্চ ইঞ্জিনগুলো ঠিকমতো কাজ করতে পারে না।

তখন আমরা `HyDE` ব্যবহার করি।

এর কাজ হলো প্রশ্নটি আসামাত্র প্রথমে একটি ছোট LLM দিয়ে একটি কাল্পনিক উত্তর লিখিয়ে নেওয়া।

তারপর সেই কাল্পনিক উত্তরটিকে এম্বেড করে ভেক্টর ডাটাবেসে সার্চ করা হয়।

যেহেতু কাল্পনিক উত্তরের লেখার ধরন আর ডাটাবেসের ডকুমেন্টের ধরন মিলে যায়, তাই সার্চের মান অনেক বেড়ে যায়।


## 🧠 Remember

`BM25` খুঁজে বের করে শব্দের বানান আর নির্দিষ্ট কিওয়ার্ড।

`Semantic Search` খুঁজে বের করে শব্দের আসল অর্থ।

আর `Reranker` এই দুইয়ের ফলাফল ছেঁকে একদম সেরা হিরের টুকরোটি আমাদের হাতে তুলে দেয়।


## ৩. Cross-Encoder কীভাবে কাজ করে?

নিচের ডায়াগ্রামটি দেখলে খুব সহজে বুঝতে পারবে কীভাবে এটি কাজ করে:

[VISUAL]
Title: Bi-Encoder vs. Cross-Encoder (Reranker) Architecture
Illustration: Comparison of separate embedding dot product versus direct deep joint attention
Placement: Under Reranker section
Purpose: Visually explain why Cross-Encoders are far more accurate but computationally heavier than Bi-Encoders.

```
Bi-Encoder (Standard Vector Search - Fast & Approximated):
Query Vector ──┐
               ├─► [ Simple Dot Product ] ──► Score (Approximated)
Doc Vector ────┘

Cross-Encoder (Reranker - Slow & Ultra-Accurate):
[ Query + Document Text ] ──► [ Deep Transformer Joint Attention ] ──► Absolute Relevance Score (0 to 1)
```

সাধারণ ভেক্টর সার্চের সময় প্রতিটি ভেক্টর আলাদাভাবে প্রসেস করে ডট প্রোডাক্ট করা হয়, যাকে বলে `Bi-Encoder`।

কিন্তু `Reranker` ইউজার কুয়্যারি আর ডকুমেন্টের টেক্সট একসাথে জোড়া লাগিয়ে দেয়।

তারপর ট্রান্সফরমার লেয়ারে গভীরভাবে অ্যাটেনশন রান করে এদের সম্পর্ক খুঁজে বের করে।

এর ফলে আমরা একদম নিখুঁত স্কোর পেয়ে যাই।


## ৪. Real World Example: Perplexity কীভাবে কাজ করে?

চলো আমরা `Perplexity` এর উদাহরণ দিয়ে পুরো ব্যাপারটা বুঝি।

যখন তুমি `Perplexity` এ কিছু লিখে সার্চ করো, তখন ব্যাকএন্ডে কী ঘটে?

প্রথমেই, তারা কোটি কোটি ওয়েবসাইটকে `BM25` কিওয়ার্ড ইনডেক্স এবং `HNSW Vector Space` দুই জায়গাতেই জমা রাখে।

এর পরের ধাপে, তোমার প্রশ্নের ওপর ভিত্তি করে তারা খুব দ্রুত একটি হাইব্রিড সার্চ চালায়।

সেখান থেকে প্রথম ধাপে ১০০টি সম্ভাব্য পেজ খুঁজে বের করা হয়।

সবশেষে আসে রির‍্যাঙ্কিংয়ের পালা।

এখানে মাত্র ৩ মিলি-সেকেন্ডে ওই ১০০টি পেজ স্ক্যান করে সেরা ৫টি পেজ প্রম্পটে পাঠিয়ে দেওয়া হয়।

এর ফলে তুমি চোখের পলকে একদম সঠিক ও নির্ভরযোগ্য তথ্য পেয়ে যাও।


## ৫. PyTorch & Cohere দিয়ে Re-ranking Code

তুমি যদি একজন ডেভেলপার হও, তবে ব্যাকএন্ডে কীভাবে এই `Reranker Model` রান করবে?

চলো পাইথনের একটি বাস্তব কোড দেখে নিই:

```python
# Cohere Rerank API Integration in Backend
import cohere

# ১. Cohere Client ইনিশিয়ালাইজ করো
co = cohere.Client("your-api-key")

# ২. ইউজার কুয়্যারি এবং হাইব্রিড সার্চের টপ ৫টি সম্ভাব্য ডক
query = "bKash PIN blocked reset timeline?"
documents = [
    "To reset PIN, visit Customer Care with NID.",
    "PIN reset takes 24 hours after verification.", # Best Match for timeline
    "Keep your password and PIN safe. Do not share.",
    "bKash offer: get cashback on utility bill payment.",
    "If verification fails, contact support center."
]

# ৩. Rerank API কল করো
print("রানিং ক্রস-এনকোডার রির‍্যাঙ্কিং...")
response = co.rerank(
    model="rerank-english-v3.0",
    query=query,
    documents=documents,
    top_n=2
)

# ৪. রির‍্যাঙ্কড Output প্রিন্ট করো
for idx, result in enumerate(response.results):
    doc_index = result.index
    score = result.relevance_score
    print(f"Rank {idx+1}: Score = {score:.4f} -> '{documents[doc_index]}'")
```


## ৬. Two-Stage Retrieval কেন দরকার?

বাস্তব প্রোডাকশন লাইফে ক্রস-এনকোডার মডেলগুলো অনেক ভারী এবং কিছুটা ধীরগতির হয়।

তাই খরচ কমাতে আর গতি বাড়াতে আমরা **Two-Stage Retrieval** ব্যবহার করি।

প্রথমে **Stage 1** এ আমরা দ্রুত একটি ভেক্টর ডাটাবেস সার্চ চালাই।

এর কাজ হলো লাখ লাখ ডকুমেন্টের মধ্য থেকে সেরা ৫০টি ডকুমেন্ট ছেঁকে আনা।

এতে সময় লাগে ৫ মিলি-সেকেন্ডেরও কম!

এরপর **Stage 2** এ আমরা ওই ৫০টি ডকুমেন্টের ওপর রির‍্যাঙ্কার মডেল চালাই।

সেখান থেকে একদম সেরা ৩টি ডকুমেন্ট বেছে নিয়ে প্রম্পটে পাঠানো হয়।

এতে সময় লাগে মাত্র ৫০ মিলি-সেকেন্ডের মতো।

এই পুরো সিস্টেমটি আমাদের সার্চের গতি এবং নিখুঁত হওয়ার মধ্যে এক দারুণ ব্যালেন্স এনে দেয়।


## Common Mistake

ভুল ধারণা:

রির‍্যাঙ্কার মডেল যেহেতু অনেক বেশি নিখুঁত, তাই ডাটাবেসের লাখ লাখ ডকুমেন্টের ওপর সরাসরি এটি রান করা ভালো।

বাস্তবতা:

লাখ লাখ লেখার ওপর সরাসরি রির‍্যাঙ্ক রান করলে একটা সার্চ শেষ হতে কয়েক মিনিট লেগে যাবে!

এমনকি তোমার সার্ভারও ক্র্যাশ করতে পারে।

তাই মনে রাখবে, রির‍্যাঙ্কার সবসময় প্রথম স্টেজের ফিল্টার করা অল্প কিছু ডকুমেন্টের ওপর চালাতে হয়।


## ৮. Mental Model: ইন্টারভিউ বোর্ড

পুরো বিষয়টি মাথায় গেঁথে নেওয়ার জন্য চলো একটি সহজ তুলনা দেখি।

ধরে নাও, আমাদের পুরো পাইপলাইনটি হলো একটি চাকরির নিয়োগ পরীক্ষা।

**Hybrid Search হলো প্রিলিমিনারি পরীক্ষা:**

১ লাখ চাকরিপ্রার্থীর মধ্য থেকে নির্দিষ্ট কিওয়ার্ড আর যোগ্যতা দেখে প্রিলিমিনারি পরীক্ষার মাধ্যমে দ্রুত ১০০০ জনকে বেছে নেওয়া হলো।

**Reranker হলো ফাইনাল ভাইভা বোর্ড:**

এই ১০০০ জনের মধ্যে থেকে সেরা ১০ জনকে ভাইভা বোর্ডে মুখোমুখি ডাকা হলো।

সেখানে গভীরভাবে প্রশ্ন করে যাচাই করার পর ফাইনাল সেরা ৩ জনকে চাকরি দেওয়া হলো।

কী, সহজ না?


## ৯. Mini Project: Custom Hybrid Search

চলো আমরা পাইথনে কোনো লাইব্রেরি ছাড়াই একদম নিজেরা একটি মিনি হাইব্রিড সার্চ এবং রির‍্যাঙ্কিং সিস্টেম তৈরি করে ফেলি।

```python
import numpy as np

# ১. Database-এর ৩টি ডকের মক টেক্সট ও Vector
docs = {
    0: {"text": "bKash credit limit and PIN reset policy center.", "vector": np.array([0.9, 0.1])},
    1: {"text": "PIN lock issue is resolved within 24 hours timeline.", "vector": np.array([0.8, 0.4])},
    2: {"text": "Earn cashback on credit card bill payment.", "vector": np.array([0.2, 0.9])}
}

# ২. ইউজার কুয়্যারি
query_text = "PIN reset timeline"
query_vector = np.array([0.85, 0.3])

# ৩. কাস্টম BM25 (Sparse) কিওয়ার্ড ম্যাচ স্কোরার
def get_sparse_score(query, doc_text):
    words = query.lower().split()
    score = 0
    for word in words:
        if word in doc_text.lower():
            score += 1.0
    return score

# ৪. কোসাইন ডেন্স সিমিলারিটি
def get_dense_score(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# ৫. হাইব্রিড Search এগ্রিগেশন (RRF Simulation)
print("Running Hybrid Search Pipeline...\n")
hybrid_results = []

for idx, doc in docs.items():
    sparse = get_sparse_score(query_text, doc["text"])
    dense = get_dense_score(query_vector, doc["vector"])
    
    # হাইব্রিড কম্বাইন্ড স্কোর (৫০% স্পার্স + ৫০% ডেন্স)
    combined_score = (0.5 * sparse) + (0.5 * dense)
    hybrid_results.append((combined_score, doc["text"]))
    print(f"Doc {idx+1}: Sparse={sparse:.2f}, Dense={dense:.4f} -> Hybrid Score = {combined_score:.4f}")

# শর্টলিস্ট টপ ডক
hybrid_results.sort(reverse=True, key=lambda x: x[0])
print(f"\n[BEST MATCH RETRIEVED] '{hybrid_results[0][1]}' with Score {hybrid_results[0][0]:.4f}")
```

**কোডটি কীভাবে কাজ করছে?**

১. আমরা প্রথমে কিওয়ার্ড আর ছোট ভেক্টর ডাটাবেস নিয়েছি।

২. এরপর স্পার্স আর ডেন্স স্কোর মিলিয়ে ফাইনাল স্কোর তৈরি করা হয়েছে।

৩. এখানে `"PIN lock issue..."` ডকটি কিওয়ার্ড আর অর্থ দুই দিক থেকেই এগিয়ে থাকায় সেরা স্কোর পেয়েছে।

৪. ব্যাকএন্ডে কাস্টম সার্চ সিস্টেম তৈরি করার সময় আমরা এই টেকনিক ব্যবহার করতে পারি।


## Interview Questions

### Beginner level

**প্রশ্ন:** RAG প্রজেক্টে Hybrid Search কেন প্রয়োজন?

**উত্তর:** এটি কিওয়ার্ড আর অর্থ ভিত্তিক সার্চ— দুটি টেকনিক একসাথে মিলিয়ে কাজ করে।

এর ফলে নামের বানান ভুল হলে বা কোনো স্পেশাল আইডি দিয়ে সার্চ করলেও একদম সঠিক তথ্য খুঁজে পাওয়া যায়।

---

### Intermediate level

**প্রশ্ন:** Two-Stage Retrieval কীভাবে সার্চের গতি বাড়াতে সাহায্য করে?

**উত্তর:** প্রথম ধাপে এটি দ্রুত ভেক্টর সার্চ করে লাখ লাখ লেখা থেকে মাত্র ৫০টি লেখা বাছাই করে।

দ্বিতীয় ধাপে শুধু ওই ৫০টি লেখার ওপর ভারী রির‍্যাঙ্কার চালানো হয়।

এতে সার্চের গতি ও নিখুঁত হওয়ার মধ্যে দারুণ ব্যালেন্স তৈরি হয়।

---

### Advanced level

**প্রশ্ন:** HyDE কীভাবে কাজ করে আর কখন এটি ব্যবহার করা বিপজ্জনক হতে পারে?

**উত্তর:** `HyDE` ইউজারের প্রশ্নের ওপর ভিত্তি করে প্রথমে একটি কাল্পনিক উত্তর তৈরি করে নেয়।

তারপর সেটি দিয়ে ডাটাবেসে সার্চ করে।

যেহেতু কাল্পনিক উত্তর ও ডাটাবেসের লেখার স্টাইল মিলে যায়, তাই সার্চের কোয়ালিটি অনেক বাড়ে।

তবে প্রজেক্টটি যদি সবসময় রিয়েল-টাইম ডেটার ওপর নির্ভর করে, তবে কাল্পনিক ডেটা সার্চকে সম্পূর্ণ ভুল দিকে নিয়ে যেতে পারে।


## Chapter Summary

চলো সংক্ষেপে পুরো চ্যাপ্টারের মূল কথাগুলো আর একবার দেখে নিই:

১. `Advanced Retrieval` আমাদের RAG সিস্টেমকে প্রোডাকশন লেভেলের জন্য একদম নিখুঁত করে তোলে।

২. `Hybrid Search` শব্দের বানান আর অর্থ— এই দুটোর ফলাফল মিলিয়ে সার্চের মান অনেক বাড়িয়ে দেয়।

৩. `Re-ranking` এর কাজ হলো প্রথম ধাপে পাওয়া লেখাগুলোর মধ্য থেকে একদম সেরা অংশটি বেছে নেওয়া।

৪. প্রোডাকশনে সার্চের গতি ঠিক রাখতে আমাদের অবশ্যই `Two-Stage Retrieval` ব্যবহার করতে হবে।


## What's Next?

দারুণ! আমরা RAG এর সব অ্যাডভান্সড টেকনিক শিখে ফেলেছি।

পরের চ্যাপ্টার থেকে শুরু হচ্ছে AI মডেলকে নিজের মতো করে পোষ মানানোর গল্প।

আমরা দেখব কীভাবে `Fine-Tuning` আর কাস্টম `Dataset` তৈরি করতে হয়।

তো চলো, পরের ধাপে পা বাড়ানো যাক!

**Chapter 14 শেষ।**
