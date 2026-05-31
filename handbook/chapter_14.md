# Chapter 14: Advanced Retrieval, Hybrid Search & Re-ranking

---

### Chapter Goal
এই চ্যাপ্টারের মূল লক্ষ্য হলো সাধারণ আরএজি (RAG) পাইপলাইনের এক্যুরেসি ৯০% থেকে ৯৯% এ উন্নীত করার জন্য সবচেয়ে শক্তিশালী প্রোডাকশন মেকানিজম—অর্থাৎ অ্যাডভান্সড রিট্রিভাল (Advanced Retrieval), হাইব্রিড সার্চ (Hybrid Search - BM25 + Dense Vector), এবং রির‍্যাঙ্কিং (Re-ranking) এর আর্কিটেকচারাল মেকানিজম ক্র্যাক করা। আপনি জানতে পারবেন কীভাবে প্যারেন্ট-ডকুমেন্ট রিট্রিভাল (Parent-Document Retrieval) এবং HyDE (Hypothetical Document Embeddings) কাজ করে এবং প্রোডাকশন প্রজেক্টে এগুলোর নিখুঁত সিলেকশন ও ইমপ্লিমেন্টেশন ক্রাইটেরিয়া আয়ত্ত করতে পারবেন।

### Why Should I Care?
বাস্তবে দেখা যায়, শুধুমাত্র বেসিক কোসাইন ভেক্টর সার্চ ব্যবহার করলে মডেল অনেক সময় কুয়্যারির প্রাসঙ্গিক বা নিখুঁত ডকুমেন্ট রিট্রাইভ করতে ব্যর্থ হয় (যেমন: নামের বানান ভুল বা কাস্টম পার্ট নাম্বার খোঁজার সময়)। হাইব্রিড সার্চ কীওয়ার্ড এবং মিনিং দুটিই একসাথে সার্চ করে এবং রির‍্যাঙ্কার ভুল রিট্রাইভাল ডকগুলোকে ইনস্ট্যান্টলি ফিল্টার করে পারফেক্ট ৩টি ডকুমেন্ট প্রম্পটে পাঠায়। এটি প্রোডাকশন আরএজি ফেইলিউর কমানোর এক নম্বর হাতিয়ার।

### Big Picture
আগের চ্যাপ্টারে আমরা আরএজি-র বেসিক চাংকিং ও ইনজেস্ট পাইপলাইন শিখেছি। এই চ্যাপ্টারে আমরা সেই পাইপলাইনকে এন্টারপ্রাইজ লেভেলের নিখুঁত সার্চ ইঞ্জিনে রূপান্তর করব। এখানে শেখা অপ্টিমাইজেশন আমাদের পরবর্তী চ্যাপ্টারের কাস্টম মডেল ফাইন-টিউনিং (Fine-Tuning) এবং আরএজি বনাম ফাইন-টিউনিংয়ের আর্কিটেকচারাল সিদ্ধান্ত নেওয়ার মূল ভিত্তি।

---

### ১. Hook: লাইব্রেরিয়ানের সেরা পৃষ্ঠা ও পুরো বইয়ের সমন্বয়

কল্পনা করুন, আপনি লাইব্রেরিতে গিয়ে লাইব্রেরিয়ানকে বললেন, **"বিকাশের ডায়নামিক পিন ব্লক কেন হয়?"** 
* **Basic RAG (বেসিক ভেক্টর সার্চ):** লাইব্রেরিয়ান বই ঘেঁটে ১টি নির্দিষ্ট প্যারাগ্রাফ খুঁজে পেলেন যা আপনার কোশ্চেনের সাথে ম্যাচ করে। কিন্তু সমস্যা হলো, সেই প্যারাগ্রাফের ভেতর লেখা আছে: *"অনুচ্ছেদ ৪ এর নিয়ম অনুসারে এটি লক হবে।"* এখন অনুচ্ছেদ ৪ কী? লাইব্রেরিয়ান তা জানেন না! ফলে এআই মডেলটি ইনকমপ্লিট বা বিভ্রান্তিকর উত্তর দেবে।

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

* **Parent-Document Retrieval:** লাইব্রেরিয়ান ভেক্টর সার্চের মাধ্যমে ছোট চাঙ্কটি খুঁজে পেলেন, কিন্তু প্রম্পটে পাঠানোর আগে তিনি সেই ছোট চাঙ্কের মূল উৎস বা পুরো "অনুচ্ছেদ ৪"-এর ৪টি প্যারাগ্রাফ একসাথে টেনে আনলেন (Parent Document)। এর ফলে এআই মডেল পুরো ব্যাকগ্রাউন্ড জেনে নিখুঁত উত্তর দেবে।

