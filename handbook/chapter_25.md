# Chapter 25: Blueprint 2 — Enterprise PDF Search Engine (pgvector + Semantic Chunking)

---

### Chapter Goal
এই চ্যাপ্টারের মূল লক্ষ্য হলো একটি Enterprise-Grade High-Performance পিডিএফ Document Search Engine (RAG) নিজের হাতে Architect করা। আমরা আগের ক্যারেক্টার বা Token চাঙ্কিংয়ের সীমাবদ্ধতা ভেঙে আধুনিক Semantic Chunking (Semantic Chunking) Implement করবো, Postgres-এর এক্সটেনশন pgvector ব্যবহার করে Vector Database অপ্টিমাইজ করবো এবং একটি সম্পূর্ণ Project Architecture দাঁড় করাবো যা নির্ভুলভাবে হাজার পৃষ্ঠার রিলেভেন্ট টেক্সট খুঁজে এনে সেকেন্ডে উত্তর Produce করতে পারে।

### Why Should I Care?
বেশিরভাগ Developer যখন আরএজি (RAG) বানান, তারা পিডিএফ রিডার দিয়ে টেক্সট রিড করে প্রতি ৫০০ ক্যারেক্টার পর পর র্যান্ডমলি কেটে (Chunk) Vector ডাটাবেসে সেভ করে। এর ফলে অনেক সময় বাক্যের মূল অর্থ বা ইনফরমেশন মাঝখান থেকে কেটে দুই টুকরো হয়ে ভিন্ন চাঙ্কে চলে যায়, যা Model-এর Hallucination বহুগুণ বাড়ায়। প্রোডাকশন লেভেলে perfect Document ম্যাচিংয়ের জন্য ডাইনামিক Semantic স্লিটিং এবং রি-র‍্যাঙ্কিং পাইপলাইন শেখা খুব জরুরি।

### Big Picture
এটি আমাদের বাস্তব Project Blueprint লেয়ারের দ্বিতীয় ফ্ল্যাগশিপ মাইলফলক। আগের চ্যাপ্টারে আমরা চ্যাট Memory Ecosystem তৈরি করা শিখেছি। এই চ্যাপ্টারে আমরা AI Companyর সবচেয়ে ডিমান্ডিং সার্ভিস— মানে এন্টারপ্রাইজ প্রাইভেট নলেজ বেস Search Engine বানানোর সম্পূর্ণ রানিং Source Code ও Architecture দেখবো।

---

### ১. The Problem: র্যান্ডম স্লিটিংয়ের ট্র্যাজেডি ও Hallucination

চলো একটি রিয়েল-ওয়ার্ল্ড Companyর পলিসি Document-এর উদাহরণ দেখি:
*"Companyর নিয়ম অনুযায়ী, যদি কোনো Developer পর পর ৩ দাও অফিসে লেট করে ঢোকে, **[৫০০ ক্যারেক্টার লিমিট শেষ! এখানে কেটে গেল]** তবে তার ওই মাসের বোনাস থেকে ১০% জরিমানা কাটা হবে।"*

তুমি যদি ফিক্সড ক্যারেক্টার স্প্লিটার (যেমন `RecursiveCharacterTextSplitter`) ব্যবহার করো, তবে চাঙ্কগুলো এমন হবে:
* **Chunk 1:** *"Companyর নিয়ম অনুযায়ী, যদি কোনো Developer পর পর ৩ দাও অফিসে লেট করে ঢোকে..."* (এখানে কোনো শাস্তির কথা উল্লেখ নেই!)
* **Chunk 2:** *"তবে তার ওই মাসের বোনাস থেকে ১০% জরিমানা কাটা হবে।"* (এখানে কেন জরিমানা কাটা হচ্ছে তার কোনো কারণ উল্লেখ নেই!)

ইউজার যখন জিজ্ঞেস করবে, *"অফিসে লেট করলে কী Penalty দেওয়া হয়?"* — Model সঠিক রিলেভেন্ট চাঙ্ক দুটি একসাথে মেলাতে পারবে না এবং উত্তর দেবে: *"অফিসে লেট করার কোনো নির্দিষ্ট Penalty খুঁজে পাওয়া যায়নি।"* একেই বলে আরএজি-র বিপর্যয় বা **Context Fragmenting**।

