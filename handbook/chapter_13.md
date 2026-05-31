# Chapter 13: RAG Fundamentals — The Open-Book Exam for LLMs

---

### Chapter Goal
এই চ্যাপ্টারের মূল লক্ষ্য হলো এলএলএম-এর জেনারেটিভ ক্ষমতার সাথে কাস্টম নলেজ বেসের মেলবন্ধন ঘটানোর পাইপলাইন—অর্থাৎ আরএজি (RAG - Retrieval-Augmented Generation) এর কোর মেকানিজম নিখুঁতভাবে বোঝা। তুমি জানতে পারবে কীভাবে আরএজি-র ইনজেস্ট (Ingestion), রিট্রিভাল (Retrieval), এবং জেনারেশন (Generation) পাইপলাইন কাজ করে এবং বিভিন্ন প্রকার চাংকিং স্ট্র্যাটেজি (Chunking - Character, Token, Recursive, Semantic) এর প্র্যাক্টিক্যাল প্রয়োগ ও প্রোডাকশন প্রজেক্টে এগুলোর নিখুঁত সিলেকশন ক্রাইটেরিয়া আয়ত্ত করতে পারবে।

### Why Should I Care?
চ্যাটজিপিটি বা জেমিনি যতই শক্তিশালী হোক না কেন, তারা তোমার কোম্পানির ইন্টারনাল পলিসি, কাস্টমারের লাইভ ট্রানজ্যাকশন বা আজ সকালের কোনো সিক্রেট আপডেট জানে না। মডেল ফাইন-টিউনিং করা অত্যন্ত ব্যয়বহুল এবং সময়সাপেক্ষ। আরএজি হলো সবচেয়ে সস্তা, নিরাপদ এবং রিয়েল-টাইম মেথড যা মডেলকে তাৎক্ষণিকভাবে নতুন তথ্য শিখিয়ে কাজ করাতে পারে। আরএজি পাইপলাইন অপ্টিমাইজেশন না জানলে তুমি কখনই এন্টারপ্রাইজ-গ্রেড এআই প্রডাক্ট আর্কিটেক্ট করতে পারবে না।

### Big Picture
আগের চ্যাপ্টারগুলোতে আমরা ভেক্টর ডাটাবেস এবং এম্বেডিংসের গাণিতিক মেকানিজম শিখেছি। এই চ্যাপ্টার থেকে আমাদের শুরু হচ্ছে **RAG (Retrieval-Augmented Generation)** এর মহাবিশ্ব। এখানে শেখা চাংকিং এবং রিট্রিভাল ভৌত অবকাঠামো আমাদের পরবর্তী চ্যাপ্টারের অ্যাডভান্সড হাইব্রিড সার্চ এবং রির‍্যাঙ্কিং বোঝার মূল ভিত্তি।

---

### ১. Hook: পরীক্ষার হলে বই খুলে পরীক্ষা দেওয়ার স্বাধীনতা

কল্পনা করো, তুমি একটি অত্যন্ত কঠিন ফাইনাল পরীক্ষা দিতে বসেছেন। 
* **Closed-Book Exam (ফাইন-টিউনিং বা বেস মডেল):** তোমাকে পরীক্ষার হলে কোনো বই বা খাতা নিতে দেওয়া হলো না। তোমাকে তোমার মস্তিষ্কে সেভ থাকা পুরনো মুখস্থ নলেজ (Trained Weights) ব্যবহার করে সব কঠিন প্রশ্নের উত্তর লিখতে হবে। প্রশ্ন যদি তোমার সিলেবাসের বাইরে আসে, তবে তুমি বানিয়ে ভুল উত্তর (Hallucination) লিখবে।

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

* **Open-Book Exam (RAG):** শিক্ষক তোমাকে পরীক্ষার হলে সম্পূর্ণ বুক এবং কোম্পানির পলিসি ফাইল সাথে নিয়ে বসার অনুমতি দিলে (Open-Book Exam)। তোমার কাজ হলো প্রশ্নটি পড়ে প্রথমে বইয়ের সূচিপত্র ঘেঁটে সঠিক চ্যাপ্টার ও প্যারাগ্রাফটি খুঁজে বের করা (Retrieval), তারপর সেই পৃষ্ঠাটি চোখের সামনে খোলা রেখে নিখুঁত ও সত্যবাদী উত্তর খসড়া করা (Generation)। 