অ্যাডভান্সড রিট্রিভাল ঠিক এই স্মার্ট লাইব্রেরিয়ানের মতো কাজ করে। এটি সার্চের জন্য ছোট ভেক্টর ব্যবহার করে স্পিড বাড়ায়, কিন্তু ডিকোডারে পাঠানোর সময় পুরো চ্যাপ্টার ইনজেক্ট করে কোয়ালিটি ম্যাক্সিমাইজ করে।

---

### ২. Core Concepts: হাইব্রিড সার্চ ও রির‍্যাঙ্কিং ইঞ্জিন

মিলিয়ন স্কেল এন্টারপ্রাইজ সার্চে নির্ভুল ফল পেতে ৩টি এডভান্সড টেকনিক ব্যবহৃত হয়:

#### ক. Hybrid Search (স্পার্স + ডেন্স সার্চ)
এটি ট্র্যাডিশনাল কিওয়ার্ড সার্চ এবং মডার্ন সিমান্টিক ভেক্টর সার্চের একটি অনন্য যুগলবন্দী।

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

1. **Sparse Search (BM25):** এটি ফাস্ট কিওয়ার্ড বা টোকেন ফ্রিকোয়েন্সি মেপে সার্চ করে। (যেমন: কাস্টমার পার্ট নাম্বার `"bKash-1234"` টাইপ করলে সিমান্টিক ভেক্টর হয়তো মিস করবে, কিন্তু BM25 হুবহু কিওয়ার্ড ম্যাচ করে দেবে)।
2. **Dense Search (Vector):** এটি অর্থ বা মিনিং মেপে সার্চ করে।
3. **RRF (Reciprocal Rank Fusion):** এই অ্যালগরিদমটি স্পার্স এবং ডেন্স সার্চের র্যাঙ্কিং স্কোর একত্রিত করে একটি একক ট্রাস্টেড র্যাঙ্ক স্কোর প্রডিউস করে।

#### খ. Re-ranking (রের‍্যাঙ্কিং)
ভেক্টর সার্চ ডাটাবেস থেকে টপ ১০টি সম্ভাব্য ডকুমেন্ট তুলে আনে। কিন্তু তাদের অর্ডারিং বা র্যাঙ্কিং ১০০% নিখুঁত নাও হতে পারে।
* **মেকানিজম:** আমরা একটি বিশেষায়িত **Cross-Encoder Reranker Model** (যেমন: Cohere Rerank বা BGE-Reranker) ব্যবহার করি। 
* এটি ইউজার কোশ্চেন এবং ১০টি ডকের প্রতিটি জোড়া আলাদা আলাদাভাবে ডিপ স্ক্যান করে পরম প্রাসঙ্গিকতা স্কোর পরিমাপ করে পুনরায় শর্টলিস্ট করে বেস্ট ৩টি ডক প্রম্পটে পাঠায়। এটি হ্যালুসিনেশন প্রায় ৯০% কমিয়ে দেয়।

#### গ. Query Rewriting & HyDE (Hypothetical Document Embeddings)
ইউজার যখন খুব ছোট বা ভাঙা বাংলায় প্রশ্ন লেখে (যেমন: `"PIN blocked bKash"`), তখন সিমান্টিক সার্চ ভালো কাজ করে না।
* **HyDE (হাইডি):** কুয়্যারি আসার সাথে সাথে আমরা প্রথমে একটি ছোট LLM-কে দিয়ে একটি কাল্পনিক বা সম্ভাব্য উত্তর (Hypothetical Answer) লেখাই।
* এবার সেই কাল্পনিক উত্তরটি এম্বেড করে ভেক্টর ডাটাবেসে সার্চ করা হয়। যেহেতু কাল্পনিক উত্তর এবং আসল ডাটাবেসের ডকের ফরম্যাট ও ডিকশন হুবহু মিলে যায়, তাই রিট্রিভাল কোয়ালিটি ড্রাস্টিকালি বুস্ট করে।

🧠 Remember

