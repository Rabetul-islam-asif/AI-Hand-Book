# Chapter 25: Blueprint 2 — Enterprise PDF Search Engine (pgvector + Semantic Chunking)

তুমি কি কখনো ভেবেছো—

একটি Enterprise-grade PDF Search Engine বা RAG বানানোর সময় সবচেয়ে বড় ভুলটা কোথায় হয়?

বেশিরভাগ Developer যখন PDF Search Engine বানান, তখন একটা কাজ করেন।

তারা পুরো Text-কে প্রতি ৫০০ Character পর পর Randomly কেটে ফেলেন।

তারপর সেগুলো Vector Database-এ Save করে দেন।

এর ফলে কী হয় জানো?

বাক্যের মূল অর্থ বা জরুরি কোনো Information মাঝখান থেকে কেটে দুই টুকরো হয়ে যায়।

সেগুলো চলে যায় আলাদা আলাদা Chunk-এ।

আর ঠিক এই কারণে AI Model বিভ্রান্ত হয়ে যায়。

সে তখন ভুলভাল বা অর্ধেক উত্তর দিতে শুরু করে।

তো চলো, এই চ্যাপ্টারে আমরা নিজের হাতে একটা Enterprise-grade High-performance PDF Document Search Engine ডিজাইন করে ফেলি。

আমরা দেখবো কীভাবে অন্ধের মতো Character কাটার বদলে বুদ্ধিমত্তার সাথে Semantic Chunking করা যায়।

কীভাবে Relational Database Postgres-এর Extension pgvector ব্যবহার করে Vector Search-কে Optimize করা যায়।

আর কীভাবে Re-ranking Pipeline দিয়ে খুব দ্রুত নির্ভুল উত্তর জেনারেট করা যায়।

তাহলে চলো, Random Splitting-এর এক মারাত্মক ট্র্যাজেডি দিয়ে শুরু করা যাক!


## ১. Random Splitting-এর ট্র্যাজেডি আর Hallucination

চলো একটা Real-world Company-র Policy Document-এর উদাহরণ দেখি।

ধরো সেখানে লেখা আছে:

*"Company-র নিয়ম অনুযায়ী, যদি কোনো Developer পর পর ৩ দিন অফিসে লেট করে ঢোকে, **[৫০০ Character Limit শেষ! ঠিক এখানে কেটে গেল]** তবে তার ওই মাসের Bonus থেকে ১০% জরিমানা কাটা হবে।"*

তুমি যদি Fixed Character Splitter যেমন `RecursiveCharacterTextSplitter` ব্যবহার করো, তাহলে কী ঘটবে?

আমাদের Chunk-গুলো দেখতে এমন হবে:

**Chunk 1:** *"Company-র নিয়ম অনুযায়ী, যদি কোনো Developer পর পর ৩ দিন অফিসে লেট করে ঢোকে..."* (কিন্তু এখানে কোনো শাস্তির কথা নেই!)

**Chunk 2:** *"তবে তার ওই মাসের Bonus থেকে ১০% জরিমানা কাটা হবে।"* (এখানে আবার কেন জরিমানা কাটা হচ্ছে, সেই কারণটাই নেই!)

এবার ভাবো, User যদি জিজ্ঞেস করে—

*"অফিসে লেট করলে কী Penalty দেওয়া হয়?"*

তখন কী হবে?

Model এই দুটি Chunk-কে একসাথে মেলাতে পারবে না।

সে তখন উত্তর দেবে:

*"অফিসে লেট করার কোনো নির্দিষ্ট Penalty খুঁজে পাওয়া যায়নি।"*

একে আমরা বলি Context Fragmenting বা RAG-এর এক বড় বিপর্যয়!

তাহলে এর সমাধান কী?

এখানেই আসে Semantic Chunking!

আচ্ছা, Semantic Chunking জিনিসটা আসলে কী?

সহজ কথায়, এটা কোনো নির্দিষ্ট Length-এর উপর নির্ভর করে না।

তাহলে এটি কীভাবে কাজ করে?

এটি প্রথমে আমাদের সব বাক্যকে আলাদা করে ফেলে।

তারপর প্রতিটি পাশাপাশি বাক্যের Embedding Vector-এর দূরত্ব বা Cosine Distance মেপে দেখে।

দূরত্ব মেপে ও কী বোঝে?

যদি দেখা যায় বাক্য ৩ এবং বাক্য ৪-এর মধ্যে অর্থের অনেক বড় পরিবর্তন ঘটেছে, যেমন Cosine Distance অনেক কমে গেছে—

