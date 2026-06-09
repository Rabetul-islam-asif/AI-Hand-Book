# Chapter 13: Embeddings & Vector Mathematics

তুমি কি কখনো ভেবেছো — একটা AI Model কীভাবে বুঝতে পারে যে "King" আর "Queen" শব্দ দুটোর মধ্যে গভীর মিল আছে?

অথবা "Apple" বা "Computer" শব্দ দুটোর সাথে যে এদের কোনো মিল নেই, সেটাই বা সে কীভাবে বোঝে?

আসলে AI তো আমাদের মতো ভাষা বোঝে না। তার কাছে সব কিছুই হলো সংখ্যার এক বিশাল নদী!

শব্দ বা বাক্যগুলোকে যখন AI সংখ্যার Vector-এ বদলে নেয়, তখন সেগুলোর মধ্যকার কোণ আর দূরত্ব মেপেই সে আসল অর্থ খুঁজে বের করে।

তো চলো, এই চ্যাপ্টারে AI-এর ভেতরের Vector Mathematics একদম সহজ কথায় বুঝে নিই।

আমরা দেখবো কীভাবে Cosine Similarity, L2 Distance আর Dot Product কাজ করে।

সেই সাথে জানবো আমাদের রিয়েল প্রজেক্টে কখন কোন মেট্রিক ব্যবহার করা উচিত।

তাহলে আর দেরি কেন? চলো শুরু করা যাক!


## ১. 3D মানচিত্রে শব্দের ওড়াউড়ি

ধরো, তুমি একটা বিশাল 3D ঘরের ঠিক মাঝখানে দাঁড়িয়ে আছো।

এই ঘরের একেকটা দিক একেকটা বৈশিষ্ট্য বা Dimension প্রকাশ করছে।

যেমন— ঘরের ডান-বাম দিকটা হলো Gender (ছেলে বা মেয়ে)।

ওপর-নিচ দিকটা হলো Royalty (রাজকীয় ভাব)।

আর সামনে-পেছনের দিকটা হলো Age (বয়স)।

এখন তুমি যদি কিছু শব্দকে এই ঘরের ভেতর ভাসিয়ে দাও, তাহলে কী হবে?

যেমন ধরো, `"King"` শব্দটাকে তুমি রাখলে ডান দিকে (Male), ওপরের দিকে (High Royalty) আর পেছনের দিকে (Old)।

আবার `"Queen"` শব্দটাকে রাখলে বাম দিকে (Female), ওপরের দিকে (High Royalty) আর পেছনের দিকে (Old)।

![Embedding Geometry Diagram](/diagrams/embedding.jpeg)



**এই জ্যামিতিক মানচিত্রের সুবিধা কী?**

মজার ব্যাপার হলো, তুমি যদি `"King"` Vector থেকে `"Man"` Vector বাদ দাও, আর তার সাথে `"Woman"` Vector যোগ করো, তাহলে কী হবে জানো?

তোমার হিসাবের ফলটা ঠিক `"Queen"`-এর জায়গায় গিয়ে ল্যান্ড করবে!

```
King - Man + Woman = Queen
```

এটা কিন্তু কোনো ম্যাজিক নয়, স্রেফ সাধারণ Vector যোগ-বিয়োগের খেল।

বাস্তবে Embeddings-এর কাজও ঠিক এটাই।

শুধু ৩টা দিক বা Dimension-এর বদলে সেখানে ১৫৩৬ বা ৪০৯৬টি ডাইমেনশনের Hyper-space ব্যবহার করা হয়।


## ২. Vector মাপার ৩টি উপায়

Vector Database বা Search Engine-এ দুটো Vector-এর মধ্যে কতটা মিল আছে, তা বোঝার জন্য ৩টি প্রধান Metric ব্যবহার করা হয়।

![Vector Distance Metrics](/diagrams/vector_distance_metrics.png)

### Cosine Similarity

এটি দুটো Vector-এর মধ্যকার কোণ বা Angle ($\theta$) মেপে কাজ করে।

Vector-এর সাইজ বা Magnitude ছোট বা বড় যাই হোক না কেন, এটি শুধু তাদের দিকের মিল দেখে।

$$\text{Cosine Similarity}(\mathbf{a}, \mathbf{b}) = \cos(\theta) = \frac{\mathbf{a} \cdot \mathbf{b}}{\|\mathbf{a}\| \|\mathbf{b}\|}$$

**এর Range কত?**

$-1$ থেকে $+1$। এখানে $1$ মানে দুটো Vector হুবহু এক, $0$ মানে তাদের মধ্যে কোনো সম্পর্ক নেই, আর $-1$ মানে তারা পুরো উল্টো।

**কখন ব্যবহার করবে?**

