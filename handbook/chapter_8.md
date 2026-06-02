# Chapter 8: Under the Hood — Tokens, Embeddings & Context Window


তুমি কি কখনো ভেবেছো — তুমি যখন ChatGPT-তে বাংলায় লেখো, সে কি সত্যিই বাংলা বোঝে? উত্তর হলো — না! সে বোঝে শুধু সংখ্যা। তোমার লেখা প্রতিটি শব্দ আসলে ভেঙে যায় ছোট ছোট Token-এ, তারপর সেগুলো হয়ে যায় সংখ্যার Vector। মজার ব্যাপার হলো, বাংলায় একটা শব্দ লিখতে ইংরেজির চেয়ে ৩ থেকে ৫ গুণ বেশি Token খরচ হয়। মানে তোমার API বিলও ৩-৫ গুণ বেশি!

তো চলো দেখি এই চ্যাপ্টারে — কীভাবে Byte Pair Encoding (BPE) তোমার টেক্সট ভেঙে Token বানায়, কীভাবে Embeddings সেই Token-কে geometric অর্থবাহী Vector-এ রূপ দেয়, আর Context Window বলতে আসলে কী বোঝায়। তুমি যদি RAG পাইপলাইন বানাতে চাও, API কস্ট কমাতে চাও, বা Prompt injection আটকাতে চাও — এই জিনিসগুলো জানা তোমার জন্য অক্সিজেনের মতো জরুরি। আর হ্যাঁ, এটাই আমাদের **Part 4 — Modern AI Foundations** এর শেষ তাত্ত্বিক চ্যাপ্টার।



## ১. AI-এর চোখে ভাষা কীভাবে বদলায়?

তুমি যখন ChatGPT বা Claude-এর Prompt বক্সে লেখো:

*"আমি AI ভালোবাসি।"*

এখন প্রশ্ন হলো — Language Model কি বাংলা বোঝে?

বা ইংরেজি?

না। Model-এর ভেতরের Neural Network শুধু সংখ্যা বোঝে।

শূন্য আর এক। অথবা হাই-ডাইমেনশনাল Floating Point Number।

তাহলে তোমার বাংলা বাক্যটা Model-এর কাছে পৌঁছায় কীভাবে?

তিনটা ধাপে।

**প্রথম ধাপ — Tokenization।**
বাক্যটা ভেঙে ছোট ছোট টুকরো হয়ে যায়।

যেমন: `["আম", "ি ", "এ", "আই ", "ভাল", "োবাস", "ি"]`

**দ্বিতীয় ধাপ — ID Mapping।**
প্রতিটা টুকরোকে একটা Unique সংখ্যা দেওয়া হয়।

যেমন: `[2456, 120, 8932, 452, 1092]`

**তৃতীয় ধাপ — Embeddings।**
প্রতিটা সংখ্যাকে ১৫৩৬ বা ৩০০০ Dimension-এর একটা Vector-এ রূপ দেওয়া হয়।

যেমন: `[[0.12, -0.45, ...], [0.89, 0.02, ...]]`

আর সবশেষে এই Vector-গুলো Model-এর Transformer Block-এ ঢোকে।

সেখানেই আসল কাজ শুরু হয়।

[VISUAL]
Title: Text to Vector pipeline
Illustration: Step-by-step transformation of raw text to tokens, to token IDs, to high-dimensional embedding vectors
Placement: After Hook Section
Purpose: Provide architectural mapping of the data ingestion pipeline in LLMs.

```
Raw Text:    "আমি AI ভালোবাসি"
                   │
                   ▼
Tokenizer:   [ "আম", "ি ", "এ", "আই ", "ভাল", "োবাস", "ি" ]  (Sub-word splitting)
                   │
                   ▼
Token IDs:   [ 12405, 342, 9821, 4402, 129 ]               (Vocabulary look-up)
                   │
                   ▼
Embeddings:  [ [0.12, -0.89, 0.45, ...], [0.02, 0.54, -0.12, ...] ] (1536-dimensional coordinates)
```


