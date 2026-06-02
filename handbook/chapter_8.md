# Chapter 8: Under the Hood — Tokens, Embeddings & Context Window



তুমি কি কখনো ভেবেছো — তুমি যখন ChatGPT-তে বাংলায় লেখো, সে কি সত্যিই বাংলা বোঝে? উত্তর হলো — না! সে বোঝে শুধু সংখ্যা। তোমার লেখা প্রতিটি শব্দ আসলে ভেঙে যায় ছোট ছোট Token-এ, তারপর সেগুলো হয়ে যায় সংখ্যার Vector। মজার ব্যাপার হলো, বাংলায় একটা শব্দ লিখতে ইংরেজির চেয়ে ৩ থেকে ৫ গুণ বেশি Token খরচ হয়। মানে তোমার API বিলও ৩-৫ গুণ বেশি!

তো চলো দেখি এই চ্যাপ্টারে — কীভাবে Byte Pair Encoding (BPE) তোমার টেক্সট ভেঙে Token বানায়, কীভাবে Embeddings সেই Token-কে geometric অর্থবাহী Vector-এ রূপ দেয়, আর Context Window বলতে আসলে কী বোঝায়। তুমি যদি RAG পাইপলাইন বানাতে চাও, API কস্ট কমাতে চাও, বা Prompt injection আটকাতে চাও — এই জিনিসগুলো জানা তোমার জন্য অক্সিজেনের মতো জরুরি। আর হ্যাঁ, এটাই আমাদের **Part 4 — Modern AI Foundations** এর শেষ তাত্ত্বিক চ্যাপ্টার।



### ১. Hook: AI-এর চোখের সামনে ভাষার convert

তুমি যখন ChatGPT বা Claude-এর Prompt বক্সে লেখেন: *"আমি AI ভালোবাসি।"*
Language Model কি বাংলা বোঝে? বা ইংরেজি?
না। Model-এর ভেতরের Neural Network-এর Matrix ক্যালকুলেটর কেবল শূন্য (0) এবং এক (1) বা হাই-ডাইমেনশনাল ফ্লটিং পয়েন্ট নাম্বার বোঝে।

Model-এর সামনে তোমার বাক্যের convertটি দেখো:
1. **Tokenization (Tokenization):** বাক্যটিকে ভেঙে ক্যারেক্টার বা সাব-ওয়ার্ডের টুকরোতে পরিণত করা হয়: `["আম", "ি ", "এ", "আই ", "ভাল", "োবাস", "ি"]`।
2. **আইডি ম্যাপিং (ID Mapping):** প্রতিটি টুকরোকে একটি ইউনিক সংখ্যা বা আইডিতে convert করা হয়: `[2456, 120, 8932, 452, 1092]`।
3. **Embeddings (Embeddings):** প্রতিটি আইডিকে ১৫৩৬ বা ৩০০০ ডাইমেনশনের একটি geometric স্থানাঙ্ক Vector-এ convert করা হয়: `[[0.12, -0.45, ...], [0.89, 0.02, ...]]`।

একেবারে শেষ মাথায় এই geometric Vectorগুলো Model-এর Transformer ব্লকে প্রবেশ করে।

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

---

### ২. Core Concepts: Model-এর Input লেয়ারের বিষয়

#### ক. Tokenization (Tokenization - শব্দ ভাঙার কৌশল)
Tokenization হলো টেক্সটকে ছোটতম অংশে বিভক্ত করা। আধুনিক এলএলএম-এ **Byte Pair Encoding (BPE)** ব্যবহার করা হয়।
* **BPE Mechanism:** এটি প্রথমে বর্ণমালা দিয়ে শুরু করে এবং বারবার Training টেক্সট Analysis করে সবচেয়ে বেশি ফ্রিকোয়েন্সিতে আসা জোড়া অক্ষরগুলোকে মার্জ করে নতুন Token তৈরি করে (যেমন: `t` এবং `h` মিলে `th`)।
* **কেন BPE বেস্ট:** এটি আউট-অফ-ভোকাবুলারি (OOV) প্রবলেম পুরোপুরি দূর করে। কোনো নতুন বা অদ্ভুত শব্দ পেলে (যেমন: *"ChatGPTify"*), BPE এটিকে ছোট ছোট পরিচিত টুকরোতে ভেঙে ফেলে প্রসেস করতে পারে, যা মডেলকে রিড করতে দেয়।