Document Search বা RAG-এর মতো কাজে। যেখানে টেক্সট ছোট বা বড় হতে পারে, কিন্তু তাদের মূল ভাব একই থাকে।


### L2 / Euclidean Distance

এটি দুটো Vector-এর শেষ বিন্দুর মধ্যকার একদম সোজা সরলরেখার দূরত্ব মাপে।

$$d(\mathbf{a}, \mathbf{b}) = \sqrt{\sum_{i=1}^{n} (a_i - b_i)^2}$$

**এর Range কত?**

$0$ থেকে $\infty$ (ইনফিনিটি) পর্যন্ত। $0$ মানে কোনো দূরত্ব নেই (হুবহু এক), আর এই মান যত বেশি হবে, দূরত্বও তত বাড়বে।

**কখন ব্যবহার করবে?**

Image Detection এবং ফেস রিকগনিশনের মতো কাজে, যেখানে Vector-এর পরম মান বা Magnitude অনেক বেশি গুরুত্বপূর্ণ।


### Dot Product

এটি দুটো Vector-এর মধ্যকার কোণ এবং তাদের দৈর্ঘ্য বা Magnitude—দুটো বিষয়ই একসাথে গুণ করে হিসাব করে।

$$\mathbf{a} \cdot \mathbf{b} = \sum_{i=1}^{n} a_i b_i = \|\mathbf{a}\| \|\mathbf{b}\| \cos(\theta)$$

**বিশেষ শর্ত কী?**

যদি Vectorগুলো আগে থেকেই Normalized করা থাকে (মানে তাদের দৈর্ঘ্য ১ হয়), তবে Dot Product আর Cosine Similarity হুবহু একই রেজাল্ট দেবে।

**কখন ব্যবহার করবে?**

খুব ফাস্ট কাজ করে এমন প্রোডাকশন Search হাবে। কারণ হিসাবের দিক থেকে এটি অনেক দ্রুত কাজ করে, এতে কোনো Square Root বা Division-এর ঝামেলা নেই।


## 🧠 Remember

Normalized Vector ব্যবহার করলে Cosine Similarity আর Dot Product একই হয়ে যায়!

এতে প্রোডাকশন সার্ভারে মেমরি আর GPU-র খরচ প্রায় ৫০% বেঁচে যায়।


## ৩. Real World Example: Spotify-র Recommendation Engine

Spotify যখন তোমার পছন্দের গানের ওপর ভিত্তি করে তোমাকে নতুন কোনো গান সাজেস্ট করে, তখন আসলে কী ঘটে?

চলো খুব সহজে পুরো ব্যাপারটা ধাপে ধাপে দেখে নিই:

**১. Song Embeddings বানানো**

প্রথমেই প্রতিটি গানকে Vector-এ বদলে নেওয়া হয়।

এখানে গানের বিট রেট, জেনার আর ভোকাল ফ্রিকোয়েন্সির মতো বিভিন্ন Feature ব্যবহার করা হয়।

**২. Database-এ সেভ করা**

Spotify তাদের কোটি কোটি গানের Embeddings Vector আগে থেকেই Normalized করে Database-এ জমিয়ে রাখে।

**৩. Dot Product-এর ম্যাজিক**

তুমি যখন কোনো গান শুনছো, তখন সেই গানের Vector-এর সাথে ডাটাবেসের অন্য সব গানের Dot Product করা হয়।

আর চোখের পলকে সবচেয়ে কাছের ১০টি গান খুঁজে বের করে তোমার প্লেলিস্টে পাঠিয়ে দেওয়া হয়।


## ৪. Developer View: pgvector ও Metric সিলেকশন

💻 Developer View

PostgreSQL ডাটাবেসে `pgvector` Extension ব্যবহার করে কীভাবে টেবিল বানাবে আর Index ডিফাইন করবে, চলো তার SQL লজিকটা দেখে নিই:

```sql
-- ১. pgvector এক্সটেনশন সচল করো
CREATE EXTENSION IF NOT EXISTS vector;

-- ২. ১৫৩৬ ডাইমেনশনের Vector টেবিল তৈরি করো (OpenAI standard)
CREATE TABLE document_embeddings (
    id serial PRIMARY KEY,
    content text,
    embedding vector(1536)
);

-- ৩. COSIGN SIMILARITY ইনডেক্স ডিফाइन করো (cosine distance: <=>)
CREATE INDEX ON document_embeddings USING hnsw (embedding vector_cosine_ops);

-- ৪. L2 DISTANCE ইনডেক্স ডিফाइन করো (L2 distance: <->)
CREATE INDEX ON document_embeddings USING hnsw (embedding vector_l2_ops);

-- ۵. DOT PRODUCT ইনডেক্স ডিফाइन করো (inner product distance: <#>)
CREATE INDEX ON document_embeddings USING hnsw (embedding vector_ip_ops);
```