#### প্রোডাকশন সলিউশন: Semantic Chunking (Semantic Chunking)
Semantic Chunking ফিক্সড লেন্থের উপর নির্ভর করে না।
* **Mechanism:** এটি প্রথমে বাক্যগুলোকে আলাদা করে এবং প্রতিটি পাশাপাশি বাক্যের Embeddings Vector-এর মধ্যকার দূরত্ব (Cosine Distance) পরিমাপ করে।
* **স্লিটিং পয়েন্ট:** যদি দেখা যায় বাক্য ৩ এবং বাক্য ৪ এর মধ্যে অর্থ বা বিষয়ের বিশাল পরিবর্তন ঘটেছে (যেমন ৯০% কোসাইন ডিস্ট্যান্স ড্রপ), তবে System বুঝে নেয় যে এখানে Paragraph বা বিষয়বস্তু বদলে গেছে। সে সাথে সাথে সেখানে স্লিটিং বা ডাইনামিক বাউন্ডারি কেটে দেয়, যাতে প্রতিটি চাঙ্ক সম্পূর্ণ স্বাধীন ও অর্থপূর্ণ থাকে।

[VISUAL]
Title: Character Splitter vs. Semantic Chunking
Illustration: Rigid fixed-character slice lines vs. dynamic gap threshold slicing based on similarity vectors
Placement: After Hook Section
Purpose: Show why Semantic Chunking provides 100% complete contexts.

```
Fixed-Character Splitter (Rigid & blind):
"We love AI engineering. [--- Slice ---] It is very fun and robust." (Splits mid-context)

Semantic Chunking (Dynamic & intelligent):
Sentence 1: "We love AI engineering."
                                         ◄─── Cosine Sim = 0.94 (Keep together)
Sentence 2: "It is very fun and robust."
                                         ◄─── Cosine Sim = 0.12 (SHARP DROP! Dynamic Slice Here ──✂──)
Sentence 3: "Postgres is a SQL database."
```

---

### ২. Core Concepts: আরএজি Data লেয়ারের মূল চালিকাশক্তি

#### ক. Postgres pgvector (রিলেশনাল Database-এর AI Engine)
pgvector হলো একটি ওপেন-সোর্স এক্সটেনশন যা Postgres ডাটাবেসকে সরাসরি হাই-ডাইমেনশনাল Vector Embeddings স্টোর এবং কুয়েরি করার ক্ষমতা দেয়।
* **কেন এটি সেরা প্রোডাকশন চয়েস:** কারণ তোমাকে আলাদা করে কোনো নতুন Vector Database (যেমন Pinecone বা Chroma) হোস্ট করতে হয় না। তোমার রিলেশনাল ইউজারের Data এবং তাদের Document-এর Vector Data একই Postgres ডাটাবেসে খুব সুরক্ষিত থাকে এবং তুমি মেটাডাটা দিয়ে ফাস্ট SQL কুয়েরি চালাতে পারো।
* **Indexিং:** pgvector মূলত দুটি Indexিং সাপোর্ট করে:
  * **IVFFlat:** দ্রুত সার্চের জন্য Clustering Loop তৈরি করে।
  * **HNSW (Hierarchical Navigable Small World):** এটি আধুনিক গ্রাফ-ভিত্তিক Indexিং। এটি IVFFlat এর চেয়ে ৩ গুণ বেশি ফাস্ট এবং প্রোডাকশনে রি-কল রেট বা perfect Document ম্যাচিং স্পীড প্রায় ১০০% নিশ্চিত করে।

#### খ. Hybrid Search (হাইব্রিড সার্চের মেলবন্ধন)
শুধু Vector Embeddings Search অনেক সময় ব্র্যান্ড নাম বা নির্দিষ্ট সিরিয়াল নাম্বারের ক্ষেত্রে ফেইল করে। তাই প্রোডাকশনে আমরা **Hybrid Search** ব্যবহার করি:
* **Dense Retrieval (Semantic):** Vector সিমিলারিটি দিয়ে অর্থ বোঝে।
* **Sparse Retrieval (Keyword):** Classical BM25 বা Postgres `tsvector` দিয়ে নির্দিষ্ট কিওয়ার্ড (যেমন: *"X-230 Pro"* বা *"Rahim"*) ম্যাচিং করায়।
* **RRF (Reciprocal Rank Fusion):** এই দুটি সার্চের Output স্কোর ফিউশন বা মার্জ করে টপ ৫টি perfect Document Produce করে।