**BM25 (Sparse)** = শব্দের বানান ও কিওয়ার্ড খোঁজে।  
**Semantic (Dense)** = শব্দের অর্থ ও ভাবার্থ খোঁজে।  
**Reranker (Cross-Encoder)** = এই দুইয়ের আউটপুট ছেঁকে সেরা হিরের টুকরোটি বের করে।

---

### ৩. Visual Explanation: ক্রস-এনকোডার রির‍্যাঙ্কিং মেকানিজম

ক্রস-এনকোডারের কাজ করার নিখুঁত গাণিতিক প্রসেসটি নিচে ডায়াগ্রামের মাধ্যমে ভিজ্যুয়ালাইজ করুন:

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

 স্ট্যান্ডার্ড ভেক্টর সার্চ প্রতিটি ভেক্টর আলাদাভাবে প্রসেস করে ডট প্রোডাক্ট করে (Bi-Encoder)। কিন্তু রির‍্যাঙ্কার ইউজার কুয়্যারি এবং ডক টেক্সট একসাথে জোড়া লাগিয়ে ট্রান্সফরমার লেয়ারে ডিপ জয়েন্ট অ্যাটেনশন রান করে রিলেশন ম্যাপ করে, যা চরম নিখুঁত স্কোর দেয়।

---

### ৪. Real World Example: Perplexity-র হাইব্রিড ইনফারেন্স পাইপলাইন

Perplexity.ai যখন আপনার কোয়্যারির জন্য ইন্টারনেট স্ক্যান করে:

1. **Hybrid Ingestion:** তারা কোটি কোটি ওয়েব সাইট BM25 কিওয়ার্ড ইডেক্স এবং HNSW ভেক্টর স্পেস উভয় দিকেই সেভ রাখে।
2. **First-Stage Retrieval:** আপনার কুয়্যারির ওপর স্পার্স ও ডেন্স হাইব্রিড সার্চ রান করে ফার্স্ট স্টেজে ১০০টি সম্ভাব্য সোর্স পেজ তুলে আনা হয়।
3. **Reranking:** একটি শক্তিশালী রির‍্যাঙ্কার মডেল (Cohere Rerank) ৩ মিলি-সেকেন্ডে ১০০টি পেজ স্ক্যান করে বেস্ট ৫টি পেজ প্রম্পটে ফিড করে, যা ইনস্ট্যান্ট হাই-কোয়ালিটি সোর্সিং গ্যারান্টি দেয়।

---

### ৫. Developer Perspective: PyTorch & Cohere কাস্টম রির‍্যাঙ্কার কোড

💻 Developer View

ডেভেলপার হিসেবে ব্যাকঅ্যান্ড এপিআই পাইপলাইনে হাইব্রিড সার্চের আউটপুটের ওপর রির‍্যাঙ্কার মডেল রান করার রিয়েল পাইথন মেথড:

```python
# Cohere Rerank API Integration in Backend
import cohere

# ১. Cohere Client ইনিশিয়ালাইজ করুন
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

# ৩. Rerank API কল করুন
print("রানিং ক্রস-এনকোডার রির‍্যাঙ্কিং...")
response = co.rerank(
    model="rerank-english-v3.0",
    query=query,
    documents=documents,
    top_n=2
)

# ৪. রির‍্যাঙ্কড আউটপুট প্রিন্ট করুন
for idx, result in enumerate(response.results):
    doc_index = result.index
    score = result.relevance_score
    print(f"Rank {idx+1}: Score = {score:.4f} -> '{documents[doc_index]}'")
```

---

### ৬. Production Perspective: Two-Stage Retrieval Optimization

🏭 Production Reality

ক্রস-এনকোডার রির‍্যাঙ্কার মডেলগুলো অত্যন্ত কম্পিউটেশনালি হেভি এবং ধীরগতির হয়। প্রোডাকশনে ল্যাটেন্সি ও কস্ট কন্ট্রোল করতে **Two-Stage Retrieval** ফ্রেমওয়ার্ক ব্যবহার করা বাধ্যতামূলক।

* **Stage 1 (Coarse Retrieval):** স্পিড বাড়ানোর জন্য প্রথমে ফাস্ট ভেক্টর ডাটাবেস সার্চ (HNSW) রান করে ১ লাখ ডক থেকে টপ ৫০টি ক্যান্ডিডেট ডক ছেঁকে তোলা হয়। (ল্যাটেন্সি < ৫ মিলি-সেকেন্ড)।
* **Stage 2 (Fine Re-ranking):** এই ৫০টি ডকের ওপর রির‍্যাঙ্কার মডেল রান করে টপ ৩টি ডকুমেন্ট প্রম্পটে ইনজেক্ট করা হয়। (ল্যাটেন্সি ~৫০ মিলি-সেকেন্ড)।
* এই টু-স্টেজ অপ্টিমাইজেশন স্পিড ও এক্যুরেসির সেরা প্রোডাকশন ব্যালেন্স দেয়।

