# Chapter 15: RAG Fundamentals — The Open-Book Exam for LLMs

---

তুমি কি কখনো ভেবেছো — ChatGPT বা Gemini যতই শক্তিশালী হোক না কেন, তারা কিন্তু তোমার কোম্পানির ইন্টারনাল পলিসি জানে না?

অথবা কোনো কাস্টমারের লাইভ ট্রানজ্যাকশন হিস্টোরি কিংবা আজ সকালের কোনো লেটেস্ট সিক্রেট আপডেট?

এসব কিন্তু তারা একদমই জানে না!

এখন এই নতুন তথ্যগুলো জানানোর জন্য কি প্রতিবার কোটি টাকা খরচ করে Model-কে Fine-Tuning করবে?

সেটা তো অসম্ভব!

আর ঠিক এখানেই জন্ম RAG বা Retrieval-Augmented Generation-এর।

তো চলো, এই চ্যাপ্টারে AI দুনিয়ার সবচেয়ে জনপ্রিয় আর দরকারি মেথড RAG-এর ভেতরের গল্পটা একদম সহজে বুঝে ফেলি।

আমরা দেখবো কীভাবে RAG-এর Ingestion, Retrieval আর Generation Pipeline-গুলো কাজ করে।

আরও দেখবো কীভাবে Recursive বা Semantic Chunking দিয়ে ডাটার আসল অর্থ ধরে রেখে Model-এর ইনপুট তৈরি করা যায়।

চলো, পরীক্ষার হলে বই ছাড়া বসা বনাম বই খুলে পরীক্ষা দেওয়ার এক দারুণ গল্প দিয়ে শুরু করা যাক!


## ১. Hook: বই খুলে পরীক্ষা দেওয়া

কল্পনা করো, তুমি একটি খুব কঠিন ফাইনাল পরীক্ষা দিতে বসেছো।

ধরা যাক, এটা একটা Closed-Book Exam। মানে কী?

তার মানে, পরীক্ষার হলে তোমাকে কোনো বই বা খাতা নিতে দেওয়া হলো না।

এখন তোমাকে তোমার মাথায় সেভ থাকা পুরনো মুখস্থ জ্ঞান দিয়ে সব প্রশ্নের উত্তর লিখতে হবে।

এই মুখস্থ জ্ঞানই হলো Model-এর Trained Weights।

কিন্তু প্রশ্ন যদি সিলেবাসের বাইরে থেকে আসে?

তখন তুমি বানিয়ে বানিয়ে ভুল উত্তর লিখতে শুরু করবে।

AI-এর ভাষায় একেই বলে Hallucination!

[VISUAL]
Title: Closed-Book LLM vs. Open-Book RAG Pipeline
Illustration: Flat prediction from weight memory vs. targeted search and context injection pipeline
Placement: After Hook Section
Purpose: Show the conceptual paradigm shift of RAG.

```
Closed-Book Model (Only Internal Weights - Risk of Hallucination):
Prompt: "bKash campaign dynamic rules?" ──► [ LLM Model ] ──► "I think the rules are..." (Wrong!)

Open-Book RAG (Retrieval-Augmented Generation - 100% Fact-based):
Prompt: "bKash campaign dynamic rules?"
  │
  ▼
[ Search Vector DB ] ──► [ Found: "Doc B: Rules are X, Y" ] ──► [ Inject Context ] ──► [ LLM ] ──► "According to Doc B, rules are X, Y"
```

আর যদি এটা একটা Open-Book Exam হয়?

তাহলে শিক্ষক তোমাকে পরীক্ষার হলে সব বই আর কোম্পানির পলিসি ফাইল সাথে নিয়ে বসার অনুমতি দিলেন।

এখন তোমার কাজ কী?

খুব সহজ! প্রশ্নটা পড়ে প্রথমে বইয়ের সূচিপত্র ঘেঁটে সঠিক পাতা আর প্যারাগ্রাফ খুঁজে বের করবে।