তখন System বুঝে নেয় যে এখানে আলোচনার বিষয় বদলে গেছে।

সে সাথে সাথে সেখানে একটা Dynamic Slice বা সীমানা তৈরি করে দেয়।

এর ফলে প্রতিটি Chunk একদম স্বাধীন এবং অর্থপূর্ণ থাকে।

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

## ২. RAG Data Layer-এর মূল চাবিকাঠি

চলো এবার RAG-এর মূল শক্তিগুলো নিয়ে কথা বলি।

প্রথমে জানা যাক Postgres pgvector নিয়ে।

এই pgvector আসলে কী?

সহজ কথায়, এটি হলো একটি Open-source Extension।

এটি আমাদের Postgres Database-কে সরাসরি High-dimensional Vector Embeddings Store এবং Query করার ক্ষমতা দেয়।

কিন্তু আমরা কেন অন্য কোনো Vector Database ব্যবহার না করে এটি ব্যবহার করবো?

কারণ হলো, তোমাকে আলাদা করে কোনো নতুন Vector Database যেমন Pinecone বা Chroma সেটআপ করতে হবে না।

তোমার User Data এবং Document-এর Vector Data একই Postgres Database-এ একদম নিরাপদে থাকবে।

তাছাড়া তুমি Metadata ব্যবহার করে খুব দ্রুত SQL Query চালাতে পারবে।

আচ্ছা, pgvector-এ Indexing কীভাবে কাজ করে?

pgvector মূলত দুটি Indexing Support করে।

প্রথমটি হলো IVFFlat।

এটি দ্রুত Search করার জন্য Clustering Loop তৈরি করে।

আর দ্বিতীয়টি হলো HNSW。

এটি একটি আধুনিক Graph-based Indexing।

মজার ব্যাপার হলো, এটি IVFFlat-এর চেয়ে ৩ গুণ বেশি দ্রুত কাজ করে।

আর Production-এ একদম সঠিক Document খুঁজে পাওয়ার হার প্রায় ১০০% নিশ্চিত করে।

এবার চলো জানা যাক Hybrid Search সম্পর্কে।

Hybrid Search আমাদের কেন প্রয়োজন?

মাঝে মাঝে শুধু Vector Embeddings Search নির্দিষ্ট কোনো Brand Name বা Serial Number খুঁজে পেতে ভুল করে।

ঠিক এই কারণেই Production-এ আমরা Hybrid Search ব্যবহার করি।

এটি কীভাবে কাজ করে?

এটি মূলত দুটি পদ্ধতির মেলবন্ধন:

প্রথমটি হলো Dense Retrieval।

এটি Vector Similarity দিয়ে মূলত বাক্যের মূল অর্থটা বোঝার চেষ্টা করে।

আর দ্বিতীয়টি হলো Sparse Retrieval।

এটি Classical BM25 বা Postgres-এর `tsvector` দিয়ে একদম নির্দিষ্ট Keyword যেমন "X-230 Pro" match করায়।

কিন্তু এই দুটির রেজাল্টকে আমরা মেলাবো কীভাবে?

সেখানেই কাজ করে RRF বা Reciprocal Rank Fusion।

এটি এই দুই ধরণের Search-এর Output Score মিলিয়ে আমাদের সামনে সেরা ৫টি নিখুঁত Document তুলে আনে।


## ৩. HNSW Graph-এর কাজের ধরন

HNSW Index কীভাবে কাজ করে, তা নিচের এই Diagram-এ দেখে নাও:

```
    [ Layer 2 (Express Nodes) ] ───────► [ Jump Node A ] ──────────┐
                                               │                   │
                                               ▼                   ▼
    [ Layer 1 (Medium Density) ] ───────► [ Node B1 ] ─────────► [ Node B2 ]
                                               │                   │
                                               ▼                   ▼
    [ Layer 0 (Dense Vector Space) ] ───► [ Local Neighbor ] ──► [ Destination Vector ]
```

সহজ কথায়, HNSW মূলত Multi-layer Highway বা Expressway-এর মতো কাজ করে।

এটি প্রথমে বড় বড় Jump দিয়ে আমাদের কাঙ্ক্ষিত Vector-এর কাছাকাছি জায়গায় পৌঁছায়।

তারপর একদম শেষের Layer-এ এসে কাছাকাছি থাকা Node-গুলো খুঁজে বের করে।

এভাবে মাত্র কয়েক Millisecond-এর মধ্যে একদম নিখুঁত Vector ম্যাচ করে ফেলে।


## ৪. Loan Policy Search-এর বাস্তব উদাহরণ