---

### ৭. Common Mistakes

🔴 Common Mistake

**ভুল ধারণা:** রির‍্যাঙ্কার মডেল যেহেতু অত্যন্ত নির্ভুল, তাই ডাটাবেসের সব লাখ লাখ ডকুমেন্টের ওপর সরাসরি রির‍্যাঙ্ক রান করা উচিত।

**বাস্তবতা:** লাখ লাখ ডকের ওপর সরাসরি ক্রস-এনকোডার রির‍্যাঙ্ক রান করলে একটি সিঙ্গেল কোয়্যারি কমপ্লিট হতে কয়েক মিনিট লেগে যাবে এবং সার্ভার ক্র্যাশ করবে। রির‍্যাঙ্কার শুধুমাত্র প্রথম স্টেজের ফাস্ট ফিল্টারড ডকুমেন্টের (সর্বোচ্চ ৫০-১০০টি) ওপর প্রয়োগ করার জন্য ডিজাইন করা হয়েছে।

---

### ৮. Mental Model: নিয়োগ পরীক্ষার ইন্টারভিউ বোর্ড

হাইব্রিড ও রির‍্যাঙ্কিং পাইপলাইনের মেন্টাল মডেল:

* **Hybrid Search (Sparse + Dense) = প্রিলিমিনারি এমসিকিউ পরীক্ষা:**
  ১ লাখ চাকরি প্রার্থীর মধ্যে থেকে কিওয়ার্ড ও বেসিক যোগ্যতা মেপে প্রিলিমিনারি পরীক্ষার মাধ্যমে দ্রুত ১০০০ জনকে শর্টলিস্ট করা হলো।
* **Reranker = ভাইভা বোর্ড (Cross-Encoder):**
  এই ১০০০ জনের মধ্য থেকে টপ ১০ জনকে ভাইভা বোর্ডে মুখোমুখি ডেকে (Deep Joint Attention) ইন-ডেপথ কোশ্চেন করে ফাইনাল সেরা ৩ জনকে চাকরি দেওয়া হলো।

---

### ৯. Mini Project: পাইথনে কাস্টম স্পার্স (Keyword) + ডেন্স (Vector) হাইব্রিড সার্চ এগ্রিগেটর

চলুন পাইথনে কাস্টম NumPy ব্যবহার করে কোনো লাইব্রেরি ছাড়া একটি পূর্ণাঙ্গ মিনি হাইব্রিড সার্চ এগ্রিগেটর এবং রির‍্যাঙ্কিং স্কোরার সিস্টেম স্ক্র্যাচ থেকে আর্কিটেক্ট করি।

