# Chapter 24: Blueprint 1 — Multi-Session Chatbot with Fact Memory (Redis + Mem0)

---

### Chapter Goal
এই চ্যাপ্টারের মূল লক্ষ্য হলো প্রোডাকশন-গ্রেড AI Memory ইকোসিস্টেম স্বহস্তে আর্কিটেক্ট করা। আমরা সাধারণ চ্যাটবটের ক্ষণস্থায়ী Memory-এর সীমাবদ্ধতা ভেঙে Redis (ফর সেশন চ্যাট হিস্টোরি) এবং Mem0 (ফর লাইফটাইম ইউজার ফ্যাক্ট Memory) ব্যবহার করে একটি কাস্টম মাল্টি-সেশন চ্যাটবট দাঁড় করাবো, যা ইউজারের দীর্ঘদিনের পছন্দ-অপছন্দ, Project-এর নাম ও ব্যক্তিগত তথ্য সেশন পরিবর্তনের পরেও নিখুঁতভাবে মনে রাখতে পারে।

### Why Should I Care?
গতানুগতিক AI চ্যাটবটগুলোর Memory থাকে কেবল একটি সেশন পর্যন্ত। ইউজার ট্যাব ক্লোজ করলে বা নতুন সেশন শুরু করলে AI সবকিছু ভুলে যায়, যা ইউজারের বিরক্তি বাড়ায়। রিয়েল-ওয়ার্ল্ড AI অ্যাসিস্ট্যান্ট (যেমন ChatGPT Plus-এর কাস্টম Memory বা প্রোডাকশন কো-পাইলট) ডিজাইন করতে হলে তোমাকে সেশন ক্যাশিং ও রিয়েল-টাইম লাইফটাইম ফ্যাক্ট এক্সট্রাকশনের হাইব্রিড Architecture রপ্ত করতে হবে।

### Big Picture
এটি আমাদের বাস্তব Project ব্লুপ্রিন্ট লেয়ারের প্রথম মাইলফলক। আগের পার্টগুলোতে আমরা যে এলএলএম সার্ভিং, Prompt ইঞ্জিনিয়ারিং এবং Data ভেক্টরাইজেশন থিওরিগুলো শিখেছি, সেগুলোকে রিয়েল-ওয়ার্ল্ড প্রোডাকশন কোডে কনভার্ট করার যাত্রা এখান থেকেই শুরু।

---

### ১. The Problem: চ্যাটবটের স্মৃতিভ্রষ্টতা ও API কস্ট বোমা

সাধারণ চ্যাটবট ডিজাইনে আমরা চ্যাট হিস্টোরি Model-এর Context উইন্ডোতে পুশ করি:
```python
messages = [
    {"role": "user", "content": "আমার নাম রহিম, আমি লারাভেল পছন্দ করি।"},
    {"role": "assistant", "content": "হ্যালো রহিম! তোমার লারাভেল প্রোজেক্টে স্বাগতম।"}
]
```
এই স্টাইলে দুটি বড় বোতলনাক বা সমস্যা রয়েছে:
1. **Token ইনফ্লেশন (Token Inflation):** প্রতিবার নতুন মেসেজ পাঠানোর সময় পুরোনো সব মেসেজ পুনরায় মডেলে পাঠাতে হয়। ১০টি মেসেজ পর তোমার API বিল ও Latency ১০ গুণ বেড়ে যাবে।
2. **সেশন এন্ড ট্র্যাজেডি (Session End Tragedy):** ইউজার লগআউট বা ট্যাব ক্লোজ করলে নতুন সেশনে AI আর মনে রাখতে পারে না যে ইউজারের নাম রহিম কিংবা সে লারাভেল পছন্দ করে।

#### প্রোডাকশন সলিউশন: হাইব্রিড Memory Architecture (Dual-Layer Memory)
* **Layer 1: Short-term Session Memory (Redis):** চ্যাটের শেষ ১০টি মেসেজের রিয়েল-টাইম ফ্লো অত্যন্ত দ্রুত ক্যাশ করে রাখার জন্য Redis ব্যবহার করা হয়।
* **Layer 2: Long-term Fact Memory (Mem0):** সম্পূর্ণ চ্যাটের ভেতরের সব ফালতু কথা ফিল্টার করে কেবল গুরুত্বপূর্ণ ফ্যাক্ট (যেমন: `{"name": "Rahim", "preference": "Laravel"}`) জেনারেট করে তা Vector Database ও গ্রাফ আর্কিটেকচারে সেভ রাখার জন্য Mem0 ব্যবহার করা হয়। সেশন পরিবর্তন হলেও এই ফ্যাক্টগুলো ব্যাকগ্রাউন্ডে ইনজেক্ট করা হয়।