#### খ. Vocabulary (শব্দভান্ডার)
একটি Model-এর ভোকাবুলারি হলো তার Token টেমপ্লেটের মোট সংখ্যার সাইজ (যেমন Llama 3 এর ভোকাবুলারি সাইজ হলো ১২৮,০০০ Token)।

#### গ. Embeddings & Vector Space (Embeddings ও Vector স্পেস - অর্থবাহী জ্যামিতি)
Embeddings হলো প্রতিটি Token-এর Math-এর অর্থ ধারণকারী একটি হাই-ডাইমেনশনাল স্থানাঙ্ক।
* **কনসেপ্ট:** একটি ৩ডি বা ১৫৩৬ডি geometric স্পেসে সমার্থক বা কাছাকাছি অর্থপূর্ণ শব্দগুলো geometric কোণ বা দূরত্বের দিক থেকে খুব কাছাকাছি অবস্থান করে।
* **Math Equation (King - Man + Woman = Queen):**
Vector স্পেসে রাজা (King) Vector থেকে পুরুষ (Man) Vector বিয়োগ করে যদি নারী (Woman) Vector যোগ করা হয়, তবে তার geometric স্থানাঙ্ক রানী (Queen) Vector-এর একদম কাছাকাছি গিয়ে ঠেকবে।

#### ঘ. Context Window (Context Window - AI-এর র‍্যাম)
Context Window হলো একটি Model এক সাথে সর্বোচ্চ কতটি Token Receive ও প্রসেস করতে পারে তার সর্বোচ্চ সীমা (যেমন: GPT-4o-র Context Window হলো ১২৮,০০০ Token)।
* **কেন এটি লিমিটেড:** যেহেতু সেলফ-Attention-এর Compute কস্ট বাক্যের দৈর্ঘ্যের সাথে স্কয়ার হারে বাড়ে, তাই Context Window অসীম করা Computationally খুব ব্যয়বহুল।

🧠 Remember

Token এবং ইংরেজি শব্দের অনুপাত সাধারণত **১টি শব্দ = ০.৭৫টি Token**। তবে বাংলা বা নন-ল্যাটিন স্ক্রিপ্টের ক্ষেত্রে ফ্রিকোয়েন্সি কম থাকায় ১টি বাংলা শব্দ লিখতে প্রায় ৩ থেকে ৫টি Token খরচ হতে পারে!

---

### ৩. Visual Explanation: Vector স্পেসে শব্দের geometric Clustering

নিচের ২ডি ভিজ্যুয়ালাইজেশনটি দেখলে বুঝতে পারবে কীভাবে Embeddings শব্দগুলোর অর্থ geometric সান্নিধ্যে প্রকাশ করে:

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

খেয়াল করো, লিঙ্গভেদে ম্যান ও ওম্যান এবং কিং ও কুইন-এর দূরত্ব ও কোণ সমান। আবার সম্পূর্ণ ভিন্ন Categoryর ফল (Apple, Banana) সম্পূর্ণ ভিন্ন জোনে Cluster হয়ে আছে।

---

### ৪. Real World Example: Token ইনফ্লেশন এবং বিলিং শক

একই বাক্যের ইংরেজি ও বাংলা API বিলিং কস্ট দেখো:
* **ইংরেজি বাক্য:** *"I am learning AI Engineering."* -> মাত্র ৬টি Token।
* **বাংলা বাক্য:** *"আমি AI Engineerিং শিখছি।"* -> Tokenizer এটিকে ভেঙে প্রায় ১৮ থেকে ২২টি Token জেনারেট করতে পারে।

