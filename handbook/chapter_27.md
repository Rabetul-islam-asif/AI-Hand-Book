# Chapter 27: Blueprint 4 — Production AI SaaS with Rate Limiting & Usage Billing

---

### Chapter Goal
এই চ্যাপ্টারের মূল লক্ষ্য হলো একটি সম্পূর্ণ প্রোডাকশন-রেডি কমার্শিয়াল AI সেস (AI SaaS) প্ল্যাটফর্মের ব্যাকঅ্যান্ড ইনফ্রাস্ট্রাকচার স্বহস্তে আর্কিটেক্ট করা। আমরা কাস্টমারদের অতিরিক্ত API হিট বা কুয়েরি বোমা ঠেকানোর জন্য Redis-ভিত্তিক Token বাকেট রেট-লিমিটিং (Rate Limiting), প্রতি ইউজারের Token ব্যবহার ট্র্যাক করার লগার এবং স্ট্রাইপ (Stripe Metered Billing) ইন্টিগ্রেশন করে ইউসেজ-বেসড বিলিং ইকোসিস্টেমের সম্পূর্ণ পাইপলাইন প্রস্তুত করবো।

### Why Should I Care?
তোমার AI প্রোডাক্ট যদি দারুণ হিট হয় এবং তুমি ইউজার প্রতি সাবস্ক্রিপশন কস্ট বা লিমিট না লাগান, তবে হ্যাকাররা বট দিয়ে প্রতি সেকেন্ডে লাখ লাখ Token কুয়েরি করে তোমার হাজার হাজার ডলারের API বিল একদিনেই পুড়িয়ে দেবে। একটি কমার্শিয়াল প্রোডাক্ট লঞ্চ করার প্রধান শর্ত হলো নিখুঁত কস্টিং ট্র্যাকিং ও কাস্টমার রেট লিমিট লক করা। এই চ্যাপ্টারটি পড়লে তুমি তোমার AI কোডকে সরাসরি একটি মুনাফা অর্জনকারী বৈশ্বিক বিজনেসে রূপান্তর করতে পারবে।

### Big Picture
এটি আমাদের বাস্তব Project ব্লুপ্রিন্ট লেয়ারের চতুর্থ তথা শেষ কমার্শিয়াল ফ্ল্যাগশিপ মাইলফলক। এরপর আমাদের ফাইনাল চ্যাপ্টারে আমরা কিয়ারের রোডম্যাপ ও AI আর্কিটেক্ট হওয়ার গাইডলাইন নিয়ে আলোচনা করে আমাদের AI হ্যান্ডবুকের মহাকাব্যিক সমাপ্তি টানবো।

---

### ১. The Problem: AI কুয়েরি বোমা ও দেউলিয়া হওয়ার ট্র্যাজেডি

ঐতিহ্যগত সফটওয়্যারে রেট লিমিট মাপা হয় সিম্পল রিকোয়েস্ট পার মিনিট (যেমন: ৬০ রিকুয়েস্ট/মিনিট) দিয়ে।
কিন্তু AI এর ক্ষেত্রে এটি সম্পূর্ণ ভিন্ন!
* একজন কাস্টমার ১ মিনিটে ১টি মেসেজ পাঠাতে পারে কিন্তু সেটিতে যদি সে এক লাখ Token-এর বিশাল Code ডাম্প করে, তবে তোমার খরচ হবে $০.৫০।
* অন্যজন কাস্টমার একই মিনিটে ৬০টি ক্ষুদ্র রিকোয়েস্ট পাঠাতে পারে কিন্তু তার টোটাল Token সাইজ মাত্র ২০০ Token, যার দাম হয়তো $০.০০০১।

AI প্রোডাকশনে তাই আমরা দুই ধরনের রেট লিমিটিং ব্যবহার করি:
1. **RPM (Requests Per Minute):** স্প্যামিং ব্লক করার জন্য।
2. **TPM (Tokens Per Minute):** মেমরি ও API কস্ট বোমা ব্লক করার জন্য।

#### প্রোডাকশন সলিউশন: Token বাকেট রেট-লিমিটিং ও মিটারড বিলিং
* **Layer 1: Redis Token Bucket (রেট লিমিটিং):** আমরা Redis ব্যবহার করে একটি ডাইনামিক Token বাকেট ডিজাইন করবো। প্রতিবার ইউজার মেসেজ পাঠালে বাকেটের Token সংখ্যা কমবে এবং প্রতি সেকেন্ডে বাকেটে অটোমেটিক নতুন Token রিফিল হবে। বাকেট শূন্য হয়ে গেলে ইউজারকে `HTTP 429 Too Many Requests` Error দেওয়া হবে।
* **Layer 2: Stripe Usage Billing (ব্যবহার অনুযায়ী বিলিং):** কাস্টমার আগে থেকে রিচার্জ না করে তার টোটাল ব্যবহারের ওপর ভিত্তি করে মাসের শেষে বিল পে করবে (মিটারড বা ইউসেজ-বেসড বিলিং—যেমন: প্রতি ১০০০ টোকেনে $০.০০৫)।