[VISUAL]
Title: Hybrid Memory Architecture (Redis + Mem0)
Illustration: User input split into Redis (short term stream) and Mem0 (long term vector fact storage) pipelines feeding to LLM
Placement: After Hook Section
Purpose: Provide architectural layout of a production-grade enterprise memory pipeline.

```
                  ┌──────────────────────┐
                  │      User Input      │
                  └──────────────────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
┌──────────────────────┐           ┌──────────────────────┐
│  Redis Cache (RAM)   │           │   Mem0 Engine (AI)   │
│  - Latest 10 Chat    │           │  - Extracts Facts    │
│    Messages          │           │  - Stores in Vector  │
└──────────────────────┘           └──────────────────────┘
            │                                 │
            └────────────────┬────────────────┘
                             ▼
                    ┌─────────────────┐
                    │ Prompt Ingest   │
                    │ + Global Facts  │
                    └─────────────────┘
                             │
                             ▼
                    🧠 [ LLM Engine ] ───► Response
```

---

### ২. Core Concepts: Memory ইঞ্জিনের মূল ভিত্তি

#### ক. Redis Chat History (স্বল্পমেয়াদী সেশন Memory)
Redis হলো একটি ইন-Memory কী-ভ্যালু Database।
* **কেন এটি ব্যবহার করবে:** এটি মাইক্রো-সেকেন্ডে রিড/রাইট কমপ্লিট করে। চ্যাটের শেষ কয়েকটি মেসেজ রিড করার জন্য ডিস্ক Database (যেমন Postgres) এ বারবার হিট করা এভয়েড করতে Redis-এর `List` বা `String` স্ট্রাকচার অনন্য।
* **টাইম টু লিভ (TTL):** আমরা সেশন চ্যাট Memory মাত্র ৩ দিন (TTL = 3 days) ক্যাশ রাখি, যাতে সার্ভারের মেমরি ওয়েস্ট না হয়।

#### খ. Mem0 (দীর্ঘমেয়াদী ফ্যাক্ট Memory)
Mem0 (পূর্বে EmbedChain) হলো একটি AI-নেটিভ Memory ইকোসিস্টেম।
* **Mechanism:** ইউজার যখনই চ্যাট করো, Mem0 ব্যাকগ্রাউন্ডে একটি লাইটওয়েট রিজনার কল করে চ্যাটের ভেতর থেকে কেবল ইউজারের ব্যক্তিগত পারসোনা বা ফ্যাক্ট আলাদা করে।
* **উদাহরণ:** ইউজার বললো, *"কাল আমার পরীক্ষা, তাই কফি খেয়ে সারারাত পড়তে হবে।"*
  Mem0 এক্সট্রাক্ট করে: `{"fact": "Prepares for exams", "habit": "Drinks coffee at night"}`। সে কিন্তু সম্পূর্ণ সিকোয়েন্স মুখস্থ করে না।
* **Vector ক্লাস্টারিং:** সেশন নতুন হলেও Prompt-এর সাথে সাথে Mem0 রিলেভেন্ট ফ্যাক্টগুলো কোসাইন সিমিলারিটি দিয়ে খুঁজে বের করে প্রম্পটে জুড়ে দেয়: *"You are talking to Rahim who loves Laravel and drinks coffee at night."*

---

### ৩. Visual Explanation: ফ্যাক্ট এক্সট্রাকশন ও স্টোরেজ Loop

Mem0 ব্যাকগ্রাউন্ডে কীভাবে ফ্যাক্ট এক্সট্রাক্ট ও আপডেট করে তা দেখে নাও:

```
[ User: "আমি সম্প্রতি নেক্সট জেএস দিয়ে কাজ করছি, লারাভেল আর ভাল্লাগেনা।" ]
                        │
                        ▼
                [ Mem0 Engine ]
                        │
                        ├─► 🔎 Detect conflict: User used to love Laravel
                        ├─► ✂️ Delete/Deprecate fact: Loves Laravel
                        └─► ➕ Insert new fact: Prefers Next.js
                                │
                                ▼
                   [ Vector Database Memory ]
```

---

### ৪. Real World Example: কাস্টম AI ট্রাভেল অ্যাসিস্ট্যান্ট