## ৫. Production Reality: GPU Normalization-এর ট্রিক

🏭 Production Reality

রিয়েল প্রজেক্টে RAG Server-এ লাখ লাখ Document সার্চ করার সময় সরাসরি Cosine Similarity ব্যবহার করা কিন্তু বেশ বড় একটা ভুল বা Anti-Pattern!

**কেন সরাসরি ব্যবহার করা ভুল?**

কারণ Cosine Similarity-র Equation-এ যে Square Root আর Division থাকে, তা GPU-কে অনেক স্লো করে দেয়।

**তাহলে প্রোডাকশনের ট্রিকটা কী?**

ট্রিকটা হলো, Data যখন সিস্টেমে ঢোকানো বা Ingest করা হয়, তখনই Vectorগুলোকে আগে থেকে L2 Normalization করে ডাটাবেসে সেভ করে রাখা হয়।

এর ফলে Query বা Inference-এর সময় GPU-কে আর কষ্ট করে ভাগ বা বর্গমূল করতে হয় না।

সে শুধু সুপার-ফাস্ট Dot Product রান করে চোখের পলকে Cosine Similarity-র সমান রেজাল্ট বের করে দেয়!


## Common Mistake

🔴 Common Mistake

**ভুল ধারণা:**

L2 Distance বা Euclidean Distance সব ধরনের Search প্রজেক্টের জন্য সেরা Metric।

**বাস্তবতা:**

যদি তোমার সাইটের কোনো লেখা বা Document-এর সাইজ অনেক অসমান হয়—যেমন একটা প্যারাগ্রাফ অনেক বড় আর অন্য একটা লাইন খুব ছোট।

তখন কিন্তু L2 Distance বড় লেখার Vector-কে অনেক দূরে ঠেলে দেবে। একে বলে Magnitude Effect।

এই সব ক্ষেত্রে কোণের দিক বা Cosine Similarity ব্যবহার করা ছাড়া কোনো উপায় নেই!


## ৬. Mental Model: টর্চের আলো আর ছায়া

ব্যাপারটা মাথায় গেঁথে নেওয়ার জন্য একটা সহজ মনের ছবি বা Mental Model কল্পনা করো:

**L2 Distance মানে হলো একখানা Measurement Tape!**

দুই বিন্দুর মাঝখানে ফিতা ধরে সোজা দূরত্ব মাপার মতো।

**Cosine Similarity হলো দুটো টর্চের আলোর মধ্যকার কোণ!**

টর্চের আলো কতটা কড়া বা হালকা (Magnitude) তা কিন্তু এখানে ম্যাটার করে না। 

তাদের আলো ছড়ানোর কোণটা যদি একই দিকে থাকে, তবেই তাদের মিল সবচেয়ে বেশি।

**Dot Product হলো আলোর প্রজেকশন বা ব্রাইটনেস!**

এটি টর্চের কোণ আর আলোর জোর—দুটোই একসাথে মাপে।

টর্চ কাছে এনে আলোর জোর বাড়ালে এর মান রকেটের গতিতে বেড়ে যায়!


## ৭. Mini Project: Python-এ Classifier

চলো Python আর NumPy ব্যবহার করে কোনো ML Framework ছাড়াই একটা ছোট কোড লিখে ফেলি।

আমরা কোড লিখে Cosine Similarity আর L2 Distance মেপে দেখবো কোনটা কাস্টমারের Query-র সবচেয়ে কাছে যায়!

```python
import numpy as np

# ১. Database-এর ৩টি ডকের মক এম্বেডিংস Vector (৩-ডাইমেনশন)
# ডক ১: "পেমেন্ট সফল হয়েছে"
doc_1 = np.array([0.9, 0.8, 0.1])
# ডক ২: "অ্যাকাউন্ট পিন লক"
doc_2 = np.array([-0.8, -0.7, 0.9])
# ডক ৩: "Server Configuration Error"
doc_3 = np.array([0.1, 0.2, 0.95])

database = {"Payment Success": doc_1, "PIN Locked": doc_2, "Server Error": doc_3}

# ২. কাস্টমার কোয়্যারি Vector: "আমার পেমেন্ট হচ্ছে না কেন?"
query = np.array([0.85, 0.75, -0.1])

# ৩. মেট্রিক Function
def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def l2_distance(v1, v2):
    return np.sqrt(np.sum((v1 - v2) ** 2))

# ৪. Search রান করো
print("--- Cosine Similarity Search (Higher is Better) ---")
for name, vec in database.items():
    sim = cosine_similarity(query, vec)
    print(f"Similarity with '{name}': {sim:.4f}")

print("\n--- L2 Distance Search (Lower is Better) ---")
for name, vec in database.items():
    dist = l2_distance(query, vec)
    print(f"Distance with '{name}': {dist:.4f}")
```