## ২. Model আসলে Input কীভাবে বোঝে?

### Tokenization কী?

ধরো তোমাকে একটা বিশাল বই পড়তে দেওয়া হলো।

তুমি কি পুরো বই একবারে গিলে খাবে?

না। তুমি পৃষ্ঠায় পৃষ্ঠায় পড়বে। লাইনে লাইনে পড়বে। শব্দে শব্দে পড়বে।

Tokenization-ও ঠিক এই কাজটাই করে।

টেক্সটকে ছোটতম টুকরোতে ভাঙে।

আধুনিক LLM-এ এই ভাঙার পদ্ধতিটার নাম **Byte Pair Encoding (BPE)**।

### BPE কীভাবে কাজ করে?

BPE প্রথমে শুধু বর্ণমালা দিয়ে শুরু করে।

তারপর Training Data বারবার ঘেঁটে দেখে — কোন দুটো অক্ষর সবচেয়ে বেশিবার পাশাপাশি আসছে?

সেই জোড়াটাকে মিলিয়ে একটা নতুন Token বানিয়ে ফেলে।

যেমন — `t` আর `h` বারবার পাশাপাশি আসে, তাই দুটো মিলে হয়ে যায় `th`।

এভাবে বারবার Merge করতে করতে সে একটা পুরো Vocabulary তৈরি করে ফেলে।

### এতে লাভ কী?

সবচেয়ে বড় লাভ হলো — কোনো শব্দই আর "অচেনা" থাকে না।

ধরো তুমি লিখলে *"ChatGPTify"*।

এই শব্দটা কোনো Dictionary-তে নেই।

কিন্তু BPE এটাকে ভেঙে ফেলবে — `Chat`, `GPT`, `ify`।

প্রতিটা টুকরো সে আগে থেকেই চেনে।

তাই কোনো শব্দ দেখে Model কখনো থমকে যায় না।

এটাকে বলে Out-of-Vocabulary Problem সমাধান।

### Vocabulary কত বড়?

একটা Model-এর Vocabulary মানে হলো — সে মোট কতগুলো Token চেনে।

যেমন Llama 3 এর Vocabulary Size ১,২৮,০০০ Token।

### Embeddings কী?

এখন পর্যন্ত আমরা টেক্সট ভেঙে Token বানিয়েছি।

Token-কে Number দিয়েছি।

কিন্তু শুধু Number দিলেই তো হবে না।

Model-কে বুঝতে হবে — এই Number-এর পেছনে কী অর্থ লুকিয়ে আছে।

এখানেই আসে Embeddings।

Embeddings হলো প্রতিটা Token-এর অর্থ ধারণকারী একটা হাই-ডাইমেনশনাল Vector।

সহজ কথায় — একটা বিশাল Geometric Space-এ প্রতিটা শব্দের একটা নির্দিষ্ট স্থানাঙ্ক আছে।

আর কাছাকাছি অর্থের শব্দগুলো সেই Space-এ কাছাকাছি বসে।

### সবচেয়ে বিখ্যাত উদাহরণ?

**King - Man + Woman = Queen**

Vector Space-এ King-এর Vector থেকে Man-এর Vector বিয়োগ করো।

তারপর Woman-এর Vector যোগ করো।

ফলাফল?

Queen-এর Vector-এর একদম কাছে গিয়ে ঠেকবে।

মানে Model শব্দের মধ্যের সম্পর্ক Geometry দিয়ে ধরতে পারে!

### Context Window কী?

ধরো তোমার Computer-এর RAM ৮ GB।

তুমি একবারে ৮ GB-র বেশি Data Load করতে পারবে না।

Context Window হলো AI Model-এর RAM।

এটা বলে — Model একবারে সর্বোচ্চ কতগুলো Token নিতে পারবে।