এই খুঁজে নেওয়াকেই বলে Retrieval।

এরপর সেই পৃষ্ঠা চোখের সামনে খোলা রেখে একদম সঠিক আর সত্য উত্তরটা তৈরি করবে।

এই উত্তর বানিয়ে দেওয়াকে বলে Generation।

RAG হলো LLM-এর জন্য ঠিক এই ওপেন-বুক পরীক্ষার মতো।

এখানে Model নিজে কিছু মুখস্থ করে রাখে না।

সে শুধু Vector Database নামের বড় "বই" থেকে দরকারি পাতা খুঁজে এনে উত্তর দেয়।


## ২. RAG আর Chunking কীভাবে কাজ করে?

একটি পুরো RAG Architecture মূলত দুটি আলাদা Pipeline-এ কাজ করে:

[VISUAL]
Title: Two Pipelines of RAG Architecture
Illustration: High-quality flowchart mapping the Offline Ingestion Pipe versus the Online Retrieval-Generation Pipe
Placement: After Core Concepts section
Purpose: Visually separate the static database preparation from the live user query flow.

```
Offline Ingestion Pipeline (একবার রান হয়):
Raw PDF/Docs ──► [ Chunking ] ──► [ Embedding ] ──► [ Upsert to Vector DB ]

Online Query Pipeline (প্রতিটি ইউজার রিকোয়েস্টে রান হয়):
User Query ──► [ Embed Query ] ──► [ Semantic Search Vector DB ] ──► [ Inject Context to Prompt ] ──► [ LLM Generation ]
```

### Ingestion Pipeline

তো এই Ingestion Pipeline জিনিসটা কী?

সহজ কথায়, এটা একটা ব্যাকগ্রাউন্ড প্রসেস।

ধাপগুলো একটু সহজ করে দেখি চলো:

প্রথম ধাপ হলো Document Loading।

এখানে আমরা PDF, Word ফাইল বা Database থেকে Raw Text রিড করি।

দ্বিতীয় ধাপ হলো Chunking।

ধরা যাক, তোমার টেক্সট ফাইলটা অনেক বড়, যেমন ৫০ পৃষ্ঠার একটা ম্যানুয়াল।

এত বড় ফাইল তো Model-এর Context Window-তে আটবে না!

তাই পুরো টেক্সটকে ছোট ছোট টুকরো বা Chunk-এ ভাগ করা হয়।

তৃতীয় ধাপ হলো Embedding।

এখানে প্রতিটি ছোট Chunk-কে Vector-এ convert করা হয়।

চর্থ ধাপ হলো Vector Database Store।

সবশেষে এই Vector-গুলোকে দ্রুত সার্চ করার জন্য Vector Database-এ Indexing করে সেভ রাখা হয়।


### Retrieval & Generation Pipeline

তাহলে Retrieval আর Generation কীভাবে কাজ করে?

এটা চলে যখন ইউজার লাইভ কোনো প্রশ্ন করে।

চলো এর ভেতরের কাজগুলো একটু বুঝে নিই:

প্রথমেই আসে Retrieve করার পালা।

ইউজারের প্রশ্নটাকে এম্বেড করে Vector Database থেকে সবচেয়ে মিল থাকা $K$ সংখ্যক (যেমন: সেরা ৩টি) Chunk খুঁজে আনা হয়।

এরপরের কাজ হলো Augment করা।

খুঁজে পাওয়া Chunk-গুলোকে মূল Prompt-এর সাথে Context হিসেবে জুড়ে দেওয়া হয়।

সবশেষে হলো Generate করা।

এখন LLM Model এই জুড়ে দেওয়া Context পড়ে একদম সত্য উত্তর লিখে দেয়।


### Chunking Strategies

মজার ব্যাপার হলো, RAG কতটা ভালো কাজ করবে তার ৮০% নির্ভর করে তুমি কীভাবে Data-কে Chunk করছো তার ওপর!

চলো দেখি কী কী উপায়ে Chunk করা যায়:

প্রথম উপায় হলো Character Chunking।

এখানে ধরো প্রতি ৫০০ ক্যারেক্টার পর পর টেক্সট কেটে দেওয়া হয়।

কিন্তু এতে একটা বড় সমস্যা আছে।

হুট করে লাইনের মাঝখানে কেটে গেলে কিন্তু বাক্যের অর্থটাই নষ্ট হয়ে যায়!

দ্বিতীয় উপায় হলো Token Chunking।

এখানে প্রতি ২০০ Token পর পর টেক্সট কাটা হয়।

কস্ট কন্ট্রোল করার জন্য এটা ভালো হলেও, তথ্যের অর্থ হারিয়ে যাওয়ার ভয় থাকে।

তৃতীয় উপায় হলো Recursive Character Chunking।

ইন্ডাস্ট্রিতে সবচেয়ে বেশি ব্যবহার করা হয় এই স্ট্যান্ডার্ড পদ্ধতিটি।

এটি প্রথমে প্যারাগ্রাফ, তারপর নতুন লাইন আর সবশেষে স্পেস দেখে খুব বুদ্ধি খাটিয়ে টেক্সট কাটে।

ফলে বাক্যের আসল অর্থ আর প্যারাগ্রাফের পূর্ণতা একদম বজায় থাকে।

চলো দেখি চতুর্থ উপায়, যা হলো Semantic Chunking।

এটি হলো সবচেয়ে অ্যাডভান্সড পদ্ধতি।

এটি পুরো টেক্সটের Embeddings Vector-এর পরিবর্তন মেপে কাজ করে।

যখনই দেখে টেক্সটের টপিক বা অর্থ বদলে যাচ্ছে, অমনি সে নতুন Chunk তৈরি করে ফেলে।


## ৩. Chunk Overlap কেন দরকার?

Chunk তৈরি করার সময় আমরা সাধারণত দুটি Chunk-এর মাঝখানে কিছুটা Overlap রাখি।

চলো নিচের ডায়াগ্রাম থেকে এর মেকানিজমটা একটু দেখে নিই:

[VISUAL]
Title: Sliding Window Chunk Overlap
Illustration: Visual representation of Text Chunks sharing boundary tokens to preserve sentence context
Placement: After Chunking section
Purpose: Ground the intuitive necessity of boundary preservation.

```
Text: "The user has blocked his PIN. He must visit bKash office to reset it."
Chunk Size: 40 characters, Overlap: 10 characters

Chunk 1: [ The user has blocked his PIN. He must vi ]
                                     ▲───────▲ (Overlap tokens)
Chunk 2:                            [ He must visit bKash office to reset it. ]
```

তো এই Overlap রেখে আমাদের লাভটা কী হলো?

যদি Overlap না থাকতো, তবে `"He must visit"` লেখাটি মাঝখান থেকে কেটে যেত।

ফলে সার্চ করে যখন দ্বিতীয় Chunk-টি পাওয়া যেত, তখন সে তার আগের Context হারিয়ে ফেলত।


## ৪. Real World Example: Perplexity-র RAG

Perplexity.ai বা ChatGPT-এর ব্রাউজিং ফিচার কীভাবে কাজ করে জানো?

চলো ধাপে ধাপে দেখে নিই:

প্রথমে তারা Search Engine থেকে পাওয়া ৫টি ওয়েব পেজ স্ক্র্যাপ করে Semantic Chunking করে।

এরপর আসে Cosine Retrieval-এর পালা।

তোমার প্রশ্নের সাথে যে Chunk-গুলোর মিল ৯০%-এর বেশি, সেগুলোকে ছেঁকে নিয়ে Prompt-এ সাজানো হয়।

সবশেষে করা হয় Context Injection আর Citation।

Prompt-এর ভেতর কড়া নির্দেশ দেওয়া থাকে: "নিচের Context ছাড়া অন্য কিছু বলবে না এবং সোর্স সাইটেশন দিয়ে দেবে।"