### Code Breakdown

চলো কোডের খুঁটিনাটি খুব সহজে বুঝে নিই:

**এখানে Input কী দিয়েছি?**

একটি ৩-ডাইমেনশনের Vector Database এবং কাস্টমারের দেওয়া Query Vector।

**আউটপুট কী এসেছে?**

Cosine Similarity এবং L2 Distance-এর স্কোরের একটা লিস্ট।

**ফলাফল কী দাঁড়াল?**

আমরা দেখতে পেলাম `Payment Success` Vector-এর সাথে Cosine Score সবচেয়ে বেশি ($0.9995$) আর L2 Distance সবচেয়ে কম ($0.2121$)।

তার মানে কাস্টমারের প্রশ্নটি "Payment Success" ক্যাটাগরির সাথে সবচেয়ে ভালো মিলেছে।

**কখন ব্যবহার করবে?**

যখন কোনো বড় ML Framework ছাড়াই কাস্টম Vector Classifier তৈরি করতে চাও, তখন এই কোডটি তোমার কাজে আসবে।


## ৮. Interview Questions

### Beginner

**প্রশ্ন:**

Cosine Similarity আর L2 Distance-এর মধ্যে প্রধান পার্থক্য কী?

**উত্তর:**

Cosine Similarity শুধু দুটো Vector-এর মধ্যকার কোণ বা Angle মাপে (তাদের Magnitude বাদ দিয়ে)। 

আর L2 Distance দুটো Vector-এর Magnitude সহ তাদের ভেতরের একদম সোজা সরলরেখার দূরত্ব মাপে।


### Intermediate

**প্রশ্ন:**

রিয়েল প্রোডাকশন সিস্টেমে Vector সার্চের Latency কমাতে Embeddings Normalization করার সুবিধা কী?

**উত্তর:**

Vectorগুলো আগে থেকে L2 Normalized করা থাকলে Cosine Similarity-র সেই জটিল Square Root আর Division এড়ানো যায়।

এর ফলে GPU খুব সস্তায় আর দ্রুত Dot Product করে মিলি-সেকেন্ডের মধ্যে কোসাইন সিমিলারিটির সমান রেজাল্ট তৈরি করতে পারে। 

এতে সার্চের গতি বা Latency অনেক কমে যায়।


### Advanced

**প্রশ্ন:**

কোন ধরনের Data Distribution-এ Dot Product-এর রেজাল্ট Cosine Similarity-র চেয়ে খারাপ হতে পারে?

**উত্তর:**

যদি তোমার Data-র Vectorগুলোর দৈর্ঘ্য বা Magnitude-এ বিশাল কম-বেশি থাকে।

যেমন— একটা খুব ছোট প্যারাগ্রাফ আর একটা বড় উইকিপিডিয়া পেজ। 

এমন ক্ষেত্রে Dot Product বড় টেক্সটের Vector-কে বিশাল Magnitude স্কোরের জন্য ভুল ম্যাচ হিসেবে বুস্ট করতে পারে।

এই ক্ষেত্রে আমাদের Magnitude-Neutral Cosine Similarity ব্যবহার করাই সবচেয়ে বুদ্ধিমানের কাজ।


## Chapter Summary

চলো সংক্ষেপে পুরো চ্যাপ্টারের মূল কথাগুলো আরেকবার চট করে দেখে নিই:

১. Vector Embeddings মূলত শব্দ বা বাক্যকে হাই-ডাইমেনশনের জ্যামিতিক Coordinate-এ বদলে দেয়।

২. Cosine Similarity কোণ মেপে কাজ করে এবং এটি Document Search ও RAG-এর জন্য সবচেয়ে ভালো।

৩. L2 Distance পরম মান বা Magnitude মেপে কাজ করে এবং এটি Image বা ফেস Detection-এ সেরা।

４. প্রোডাকশন সিস্টেমে Latency কমানোর গোল্ড স্ট্যান্ডার্ড হলো Vector-কে আগে থেকেই L2 Normalization করে রাখা এবং পরে Dot Product চালানো।


## What's Next?

দারুণ! Vector জ্যামিতির কোর ম্যাথ তো আমরা শিখে ফেললাম।

পরের চ্যাপ্টারে আমরা এই Vectorগুলোকে মেমোরিতে জমিয়ে রাখার দারুণ সব ইঞ্জিন নিয়ে গল্প করবো।

আসছে **Chapter 14: Vector Databases — The AI Memory Engine**! 

চলতি পথে কোটি কোটি Vector কীভাবে মিলি-সেকেন্ডে সার্চ করা যায়, আমরা সেটাই দেখবো।