[VISUAL]
Title: Usage Billing & Rate Limiting Pipeline
Illustration: User request passing through Redis Token Bucket validator, getting logged for OpenAI token usage, and reporting usage event to Stripe Billing
Placement: After Hook Section
Purpose: Show business-grade SaaS billing architecture.

```
                  ┌──────────────────────┐
                  │    User Request      │
                  └──────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────┐
│  1. REDIS RATE LIMITER (Token Bucket RPM/TPM Check)     │
│  - If bucket empty ──► Return HTTP 429 Too Many Requests│
└────────────────────────────────────────────────────────┘
                             │ (Allowed)
                             ▼
                 🧠 [ Run AI Generation ] ──► Compute Tokens Used
                             │
                             ▼
┌────────────────────────────────────────────────────────┐
│  2. USAGE BILLING TRACKER (Stripe API integration)     │
│  - Log tokens to DB                                    │
│  - Send metered usage event to Stripe: 'token_used'    │
└────────────────────────────────────────────────────────┘
```

---

### ২. Core Concepts: কমার্শিয়াল AI ইঞ্জিনের মূল ভিত্তি

#### ক. Token Bucket Algorithm (Token বাকেট Algorithm)
* **কনসেপ্ট:** একটি বাকেটের সর্বোচ্চ ধারণক্ষমতা $B$ এবং প্রতি সেকেন্ডে বাকেটে $R$ হারে Token ড্রপ বা রিফিল হয়।
* **অ্যাকশন:** প্রতিবার ইউজার API কল করলে বাকেট থেকে $N$ টি Token তুলে নেওয়া হয়। বাকেটের সাইজের চেয়ে কল সাইজ বড় হলে কল ব্লক করা হয়।

#### খ. Stripe Metered Billing (স্ট্রাইপ মিটারড বিলিং)
স্ট্রাইপে আমরা কাস্টমারকে আনলিমিটেড ইউজ করার স্বাধীনতা দিই এবং মাসের শেষে তার মোট মিটারড ব্যবহার হিসাব করে কাস্টমারের ক্রেডিট কার্ড থেকে ডিরেক্ট চার্জ কেটে নেওয়া হয়।
* **Stripe Usage Event:** প্রতিবার AI Response শেষ হলে ব্যাকগ্রাউন্ডে স্ট্রাইপে একটি ইভেন্ট পুশ করা হয়: `stripe.SubscriptionItem.create_usage_record(subscription_item_id, quantity=1500, timestamp=now)`।

---

### ৩. Visual Explanation: Token বাকেট লিক Mechanism

Token বাকেটের গাণিতিক রিফিল Mechanism ভিজুয়ালি দেখো:

```
    Refill Water Drops (R = 5 Tokens/Sec)  ──────►  [  *  *  *  ]  (Refills to Max Bucket Capacity B = 100)
                                                    [  *  *  *  ]
                                                    [  *  *  *  ]
                                                          │
                                                          ▼ (User consumes N tokens on Request)
                                                    [ HTTP 200 OK ]
```

যদি ইউজার ১ সেকেন্ডে একসাথে ২০০ Token রিট্রাইভ বা তুলে নিতে চায়, বাকেটের সর্বোচ্চ সাইজ ১০০ হওয়ায় গেট সাথে সাথে লক হয়ে যাবে এবং লিক ব্লক করবে।

---

### ৪. Real World Example: Midjourney স্টাইল জেনারেশন ক্রেডিট

Midjourney বা রানওয়ে AI-তে সাবস্ক্রাইব করার পর:
* তুমি পান ২৫টি ফাস্ট ক্রেডিট। তুমি জেনারেশন অন করলে ক্রেডিট Loss হিসেব হয় এবং ফাস্ট ক্রেডিট জিরো হয়ে গেলে AI তোমাকে স্লো লাইনে ফেলে দেয়।
* এই পুরো ক্রেডিট ডিক্রিমেন্ট ও ফাস্ট/স্লো ট্র্যাফিক রাউটিং ব্যাকগ্রাউন্ডে Redis মেমরি কী-ভ্যালু ডিক্রিমেন্ট Mechanism দিয়ে ওয়ান-টাইম রান করানো হয়, যা কাস্টমারকে কুপন লিমিট হ্যান্ডেল করতে দেয়।