---

### ৩. Visual Explanation: HNSW গ্রাফ Vector নেটওয়ার্ক

HNSW Index কীভাবে কাজ করে তার Architecture geometric গ্রাফে দেখে নাও:

```
    [ Layer 2 (Express Nodes) ] ───────► [ Jump Node A ] ──────────┐
                                               │                   │
                                               ▼                   ▼
    [ Layer 1 (Medium Density) ] ───────► [ Node B1 ] ─────────► [ Node B2 ]
                                               │                   │
                                               ▼                   ▼
    [ Layer 0 (Dense Vector Space) ] ───► [ Local Neighbor ] ──► [ Destination Vector ]
```

HNSW মূলত মাল্টি-লেয়ার হাইওয়ে বা এক্সপ্রেসওয়ের মতো কাজ করে। এটি প্রথমে বড় বড় জাম্প দিয়ে Vector-এর কাছাকাছি জোনে পৌঁছায় এবং এরপর লোকাল নেইবার গ্রাফে ট্রাভার্স করে সেকেন্ডে একদম perfect Vector ম্যাচিং লক করে।

---

### ৪. Real World Example: ব্যাংকের লোন পলিসি Search

একজন লোন অফিসার ব্যাংকের secretীয় Document Search করতে চান:
*"গ্রাহকের বয়স ৬০ এর বেশি হলে, সুদের হার ১% বেশি হবে এবং ৫ লাখের বেশি লোনে অবশ্যই নোটারি বন্ড লাগবে।"*

* **ভুল Chunking:** অফিসার কুয়েরি করলে: *"৬০ বছর বয়সীদের লোন পলিসি কী?"* চাঙ্ক মাঝখান থেকে কেটে যাওয়ায় System লোন সুদের মান ১% খুঁজে পেলো, কিন্তু নোটারি বন্ডের ইনফরমেশন ফিল্টার আউট হয়ে গেল।
* **Semantic আরএজি:** Semantic Chunking পুরো অনুচ্ছেদটিকে একটি সলিড চাঙ্ক হিসেবে ক্যাশ রাখায় অফিসারকে এক সাথে সুদের হার এবং নোটারি বন্ডের প্রয়োজনীয়তা—উভয় ইনফরমেশনই perfect রেসপন্সে প্রেজেন্ট করলো।

---

### ৫. Developer Perspective: Postgres pgvector + Semantic Chunking সম্পূর্ণ পাইপলাইন Implementation

💻 Developer View

চলো পাইথনে Code করে একটি রিয়েল-ওয়ার্ল্ড পিডিএফ Semantic Chunking Loop এবং pgvector Indexিং ডেপ্লয় করার সম্পূর্ণ Source Code Architect করি।