ব্যস! এর ফলে AI কোনো Hallucination ছাড়াই একদম perfect উত্তর আর সোর্স লিংক তৈরি করে দেয়।


## ৫. Developer Perspective: Recursive Splitter

💻 Developer View

পাইথনে `langchain` লাইব্রেরি ব্যবহার করে কীভাবে Custom রিকিউরসিভ স্প্লিটার আর Overlap তৈরি করবে, চলো সেই কোডটা দেখে নিই:

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# ১. র টেক্সট ম্যানুয়াল
corporate_policy = """
bKash PIN Reset Policy:
1. Customer can dial *247# to reset PIN using NID.
2. In case of verification failure, customer must visit nearest Customer Care Center.
3. Bring original NID copy and active SIM card for biometrics.
"""

# ২. Recursive Text Splitter ইনিশিয়ালাইজ করো
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,      # প্রতি চাঙ্কের সর্বোচ্চ দৈর্ঘ্য
    chunk_overlap=20,    # দুই চাঙ্কের মধ্যকার ওভারল্যাপ
    length_function=len,
    separators=["\n\n", "\n", " ", ""] # অগ্রাধিকার তালিকা
)

# ৩. টেক্সট স্প্লিট করো
chunks = text_splitter.split_text(corporate_policy)

# ৪. Output প্রিন্ট করো
print(f"মূল পলিসির দৈর্ঘ্য: {len(corporate_policy)} ক্যারেক্টার।")
print(f"তৈরি হওয়া মোট চাঙ্ক সংখ্যা: {len(chunks)}\n")

for idx, chunk in enumerate(chunks):
    print(f"Chunk {idx+1} ({len(chunk)} chars):")
    print(f"'{chunk}'")
    print("-" * 30)
```


## ৬. Production Perspective: Security Filter

🏭 Production Reality

আসল প্রোডাকশন সিস্টেমে কাজ করার সময় সবচেয়ে বিপজ্জনক রিস্ক হলো Context Leakage বা অনধিকার অ্যাক্সেস।

এটা আবার কী জিনিস?

ধরা যাক, একজন সাধারণ কাস্টমার চ্যাটবটে এমনভাবে প্রশ্ন করল যাতে কোম্পানির ইন্টারনাল AI হ্যাক হয়ে গেল!

আর এর ফলে সে কোনো অ্যাডমিনের স্যালারি শিট বা সিক্রেট প্রোজেক্টের তথ্য জেনে গেল।

তাহলে এর সমাধান কী?

খুব সহজ! ডাটাবেজে প্রতিটি Vector সেভ করার সময় তার Metadata-তে Access Control List বা ACL ট্যাগ করে দেওয়া হয়।

যেমন: `{"role_allowed": "admin"}`।

কাস্টমার যখন চ্যাট করবে, তখন সার্চ করার সময় মেটাডেটা ফিল্টার অ্যাপ্লাই করা হয়।

এর ফলে সাধারণ ইউজারের সার্চে কোনো অ্যাডমিন ডকুমেন্ট কখনোই আসবে না।


## ७. Common Mistakes

🔴 Common Mistake

ভুল ধারণা:

RAG প্রজেক্টে Chunk Size যত বড় রাখা যাবে, উত্তর তত ভালো হবে।

বাস্তবতা:

অতিরিক্ত বড় Chunk ব্যবহার করলে Prompt-এর ভেতর অপ্রাসঙ্গিক তথ্য ঢুকে যায়।

এতে LLM উল্টো বিভ্রান্ত হয়ে পড়ে।

তা ছাড়া বড় Chunk-এর কারণে VRAM ব্লো-আপ হতে পারে আর Latency-ও বেড়ে যায়।

RAG-এর গোল্ডেন রুল মনে রেখো: "Retrieve only what is essential"। অর্থাৎ শুধু দরকারি অংশটুকুই নাও, বেশি নয়।


## ৮. Mental Model: লাইব্রেরিয়ান আর তোতাপাখি

RAG পাইপলাইন সহজে মনে রাখার জন্য চলো একটা মজার গল্প ভাবি।

এখানে আমাদের কাছে দুটি চরিত্র আছে:

প্রথম চরিত্র হলো Vector DB, যে আসলে একজন স্মার্ট লাইব্রেরিয়ান!

সে পুরো লাইব্রেরির বইগুলোর পাতা আর অর্থ খুব সুন্দর করে সাজিয়ে রেখেছে।

কোনো প্রশ্ন আসার সাথে সাথে সে একদম পারফেক্ট ৫টি পৃষ্ঠা খুঁজে বের করে নিয়ে আসে।

দ্বিতীয় চরিত্র হলো LLM, যে আসলে একটি বাচাল তোতাপাখি!

তোতাপাখি নিজে থেকে কিন্তু কোনো তথ্য জানে না।

কিন্তু সে অসম্ভব সুন্দর করে কথা বলতে পারে।

লাইব্রেরিয়ান যখন তাকে সেই ৫টি পৃষ্ঠা এনে দেয়, তোতাপাখি তখন লাইভ রিড করে চমৎকার মিষ্টি ভাষায় উত্তর বুঝিয়ে দেয়।


## ৯. Mini Project: স্ক্র্যাচ থেকে RAG পাইপলাইন

চলো, পাইথনে NumPy ব্যবহার করে কোনো ML Framework ছাড়াই একটা মিনি RAG পাইপলাইন বানিয়ে ফেলি!

```python
import numpy as np