একটি AI ট্যুর গাইড অ্যাপ:
* **সেশন ১:** ইউজার বললে, *"আমি থাইল্যান্ড ট্রিপের জন্য হোটেল খুঁজছি। বাই দ্য ওয়ে, আমার সী-ফুড অ্যালার্জি আছে।"*
* **সেশন ২ (১ মাস পর):** ইউজার ট্যাব ওপেন করে বললে, *"আমি কক্সবাজার যাচ্ছি, সেরা রেস্টুরেন্ট সাজেস্ট করো।"*
* **ম্যাজিক:** চ্যাটবট কক্সবাজারের সেরা ৫টি রেস্টুরেন্ট সাজেস্ট করার সময় সি-ফুড অপশনগুলো অটোমেটিক্যালি ফিল্টার আউট করে দেবে এবং ইউজারকে মনে করিয়ে দেবে, *"যেহেতু তোমার সী-ফুড অ্যালার্জি আছে, তাই এই রেস্টুরেন্টের মাটন চপ ট্রাই করতে পারো।"* এটিই হলো গোল্ড-স্ট্যান্ডার্ড AI ইউজার এক্সপেরিয়েন্স।

---

### ৫. Developer Perspective: Redis + Mem0 + LangChain হাইব্রিড চ্যাটবট ইমপ্লিমেন্টেশন

💻 Developer View

চলো পাইথনে একটি সম্পূর্ণ রানিং, প্রোডাকশন-গ্রেড Multi-Session Memory পাইপলাইন স্ক্র্যাচ থেকে Code করি।

```python
import os
import redis
import json
from mem0 import Memory
from openai import OpenAI

# ১. এনভায়রনমেন্ট ও ক্লায়েন্ট সেটআপ
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
client = OpenAI()

# Redis Setup (Windows/Local host running Redis default port 6379)
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Mem0 Setup (Local Vector Database Memory)
mem0_config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {"host": "localhost", "port": 6333}
    }
}
# We use simple local memory storage for mock validation
memory = Memory()

# ২. চ্যাট হিস্টোরি রিড/রাইট হেল্পারস (Redis Layer)
def save_chat_to_redis(session_id, role, content):
    key = f"chat_session:{session_id}"
    message = json.dumps({"role": role, "content": content})
    r.rpush(key, message)
    r.expire(key, 86400 * 3) # TTL set to 3 days

def get_chat_from_redis(session_id, limit=6):
    key = f"chat_session:{session_id}"
    raw_messages = r.lrange(key, -limit, -1)
    return [json.loads(msg) for msg in raw_messages]

# ৩. হাইব্রিড Memory চ্যাট Engine
def run_chatbot_session(user_id, session_id, user_message):
    print(f"\n--- Processing Message for User {user_id} in Session {session_id} ---")
    
    # Step A: Long-term memory query (Mem0)
    # ইউজারের সাথে রিলেভেন্ট ফ্যাক্টগুলো খুঁজে আনুন
    print("Retrieving long-term facts from Mem0...")
    user_facts = memory.get_all(user_id=user_id)
    fact_context = ""
    if user_facts:
        facts_list = [f["text"] for f in user_facts]
        fact_context = "User Profile Facts:\n- " + "\n- ".join(facts_list)
        print("Facts retrieved:\n", fact_context)
    
    # Step B: Short-term memory query (Redis)
    print("Retrieving latest session chat history from Redis...")
    latest_history = get_chat_from_redis(session_id)
    
    # Step C: Mem0 ব্যাকগ্রাউন্ডে নতুন ফ্যাক্ট সেভ করো
    memory.add(user_message, user_id=user_id)
    
    # Step D: Prompt ইনজেকশন ও এলএলএম কল
    system_prompt = f"""
    You are a helpful personal assistant. Use the following long-term user profile facts if relevant:
    {fact_context}
    
    Answer the user warmly, respecting their history.
    """
    
    messages = [{"role": "system", "content": system_prompt}]
    for msg in latest_history:
        messages.append(msg)
    messages.append({"role": "user", "content": user_message})
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7
    )
    assistant_reply = response.choices[0].message.content
    
    # Step E: Redis সেশন ক্যাশে চ্যাট সেভ করো
    save_chat_to_redis(session_id, "user", user_message)
    save_chat_to_redis(session_id, "assistant", assistant_reply)
    
    return assistant_reply

# --- ৪. MOCK VALIDATION TEST RUN ---
# সেশন ১: রহিম তার Project-এর কথা জানালো
user_id = "user_rahim_123"
session_1 = "session_mon_9am"
reply1 = run_chatbot_session(user_id, session_1, "হ্যালো AI! আমি রহিম। আমি এখন নেক্সট জেএস দিয়ে কাজ করছি।")
print("AI Reply 1:", reply1)

# সেশন ২: রহিম সম্পূর্ণ নতুন সেশন ও দিন শুরু করলো, সে কিন্তু নেক্সট জেএস এর কথা আর মুখে আনবে না!
session_2 = "session_wed_10pm"
reply2 = run_chatbot_session(user_id, session_2, "হ্যালো! আমার কারেন্ট Project-এর জন্য সেরা ইউআই Library সাজেস্ট করো তো।")
print("AI Reply 2:", reply2)
```