```python
import os
import numpy as np
import psycopg2
from psycopg2.extras import register_vector
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity

# ১. এনভায়রনমেন্ট ও ক্লায়েন্ট সেটআপ
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
client = OpenAI()

# ২. ডাইনামিক Semantic চাঙ্কার (Semantic Chunking Library)
def semantic_chunk_text(text, threshold=0.85):
    # বাক্য স্প্লিট
    sentences = [s.strip() + "." for s in text.split(".") if len(s.strip()) > 5]
    if len(sentences) < 2:
        return sentences
        
    # প্রতিটি বাক্যের এম্বেডিংস জেনারেট করো
    print(f"Generating embeddings for {len(sentences)} sentences...")
    resp = client.embeddings.create(input=sentences, model="text-embedding-3-small")
    embeddings = [e.embedding for e in resp.data]
    
    # পাশাপাশি বাক্যের কোসাইন সিমিলারিটি বের করো
    chunks = []
    current_chunk = sentences[0]
    
    for i in range(len(sentences) - 1):
        vec1 = np.array(embeddings[i]).reshape(1, -1)
        vec2 = np.array(embeddings[i+1]).reshape(1, -1)
        sim = cosine_similarity(vec1, vec2)[0][0]
        
        # যদি সিমিলারিটি থ্রেশহোল্ডের নিচে ড্রপ করে, নতুন চাঙ্ক করো
        if sim < threshold:
            chunks.append(current_chunk)
            current_chunk = sentences[i+1]
        else:
            current_chunk += " " + sentences[i+1]
            
    chunks.append(current_chunk)
    return chunks

# ৩. Postgres pgvector Database ইন্টিগ্রেশন
def store_and_search_chunks(chunks, query_text):
    # Postgres কানেকশন
    conn = psycopg2.connect(
        host="localhost",
        database="enterprise_rag",
        user="postgres",
        password="yourpassword",
        port="5432"
    )
    cur = conn.cursor()
    
    # pgvector এক্সটেনশন এনাবল ও Vector রেজিস্টার
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    conn.commit()
    register_vector(conn)
    
    # টেবিল তৈরি (Dimension = 1536 for text-embedding-3-small)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS doc_chunks (
            id serial PRIMARY KEY,
            content text,
            embedding vector(1536)
        );
    """)
    conn.commit()
    
    # Data ইনসার্ট Loop
    print(f"Storing {len(chunks)} semantic chunks into Postgres pgvector...")
    for chunk in chunks:
        # Generate chunk embedding
        resp = client.embeddings.create(input=chunk, model="text-embedding-3-small")
        emb = resp.data[0].embedding
        
        cur.execute("INSERT INTO doc_chunks (content, embedding) VALUES (%s, %s);", (chunk, emb))
    conn.commit()
    
    # HNSW ইনডেক্স তৈরি (For fast production cosine search)
    cur.execute("CREATE INDEX IF NOT EXISTS doc_hnsw_idx ON doc_chunks USING hnsw (embedding vector_cosine_ops);")
    conn.commit()
    
    # ৪. সিমিলারিটি কোসাইন কুয়েরি রান করো (RAG Retrieval)
    print(f"\nSearching for query: '{query_text}'")
    query_resp = client.embeddings.create(input=query_text, model="text-embedding-3-small")
    query_emb = query_resp.data[0].embedding
    
    # Cosine distance operator '<=>' ব্যবহার করে টপ ৩টি রিলেভেন্ট চাঙ্ক রিট্রিভ
    cur.execute("SELECT content, 1 - (embedding <=> %s) AS similarity FROM doc_chunks ORDER BY embedding <=> %s LIMIT 3;", (query_emb, query_emb))
    results = cur.fetchall()
    
    print("\n--- RAG SEARCH RESULTS ---")
    for idx, row in enumerate(results):
        print(f"Match {idx+1} [Similarity: {row[1]:.4f}]:\n{row[0]}\n")
        
    cur.close()
    conn.close()

# --- ৫. MOCK VALIDATION RUN ---
raw_pdf_text = "আমাদের কোম্পানি পলিসি অনুযায়ী প্রতি বছর জানুয়ারি মাসে এমপ্লয়ীদের পারফরম্যান্স বোনাস রিলিজ করা হয়। তবে যদি কোনো Developer পর পর ৩ দিন অফিসে লেট করে ঢোকে, তবে তার ওই মাসের বোনাস থেকে ১০% জরিমানা কাটা হবে। অন্যদিকে সেলস টিমের ক্ষেত্রে টার্গেট ফিলাপ না হলে বেসিক স্যালারি থেকে ৫% ডিডাকশন করা হয়।"

# Semantic Chunking রান
semantic_chunks = semantic_chunk_text(raw_pdf_text, threshold=0.82)
print("Generated Semantic Chunks:\n", semantic_chunks)

# Database স্টোর ও কুয়েরি Test
# (Postgres locally running default state validation)
# store_and_search_chunks(semantic_chunks, "লেট করলে এমপ্লয়ীদের কী জরিমানা কাটা হয়?")
```

---

### VI. Production Perspective: PGVector অপ্টিমাইজেশন ও মেমরি সাইজিং

🏭 Production Reality