তুমি যদি কোনো প্রোডাকশন আরএজি (RAG) পাইপলাইনে বাংলা পিডিএফ ব্যবহার করো, তবে তোমার API খরচ ইংরেজি Project-এর চেয়ে ৪ গুণ বেশি হবে। এই কারণে বড় প্রোজেক্টে Custom বেঙ্গলি Tokenizer বা লোকাল Model হোস্ট করাই বেস্ট ডিজাইন সিদ্ধান্ত।

---

### ৫. Developer Perspective: Tiktoken ও OpenAI Embeddings API ব্যবহার

💻 Developer View

চলো পাইথনে Code করে Practically দেখি কীভাবে OpenAI-এর অফিসিয়াল Tokenizer `tiktoken` দিয়ে Token কাউন্ট করতে হয় এবং কীভাবে Embeddings Vector জেনারেট করতে হয়।

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

---

### VI. Production Perspective: Context Compaction

🏭 Production Reality

লং-টার্ম চ্যাট এজেন্টের ক্ষেত্রে Customার চ্যাট হিস্টোরি বারবার যোগ হতে থাকলে এক সময় তা Context Window লিমিট ক্রস করে এবং API খরচ আকাশে ওঠে।

প্রোডাকশন সলিউশন: **Context Compaction & Summary Strategy**
* চ্যাট হিস্টোরি যখনই ৪০০০ Token ক্রস করে, ব্যাকগ্রাউন্ডের একটি লাইট Model সম্পূর্ণ হিস্টোরিকে কম্প্যাক্ট বা সামারাইজ করে ফেলে।
* ফাইনাল চ্যাটে আমরা কেবল সামারি Vector ও লেটেস্ট ৫টি মেসেজ মডেলে পাস করি, যা ৮৫% API কস্ট রিডিউস করে।

---

### VII. Common Mistakes

🔴 Common Mistake

**ভুল ধারণা:** Embeddings এপিআইতে টেক্সট Input দেওয়ার আগে Regular Expression (Regex) দিয়ে সব যতিচিহ্ন ও ইমোজি রিমুভ করে ক্লিন টেক্সট পাঠানো উচিত।

**বাস্তবতা:** ইমোজি এবং যতিচিহ্ন Embeddingsের ক্ষেত্রে খুব গুরুত্বপূর্ণ Context বহন করে (যেমন: `:-)` বা `:-(` Model-এর সেন্টিমেন্ট এনালাইসিস সম্পূর্ণ উল্টে দিতে পারে)। তাই Embeddingsের জন্য সবসময় একদম র অ্যান্ড আনফিল্টারড টেক্সট পাঠানোই বেস্ট প্র্যাকটিস।

---

### VIII. Mental Model: কুইক স্যান্ড বা সংখ্যার নদী

Token ও Embeddingsের মেন্টাল Model:

**"Tokenizer হলো কাগজের কল কারখানা যা তোমার টেক্সটকে ছোট ছোট টুকরোতে কাটে। আর Embeddings হলো একটি মায়াবী সংখ্যার নদী (River of Numbers) যেখানে শব্দগুলো ভেসে চলে। একই অর্থপূর্ণ শব্দগুলো নদীর একই মোহনায় কাছাকাছি সাঁতার কাটে, আর বিপরীত অর্থপূর্ণ শব্দগুলো নদীর বিপরীত পাড়ে ভেসে চলে।"**

---

### IX. Mini Project: স্ক্র্যাচ বাইট পেয়ার এনকোডিং (BPE) Algorithm

চলো পাইথনে BPE Tokenizationের মূল Mechanism (সবচেয়ে বেশি ফ্রিকোয়েন্সিতে আসা ক্যারেক্টার পেয়ার মার্জ করা) স্ক্র্যাচ থেকে ডিজাইন করি।