ধরো, একজন Loan Officer ব্যাংকের একটি ফাইল থেকে কোনো তথ্য খুঁজছেন।

সেখানে লেখা আছে:

*"গ্রাহকের বয়স ৬০ এর বেশি হলে, সুদের হার ১% বেশি হবে এবং ৫ লাখের বেশি লোনে অবশ্যই নোটারি বন্ড লাগবে।"*

এখন ভুল Chunking-এর কারণে কী সমস্যা হতে পারে?

Officer যখন Search করলেন—

*"৬০ বছর বয়সীদের Loan Policy কী?"*

তখন Chunk মাঝখান থেকে কেটে যাওয়ার কারণে System শুধু সুদের হারের তথ্যটি খুঁজে পেলো।

কিন্তু নোটারি বন্ডের প্রয়োজনীয় অংশটি একদম হারিয়ে গেল।

তাহলে Semantic Chunking কীভাবে এই সমস্যার সমাধান করে?

এটি পুরো Paragraph-টিকে একটি সম্পূর্ণ Chunk হিসেবে জমিয়ে রাখে।

এর ফলে Officer যখন কুয়েরি করেন, তখন সে সুদের হার এবং নোটারি বন্ড—দুটি তথ্যই একসাথে পেয়ে যান।

খুবই চমৎকার, তাই না?


## ৫. Python দিয়ে Postgres pgvector এবং Semantic Chunking Implementation

💻 Developer View

চলো এবার সরাসরি Code-এ হাত দেওয়া যাক!

আমরা Python দিয়ে একটি Real-world Semantic Chunking Loop তৈরি করবো।

একই সাথে pgvector Indexing ব্যবহার করার সম্পূর্ণ Pipeline তৈরি করে ফেলবো।

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


## ۶. Production-এ pgvector Optimize আর Memory Scaling

 Production Reality

Production Level-এ যখন তুমি কোটি কোটি Chunk নিয়ে কাজ করবে, তখন GPU বা CPU-এর Memory ক্র্যাশ করতে পারে।

এই সমস্যা এড়াতে আমাদের কিছু জরুরি বিষয় মাথায় রাখতে হবে।

যেমন RAM এবং Vector Storage-এর হিসাব।

HNSW Indexing-এর সময় পুরো Graph Network-টি RAM-এর ওপর জমা থাকে।

সেখানেই সব Computation চলে।

তাই তোমার Database Server-এর RAM সাইজ অবশ্যই টোটাল Vector Memory-র চেয়ে অন্তত ১.৫ গুণ বেশি হতে হবে।

তাড়াও আর কীভাবে আমরা Performance বাড়াতে পারি?

আমরা Dimension Reduction করতে পারি।

API-এর খরচ এবং Query Latency কমানোর জন্য `text-embedding-3-small` Model-এর `dimensions` Parameter ব্যবহার করা যায়।

এর মাধ্যমে আমরা ১৫৩৬ Dimension-কে কমিয়ে ২৫৬ বা ৫১২-তে নিয়ে আসতে পারি।

এতে Accuracy-র কোনো ক্ষতি ছাড়াই Query-র গতি প্রায় ৪ গুণ বেড়ে যায়!


## ৭. কিছু কমন ভুল

🔴 Common Mistake

অনেকেরই একটা ভুল ধারণা থাকে।

তারা মনে করেন, RAG System-এ যত বেশি Document খুঁজে Model-এর Prompt-এ পাঠানো যাবে, AI তত ভালো উত্তর দেবে।

কিন্তু আসলে কি তাই?

একেবারেই না!

একে আমরা বলি Lost in the Context Window Clutter।

Prompt-এর ভেতর ফালতু এবং অতিরিক্ত Duplicate Text দিলে Model কনফিউজড হয়ে যায়।

একই সাথে কাজের গতি বা Latency-ও অনেক বেড়ে যায়।

তাই Production-এ সবসময় সেরা ৩ থেকে ৫টি একদম নিখুঁত Semantic Chunk পাঠানোই সবচেয়ে বুদ্ধিমানের কাজ।


## ৮. Mental Model: সুনিপুণ কাঁচি বনাম অন্ধ কুড়াল

চলো বিষয়টাকে একটা সহজ উদাহরণ দিয়ে বোঝার চেষ্টা করি।

আগের Character Chunking ছিল অন্ধের মতো কুড়াল দিয়ে কাগজ কাটার মতো।

যা বাক্যের ঠিক মাঝখান থেকেও কেটে টুকরো টুকরো করে ফেলতো।

আর আমাদের আজকের Semantic Chunking হলো একটি সুনিপুণ কাঁচি।