---

### VI. Production Perspective: সেশন ডিকনফ্লিক্সন ও কনকারেন্সি

🏭 Production Reality

প্রোডাকশন গ্রেড অ্যাসিস্ট্যান্ট হোস্ট করার সময় একই সাথে দুই জায়গায় রাইট (Concurrent Writes) করার সময় কনফ্লিক্ট এড়াতে কিছু Condition সেট করতে হয়:

* **Redis Fail-safe:** Redis যদি সাময়িকভাবে ডাউন হয়ে যায়, চ্যাট যেন ক্র্যাশ না করে। এর জন্য Code ব্লকটি `try-except` ব্লকে রেখে ব্যাকআপ Memory বা Loop রান করতে হবে।
* **Mem0 Delay:** Mem0-তে ফ্যাক্ট রাইট করার প্রসেসটি অত্যন্ত কম্পিউট ইনটেনসিভ হওয়ায় এটি মূল API Response লুপে না রেখে Celery বা Redis Queue ব্যবহার করে **Asynchronous Background Task** হিসেবে রান করা প্রোডাকশন-গ্রেড বেস্ট প্র্যাকটিস।

---

### VII. Common Mistakes

🔴 Common Mistake

**ভুল ধারণা:** ইউজারের চ্যাটের প্রতিটি মেসেজকে ফ্যাক্ট হিসেবে Mem0-তে পুশ করা।

**বাস্তবতা:** ইউজার যদি চ্যাটে বলো, *"হ্যালো"*, *"কেমন আছো?"*, বা *"আজ বৃষ্টি হচ্ছে"*—এগুলো কোনো কাজের ফ্যাক্ট নয়। এগুলো মেমোরিতে পুশ করলে Vector Database আর্বেজ বা জাবরা ডাটায় ভরে যাবে। তাই Mem0 কনফিগারেশনে অবশ্যই Prompt বা ইউজার মেসেজের সেন্টিমেন্ট ও ইনফরমেশন থ্রেশহোল্ড চেক ফিল্টার ডিফাইন করে রাখা উচিত যাতে হাবিজাবি তথ্য ফিল্টার আউট হয়ে যায়।

---

### VIII. Mental Model: ডেস্ক File বনাম গ্লোবাল ডায়েরি

হাইব্রিড Memory-এর মেন্টাল Model:

**"Redis হলো তোমার ডেস্কের ফাইলবক্স (Short-term RAM) যা শুধু আজকের রানিং Project-এর পৃষ্ঠাগুলো ক্যাশ রাখে। আর Mem0 হলো তোমার ক্যাবিনেটের ডায়েরি (Long-term ROM) যেখানে তোমার সারা জীবনের গুরুত্বপূর্ণ কন্টাক্ট ও অভ্যাসগুলো চিরতরে রেকর্ড হয়ে থাকে।"**

---

### IX. Mini Project: স্ক্র্যাচ সেশন Window বাফার (Sliding Window Buffer)

চলো NumPy বা পাইথনে কোনো Library ছাড়া একটি স্লাইডিং Window বাফার Code করি যা সেশন হিস্টোরি ৬টি Token সাইজের বেশি হয়ে গেলে প্রথম দিকের মেসেজগুলো অটোমেটিক্যালি ক্লিয়ার বা স্লাইড করে দেয়।

```python
class SlidingWindowHistory:
    def __init__(self, max_buffer=3):
        self.max_buffer = max_buffer
        self.history = []
        
    def add_message(self, role, content):
        if len(self.history) >= self.max_buffer * 2: # ১ সেশন = ১ ইউজার + ১ অ্যাসিস্ট্যান্ট
            # স্লাইড আউট ওল্ডেস্ট কিউ
            self.history.pop(0)
            self.history.pop(0)
        self.history.append({"role": role, "content": content})
        
    def get_history(self):
        return self.history

# Test স্লাইডিং
buffer = SlidingWindowHistory(max_buffer=2)
buffer.add_message("user", "Msg 1")
buffer.add_message("assistant", "Ans 1")
buffer.add_message("user", "Msg 2")
buffer.add_message("assistant", "Ans 2")
buffer.add_message("user", "Msg 3")  # This will slide out Msg 1 / Ans 1
buffer.add_message("assistant", "Ans 3")

print("Sliding Window Active Cache:")
for msg in buffer.get_history():
    print(f"{msg['role']}: {msg['content']}")
```