```python
import collections

# ১. Input Training টেক্সট
# প্রতিটি শব্দের শেষে স্পেশাল স্টপ মার্কার '</w>' যোগ করা হয়
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

---

### X. Interview Questions

#### Beginner
1. **প্রশ্ন:** "Token (Token)" বলতে কী বোঝেন এবং ১টি ইংরেজি শব্দ গড়ে কত Token খরচ করে?
   * **উত্তর:** Token হলো টেক্সটের ছোটতম অংশ বা ক্যারেক্টার total যা মডেলে Input হিসেবে ঢোকে। সাধারণত ১টি ইংরেজি শব্দ ০.৭৫টি Token খরচ করে (মানে ১০০ শব্দ = ১৩৩ Token)।

#### Intermediate
2. **প্রশ্ন:** কেন বাংলা বা অন্যান্য নন-ল্যাটিন ভাষা AI এপিআইতে বেশি খরচ বা Token চার্জ করে?
   * **উত্তর:** বিশ্বখ্যাত Tokenizeারগুলো (যেমন BPE) মূলত বিশাল ইংরেজি টেক্সট কর্পাসের উপর ট্রেইনড। ফলে ভোকাবুলারিতে বাংলা শব্দের ফ্রিকোয়েন্সি কম থাকায় তারা বাংলা শব্দকে সরাসরি চিনতে পারে না এবং ভেঙে ভেঙে একক ক্যারেক্টার বা ছোট সিলেবলে ভাগ করে। এর ফলে ১টি বাংলা শব্দের জন্য ইংরেজি অপেক্ষা ৩ থেকে ৫ গুণ বেশি Token জেনারেট হয়।

#### Advanced
3. **প্রশ্ন:** Vector স্পেসে Embeddingsের "কোসাইন সিমিলারিটি (Cosine Similarity)" কেন "ইউক্লিডিয়ান দূরত্ব (L2 Distance)" এর চেয়ে বেশি কার্যকর?
   * **উত্তর:** ইউক্লিডিয়ান দূরত্ব ডিরেক্ট ম্যাগনিটিউড বা Vector-এর দৈর্ঘ্যের ওপর প্রভাব ফেলে। যদি দুটি Document-এর বিষয়বস্তু একদম এক হয়, কিন্তু একটি ছোট আর একটি অনেক বড় হয়, তবে Vector-এর দৈর্ঘ্য বেশি হওয়ায় তাদের ইউক্লিডিয়ান দূরত্ব অনেক বেশি দেখাবে। কোসাইন সিমিলারিটি মূলত Vector দুটির মধ্যবর্তী কোণ মাপে, Vector-এর দৈর্ঘ্য বা সাইজ উপেক্ষা করে। তাই এটি অর্থগত মিল বা ডিরেকশন ট্র্যাকিংয়ে অনেক বেশি পারফেক্ট।

---

### XI. Chapter Summary
* **Byte Pair Encoding (BPE)** ভোকাবুলারির বাইরে কোনো শব্দ ডেড বা ক্র্যাশ হতে দেয় না।
* **Embeddings** প্রতিটি Tokenকে হাই-ডাইমেনশনাল Vector স্থানাঙ্কে রূপ দিয়ে geometric অর্থ দেয়।
* কস্ট ও Latency Optimization-এর জন্য প্রোডাকশনে **Context Compaction** ট্যাকটিকস ব্যবহার করা খুব জরুরি।

---

### XII. What's Next
আমরা ভালোভাবে মডার্ন AI ফাউন্ডেশনের খুব গুরুত্বপূর্ণ তাত্ত্বিক এবং Data লেয়ারের চ্যাপ্টারগুলো শেষ করেছি। পরবর্তী চ্যাপ্টার থেকে আমাদের শুরু হচ্ছে লার্জ Language Model Ecosystem-এর মূল পরিচয়: **Part 5 — LLMs এর Chapter 9: The LLM Ecosystem — Decoder-only, Encoder-only & Encoder-Decoder**। কীভাবে BERT, GPT এবং T5 একে অপরের থেকে সম্পূর্ণ ভিন্ন কাজে ব্যবহৃত হয় এবং কেন Decoderের জয়জয়কার, তা আমরা বিস্তারিত শিখবো।

---
**Chapter 8 শেষ।**