```python
import numpy as np

# ১. ডাটাবেসের ৩টি ডকের মক টেক্সট ও ভেক্টর
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

# ৫. হাইব্রিড সার্চ এগ্রিগেশন (RRF Simulation)
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

#### Code Breakdown:
* **Input:** কিওয়ার্ড ম্যাচিং ও ২-ডাইমেনশন ভেক্টর ডাটাবেস।
* **Output:** স্পার্স ও ডেন্স স্কোর একত্রিত করে জেনারেট হওয়া ফাইনাল হাইব্রিড র্যাঙ্কিং।
* **Why it works:** `PIN lock issue...` ডকটিতে কিওয়ার্ড ম্যাচ ও ভেক্টর সিমান্টিক উভয় স্কোর হাই থাকায় এটি বেস্ট র্যাঙ্ক স্কোর লাভ করেছে।
* **When to use:** ব্যাকঅ্যান্ডে কাস্টম হাইব্রিড সার্চ মার্জার ও র্যাঙ্কিং এগ্রিগেটর মডিউল অপ্টিমাইজ করার জন্য।

---

### ১০. Interview Questions

#### Beginner
1. **প্রশ্ন:** আরএজি প্রজেক্টে হাইব্রিড সার্চের প্রয়োজনীয়তা কী?
   * **উত্তর:** হাইব্রিড সার্চ কিওয়ার্ড ম্যাচিং (Sparse BM25) এবং মিনিং ম্যাচিং (Dense Vector) দুটি টেকনিক একসাথে কম্বাইন করে। ফলে নামের বানান ভুল, স্পেশাল পার্ট নাম্বার বা কোড কিওয়ার্ড এবং সাধারণ অর্থের ভাবার্থ উভয়ই নির্ভুলভাবে রিট্রাইভ করা সম্ভব হয়।

#### Intermediate
2. **প্রশ্ন:** টু-স্টেজ রিট্রিভাল (Two-Stage Retrieval) প্রোডাকশনে ল্যাটেন্সি অপ্টিমাইজেশনে কীভাবে সাহায্য করে?
   * **উত্তর:** এটি প্রথম স্টেজে ফাস্ট ভেক্টর সার্চ (HNSW) রান করে মিলি-সেকেন্ডে লক্ষাধিক ডক থেকে ৫০টি ক্যান্ডিডেট শর্টলিস্ট করে। দ্বিতীয় স্টেজে শুধুমাত্র এই ৫০টি ডকের ওপর কম্পিউটেশনালি হেভি ও ধীরগতির ক্রস-এনকোডার রির‍্যাঙ্কার রান করে সেরা ৩টি ডক সিলেক্ট করে, যা সার্চ স্পিড ও এক্যুরেসির বেস্ট প্রোডাকশন কম্বিনেশন দেয়।

#### Advanced
3. **প্রশ্ন:** HyDE (Hypothetical Document Embeddings) কীভাবে রিট্রিভাল এক্যুরেসি উন্নত করে এবং কোন প্রজেক্টে এটি ব্যবহার করলে রিট্রিভাল কোয়ালিটি হ্রাস পাওয়ার ঝুঁকি থাকে?
   * **উত্তর:** HyDE ইউজার কুয়্যারির ওপর ভিত্তি করে প্রথমে একটি কাল্পনিক উত্তর জেনারেট করে এবং সেটি এম্বেড করে সার্চ করে। যেহেতু কাল্পনিক উত্তর এবং আসল ডকের রাইটিং ফরম্যাট হুবহু মিলে যায়, রিট্রিভাল বুস্ট হয়। তবে প্রজেক্ট যদি রিয়েল-টাইম ফ্যাট বা ডায়নামিক সংখ্যার ওপর নির্ভরশীল হয়, তবে কাল্পনিক উত্তরের কাল্পনিক ডেটা সার্চকে সম্পূর্ণ অন্যদিকে ডাইভার্ট করে দিতে পারে (Hallucinated retrieval risk)।

---

### ১১. Chapter Summary
* **Advanced Retrieval** আরএজি-র এক্যুরেসি ও ইনফরমেশন সিকিউরিটি প্রোডাকশন গ্রেডে উন্নীত করে।
* **Hybrid Search** স্পার্স ও ডেন্স রিট্রিভালের স্কোর RRF এর মাধ্যমে মার্জ করে সার্চ এক্যুরেসি বাড়ায়।
* **Re-ranking** ক্রস-এনকোডারের সাহায্যে টপ ক্যান্ডিডেটগুলোর গভীর অর্থ স্ক্যান করে ফাইনাল সোর্স সিলেক্ট করে।
* প্রোডাকশন এন্টারপ্রাইজ আরএজি-তে ল্যাটেন্সি মিনিমাইজ করতে সর্বদা **Two-Stage Retrieval** ব্যবহার করা ম্যান্ডেটরি।

---

### ১২. What's Next
দারুণ! আমরা সফলভাবে আরএজি-র সব এডভান্সড টেকনিক ও আর্কিটেকচার জয় করে ফেলেছি। পরবর্তী চ্যাপ্টার থেকে আমাদের শুরু হচ্ছে মডেল পোষ মানানো বা এআই টিউনিংয়ের সবচেয়ে ক্রুশিয়াল অধ্যায়: **Part 8 — Fine-Tuning এর Chapter 15: Supervised Fine-Tuning (SFT) & Dataset Preparation**। আরএজি বনাম ফাইন-টিউনিংয়ের গাইডলাইন এবং কাস্টম ডেসক্রিপটিভ ডেটাসেট কীভাবে প্রিপেয়ার করতে হয়, তা আমরা বিস্তারিত শিখব।

---
**Chapter 14 সমাপ্ত।**
