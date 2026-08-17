# Chapter 9: Agent Observability & Evals (এজেন্ট ট্র্যাকিং ও মূল্যায়ন)

---

একটি সাধারণ ওয়েব অ্যাপ্লিকেশনে যদি এরর আসে, আমরা সেন্ট্রি বা ডেটাডগে স্ট্যাকট্রেস দেখে সাথে সাথে বুঝতে পারি ৫ নম্বর লাইনে `NullPointerException` এসেছে।

কিন্তু একটি AI এজেন্ট যখন ফেইল করে— সে হয়তো ৩ নম্বর স্টেপে একটি অপ্রয়োজনীয় সার্চ করেছে, ৪ নম্বর স্টেপে ভুল ডাটা ফিল্টার করেছে এবং ৬ নম্বর স্টেপে গিয়ে ভুল কনক্লুশনে পৌঁছেছে।

এখানে কোনো সাধারণ কোড ক্র্যাশ নেই; আছে **কগনিটিভ লজিক্যাল ফেইলিউর (Cognitive Failure)**।

এজন্য এজেন্টের জন্য প্রয়োজন বিশেষায়িত **Distributed Agent Tracing & Evaluation Frameworks**।

---

## ১. The Anatomy of an Agent Trace (ট্রেসের স্তরবিন্যাস)

[VISUAL]
Title: Hierarchical Distributed Span Tree for AI Agent Observability
```
[TRACE] Run Agent Task ("Fix DB Bug") ── [Total Time: 3.4s | Cost: $0.024]
  │
  ├── [SPAN 1] LLM Call (Think & Plan) ── [Time: 1.1s | Tokens: 450 | Model: Claude 3.7]
  │     └── Output: Tool Call `read_log_file(path='/var/log/db.err')`
  │
  ├── [SPAN 2] Tool Execution `read_log_file` ── [Time: 0.2s | Exit Code: 0]
  │     └── Output: "ERROR: Connection pool exhausted at max 20"
  │
  ├── [SPAN 3] LLM Call (Diagnose & Patch) ── [Time: 1.5s | Tokens: 820]
  │     └── Output: Tool Call `edit_config(pool_size=50)`
  │
  └── [SPAN 4] Tool Execution `edit_config` ── [Time: 0.1s | Exit Code: 0]
        └── Output: "Config updated successfully."
```

---

## ২. The 3 Golden Metrics of Agent Evals (এজেন্ট মূল্যায়নের ৩ স্তম্ভ)

```
                       ┌─────────────────────────────┐
                       │   AGENT EVALUATION TRIAD    │
                       └──────────────┬──────────────┘
                                      │
            ┌─────────────────────────┼─────────────────────────┐
            ▼                         ▼                         ▼
  ┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
  │ TASK SUCCESS RATE │     │  STEP EFFICIENCY  │     │ TOOL ACCURACY     │
  │     (Pass@1)      │     │  (Trajectory Opt) │     │ (Precision/Recall)│
  │ Did the agent     │     │ How many steps    │     │ Did it call the   │
  │ achieve the goal? │     │ did it take?      │     │ right tool?       │
  └───────────────────┘     └───────────────────┘     └───────────────────┘
```

1. **Task Success Rate (Pass@1 / Pass@k):** প্রদত্ত ১০০টি টেস্ট টাস্কের মধ্যে কয়টি টাস্ক স্বয়ংক্রিয়ভাবে পাস করেছে।
2. **Step Efficiency (Trajectory Length):** কাজটি কি ৩ স্টেপে শেষ করা গেছে নাকি এজেন্ট অপ্রয়োজনীয়ভাবে ১২ স্টেপ ঘোরাঘুরি করেছে।
3. **Tool Calling Precision:** সঠিক প্যারামিটারে সঠিক সময়ে টুল কল হয়েছে কি না।

---

## ৩. Open-Source Tracing with OpenInference & Phoenix

### কোড উদাহরণ: এজেন্টে অটো-ইনস্ট্রুমেন্টেশন যোগ করা