আরএজি (RAG) হলো এলএলএম-এর জন্য ঠিক এই ওপেন-বুক পরীক্ষার মতো। মডেল নিজে কিছু মুখস্থ করে না, সে ভেক্টর ডাটাবেস নামক "বই" থেকে রিলেটেড পাতা খুঁজে এনে উত্তর দেয়।

---

### ২. Core Concepts: আরএজি ও চাংকিং মেকানিজম

একটি পূর্ণাঙ্গ আরএজি আর্কিটেকচার মূলত দুটি আলাদা পাইপলাইনে কাজ করে:

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

#### ক. Ingestion Pipeline (উপাত্ত সংরক্ষণ পাইপলাইন)
এটি একটি অফলাইন বা ব্যাকগ্রাউন্ড প্রসেস।
1. **Document Loading:** পিডিএফ, ওয়ার্ড ফাইল বা ডাটাবেস থেকে র টেক্সট রিড করা।
2. **Chunking (খন্ডন):** টেক্সট ফাইলটি অনেক বড় হলে (যেমন: ৫০ পৃষ্ঠার ম্যানুয়াল) মডেলের কনটেক্সট উইন্ডোতে আটবে না। তাই টেক্সটকে ছোট ছোট খণ্ডে বিভক্ত করা হয়।
3. **Embedding:** প্রতিটি ছোট খণ্ড বা চাঙ্ককে ভেক্টরে রূপান্তর করা।
4. **Vector Database Store:** ভেক্টরগুলোকে ফাস্ট সার্চের জন্য ইনডেক্সিং করে সেভ রাখা।

#### খ. Retrieval & Generation Pipeline (তথ্য সংগ্রহ ও জেনারেশন)
এটি ইউজারের লাইভ রিকোয়েস্ট রান করার সময় চলে।
1. **Retrieve:** ইউজারের প্রশ্নটি এম্বেড করে ভেক্টর ডাটাবেস থেকে টপ $K$ সংখ্যক (যেমন: সেরা ৩টি) রিলেটেড চাঙ্ক খুঁজে আনা।
2. **Augment:** সেই ৩টি চাঙ্ক প্রম্পটের সাথে কনটেক্সট হিসেবে জোড়া লাগানো।
3. **Generate:** এলএলএম মডেল সেই ইনজেক্টেড কনটেক্সট পড়ে ফ্যাট-ভিত্তিক সত্য উত্তর লিখে দেয়।

#### গ. Chunking Strategies (খন্ডন কৌশল)
আরএজি-র সাফল্যের ৮০% নির্ভর করে তুমি কীভাবে ডেটা খণ্ড বা চাঙ্ক করছো তার ওপর:

1. **Character Chunking (ক্যারেক্টার খন্ডন):** প্রতি ৫০০ ক্যারেক্টার পর পর কেটে দেওয়া। 
   * **সমস্যা:** কন্ডিশনাল লাইনের মাঝখানে কেটে যাওয়ায় অর্থ নষ্ট হয়।
2. **Token Chunking (টোকেন খন্ডন):** প্রতি ২০০ টোকেন পর পর কাটা। কস্ট কন্ট্রোলের জন্য ভালো, তবে অর্থগত লস হতে পারে।
3. **Recursive Character Chunking (পুনরাবৃত্তিমূলক খন্ডন):** এটি ইন্ডাস্ট্রির সবচেয়ে প্রিয় ও স্ট্যান্ডার্ড পদ্ধতি। এটি প্রথমে প্যারাগ্রাফ (`\n\n`), তারপর লাইন (`\n`), তারপর স্পেস দেখে ইন্টেলিজেন্টলি কাটে যাতে বাক্যের অর্থ ও প্যারাগ্রাফের পূর্ণতা বজায় থাকে।
4. **Semantic Chunking (অর্থগত খন্ডন):** এটি সবচেয়ে অ্যাডভান্সড পদ্ধতি। এটি পুরো টেক্সটের এম্বেডিংস ভেক্টরের পরিবর্তন পরিমাপ করে। যখনই টেক্সটের টপিক বা মিনিং চেঞ্জ হয় (Cosine distance বাড়ে), সে নতুন চাঙ্ক তৈরি করে।

---