যেমন GPT-4o-র Context Window হলো ১,২৮,০০০ Token।

### Context Window সীমিত কেন?

কারণ Self-Attention-এর Computation Cost বাক্যের দৈর্ঘ্যের সাথে স্কোয়ার হারে বাড়ে।

মানে বাক্য ২ গুণ লম্বা হলে Cost ৪ গুণ বেড়ে যায়।

তাই Context Window অসীম বানানো Computationally অসম্ভব।

## 🧠 Remember

ইংরেজিতে ১টা শব্দ মোটামুটি ০.৭৫টা Token খরচ করে।

মানে ১০০ শব্দ = প্রায় ১৩৩ Token।

কিন্তু বাংলা বা অন্যান্য Non-Latin Script-এ ব্যাপারটা একদম আলাদা।

বাংলায় ১টা শব্দ লিখতে ৩ থেকে ৫টা Token লাগতে পারে!


## ৩. Vector Space-এ শব্দ কোথায় বসে?

নিচের ছবিটা দেখো।

এটা একটা ২D Visualization।

এখানে দেখানো হচ্ছে — Embeddings কীভাবে শব্দগুলোর অর্থ Geometric অবস্থান দিয়ে প্রকাশ করে:

```
Dimension Y (Royalty)
 ▲
 │     [ King ]             [ Queen ]
 │     
 │     
 │     [ Man ]              [ Woman ]
 │                                        [ Apple ]
 │                                                 [ Banana ]
 └───────────────────────────────────────────────────────────► Dimension X (Gender)
```

খেয়াল করো।

Man থেকে Woman-এর দূরত্ব আর King থেকে Queen-এর দূরত্ব প্রায় সমান।

মানে Gender-এর সম্পর্কটা Model Geometry দিয়ে ধরেছে।

আবার সম্পূর্ণ ভিন্ন জিনিস — Apple, Banana — সেগুলো সম্পূর্ণ আলাদা জোনে Cluster হয়ে বসে আছে।


## ৪. বাংলা লিখলে API বিল কেন বেশি?

একই কথা ইংরেজি আর বাংলায় লিখে দেখো।

**ইংরেজি:** *"I am learning AI Engineering."*

এটা মাত্র ৬টা Token।

**বাংলা:** *"আমি AI Engineering শিখছি।"*

Tokenizer এটাকে ভেঙে ১৮ থেকে ২২টা Token বানাবে!

একই কথা। কিন্তু Token ৩-৪ গুণ বেশি।

এখন ভাবো — তুমি একটা Production RAG Pipeline বানাচ্ছো।

সেখানে বাংলা PDF Process করছো।

তোমার API খরচ ইংরেজি Project-এর তুলনায় ৪ গুণ বেশি হবে।

তাহলে সমাধান কী?

বড় Project-এ Custom Bengali Tokenizer তৈরি করো।

অথবা Local Model Host করো।

এটাই সবচেয়ে Smart Design Decision।


## ৫. Code দিয়ে দেখি — Token Count ও Embeddings

💻 Developer View

চলো Python-এ Practically দেখি।

OpenAI-এর Official Tokenizer `tiktoken` দিয়ে Token Count করবো।

আর Embeddings Vector-এর Cosine Similarity মাপবো।

```python
import tiktoken
import numpy as np

# ১. Tokenizer initialization (Llama-3 and GPT-4o use 'cl100k_base' or 'o200k_base')
encoding = tiktoken.get_encoding("cl100k_base")

# ২. টোকেনাইজিং ও ডিকোড Test
text = "আমি AI ভালোবাসি।"
tokens = encoding.encode(text)
print("Text to Token IDs:", tokens)
print("Token Count:", len(tokens))

# প্রতিটি আইডি আলাদাভাবে ডিকোড করে টুকরো দেখো
for t in tokens:
    print(f"ID {t} -> '{encoding.decode([t])}'")

# ৩. মক এম্বেডিংস Vector-এর কস-সিমিলারিটি (Cosine Similarity)
# দুটি এম্বেডিংসের জ্যামিতিক কোণ মাপা
def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# কাল্পনিক এম্বেডিংস Vector (Dimension = 3)
v_king = np.array([0.9, 0.1, 0.8])
v_man = np.array([0.2, 0.1, 0.9])
v_apple = np.array([-0.8, 0.9, 0.1])

print(f"\nSimilarity (King, Man): {cosine_similarity(v_king, v_man):.4f}") # High similarity
print(f"Similarity (King, Apple): {cosine_similarity(v_king, v_apple):.4f}") # Low/Negative similarity
```