প্রোডাকশন লেভেলে কোটি কোটি চাঙ্ক হ্যান্ডেল করার সময় GPU/CPU Memory ক্র্যাশ এড়াতে কিছু কড়াকড়ি গাইডলাইন মেনে চলতে হয়:

* **RAM vs. Vector Storage:** HNSW Indexিংয়ের ক্ষেত্রে পুরো গ্রাফ নেটওয়ার্কটি র‍্যামের (RAM) ওপর স্টোর হয়ে Computation রান করে। তাই তোমার Database সার্ভারের র‍্যাম সাইজ অবশ্যই Index করা টোটাল Vector-এর Memory সাইজের চেয়ে ১.৫ গুণ বেশি হতে হবে।
* **Dimension Reduction:** API কস্ট এবং Query Latency কমাতে `text-embedding-3-small` এর `dimensions` Parameter ব্যবহার করে ১৫৩৬ ডাইমেনশনকে ডাইনামিকালি সংকুচিত করে ২৫৬ বা ৫১২ ডাইমেনশনে নিয়ে আসা যায়, যা এক্যুরেসির কোনো ক্ষতি ছাড়াই Query স্পীড ৪ গুণ বুস্ট করে।

---

### VII. Common Mistakes

🔴 Common Mistake

**ভুল ধারণা:** RAG সিস্টেমে যত বেশি রিলেভেন্ট Document Query করে Model-এর Promptে পাঠানো হবে, AI তত ভালো উত্তর দেবে।

**বাস্তবতা:** একে বলে **Lost in the Context window clutter**। Prompt-এর মধ্যে অপ্রয়োজনীয় ও অতিরিক্ত Duplicate টেক্সট ফিড করলে Model-এর মনোযোগ বিঘ্নিত হয় এবং Latency বেড়ে যায়। প্রোডাকশনে সবসময় টপ ৩ বা ৫টি একদম perfect Semantic চাঙ্ক পাঠানোই Architectural বেস্ট প্র্যাকটিস।

---

### VIII. Mental Model: সুনিপুণ কাঁচি বনাম অন্ধ কুড়াল

Semantic চাঙ্কিংয়ের মেন্টাল Model:

**"আগের Character Chunking হলো অন্ধের মতো কুড়াল দিয়ে পেপার কাটা, যা বাক্যের মাঝখান থেকেও টুকরো করে ফেলে। আর Semantic Chunking হলো সুনিপুণ কাঁচি, যা কেবল Paragraph বা বাক্য শেষ হওয়ার অর্থপূর্ণ সন্ধিক্ষণেই ফোল্ডিং কাটে।"**

---

### IX. Mini Project: স্ক্র্যাচ Cosine Similarity ডিস্ট্যান্স ক্যালকুলেটর

চলো NumPy ব্যবহার করে দুটি Embeddings Vector-এর মধ্যকার geometric দূরত্ব ও কোসাইন সিমিলারিটি স্ক্র্যাচ থেকে ক্যালকুলেট করি, যা pgvector ব্যাকগ্রাউন্ডে রান করে।

```python
import numpy as np

# দুটি ৩ডি এম্বেডিংস Vector
vec_chunk = np.array([0.25, 0.88, 0.05])
vec_query = np.array([0.28, 0.85, 0.12])

# ১. ডট প্রোডাক্ট
dot_product = np.dot(vec_chunk, vec_query)

# ২. Vector-এর ম্যাগনিটিউড (দৈর্ঘ্য)
norm_chunk = np.linalg.norm(vec_chunk)
norm_query = np.linalg.norm(vec_query)

# ৩. কোসাইন সিমিলারিটি
cosine_sim = dot_product / (norm_chunk * norm_query)

# ৪. pgvector Cosine Distance (1 - Cosine Similarity)
cosine_dist = 1 - cosine_sim

print(f"Cosine Similarity (Closer to 1.0 is better): {cosine_sim:.4f}")
print(f"pgvector Cosine Distance (Closer to 0.0 is better): {cosine_dist:.4f}")
```

---

### X. Interview Questions