যা কেবল Paragraph বা বাক্য শেষ হওয়ার সুন্দর ও অর্থপূর্ণ জায়গায় নিখুঁত কাট দেয়।


## ৯. Mini Project: স্ক্র্যাচ থেকে Cosine Similarity বের করা

চলো এবার NumPy ব্যবহার করে দুটি Embedding Vector-এর ভেতরের জ্যামিতিক দূরত্ব আর Cosine Similarity স্ক্র্যাচ থেকে হিসাব করি।

পেছনের ব্যাকগ্রাউন্ডে pgvector মূলত এই কাজটিই করে থাকে।

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


## ১০. ইন্টারভিউতে কেমন প্রশ্ন হতে পারে?

### Beginner Level

**প্রশ্ন:** RAG System-এ Fixed-size Chunking-এর চেয়ে Semantic Chunking কেন বেশি কাজের?

**উত্তর:** 

Fixed-size Chunking মূলত Character বা Token-এর দৈর্ঘ্য মেপে Randomly কাটাছেঁড়া করে।

এর ফলে বাক্যের মূল অর্থ মাঝখান থেকে কেটে দুই ভাগ হয়ে যায়।

কিন্তু Semantic Chunking পাশাপাশি থাকা বাক্যের অর্থগত মিল পরীক্ষা করে।

সে কেবল তখনই কাটে, যখন বিষয়ের পরিবর্তন ঘটে।

তাই প্রতিটি Chunk সম্পূর্ণ থাকে এবং ভুল উত্তর বা Hallucination-এর ঝুঁকি কমে।


### Intermediate Level

**প্রশ্ন:** Postgres-এর pgvector-এ IVFFlat-এর চেয়ে HNSW Index কেন বেশি ব্যবহার করা হয়?

**উত্তর:** 

IVFFlat Index তৈরি করতে মেমরি কম লাগলেও Vector-এর সংখ্যা বাড়লে Query গতি কমে যায়।

তাছাড়া ভালো ফলের জন্য একে বারবার Re-train করতে হয়।

অন্যদিকে, HNSW হলো Graph-based Multi-layer Indexing।

এটি খুব দ্রুত এবং নিখুঁতভাবে সবচেয়ে কাছের Vector খুঁজে বের করতে পারে।

ভবিষ্যতে কোটি কোটি Data থাকলেও এর গতি বা নির্ভুলতা কমে না।


### Advanced Level

**প্রশ্ন:** Reciprocal Rank Fusion বা RRF কীভাবে Hybrid Search-এর ফলাফলকে নিখুঁত করে?

**উত্তর:** 

RRF হলো এমন একটি Algorithm যা Dense Vector Search and Sparse Keyword Search-এর র‍্যাঙ্কিং পজিশনকে মিলিয়ে দেয়।

এর জন্য এটি তাদের র‍্যাঙ্কের ব্যস্তানুপাতিক Sum:

$Score = \sum \frac{1}{k + r}$

এই Formula ব্যবহার করে নতুন Rank নির্ধারণ করে।

এর ফলে যদি কোনো Document বা Keyword দুটি সার্চেই ভালো পজিশনে থাকে, তবে সে সবার উপরে চলে আসে।

এটি যেকোনো একটি সার্চ ব্যবহারের চেয়ে দ্বিগুণ নিখুঁত ফলাফল দেয়।


## ১১. আমরা কী শিখলাম?

আজকে আমরা বেশ কিছু গুরুত্বপূর্ণ জিনিস শিখে ফেললাম।

প্রথমত, Semantic Chunking হলো বাক্যের অর্থের মিল দেখে বুদ্ধিমানের সাথে Dynamic Slice করার এক দারুণ পদ্ধতি।

দ্বিতীয়ত, pgvector এবং HNSW Indexing আমাদের চেনা Postgres Database-কে সরাসরি AI-native Vector Database বানিয়ে দেয়।

আর শেষ কথা হলো, খরচ এবং Quality ঠিক রাখার জন্য Hybrid Search আর Dimension Optimization করা খুবই জরুরি।


## ১২. What's Next?

পরের Chapter-এ আমরা বানাবো এক রোমাঞ্চকর Project!

সেখানে আমরা শিখবো কীভাবে একটি Agentic CLI Code Writer তৈরি করা যায়।

যে নিজে Code লিখবে, Test করবে এবং Error আসলে নিজেই তা ঠিক বা Heal করবে।

দারুণ হবে না বিষয়টা? চলো পরের চ্যাপ্টারে যাই!

**Chapter 25 শেষ।**