# ১. কোম্পানির পলিসি Database (আমাদের বইয়ের পৃষ্ঠা)
docs = [
    "dial *247# to reset your PIN code with NID verification.",
    "for verification failure, visit the nearest bKash center.",
    "bring your original NID copy and active SIM card for biometrics."
]

# ২. মক এম্বেডিংস ডিকশনারি (৩-ডাইমেনশন Vector)
# [পিন/ভেরিফিকেশন, ফিজিক্যাল ভিজিট/সেন্টার, প্রয়োজনীয় Document]
doc_embeddings = np.array([
    [0.9, 0.1, 0.0],  # doc 1: PIN reset
    [0.2, 0.95, 0.1], # doc 2: Visit center
    [0.1, 0.3, 0.95]  # doc 3: Bring documents
])

# ৩. কাস্টমার কুয়্যারি: "NID Verification fail hole kothay jabo?"
query = "NID Verification fail hole kothay jabo?"
# কুয়্যারি Vector এম্বেডিংস (মক রিপ্রেজেন্টেশন)
query_vector = np.array([0.15, 0.9, 0.1])

# ৪. Cosine Similarity রিট্রিভাল
def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

print("Searching Vector DB for relevant context...")
scores = []
for idx, doc_vec in enumerate(doc_embeddings):
    score = cosine_similarity(query_vector, doc_vec)
    scores.append((score, docs[idx]))
    print(f"Similarity with Doc {idx+1}: {score:.4f}")

# টপ ১টি বেস্ট ডক সিলেক্ট করো
scores.sort(reverse=True, key=lambda x: x[0])
best_context = scores[0][1]

print(f"\n[RETRIEVED CONTEXT] '{best_context}'\n")

# ৫. LLM Prompt ইনজেকশন (Augmented Prompt Generation)
augmented_prompt = f"""
You are a helpful bKash customer assistant. Use the following context to answer the user query.
If you don't know the answer, say "আমি জানি না"। Do not make up facts.

Context:
{best_context}

User Query:
{query}

Answer:
"""