#### Beginner
1. **প্রশ্ন:** RAG সিস্টেমে "Fixed-size Chunking" এর চেয়ে "Semantic Chunking" কেন বেশি কার্যকর?
   * **উত্তর:** Fixed-size chunking ক্যারেক্টার বা Token-এর দৈর্ঘ্য হিসাব করে র্যান্ডমলি স্লিট করে, যার ফলে বাক্যের মূল অর্থ মাঝখান থেকে কেটে দুই টুকরো হয়ে যায়। Semantic Chunking পাশাপাশি বাক্যের অর্থগত সিমিলারিটি মেপে কেবল বিষয়ের পরিবর্তনের জায়গায় স্লিট করায় প্রতিটি চাঙ্ক স্বয়ংসম্পূর্ণ থাকে এবং Hallucination কমে।

#### Intermediate
2. **প্রশ্ন:** Postgres-এ pgvector এক্সটেনশনে IVFFlat এর চেয়ে HNSW Index কেন প্রোডাকশনে বেশি ব্যবহৃত হয়?
   * **উত্তর:** IVFFlat Index তৈরি করতে কম মেমরি লাগে কিন্তু Vector-এর সংখ্যা বাড়লে Query স্পীড স্লো হতে থাকে এবং এর এক্যুরেসির জন্য রি-ট্রেনিং দরকার হয়। HNSW গ্রাফ-ভিত্তিক মাল্টি-লেয়ার Indexিং হওয়ায় খুব দ্রুত ও নির্ভুলভাবে নিকটতম নেইবার খুঁজে বের করে এবং ট্রিলিয়ন স্কেলেও এর Prediction স্পীড ও এক্যুরেসির অবক্ষয় ঘটে না।

#### Advanced
3. **প্রশ্ন:** "Reciprocal Rank Fusion (RRF)" কীভাবে হাইব্রিড সার্চের ফলাফলকে perfect করে?
   * **উত্তর:** RRF হলো এমন একটি Algorithm যা ডেন্স Vector সিমিলারিটি সার্চের র‍্যাঙ্কিং পজিশন এবং স্পার্স কিওয়ার্ড সার্চের র‍্যাঙ্কিং পজিশনকে তাদের র‍্যাঙ্কের ব্যস্তানুপাতিক sum ($Score = \sum \frac{1}{k + r}$) দিয়ে ফিউশন করে নতুন র‍্যাঙ্ক ডিফাইন করে। এর ফলে কোনো Document Vector বা কিওয়ার্ড—উভয় সার্চেই ভালো পজিশনে থাকলে সে হাই রেটিং পেয়ে টপ কুয়েরিতে চলে আসে, যা সিঙ্গেল সার্চের চেয়ে দ্বিগুণ নির্ভুল।

---

### XI. Chapter Summary
* **Semantic Chunking** অর্থগত অমিল মেপে ডাইনামিক স্লিটিং করার revolutionary প্রসেস।
* **pgvector** ও **HNSW** Indexিং রিলেশনাল Database Postgres-কে AI-নেটিভ Vector স্পেড দেয়।
* কস্ট ও Quality ব্যালেন্সের জন্য প্রোডাকশনে **Hybrid Search** এবং ডাইমেনশন Optimization খুব গুরুত্বপূর্ণ।

---

### XII. What's Next
আমরা ভালোভাবে Semantic আরএজি পিডিএফ Search Engine Architecture সম্পন্ন করেছি। পরের chapter-এ আমরা প্রবেশ করতে যাচ্ছি AI এজেন্টের সবচেয়ে জটিল ও রোমাঞ্চকর প্রোজেক্টে: **Part 11 — Building Real AI Products এর Chapter 26: Blueprint 3 — Agentic CLI Code Writer with Auto-Test Healing**। কীভাবে একটি AI এজেন্ট তোমার Computeারে স্বয়ংক্রিয়ভাবে Code লিখবে, Code লিখে নিজেই টার্মিনাল Test রান করবে, Test Error আসলে নিজেই সেই Error Log রিড করে Code সেলফ-কারেকশন বা হিলিং সম্পন্ন করবে, তা আমরা পাইথনে সম্পূর্ণ রানিং রিঅ্যাক্ট এজেন্ট Loop Architect করে নিজের হাতে Test করবো।

---
**Chapter 25 শেষ।**