### ৩. Visual Explanation: চাঙ্ক ওভারল্যাপের গুরুত্ব

চাংক করার সময় আমরা সর্বদা দুটি চাঙ্কের মাঝখানে কিছুটা ওভারল্যাপ (Overlap) রাখি। এর মেকানিজমটি নিচে ডায়াগ্রামের মাধ্যমে ভিজ্যুয়ালাইজ করো:

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

* **ওভারল্যাপের সুবিধা:** যদি ওভারল্যাপ না থাকতো, তবে `"He must visit"` শব্দটি মাঝখান থেকে কেটে যেত, ফলে রিট্রিভালের সময় দ্বিতীয় চাঙ্কটি তার পূর্ববর্তী কনটেক্সট হারিয়ে ফেলত।

---

### ৪. Real World Example: Perplexity-র সোর্স সাইটেশন আরএজি

Perplexity.ai বা চ্যাটজিপিটির ব্রাউজিং ফিচার যেভাবে উত্তর জেনারেট করে:

1. **Semantic Chunking:** তারা সার্চ ইঞ্জিন থেকে পাওয়া ৫টি ওয়েব পেজ স্ক্র্যাপ করে সেগুলোর সিমান্টিক চাঙ্ক তৈরি করে।
2. **Cosine Retrieval:** তোমার কুয়্যারির সাথে যে চাঙ্কগুলোর মিল ৯০%-এর বেশি, সেগুলো ছেঁকে নিয়ে প্রম্পটে সাজায়।
3. **Context Injection & Citation:** প্রম্পটের ভেতর কড়া সিস্টেম রুল থাকে: `"Answer only using the context below and cite your sources [1], [2]..."`। এর ফলে এআই হ্যালুসিনেশনহীন নিখুঁত উত্তর ও সাইটেশন প্রডিউস করে।

---

### ৫. Developer Perspective: Recursive Character Splitter ইমপ্লিমেন্টেশন

💻 Developer View

পাইথনে `langchain` লাইব্রেরি ব্যবহার করে কাস্টম রিকিউরসিভ স্প্লিটার ও চাঙ্ক ওভারল্যাপ ডিফাইন করার রিয়েল কোড:

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

# ৪. আউটপুট প্রিন্ট করো
print(f"মূল পলিসির দৈর্ঘ্য: {len(corporate_policy)} ক্যারেক্টার।")
print(f"তৈরি হওয়া মোট চাঙ্ক সংখ্যা: {len(chunks)}\n")

for idx, chunk in enumerate(chunks):
    print(f"Chunk {idx+1} ({len(chunk)} chars):")
    print(f"'{chunk}'")
    print("-" * 30)