print("--- AUGMENTED PROMPT SENT TO LLM ---")
print(augmented_prompt)
```

#### Code Breakdown:

* **Input:** কাস্টমারের Query Vector আর ৩-ডাইমেনশনের পলিসি Embeddings।
* **Output:** সবচেয়ে ভালো ম্যাচ হওয়া ডকুমেন্ট রিট্রিভ করে তৈরি করা ফাইনাল Prompt।
* **Why it works:** কোসাইন সিমিলারিটি মেপে `visit the nearest bKash center` ডকুমেন্টটি নিখুঁতভাবে খুঁজে বের করে Prompt-এ ইনজেক্ট করা হয়েছে।
* **When to use:** নিজের মতো করে কাস্টম RAG পাইপলাইন একদম স্ক্র্যাচ থেকে বানাতে চাইলে এটি ব্যবহার করবে।


## ১০. Interview Questions

### Beginner

১. **প্রশ্ন:** RAG কী আর এটি কেন ব্যবহার করা হয়?

* **উত্তর:** RAG হলো Retrieval-Augmented Generation। এটি Model-এর নিজস্ব মেমোরির ওপর নির্ভর না করে বাইরের কোনো Vector Database থেকে রিয়েল-টাইমে একদম সঠিক তথ্য খুঁজে আনে। এরপর তা Prompt-এর সাথে জুড়ে দিয়ে উত্তর তৈরি করে। এটি Hallucination কমাতে আর কোম্পানির কাস্টম ডাটা মডেলে ব্যবহার করতে দারুণ সাহায্য করে।

### Intermediate

২. **প্রশ্ন:** Recursive Character Chunking কেন সাধারণ ক্যারেক্টার চাংকিংয়ের চেয়ে ভালো?

* **উত্তর:** সাধারণ ক্যারেক্টার চাংকিং লাইনের মাঝখানেই টেক্সট কেটে ফেলে বাক্যের অর্থ নষ্ট করতে পারে। কিন্তু Recursive Character Splitter বুদ্ধি খাটিয়ে প্যারাগ্রাফ, নতুন লাইন আর স্পেস দেখে কাটে। ফলে প্রতিটি খণ্ডের অর্থ একদম অক্ষুণ্ণ থাকে।

### Advanced

৩. **প্রশ্ন:** প্রোডাকশনে Document Leakage কীভাবে আটকানো হয়?

* **উত্তর:** এর জন্য প্রতিটি Vector ডাটাবেজে রাখার সময় তার Metadata-তে Access Control List বা ACL ট্যাগ করে দেওয়া হয়। ইউজার যখন প্রশ্ন করে, তখন সার্চে মেটাডেটা ফিল্টার অ্যাপ্লাই করা হয়। এর ফলে ইউজারের রোল আইডির বাইরে কোনো সিক্রেট ডকুমেন্ট কখনোই রিট্রিভ হতে পারে না।


## ১১. Summary

তো এই চ্যাপ্টারে আমরা কী কী শিখলাম?

চলো এক নজরে দেখে নিই:

প্রথমত, RAG মূলত একটি ক্লোজড-বুক AI মডেলকে ওপেন-বুক ফ্যাট-বেসড সিস্টেমে রূপান্তর করে।

দ্বিতীয়ত, Ingestion Pipeline অফলাইনে Chunking আর Embedding করে আমাদের Vector Database তৈরি করে।

তৃতীয়ত, ডকের আসল অর্থ ধরে রাখতে Recursive Chunking আর Overlap সবচেয়ে বেশি কাজে আসে।

সবশেষে, প্রোডাকশন সিস্টেমে ডাটার সিকিউরিটি নিশ্চিত করতে ACL Filtering ব্যবহার করা জরুরি।


## ১২. What's Next?

দারুণ! RAG আর Chunking-এর মূল বিষয়গুলো আমরা শিখে ফেলেছি।

পরের চ্যাপ্টারে আমরা দেখবো কীভাবে এই পাইপলাইনকে আরও নিখুঁত ও প্রোডাকশন-রেডি করা যায়।

সেখানে আমরা HyDE, Parent-Document Retrieval এবং Re-ranking নিয়ে আলোচনা করবো।

চলো তাহলে, পরের চ্যাপ্টারে যাওয়া যাক!

**Chapter 15 শেষ।**