```python
from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor
from openinference.instrumentation.langchain import LangChainInstrumentor

# ১. লোকাল ফিনিক্স ট্রেসার ইনিশিয়ালাইজ করা (UI on http://localhost:6006)
tracer_provider = register(
    project_name="autonomous-agent-production",
    endpoint="http://localhost:6006/v1/traces"
)

# ২. ওপেনএআই ও ল্যাংগ্রাফ অটো-ইন্সট্রুমেন্ট করা
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
LangChainInstrumentor().instrument(tracer_provider=tracer_provider)

# এখন এজেন্ট যা কিছু রান করবে, প্রতি স্টেপের ইনপুট, আউটপুট, টোকেন ও কস্ট স্বয়ংক্রিয়ভাবে ফিনিক্সে ভিজ্যুয়ালাইজ হবে!
```

---
Developer Perspective
এজেন্ট মূল্যায়নের জন্য সবচেয়ে শক্তিশালী টেকনিক হলো **LLM-as-a-Judge with Ground Truth Trajectory**। শুধু ফাইনাল আউটপুট চেক না করে, এজেন্টের পুরো `Action Sequence` ভেরিফাই করো। যেমন: ডাটাবেস ফিক্স করার আগে সে ব্যাকআপ নিয়েছিল কি না— এই ইন্টারমিডিয়েট স্টেপগুলো ইভ্যালুয়েট করা প্রোডাকশন কোয়ালিটি নিশ্চিত করে।

---
Production Reality
প্রোডাকশনে ১ কোটি রিকোয়েস্ট আসলে সবগুলোর পূর্ণ ট্রেস সেভ করলে ক্লাউড স্টোরেজ বিল বিশাল হতে পারে। এজন্য প্রোডাকশন সিস্টেমে **Trace Sampling (যেমন ১০% র্যান্ডম ট্র্যাকিং)** এবং **Error-First Sampling (এরর বা ফেইল হওয়া টাস্কগুলো ১০০% ক্যাপচার করা)** পলিসি ব্যবহার করা হয়।

---
Common Mistake
ইভ্যালুয়েশন ডেটাসেট তৈরি না করে অন্ধের মতো এজেন্টের প্রম্পট পরিবর্তন করা। প্রম্পটে সামান্য ১ লাইন চেঞ্জ করলে কোনো একটি ক্ষেত্রে পারফর্মেন্স বাড়লেও অন্য ১০টি ক্ষেত্রে এজেন্টের আচরণ নষ্ট হতে পারে (Regression)। সবসময় একটি ফিক্সড ৫০-১০০ টাস্কের গোল্ডেন বেঞ্চমার্ক সেটে অটোমেটেড টেস্ট চালিয়ে তারপর নতুন প্রম্পট ডিপ্লয় করতে হবে।

---

## Interview Flashcards

#### Beginner Level
* **প্রশ্ন:** Agent Tracing সাধারণ লগিংয়ের চেয়ে কীভাবে আলাদা?
* **উত্তর:** সাধারণ লগিং কেবল প্লেইন টেক্সট দেখায়। Agent Tracing একটি হায়ারার্কিক্যাল স্প্যান ট্রির মাধ্যমে মডেলের থট, কোন প্রম্পট গিয়েছিল, কোন টুল কল হয়েছিল, কত টোকেন ও কত মিলি-সেকেন্ড খরচ হয়েছিল— পুরো এক্সিকিউশন ট্র্যাজেক্টরি ভিজ্যুয়ালাইজ করে।

#### Intermediate Level
* **প্রশ্ন:** Step Efficiency বলতে কী বোঝায়?
* **উত্তর:** একটি টাস্ক সফলভাবে সম্পন্ন করতে এজেন্টের সর্বনিম্ন প্রয়োজনীয় পদক্ষেপের সংখ্যা। কম স্টেপে নির্ভুল কাজ শেষ করা মানে কম লেটেন্সি ও কম টোকেন কস্ট।

#### Advanced Level
* **প্রশ্ন:** এজেন্টে Trajectory-level Evaluation কীভাবে করা হয়?
* **উত্তর:** শুধু ফাইনাল রেজাল্ট না দেখে এজেন্টের সম্পূর্ণ ডিসিশন পাথ (Step 1 $\to$ Step 2 $\to$ Step 3) নিরীক্ষা করা হয়। এতে কোনো অপ্রয়োজনীয় লুপ বা বিপজ্জনক স্টেপ নেওয়া হয়েছিল কি না তা নির্ধারণ করা যায়।
