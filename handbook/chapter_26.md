# Chapter 26: Blueprint 1 — Multi-Session Chatbot with Fact Memory (Redis + Mem0)

---

তুমি কি কখনো খেয়াল করেছ?

ChatGPT-তে গতকাল হয়তো বললে, "আমি রহিম, Laravel পছন্দ করি।"

আজকে নতুন একটা চ্যাট খুলতেই AI সব ভুলে গেল!

মনে হচ্ছে সে তোমাকে চেনেই না!

বিষয়টা সত্যিই বিরক্তিকর, তাই না?

আসল প্রোডাকশন চ্যাটবটে এমন হলে কাস্টমার তো পালাবেই!

তো চলো, আজ এই সমস্যাটা আমরা নিজের হাতে সমাধান করি।

এই চ্যাপ্টারে আমরা Redis দিয়ে সেশনের চ্যাট হিস্টোরি ক্যাশ করব।

আর Mem0 দিয়ে ইউজারের সারাজীবনের ফ্যাক্ট বা তথ্য Vector Database-এ চিরকালের জন্য সেভ রাখব।

সেশন চেঞ্জ হোক বা ট্যাব ক্লোজ হোক—তোমার চ্যাটবট সব মনে রাখবে।

এটা আমাদের রিয়েল প্রডাক্ট Blueprint সিরিজের প্রথম মাইলফলক।

আগের চ্যাপ্টারগুলোর থিওরি এবার আমরা সরাসরি কোডে রূপ দেব!

### ১. সমস্যা: চ্যাটবটের ভুলে যাওয়া আর API বিলের চাপ

সাধারণ চ্যাটবট ডিজাইনে আমরা চ্যাট হিস্টোরি Model-এর Context উইন্ডোতে পুশ করি:

```python
messages = [
    {"role": "user", "content": "আমার নাম রহিম, আমি Laravel পছন্দ করি।"},
    {"role": "assistant", "content": "হ্যালো রহিম! তোমার Laravel প্রোজেক্টে স্বাগতম।"}
]
```

এই ডিজাইনে বড় দুটি সমস্যা আছে।

প্রথম সমস্যা হলো Token Inflation।

আমরা যখন প্রতিবার নতুন মেসেজ পাঠাই, তখন পুরোনো সব মেসেজ আবার মডেলে পাঠাতে হয়।

১০টা মেসেজ পরেই দেখবে তোমার API বিল আর Latency অনেক বেড়ে গেছে!

দ্বিতীয় সমস্যা হলো Session End Tragedy।

ইউজার লগআউট করলে বা ট্যাব ক্লোজ করলে নতুন সেশনে AI আর কিছুই মনে রাখতে পারে না।

সে ভুলেই যায় ইউজারের নাম রহিম, আর সে Laravel পছন্দ করে!

তাহলে এর আসল সমাধান কী?

এর সমাধান হলো Hybrid Memory Architecture!

এখানে আমরা মেমরিকে দুটি ভাগে ভাগ করি।

প্রথম ভাগটি হলো Short-term Session Memory।

এর জন্য আমরা Redis ব্যবহার করি।

চ্যাটের শেষ ১০টি মেসেজ খুব দ্রুত ক্যাশ করে রাখার কাজ করে এটি।

আর দ্বিতীয় ভাগটি হলো Long-term Fact Memory।

এর জন্য আমরা Mem0 ব্যবহার করি।

চ্যাটের ভেতরের সব হাবিজাবি কথা বাদ দিয়ে এটি শুধু দরকারি তথ্যগুলো ফিল্টার করে।

যেমন: `{"name": "Rahim", "preference": "Laravel"}`।

তারপর এগুলো Vector Database আর Graph Architecture-এ সেভ করে রাখে।

সেশন বদলে গেলেও এই তথ্যগুলো ব্যাকগ্রাউন্ডে ইনজেক্ট করা হয়।

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
                     [ LLM Engine ] ───► Response