---

### ৫. Developer Perspective: Redis Rate Limiter + Stripe API মিটারড বিলিং সম্পূর্ণ পাইপলাইন ইমপ্লিমেন্টেশন

💻 Developer View

চলো পাইথনে একটি রানিং, প্রোডাকশন-গ্রেড AI সেস (AI SaaS) ব্যাকঅ্যান্ড লজিক ডিজাইন করি যা একই সাথে Redis দিয়ে TPM/RPM চেক করবে এবং Token ইউসেজ সরাসরি স্ট্রাইপ এপিআইতে পুশ করবে।

```python
import os
import time
import redis
import stripe
from openai import OpenAI

# ১. এনভায়রনমেন্ট ও ক্লায়েন্ট সেটআপ
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
stripe.api_key = "your-stripe-secret-key"
client = OpenAI()

# Redis Setup (Windows/Local running Redis)
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# ২. Redis Token Bucket Rate Limiter (RPM & TPM Checker)
def check_rate_limit(user_id, token_cost, max_tokens=10000, refill_rate=50):
    key_tokens = f"rate_limit:{user_id}:tokens"
    key_last_update = f"rate_limit:{user_id}:last_update"
    
    now = time.time()
    
    # বাকেটের ওল্ড Data রিড করো
    last_update = r.get(key_last_update)
    current_tokens = r.get(key_tokens)
    
    if last_update is None or current_tokens is None:
        # ফার্স্ট টাইম ইউজার: ফুল বাকেট এলোকেট করো
        r.set(key_tokens, max_tokens)
        r.set(key_last_update, now)
        current_tokens = max_tokens
    else:
        last_update = float(last_update)
        current_tokens = float(current_tokens)
        
        # রিফিল Calculation: সময় ব্যবধান * রিফিল রেট
        elapsed = now - last_update
        refilled = elapsed * refill_rate
        current_tokens = min(max_tokens, current_tokens + refilled)
        
        r.set(key_tokens, current_tokens)
        r.set(key_last_update, now)
        
    # রেট লিমিট Validation
    if current_tokens >= token_cost:
        # Token কেটে নিয়ে অ্যাক্সেস গ্র্যান্ট করো
        r.set(key_tokens, current_tokens - token_cost)
        return True, current_tokens - token_cost
    else:
        return False, current_tokens

# ৩. স্ট্রাইপ মিটারড বিলিং রিপোর্টার
def report_usage_to_stripe(stripe_sub_item_id, tokens_used):
    print(f"[💳 Stripe API] Reporting {tokens_used} tokens used for subscription item {stripe_sub_item_id}...")
    try:
        # মিটারড ইভেন্ট রেকর্ড সাবমিট
        stripe.SubscriptionItem.create_usage_record(
            stripe_sub_item_id,
            quantity=tokens_used,
            timestamp=int(time.time()),
            action="increment"
        )
        print("[🎉 Stripe API] Usage reported successfully!")
    except Exception as e:
        print("[🔴 Stripe Error] Failed to report usage:", e)

# ৪. প্রোডাকশন SaaS API রিকোয়েস্ট হ্যান্ডলার Loop
def process_saas_ai_request(user_id, stripe_sub_item_id, user_prompt):
    # কাল্পনিক এস্টিমেটেড Token কস্ট (যেমন Prompt সাইজ)
    estimated_cost = len(user_prompt.split()) * 3 # ৩ Token পার শব্দ গড়ে
    
    # Step A: Rate Limit Check
    allowed, remaining = check_rate_limit(user_id, token_cost=estimated_cost)
    
    if not allowed:
        print(f"\n[🛑 HTTP 429 Too Many Requests] User {user_id} is rate limited! Remaining tokens in bucket: {remaining:.2f}")
        return "Error: Rate Limit Exceeded. Please slow down."
        
    print(f"\n[🟢 Request Allowed] Processing AI query for {user_id}. Tokens Remaining: {remaining:.2f}")
    
    # Step B: Run AI Generation
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_prompt}]
    )
    
    reply = response.choices[0].message.content
    
    # Step C: Real Token Count Calculation
    prompt_tokens = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens
    total_tokens = response.usage.total_tokens
    print(f"[📊 Token Log] Prompt: {prompt_tokens}, Completion: {completion_tokens}, Total: {total_tokens}")
    
    # Step D: Report to Stripe Billing
    report_usage_to_stripe(stripe_sub_item_id, total_tokens)
    
    return reply

# --- ৫. MOCK VALIDATION RUN ---
user_id = "cus_rahim_99"
stripe_sub_item = "si_12345_mock" # Mock Stripe Subscription Item ID

# ১ম রিকোয়েস্ট: সাকসেসফুলি রান হবে
reply1 = process_saas_ai_request(user_id, stripe_sub_item, "আমাদের কোম্পানির জন্য একটি রেট লিমিটিং প্রোটোকল লিখে দাও।")
print("SaaS AI Response:", reply1)

# ২য় রিকোয়েস্ট (তাত্ক্ষণিকভাবে): বাকেটে Token রিফিলের টাইম না পাওয়ায় রেট লিমিট ট্র্যাপ হবে
reply2 = process_saas_ai_request(user_id, stripe_sub_item, "বাকি ডিটেইলস আরও ৩০০ শব্দে বুঝিয়ে দাও তো প্লিজ।" * 20)
print("SaaS AI Response:", reply2)
```