---

### X. Interview Questions

#### Beginner
1. **প্রশ্ন:** একটি প্রোডাকশন চ্যাটবটে "Short-term Memory" এবং "Long-term Memory" এর প্র্যাক্টিক্যাল পার্থক্য কী?
   * **উত্তর:** Short-term memory (যেমন Redis) চ্যাটের লেটেস্ট মেসেজগুলোর রিয়েল-টাইম ফ্লো মনে রাখে যাতে কন্টিনিউয়াস টকিং নিখুঁত হয়। আর Long-term memory (যেমন Mem0) চ্যাটের ভেতরের অপ্রয়োজনীয় টেক্সট বাদ দিয়ে কেবল ব্যক্তিগত তথ্য ও পছন্দ এক্সট্রাক্ট করে Vector ডাটাবেসে চিরতরে সংরক্ষণ করে যা সেশন শেষ হওয়ার পরও ডায়নামিকালি অ্যাক্সেস করা যায়।

#### Intermediate
2. **প্রশ্ন:** কেন Redis-এর চ্যাট ক্যাশে "TTL (Time-to-Live)" সেট করা প্রোডাকশন আর্কিটেকচারে অত্যন্ত গুরুত্বপূর্ণ?
   * **উত্তর:** সেশন ক্যাশে TTL সেট না করলে কোটি কোটি ইউজারের রিয়েল-টাইম আর্বেজ চ্যাট Database-এর Memory স্থায়ীভাবে ব্লক করে ফেলবে, যা Database স্টোরেজ কস্ট এবং রিকোয়েস্ট Latency বহুগুণ বাড়িয়ে দেবে। ৩ থেকে ৭ দিনের TTL সেট রাখলে ওল্ড সেশন Data অটো-ক্লিয়ার হয়, যা সিস্টেমকে লাইটওয়েট ও ফাস্ট রাখে।

#### Advanced
3. **প্রশ্ন:** Mem0 কীভাবে ইউজারের পূর্ববর্তী Memory-এর সাথে নতুন চ্যাট তথ্যের বিরোধ (Memory Conflict) হ্যান্ডেল করে?
   * **উত্তর:** Mem0 তার Vector স্টোর লুপে নতুন ফ্যাক্ট আসার পর একটি লজিক্যাল কম্প্যারিজম বা সেলফ-আপডেট Loop চালায়। যদি নতুন ফ্যাক্ট পূর্ববর্তী Memory-এর সম্পূর্ণ বিপরীত হয় (যেমন: পূর্বে ছিল "Loves PHP" এবং নতুন তথ্য আসলো "Loves Python, hates PHP"), তবে সে Vector Database-এর পূর্ববর্তী রেকর্ডটি হয় ডেপ্রিকেট বা এডিট করে নতুন ভ্যালুটি আপডেট করে রিডান্ডেন্সি ব্লক করে।

---

### XI. Chapter Summary
* **Hybrid Memory** প্রোডাকশন চ্যাটবট ডিজাইনের লাইফ সেভার টেকনিক।
* **Redis** সেশন চ্যাট Memory ফাস্ট রিড করে এবং **Mem0** Vector মেমোরিতে লাইফটাইম ফ্যাক্ট সেভ রাখে।
* অ্যাসিনক্রোনাস ব্যাকগ্রাউন্ড টাঙ্গল ব্যবহার করে প্রোডাকশনে Latency ও সেশন ডিকনফ্লিক্সন নিশ্চিত করতে হবে।

---

### XII. What's Next
আমরা সাকসেসফুলি প্রথম প্রোডাকশন ব্লুপ্রিন্ট চ্যাট Memory Architecture সম্পন্ন করেছি। পরবর্তী চ্যাপ্টারে আমরা পদার্পণ করতে যাচ্ছি AI ডোমেইনের সবচেয়ে জনপ্রিয় ও পাওয়ারফুল এন্টারপ্রাইজ প্রজেক্টে: **Part 11 — Building Real AI Products এর Chapter 25: Blueprint 2 — Enterprise PDF Search Engine (pgvector + Semantic Chunking)**। কীভাবে হাজার পৃষ্ঠার কোম্পানির গোপনীয় পিডিএফ File ভেঙে রিভোলিউশনারি Semantic Chunking করা হয় এবং Postgres pgvector Database অপ্টিমাইজ করে সেকেন্ডে সঠিক File কুয়েরি করা হয়, তা আমরা সম্পূর্ণ Source Code দিয়ে আর্কিটেক্ট করবো।

---
**Chapter 24 সমাপ্ত।**