```

---

### ৬. Production Perspective: Context Leakage ও সিকিউরিটি ফিল্টার

🏭 Production Reality

রিয়েল এন্টারপ্রাইজ আরএজি প্রোডাকশনে সবচেয়ে বিপজ্জনক রিস্ক হলো **Context Leakage** বা অনধিকার অ্যাক্সেস।

* **Context Leakage:** একজন সাধারণ কাস্টমার চ্যাটবটে এমন প্রশ্ন করল যা কোম্পানির ইন্টারনাল এআই হ্যাক করে কোনো অ্যাডমিনের স্যালারি শিট বা সিক্রেট প্রজেক্টের ভেক্টর রিট্রাইভ করে প্রম্পটে ইনজেক্ট করে ফেলল।
* **সমাধান:** প্রোডাকশন সিস্টেমে প্রতিটি ভেক্টর ইনজেস্ট করার সময় তার মেটাডেটাতে **Access Control List (ACL)** ট্যাগ করে দেওয়া হয় (যেমন: `{"role_allowed": "admin"}`)। কাস্টমার চ্যাট কুয়্যারি রান করার সময় ভেক্টর সার্চ ফোর্সেবলি মেটাডেটা ফিল্টার অ্যাপ্লাই করে যাতে সাধারণ ইউজারের কুয়্যারিতে অ্যাডমিন ডক কোনো অবস্থাতেই রিট্রাইভড না হতে পারে।

---

### ৭. Common Mistakes

🔴 Common Mistake

**ভুল ধারণা:** আরএজি প্রজেক্টে চাঙ্ক সাইজ যত বড় রাখা যাবে, কনটেক্সট তত বেশি মডেলে পৌঁছাবে এবং উত্তর তত ভালো হবে।

**বাস্তবতা:** অতিরিক্ত বড় চাঙ্ক ব্যবহার করলে প্রম্পটের ভেতর অপ্রাসঙ্গিক (Noise/Irrelevant) তথ্য ইনজেক্ট হয়ে যায়, যা এলএলএম-কে বিভ্রান্ত করে। তাছাড়া বড় চাঙ্ক কনটেক্সট উইন্ডোর VRAM ব্লো-আপ ঘটায় এবং ল্যাটেন্সি বৃদ্ধি করে। আরএজি-র গোল্ডেন রুল হলো: **"Retrieve only what is essential (প্রাসঙ্গিক টুকু রিট্রাইভ করো, বেশি নয়)"**।

---

### ৮. Mental Model: স্মার্ট লাইব্রেরিয়ান ও তোতাপাখি জুড়ি

আরএজি পাইপলাইনের মেন্টাল মডেল:

* **Vector DB = স্মার্ট লাইব্রেরিয়ান:** সে পুরো লাইব্রেরির বইয়ের পাতা সূচিপত্র ও মিনিং অনুসারে সাজিয়ে রেখেছে। প্রশ্ন আসার সাথে সাথে সে পারফেক্ট ৫টি পৃষ্ঠা ছিঁড়ে নিয়ে আসে।
* **LLM = বাচাল তোতাপাখি (The Storyteller):** তোতাপাখি নিজে কিছু জানে না, কিন্তু সে অসম্ভব ভালো কথা বলতে পারে। লাইব্রেরিয়ান যখন তাকে সেই ৫টি পৃষ্ঠা দেয়, সে সেই পৃষ্ঠাগুলো লাইভ রিড করে চমৎকার মিষ্টি ও সত্যবাদী ভাষায় উত্তর লিখে দেয়।

---

### ৯. Mini Project: পাইথনে স্ক্র্যাচ থেকে একটি আরএজি (RAG) পাইপলাইন

চলো পাইথনে কাস্টম NumPy ব্যবহার করে কোনো এমএল ফ্রেমওয়ার্ক ছাড়া একটি পূর্ণাঙ্গ মিনি আরএজি রিট্রিভাল ও ইনফারেন্স কনটেক্সট ইনজেক্টর সিস্টেম আর্কিটেক্ট করি।

```python
import numpy as np

# ১. কোম্পানির পলিসি ডাটাবেস (আমাদের বইয়ের পৃষ্ঠা)
docs = [
    "dial *247# to reset your PIN code with NID verification.",
    "for verification failure, visit the nearest bKash center.",
    "bring your original NID copy and active SIM card for biometrics."
]

# ২. মক এম্বেডিংস ডিকশনারি (৩-ডাইমেনশন ভেক্টর)
# [পিন/ভেরিফিকেশন, ফিজিক্যাল ভিজিট/সেন্টার, প্রয়োজনীয় ডকুমেন্ট]
doc_embeddings = np.array([
    [0.9, 0.1, 0.0],  # doc 1: PIN reset
    [0.2, 0.95, 0.1], # doc 2: Visit center
    [0.1, 0.3, 0.95]  # doc 3: Bring documents
])

# ৩. কাস্টমার কুয়্যারি: "NID Verification fail hole kothay jabo?"
query = "NID Verification fail hole kothay jabo?"
# কুয়্যারি ভেক্টর এম্বেডিংস (মক রিপ্রেজেন্টেশন)
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

# ৫. LLM প্রম্পট ইনজেকশন (Augmented Prompt Generation)
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
* **Input:** কাস্টমার কুয়্যারি ভেক্টর এবং ৩-ডাইমেনশন পলিসি এম্বেডিংস।
* **Output:** বেস্ট ম্যাচ ডক রিট্রিভ করে জেনারেট হওয়া ফাইনাল এআই ইনজেকশন প্রম্পট।
* **Why it works:** ভেক্টর সিমিলারিটি কোসাইন মেপে `visit the nearest bKash center` ডকটি নির্ভুলভাবে রিট্রাইভ করেছে এবং প্রম্পটে ইনজেক্ট করেছে।
* **When to use:** কাস্টম আরএজি (RAG) প্রম্পট বিল্ডিং ও রিট্রিভাল পাইপলাইন স্ক্র্যাচ থেকে ডিজাইন করার জন্য।