---

### VI. Production Perspective: ডেডিকেটেড ক্যাশ ও Database রোলব্যাক

🏭 Production Reality

প্রোডাকশনে যখন তুমি বড় স্কেলে AI সেস Deploy করবে, তখন তোমাকে নিচের ক্যাশ ডিজাইন গাইডলাইন মেনে চলতে হবে:

* **Redis cluster replication:** রেট লিমিটিং Data হারিয়ে গেলে সার্ভিস ডাউন হয়ে যেতে পারে। তাই প্রোডাকশনে Redis মেমরি ক্লাস্টার মাস্টার-স্ল্যাভ রেপ্লিকেশনে রান করানো আবশ্যক।
* **Stripe Idempotency Key:** নেটওয়ার্ক Error-এর কারণে স্ট্রাইপে যেন একই বিলিং Data ২ বার সাবমিট না হয়, তার জন্য প্রতি রিকোয়েস্টে স্ট্রাইপ এপিআইতে অবশ্যই একটি ইউনিক `Idempotency-Key` (যেমন ইউজারের রিকোয়েস্ট আইডি বা ইউইউআইডি) হেডার হিসেবে পাঠাতে হবে।

---

### VII. Common Mistakes

🔴 Common Mistake

**ভুল ধারণা:** রেট লিমিটিং Algorithm রিলেশনাল Database Postgres বা MongoDB দিয়ে Code করা।

**বাস্তবতা:** রিলেশনাল Database ডিস্ক স্টোরেজ বা File আইও (I/O) স্পীডে চলে। প্রতি মিলিসেকেন্ডে প্রতি রিকোয়েস্টের জন্য ডাটাবেসে রিড-রাইট হিট মারলে Database-এর কনকারেন্সি লক হয়ে যাবে এবং তোমার পুরো ওয়েবসাইট ডাউন হয়ে যাবে। তাই রেট লিমিটের মান ক্যাশ করার জন্য সবসময় মাইক্রো-সেকেন্ড গতির ইন-Memory Redis-ই একমাত্র স্ট্যান্ডার্ড পছন্দ।

---

### VIII. Mental Model: পার্কিং লটের Token গেট

মিটারড বিলিং ও রেট লিমিটের মেন্টাল Model:

**"রেট লিমিট হলো পার্কিং লটের এন্ট্রি গেট যেখানে একটি নির্দিষ্ট বাকেটে Token রিফিল হয়। তোমার কাছে যথেষ্ট Token থাকলে গেট খুলে যায় এবং তুমি ভেতরে ঢুকতে পারো। আর মিটারড বিলিং হলো তোমার ট্যাক্সি মিটার—তুমি যতটুকু পথ চলবে (Tokens used), ট্যাক্সি ড্রাইভার ঠিক ততটুকু অনুযায়ী কিলোমিটার হিসেব করে মাসের শেষে বিল কাটবে।"**

---

### IX. Mini Project: স্ক্র্যাচ Token Bucket রিফিল এমুলেটর

চলো NumPy বা পাইথনে কোনো Database ছাড়া একটি সম্পূর্ণ বাকেট রিফিল ক্লাস Code করি এবং সেকেন্ডের ব্যবধানে বাকেটের ডাইনামিক রিফিল রেট Test করে ভিজুয়ালাইজ করি।

```python
import time

class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.refill_rate = refill_rate # Tokens per second
        self.tokens = capacity
        self.last_update = time.time()
        
    def consume(self, amount):
        now = time.time()
        elapsed = now - self.last_update
        
        # রিফিল Token যোগ
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_update = now
        
        if self.tokens >= amount:
            self.tokens -= amount
            return True
        return False

# Test রান
bucket = TokenBucket(capacity=10, refill_rate=2)
print("Consuming 8 tokens...", bucket.consume(8)) # True
print("Consuming 5 tokens...", bucket.consume(5)) # False (only 2 left)
print("Waiting 2 seconds for refill...")
time.sleep(2)
print("Consuming 5 tokens...", bucket.consume(5)) # True (refilled 4 tokens)
```