## ৬. Production-এ Context Window ম্যানেজ করবে কীভাবে?

🏭 Production Reality

ধরো তুমি একটা Long-term Chat Agent বানিয়েছো।

Customer চ্যাট করতে থাকে।

প্রতিটা Message History-তে জমা হতে থাকে।

একসময় কী হয়?

History এত বড় হয়ে যায় যে Context Window Limit Cross করে।

আর API খরচ আকাশে উঠে যায়।

তাহলে সমাধান কী?

**Context Compaction & Summary Strategy।**

কাজটা সহজ।

চ্যাট History যখনই ৪০০০ Token Cross করবে, Background-এ একটা ছোট Model পুরো History-কে Summarize করে ফেলবে।

তারপর Final Chat-এ শুধু Summary আর Latest ৫টা Message পাঠাবে।

ফলাফল?

৮৫% API Cost কমে যায়।


## ৭. Common Mistake

🔴 Common Mistake

অনেকে মনে করে — Embeddings API-তে Text পাঠানোর আগে Regex দিয়ে সব Punctuation আর Emoji সরিয়ে "Clean" Text পাঠানো উচিত।

এটা ভুল।

কারণ Emoji আর Punctuation অনেক গুরুত্বপূর্ণ Context বহন করে।

যেমন `:-)` আর `:-(`।

এই দুটোর অর্থ সম্পূর্ণ উল্টো।

Model-এর Sentiment Analysis-এ এরা বিশাল Role রাখে।

তাই Embeddings-এর জন্য সবসময় Raw, Unfiltered Text পাঠাও।

কোনো কিছু Clean করতে যেও না।


## ৮. Mental Model

Tokenizer আর Embeddings-এর একটা সুন্দর ছবি মাথায় রাখো।

**Tokenizer হলো কাগজের কারখানা।**

তোমার টেক্সটকে ছোট ছোট টুকরোতে কাটে।

**Embeddings হলো একটা মায়াবী সংখ্যার নদী।**

শব্দগুলো সেই নদীতে ভেসে চলে।

একই অর্থের শব্দগুলো নদীর একই মোহনায় কাছাকাছি সাঁতার কাটে।

আর বিপরীত অর্থের শব্দগুলো নদীর দুই পাড়ে ভেসে চলে।


## ৯. Mini Project — BPE Algorithm স্ক্র্যাচ থেকে

চলো Python-এ BPE-র মূল কাজটা নিজে হাতে করে দেখি।

সবচেয়ে বেশি আসা Character Pair খুঁজে বের করবো।

তারপর সেটা Merge করবো।