---

### ১০. Interview Questions

#### Beginner
1. **প্রশ্ন:** আরএজি (RAG) কী এবং এআই চ্যাটবটে এটি কেন ব্যবহার করা হয়?
   * **উত্তর:** RAG হলো Retrieval-Augmented Generation। এটি মডেলের ইন্টারনাল ওয়েটসের ওপর নির্ভর না করে এক্সটার্নাল নলেজ বেস (ভেক্টর ডাটাবেস) থেকে রিয়েল-টাইম সঠিক তথ্য খুঁজে এনে প্রম্পটের সাথে ইনজেক্ট করে উত্তর জেনারেট করার মেথড। এটি হ্যালুসিনেশন কমাতে ও কোম্পানির কাস্টম ডেটা মডেলে ইন্টিগ্রেট করতে সাহায্য করে।

#### Intermediate
2. **প্রশ্ন:** Recursive Character Chunking কেন সাধারণ ক্যারেক্টার চাংকিংয়ের চেয়ে বেশি কার্যকর?
   * **উত্তর:** সাধারণ ক্যারেক্টার চাংকিং যেকোনো জায়গায় কন্ডিশনাল লাইনের মাঝখানে কেটে ফেলে বাক্যের অর্থ নষ্ট করে। কিন্তু Recursive Character Splitter নির্দিষ্ট অগ্রাধিকার তালিকায় প্যারাগ্রাফ, লাইন এবং স্পেস দেখে ইন্টেলিজেন্টলি কাটে, যা প্রতিটি খণ্ডের অর্থগত পূর্ণতা অক্ষুণ্ণ রাখে।

#### Advanced
3. **প্রশ্ন:** এন্টারপ্রাইজ আরএজি প্রোডাকশনে "Document Leakage / Authorization Bypass" কীভাবে প্রতিহত করা হয়?
   * **উত্তর:** এটি প্রতিহত করতে ডেটা ইনজেস্ট করার সময় প্রতিটি ভেক্টর ডকের মেটাডেটাতে **Access Control List (ACL)** ট্যাগ করে দেওয়া হয়। ইউজার চ্যাট কুয়্যারি রান করার সময় ভেক্টর সার্চ কুয়েরিতে বাধ্যতামূলক ফিল্টার অ্যাপ্লাই করা হয় যাতে ইউজারের ইউজার-রোল আইডির বাইরে কোনো সিক্রেট ডাটাবেস ভেক্টর ইনজেক্ট না হতে পারে।

---

### ১১. Chapter Summary
* **RAG** ক্লোজড-বুক এআই মডেলকে একটি ওপেন-বুক ফ্যাট-বেসড এআই সিস্টেমে রূপান্তর করে।
* **Ingestion Pipeline** অফলাইনে চাংকিং ও এম্বেডিংস করে ভেক্টর ডাটাবেস প্রস্তুত করে।
* **Recursive Chunking** এবং **Overlap** ডকের সীমানাগত অর্থ রক্ষা করার জন্য সবচেয়ে গুরুত্বপূর্ণ।
* প্রোডাকশন সিস্টেমে ডেটা সিকিউরিটি নিশ্চিত করতে মেটাডেটা **ACL Filtering** ব্যবহার করা আবশ্যিক।

---

### ১২. What's Next
দারুণ! আমরা সফলভাবে আরএজি-র কোর ফাউন্ডেশন এবং চাংকিং মেকানিক্স জয় করে ফেলেছি। পরবর্তী চ্যাপ্টারে আমরা এই রিট্রিভাল পাইপলাইনকে আরও নিখুঁত ও প্রোডাকশন-রেডি করার অ্যাডভান্সড সোপান নিয়ে আলোচনা করব: **Chapter 14: Advanced Retrieval, Hybrid Search & Re-ranking**। HyDE, প্যারেন্ট-ডকুমেন্ট রিট্রিভাল, BM25 স্পার্স সার্চ ও রির‍্যাঙ্কিং কীভাবে আরএজি-র এক্যুরেসি ৯৯%-এ নিয়ে যায়, তা আমরা বিস্তারিত শিখব।

---
**Chapter 13 সমাপ্ত।**