---

### X. Interview Questions

#### Beginner
1. **প্রশ্ন:** প্রথাগত সফটওয়্যারের চেয়ে AI সেস (AI SaaS)-এ রেট লিমিটিং কেন ভিন্নভাবে ডিজাইন করতে হয়?
   * **উত্তর:** প্রথাগত সফটওয়্যারে শুধু রিকোয়েস্ট কাউন্ট (RPM) করলেই চলে। কিন্তু AI-তে প্রতিটি রিকোয়েস্টের Context সাইজ ভিন্ন হওয়ায় Token ব্যবহারের মান অনেক ওঠানামা করে। তাই কস্টিং কন্ট্রোল করতে RPM এর পাশাপাশি Token পার মিনিট (TPM) রেট লিমিটিং ডিজাইন করা অত্যন্ত আবশ্যিক।

#### Intermediate
2. **প্রশ্ন:** "Token Bucket Algorithm" কীভাবে কাজ করে এবং এর সুবিধা কী?
   * **উত্তর:** Token বাকেট অ্যালগরিদমে একটি বাকেট ডিফাইন থাকে যা সর্বোচ্চ ধারণক্ষমতা পর্যন্ত Token হোল্ড করতে পারে এবং একটি নির্দিষ্ট সময় পরপর অটো-রিফিল হয়। সুবিধা হলো—এটি ট্র্যাফিক স্পাইক হ্যান্ডেল করতে পারে (কাস্টমার একবারে ১০টি Token কল করতে পারে), আবার কন্টিনিউয়াস স্প্যামিং বন্ধ করতে রিফিল রেট অনুযায়ী স্পীড কন্ট্রোল করে।

#### Advanced
3. **প্রশ্ন:** স্ট্রাইপ মিটারড বিলিংয়ে "Idempotency Key" ব্যবহার না করলে কী কমার্শিয়াল বিপর্যয় ঘটতে পারে?
   * **উত্তর:** যদি নেটওয়ার্ক সংযোগের সমস্যার কারণে AI Response সফল হওয়ার পর বিলিং রিপোর্ট সাবমিটের সময় রিকোয়েস্টটি ড্রপ করে এবং ব্যাকঅ্যান্ড আবার রি-ট্রাই করে, তবে আইডেমপোটেন্সি কী না থাকলে স্ট্রাইপ এটিকে দুটি আলাদা ব্যবহার হিসেবে গণ্য করবে। এর ফলে গ্রাহকের একই ব্যবহারের জন্য ২ বার বা ডবল বিলিং চার্জ হয়ে যাবে, যা কমার্শিয়াল লিগ্যাল ও ট্রাস্ট ক্রাইসিস তৈরি করবে।

---

### XI. Chapter Summary
* **TPM & RPM** AI সেস প্ল্যাটফর্মের আর্থিক ও নিরাপত্তা পাহারাদার।
* **Redis Token Bucket** ডাইনামিক ট্র্যাফিক অপটিমাইজ ও স্প্যামিং লক করে।
* **Stripe Metered Billing** কাস্টমার কস্টিং ট্র্যাক করে বৈশ্বিক পেমেন্ট পাইপলাইন এস্টাবলিশ করে।

---

### XII. What's Next
আমরা হ্যান্ডবুকের সমস্ত এডভান্সড কমার্শিয়াল AI Project ব্লুপ্রিন্ট ও তাদের ইনফ্রাস্ট্রাকচারাল মেকানিক্স সফলভাবে শেষ করেছি! 

এখন আমাদের সামনে কেবল শেষ এবং অত্যন্ত গাইডলাইন সমৃদ্ধ সমাপনী চ্যাপ্টার: **Part 12 — AI Career Roadmap এর Chapter 28: Transitioning to an AI Engineer / AI Architect**। কীভাবে একজন ট্র্যাডিশনাল Developer তার পূর্ববর্তী সব স্কিল ধরে রেখে AI ও এমএল ইকোসিস্টেমে মুভ করবে, কোন কোন Library প্র্যাকটিস করবে এবং কীভাবে রিয়েল Project পোর্টফোলিও বানাবে, তার একটি পূর্ণাঙ্গ ক্যারিয়ার গাইডলাইন ম্যাপ আমরা স্বহস্তে ডিকোড করবো।

---
**Chapter 27 সমাপ্ত।**