```

### ২. মূল আইডিয়া: Memory কীভাবে কাজ করে?

মেমরির মূল ভিত্তি বোঝার জন্য চলো দুইটা জিনিস খুব ভালো করে জেনে নিই।

প্রথমটি হলো Redis Chat History।

প্রশ্ন হতে পারে, Redis আসলে কী?

এটি হলো একটি সুপার ফাস্ট In-Memory Key-Value Database।

কিন্তু এটি আমরা কেন ব্যবহার করব?

কারণ এটি মাইক্রো-সেকেন্ডের মধ্যে ডেটা রিড আর রাইট করতে পারে।

চ্যাটের শেষ কয়েকটি মেসেজ পাওয়ার জন্য আমাদের ডিস্ক ডেটাবেজে বারবার হিট করার কোনো দরকার নেই।

Redis-এর List বা String স্ট্রাকচার এ কাজের জন্য একদম পারফেক্ট।

তাহলে এই ডেটা কতদিন থাকবে?

এর জন্য আমরা ব্যবহার করি TTL বা Time to Live।

আমরা সেশনের চ্যাট হিস্টোরি মাত্র ৩ দিনের জন্য ক্যাশ করে রাখি।

এতে সার্ভারের মেমরি নষ্ট হয় না।

এবার আসি দ্বিতীয় বিষয়ে—যা হলো Mem0।

প্রশ্ন হলো, Mem0 আসলে কী জিনিস?

এটি হলো একটি AI-Native Memory Ecosystem।

এটি কীভাবে কাজ করে?

তুমি যখনই চ্যাট করবে, Mem0 ব্যাকগ্রাউন্ডে একটি ছোট রিজনার রান করবে।

সে পুরো চ্যাট থেকে শুধু তোমার পার্সোনাল ইনফরমেশন বা দরকারি ফ্যাক্ট আলাদা করে নেবে।

যেমন ধরো, তুমি বললে, "কাল আমার পরীক্ষা, তাই কফি খেয়ে সারারাত পড়তে হবে।"

Mem0 এখান থেকে কী বের করবে?

সে বের করবে: `{"fact": "Prepares for exams", "habit": "Drinks coffee at night"}`।

মজার ব্যাপার হলো, সে কিন্তু তোমার পুরো চ্যাট মুখস্থ করে না!

তাহলে নতুন সেশনে সে কীভাবে মনে রাখে?

সেশন নতুন হলেও Mem0 তোমার প্রশ্নের সাথে মিল রেখে রিলেভেন্ট ফ্যাক্টগুলো খুঁজে বের করে。

তারপর সেগুলো Prompt-এর সাথে জুড়ে দেয়।

যেমন: *"You are talking to Rahim who loves Laravel and drinks coffee at night."*

### ৩. Fact কীভাবে সেভ হয়?

Mem0 ব্যাকগ্রাউন্ডে কীভাবে ফ্যাক্ট বের করে আর আপডেট করে, চলো তা দেখে নিই:

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

### ৪. একটা বাস্তব উদাহরণ

চলো একটি AI ট্যুর গাইড অ্যাপের কথা চিন্তা করি।

সেশন ১-এ ইউজার বলল, "আমি থাইল্যান্ড ট্রিপের জন্য হোটেল খুঁজছি। আর হ্যাঁ, আমার সী-فوড অ্যালার্জি আছে।"

এর ঠিক ১ মাস পর সেশন ২ শুরু হলো।

ইউজার এবার ট্যাব ওপেন করে বলল, "আমি কক্সবাজার যাচ্ছি, কিছু ভালো রেস্টুরেন্ট সাজেস্ট করো।"

এখানেই আসল ম্যাজিক!

চ্যাটবট যখন কক্সবাজারের রেস্টুরেন্ট সাজেস্ট করবে, তখন সে সী-ফুড অপশনগুলো নিজে থেকেই বাদ দিয়ে দেবে।

সে ইউজারকে মনে করিয়ে দেবে, "যেহেতু তোমার সী-ফুড অ্যালার্জি আছে, তাই এই রেস্টুরেন্টের মাটন চপ ট্রাই করতে পারো।"

একেবারেই চমৎকার একটি ইউজার এক্সপেরিয়েন্স, তাই না?

### ৫. চলো কোড করি!

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

### ৬. প্রোডাকশনে ব্যবহারের নিয়ম

🏭 Production Reality

যখন তুমি প্রোডাকশন গ্রেড চ্যাটবট হোস্ট করবে, তখন কিছু বিষয় মাথায় রাখতে হবে।

যেমন, একই সাথে কয়েক জায়গায় রাইট করার সময় কনফ্লিক্ট হতে পারে।

এই সমস্যাগুলো এড়াতে চলো কিছু জিনিস জেনে নিই।

প্রথমটি হলো Redis Fail-safe।

যদি কোনো কারণে Redis ডাউন হয়ে যায়, তাহলে কী হবে?

চ্যাট যেন কোনোভাবেই ক্র্যাশ না করে!

এর জন্য আমাদের কোড ব্লকটি একটি `try-except` ব্লকে রাখতে হবে।

এতে কোনো সমস্যা হলে ব্যাকআপ মেমরি বা লুপ রান করানো যাবে।

দ্বিতীয়টি হলো Mem0 Delay।

Mem0-তে ফ্যাক্ট সেভ করার কাজটা বেশ ভারী বা Compute Intensive।

তাই এটি মূল API Response লুপে রাখা একদমই ঠিক নয়।

তাহলে উপায় কী?

এজন্য Asynchronous Background Task হিসেবে Celery বা Redis Queue ব্যবহার করা সবচেয়ে ভালো।

### ৭. সাধারণ কিছু ভুল

🔴 Common Mistake

অনেকেরই একটা ভুল ধারণা থাকে।

তারা মনে করে, ইউজারের চ্যাটের প্রতিটি মেসেজকেই ফ্যাক্ট হিসেবে Mem0-তে পুশ করতে হবে।

কিন্তু ভেবে দেখো, ইউজার যদি বলে "হ্যালো", "কেমন আছো?" বা "আজ বৃষ্টি হচ্ছে"—এগুলো কি কোনো কাজের তথ্য?

একদমই নয়!

এগুলো মেমোরিতে পুশ করলে তোমার Vector Database আবর্জনায় ভরে যাবে।

তাহলে কী করা উচিত?

Mem0 Configuration-এ অবশ্যই একটি ফিল্টার সেট করে রাখতে হবে।

এটি ইউজার মেসেজের সেন্টিমেন্ট আর ইনফরমেশন চেক করবে।

এতে করে সব হাবিজাবি তথ্য নিজে থেকেই বাদ চলে যাবে।

### ৮. মনে রাখার সহজ উপায়

চলো এই পুরো সিস্টেমটা সহজে মনে রাখার একটা উপায় বা Mental Model দেখে নিই।

"Redis হলো তোমার ডেস্কের ফাইলবক্স বা Short-term Memory।

এটি শুধু আজকের রানিং প্রোজেক্টের পৃষ্ঠাগুলো ক্যাশ করে রাখে।

আর Mem0 হলো তোমার ঘরের আলমারির ডায়েরি বা Long-term Memory।

যেখানে তোমার সারাজীবনের গুরুত্বপূর্ণ কন্টাক্ট আর অভ্যাসগুলো চিরকালের জন্য রেকর্ড হয়ে থাকে।"

### ৯. মিনি প্রজেক্ট: Sliding Window Buffer

চলো পাইথনে কোনো লাইব্রেরি ছাড়া একটি Sliding Window Buffer তৈরি করি।

সেশন হিস্টোরি বড় হয়ে গেলে এটি প্রথম দিকের মেসেজগুলো নিজে থেকেই ডিলিট বা স্লাইড করে দেয়।

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

### ১০. ইন্টারভিউ প্রশ্ন

#### Beginner

**প্রশ্ন:** চ্যাটবটে Short-term Memory আর Long-term Memory-র আসল পার্থক্য কী?

**উত্তর:** Short-term Memory (যেমন Redis) চ্যাটের একদম শেষের মেসেজগুলো মনে রাখে।

এতে করে ইউজারের সাথে কথা বলার সময় তার ফ্লো ঠিক থাকে।

আর Long-term Memory (যেমন Mem0) ফালতু কথা বাদ দিয়ে শুধু দরকারি তথ্যগুলো Vector Database-এ চিরকালের জন্য সেভ করে।

যা সেশন শেষ হওয়ার পরও খুব সহজে ব্যবহার করা যায়।

#### Intermediate

**প্রশ্ন:** Redis চ্যাট ক্যাশে TTL বা Time-to-Live সেট করা কেন এত দরকারি?

**উত্তর:** এটি না করলে কোটি কোটি ইউজারের আর্বেজ চ্যাট ডেটাবেজের মেমরি চিরতরে ব্লক করে ফেলবে।

যার ফলে ডেটাবেজ স্টোরেজ কস্ট এবং Latency অনেক বেড়ে যাবে।

তাই ৩ থেকে ৭ দিনের TTL সেট করে রাখলে পুরোনো চ্যাট নিজে থেকেই ডিলিট হয়ে যায়।

এতে সিস্টেম সবসময় ফাস্ট আর হালকা থাকে।

#### Advanced

**প্রশ্ন:** নতুন তথ্যের সাথে পুরোনো তথ্যের অমিল বা Memory Conflict হলে Mem0 কীভাবে তা সামলায়?

**উত্তর:** Mem0 তার Vector Store-এ নতুন কোনো ফ্যাক্ট আসার পর একটি সেলф-আপডেট লুপ চালায়।

যদি নতুন ফ্যাক্ট আগের মেমরির উল্টো হয়, তবে সে আগের রেকর্ডটি এডিট করে বা বাদ দিয়ে নতুন ভ্যালু আপডেট করে নেয়।

### ১১. আমরা যা শিখলাম

চলো চট করে দেখে নিই এই চ্যাপ্টারে আমরা কী কী শিখলাম।

প্রথমত, Hybrid Memory হলো প্রোডাকশন চ্যাটবট ডিজাইনের জন্য একদম লাইফ সেভার একটি টেকনিক।

দ্বিতীয়ত, Redis সেশনের চ্যাট খুব দ্রুত রিড করতে সাহায্য করে।

আর Mem0 ইউজারের লাইфটাইম ফ্যাক্ট বা তথ্য Vector Database-এ সেভ রাখে।

সবশেষে, প্রোডাকশনে Latency আর কনফ্লিক্ট এড়াতে Asynchronous ব্যাকগ্রাউন্ড টাস্ক ব্যবহার করা উচিত।

### ১২. সামনে কী আসছে?

আমরা সফলভাবে আমাদের প্রথম চ্যাটবট Memory Architecture তৈরি করে ফেলেছি!

পরের চ্যাপ্টারে আমরা বানাবো একটি Enterprise PDF Search Engine।

সেখানে শিখবো কীভাবে হাজার পৃষ্ঠার পিডিএফ ফাইল ভেঙে Semantic Chunking করা হয়।

সবশেষে, pgvector ডেটাবেজ দিয়ে কীভাবে কয়েক সেকেন্ডে সঠিক ফাইল খুঁজে বের করা যায়, তাও কোডসহ দেখবো।

**Chapter 26 শেষ।**