```python
import collections

# ১. Input Training টেক্সট
# প্রতিটি শব্দের শেষে স্পেশাল স্টপ মার্কার '</w>' যোগ করা হয়
vocab = {
    'l o w </w>': 5,
    'l o w e r </w>': 2,
    'n e w e s t </w>': 6,
    'w i d e s t </w>': 3
}

# ২. সবচেয়ে বেশি ফ্রিকোয়েন্সির ক্যারেক্টার পেয়ার খোঁজা
def get_stats(vocab):
    pairs = collections.defaultdict(int)
    for word, freq in vocab.items():
        symbols = word.split()
        for i in range(len(symbols)-1):
            pairs[symbols[i], symbols[i+1]] += freq
    return pairs

# ৩. পেয়ার মার্জ করা ভোকাবুলারিতে
def merge_vocab(pair, v_in):
    v_out = {}
    bigram = ' '.join(pair)
    replacement = ''.join(pair)
    for word in v_in:
        w_out = word.replace(bigram, replacement)
        v_out[w_out] = v_in[word]
    return v_out

# ১টি মার্জ ইটারেশন Test
pairs = get_stats(vocab)
best_pair = max(pairs, key=pairs.get)
vocab = merge_vocab(best_pair, vocab)

print(f"Best pair to merge: {best_pair} (Occurrences: {pairs[best_pair]})")
print("Updated Vocab after 1 merge:\n", vocab)
```


## ১০. Interview Questions

### Beginner

**প্রশ্ন:** Token বলতে কী বোঝো? ১টা ইংরেজি শব্দ গড়ে কত Token খরচ করে?

**উত্তর:** Token হলো টেক্সটের ছোটতম টুকরো যা Model-এ Input হিসেবে ঢোকে।

সাধারণত ১টা ইংরেজি শব্দ ০.৭৫টা Token খরচ করে।

মানে ১০০ শব্দ = প্রায় ১৩৩ Token।

### Intermediate

**প্রশ্ন:** বাংলা বা অন্যান্য Non-Latin ভাষা AI API-তে বেশি Token কেন খরচ করে?

**উত্তর:** BPE-র মতো Tokenizer মূলত বিশাল ইংরেজি Text Corpus-এর উপর Trained।

তাই Vocabulary-তে বাংলা শব্দের Frequency অনেক কম।

ফলে Tokenizer বাংলা শব্দকে সরাসরি চিনতে পারে না।

ভেঙে ভেঙে ছোট ছোট Character বা Syllable-এ ভাগ করে।

এজন্যই ১টা বাংলা শব্দে ইংরেজির তুলনায় ৩ থেকে ৫ গুণ বেশি Token লাগে।

### Advanced

**প্রশ্ন:** Cosine Similarity কেন Euclidean Distance-এর চেয়ে বেশি কার্যকর?

**উত্তর:** ধরো দুটো Document-এর বিষয়বস্তু একদম এক।

কিন্তু একটা ছোট, আরেকটা অনেক বড়।

Euclidean Distance দৈর্ঘ্যের উপর নির্ভর করে।

তাই বড় Document-এর Vector লম্বা হওয়ায় Distance অনেক বেশি দেখাবে।

যদিও অর্থ একই!

Cosine Similarity এই সমস্যা সমাধান করে।

কারণ সে Vector-এর দৈর্ঘ্য উপেক্ষা করে।

শুধু দুই Vector-এর মধ্যবর্তী কোণ মাপে।

তাই অর্থগত মিল বোঝাতে Cosine Similarity অনেক বেশি নির্ভরযোগ্য।


## Chapter Summary

এই Chapter-এ আমরা শিখলাম:

* BPE যেকোনো অচেনা শব্দকে ছোট টুকরোতে ভেঙে Handle করে।
* Embeddings প্রতিটা Token-কে Geometric Vector-এ রূপ দিয়ে অর্থ দেয়।
* কাছাকাছি অর্থের শব্দ Vector Space-এ কাছাকাছি বসে।
* বাংলায় Token খরচ ইংরেজির ৩-৫ গুণ বেশি।
* Production-এ Context Compaction দিয়ে API Cost ৮৫% কমানো যায়।


## What's Next?

Modern AI Foundation-এর তাত্ত্বিক Part শেষ!

পরবর্তী Chapter থেকে শুরু হচ্ছে **Part 5 — LLMs**।

Chapter 9-এ দেখবো — BERT, GPT আর T5 কীভাবে আলাদা এবং কেন Decoder-only Architecture-এর এত জয়জয়কার।

**Chapter 8 শেষ।**
