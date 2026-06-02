# Chapter 21: Harness Engineering — Constitutional Guides & Evaluator Sensors

ধরো, তোমার কাছে দুনিয়ার সবচেয়ে শক্তিশালী Engine আছে।

কিন্তু সেই Engine-কে চাকার ওপর বসিয়ে ব্রেক আর স্টিয়ারিং ছাড়া হাইওয়েতে ছেড়ে দিলে কী হবে?

নিশ্চিত ক্র্যাশ!

AI-এর ক্ষেত্রেও কিন্তু ঠিক এই জিনিসটাই ঘটে।

মজার ব্যাপার হলো, ৬৫% এন্টারপ্রাইজ AI Project কিন্তু Model-এর দোষে ফেইল করে না।

ফেইল করে কারণ তার চারপাশের Harness ঠিক থাকে না।

সহজ কথায় বলতে গেলে, **Agent = Model + Harness**।

এখানে Model হলো গাড়ির Engine।

আর Harness হলো গাড়ির স্টিয়ারিং, ব্রেক আর সিটবেল্ট।

যেমন ধরো, `AGENTS.md` ফাইল দিয়ে Constitutional Guide বা নিয়ম সেট করা।

আবার Linter আর Unit Test দিয়ে Deterministic Sensor বসানো।

কিংবা LLM-as-a-Judge দিয়ে সাবজেক্টিভ টোন চেক করা।

এই নিরাপত্তাগুলো ছাড়া তোমার AI এজেন্ট প্রোডাকশনে গেলে নির্ঘাত Server ক্র্যাশ করবে, আর তোমার ওয়ালেট ড্রেইন করে দেবে!

তো চলো দেখি কীভাবে `AGENTS.md` কনফিগার করতে হয়।

জানবো Probabilistic আর Deterministic গার্ডরেইলের আসল তফাত কী।

আর কীভাবে Cascade Sensor Pipeline ডিজাইন করতে হয়।

এটা বুঝতে পারলে পরের চ্যাপ্টারের Observability, Tracing আর প্রোডাকশন Blueprint সব একদম পানির মতো সহজ হয়ে যাবে।

Deal?


### ১. রেসিং কার বনাম নিরাপত্তা বেষ্টনী

একটু ভেবে দেখো তো।

তুমি বাজারের সবচেয়ে শক্তিশালী রেসিং কারের Engine কিনে আনলে।

যেমন ধরো, একটা V12 Twin-Turbo Engine!

এটা হলো তোমার বেস AI Model বা LLM।

এখন তুমি যদি স্রেফ চাকা আর ইঞ্জিনের ওপর একটা সিট বসিয়ে হাইওয়েতে স্পিড তুলে দাও, তাহলে কী হবে?

গাড়িটা হয়তো সেকেন্ডে ৩০০ কিমি বেগে ছুটবে।

কিন্তু তোমার গাড়িতে কোনো স্টিয়ারিং নেই, ব্রেক নেই, সিটবেল্ট বা এয়ারব্যাগও নেই!

প্রথম বাঁকেই গাড়িটা ক্র্যাশ করবে, তাই না?

[VISUAL]
Title: Model alone vs. Model + Harness System
Illustration: Heavy high-speed engine vs. fully structured car chassis with dashboard, brakes, and safety systems
Placement: After Hook Section
Purpose: Show that a production Agent is a complete car, not just an engine.

```
Model Alone (High Risk Engine):
[ Massive GPU Engine (LLM) ] ──► (No steering/breaks) ──► Crash / Wallet Drainage 

Agent = Model + Harness (Flagship Safe Racing Car ✓):
[ Host Client ] ──► [ Guides (AGENTS.md) ] ──► [ Model Engine ] ──► [ Sensors (Evals) ] ──► Safe Response
```

আর যদি তুমি ইঞ্জিনের চারপাশে একটা মজবুত চেসিস বসাও?

साथে জোড়ো একটা দারুণ স্টিয়ারিং, ডিস্ক ব্রেক আর সুন্দর একটা ড্যাশবোর্ড স্ক্রিন?

তখনই কিন্তু এটা একটা সত্যিকারের স্পোর্টস কার হয়ে উঠবে!

এটাই হলো Agent = Model + Harness।

বিখ্যাত AI Engineer Mitchell Hashimoto এই সমীকরণটি আমাদের দেখিয়েছেন।

তাহলে মনে প্রশ্ন আসতে পারে— Model আর Harness-এর মূল পার্থক্যটা ঠিক কোথায়?

সহজ কথায়, Model হলো স্রেফ গাড়ির Engine।

এর কাজ শুধু Token ইনপুট নেওয়া আর Token আউটপুট দেওয়া।

আর Harness কী?

Harness হলো তোমার মেইন অ্যাপ্লিকেশনের চারপাশের নিরাপত্তা বেষ্টনী।

যা তোমার সিস্টেমকে একদম প্রোডাকশন-রেডি করে তোলে।


### ২. হারনেসের তিন স্তর

একটা কাস্টম Harness মূলত ৩টি স্তরে কাজ করে।

চলো এই স্তরগুলো একটু সহজভাবে বুঝে নিই।

[VISUAL]
Title: 3-Layer Harness Architecture
Illustration: Directed hierarchy mapping Guides down to the Execution Loop, guarded by Sensors on a Ground Truth context
Placement: After Core Concepts section
Purpose: Define the structural layers of a Harness.

```
┌────────────────────────────────────────────────────────┐
│                      HARNESS CONTAINER                 │
│                                                        │
│   ┌────────────────────────────────────────────────┐   │
│   │   Layer 1: GUIDES (System Prompts, AGENTS.md)  │   │
│   └───────────────────────┬────────────────────────┘   │
│                           │                            │
│                           ▼                            │
│   ┌────────────────────────────────────────────────┐   │
│   │   Layer 2: CONTEXT & STATES (Memory, RAG, ACL) │   │
│   └───────────────────────┬────────────────────────┘   │
│                           │                            │
│                           ▼                            │
│   ┌────────────────────────────────────────────────┐   │
│   │   Layer 3: SENSORS & EVALS (Linter, Unit Tests)│   │
│   └────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘
```

প্রথম স্তরটা কী?

এটা হলো **Layer 1: Guides** বা আমাদের সংবিধান।

এজেন্টকে গাইড করার জন্য এটা হলো আমাদের আগে থেকে লিখে রাখা রুল বুক।

যেমন ধরো, `AGENTS.md` ফাইল।

এটি একটি ওপেন ইন্ডাস্ট্রি Standard।

আমরা প্রজেক্টের রুট ডিরেক্টরিতে এই ফাইলটি রেখে দিই।

Cursor বা Claude Code-এর মতো টুলগুলো রান হওয়ার সময় এই ফাইলটি নিজে নিজেই পড়ে নেয়।

ফাইলটি পড়ে তারা প্রজেক্টের Coding Conventions, টেক স্ট্যাক আর কড়া নিষেধাজ্ঞাগুলো জেনে নেয়।

তাহলে দ্বিতীয় স্তরটা কী কাজ করে?

এটি হলো **Layer 2: Context & States**।

সহজ কথায়, এজেন্ট প্রতি Iteration-এ কী ডেটা দেখবে, তা এটি ঠিক করে দেয়।

এর ফলে আমাদের সিস্টেম Context Rot বা পুরনো ডেটার ঝামেলা থেকে বেঁচে যায়।

আর শেষ স্তরটা কী?

সেটা হলো **Layer 3: Sensors** বা আমাদের প্রতিরক্ষা ব্যবস্থা।

এজেন্ট যখন কোনো অ্যাকশন নেয় বা কোড জেনারেট করে, তখন সেটা ইউজারের কাছে যাওয়ার আগে এই সেন্সরগুলোর কঠিন টেস্ট পার হতে হয়।

এখানে দুই ধরনের সেন্সর কাজ করে।

প্রথমটা হলো **Computational Sensors**।

যেমন লিন্টার, টাইপ চেকার বা ইউনিট টেস্ট।

এগুলো পুরোপুরি Deterministic— মানে কোনো দ্বিধা ছাড়া ১০০% পাস অথবা ফেইল!

দ্বিতীয়টা হলো **LLM-as-a-Judge**।

কথার টোন কেমন, বা বাংলায় শালীনতা বজায় আছে কি না— এগুলো চেক করার জন্য একটা ছোট জাজ Model ব্যবহার করা হয়।

🧠 **একটি জরুরি কথা মনে রেখো**

Probabilistic Guide বা আমাদের কন্সটিটিউশনাল নির্দেশাবলী কিন্তু রুলস পুরোপুরি মানতে পারে না।

সে নিয়মগুলো ফলো করার চেষ্টা করে মাত্র ৭০% সময়।

কিন্তু Deterministic Sensor সিস্টেমকে ১০০% নিয়ম মানতে বাধ্য করে!

তাই নিরাপত্তার জন্য সবচেয়ে জরুরি নিয়মগুলো সব সময় Deterministic Sensor লেয়ারেই রাখা উচিত।


### ৩. ফিডব্যাক ও ভ্যালিডেশন লুপ

এজেন্ট যখন কোনো কোড লেখে এবং বলে যে সে কাজ শেষ করেছে, তখন কী হয়?

সেন্সর যদি দেখে কোডে সিন্ট্যাক্স ভুল আছে, তখন সে একটা অটোমেটিক লুপ তৈরি করে।

চলো দেখি এই লুপটা কীভাবে কাজ করে:

[VISUAL]
Title: Validation Sensor Loop
Illustration: Block diagram showing code output blocked by sensor, feedback generated, and model retrying
Placement: After validation loop section
Purpose: Ground the mathematical intuition of automated error recovery.

```
Agent: "I added the feature, done!" ──► [ POST-SENSOR (Linter/tsc) ] ──► FAIL! (Syntax Error)
                                                    │
[ Retry Force ] ◄── [ Feedback: "Fix Syntax line 5" ] ◄──┘
      │
      ▼
Agent: "Ah, my bad!" ──► [ Fixes Code ] ──► [ POST-SENSOR ] ──► PASS ✓ ──► Final User Output
```


### ৪. রিয়েল লাইফ উদাহরণ: Claude Code

অ্যানথ্রপিকের দারুণ সিএলআই এডিটর Claude Code-এর কথা তো জানো!

সে কীভাবে তোমার কোডবেস সুরক্ষিত রাখে, দেখেছ?

প্রথমে সে Constitutional Alignment-এর কাজ করে।

ওপেন হওয়ার সাথে সাথে সে প্রজেক্টের `CLAUDE.md` আর `AGENTS.md` ফাইলগুলো পড়ে নেয়।

এরপর আসে Deterministic Safety-র পালা।

তুমি যখন তাকে কোনো কোড পরিবর্তন করতে বলো, সে কোড লিখে সেভ করে।

তারপর ব্যাকগ্রাউন্ডে নিজে থেকেই `pnpm test` বা `npm run lint` রান করে।

টেস্ট ফেইল করলে সে নিজেই Error খুঁজে বের করে কোড ঠিক করে ফেলে!


### ৫. প্রজেক্টের AGENTS.md কনফিগারেশন

💻 **ডেভলপার ভিউ**

চলো এবার একটা স্ট্যান্ডার্ড `AGENTS.md` ফাইলের টেমপ্লেট দেখে নিই।

এটি তুমি তোমার প্রজেক্টের রুট ডিরেক্টরিতে ব্যবহার করতে পারো:

```markdown
# PocketSchool LMS — Developer Agent Guide

## Stack Info
- Backend: Node.js + NestJS + Prisma
- Frontend: Next.js (App Router)
- Database: PostgreSQL

## Code Conventions
- Use NestJS controller-service pattern (no raw express routes).
- Never hardcode dynamic credentials.
- Write unit tests under `.spec.ts` files.

## DO NOT Rules
- DO NOT delete database migrations manually.
- DO NOT use `console.log` in production (use NestJS Logger service).
- DO NOT expose `.env` credentials in any code commit.

## Evaluation & Test Command
- Run tests: `pnpm test`
- Lint check: `pnpm lint`
```


### ৬. প্রোডাকশনে সেন্সর অপ্টিমাইজেশন

🚀 **প্রোডাকশন রিয়েলিটি**

Inference-এর স্পিড বুস্ট করার জন্য প্রোডাকশন হারনেস ইঞ্জিনে Sensor Pruning নিশ্চিত করতে হয়।

কিন্তু সব সেন্সর যদি একসাথে রান করো, তাহলে কী হবে?

এতে সময় যেমন বেশি লাগবে, তেমনি কস্টও বেড়ে যাবে।

এর সমাধান হলো একটা Cascade Flow বা ধাপভিত্তিক পাইপলাইন তৈরি করা।

প্রথমে সবচেয়ে সস্তা আর ফাস্ট Computational Sensor রান করো।

যেমন লিন্টার, যা ১ মিলি-সেকেন্ডের কম সময়ে রান হয়।

লিন্টার পাস করলে এবার সেকেন্ড ধাপে Unit Tests রান করো।

আর সবশেষে সাবজেক্টিভ চেক করার জন্য সবচেয়ে দামি LLM-as-a-Judge রান করো।

এই বুদ্ধিমান অর্ডারিংয়ের কারণে কোনো ভুল থাকলে তা শুরুতেই ধরা পড়ে যায়।

ফলে আমাদের অনেক টাকা আর সময় বেঁচে যায়!


### ৭. কিছু সাধারণ ভুল

⚠️ **একটি সাধারণ ভুল**

অনেকেই ভাবেন, Prompt-এর ভেতর `"কখনো পিন কোড শেয়ার করবে না"` লিখে রাখলেই সিকিউরিটি নিশ্চিত!

কিন্তু আসল সত্যিটা কী?

Prompt-এর এই নিয়মগুলো আসলে Probabilistic।

হ্যাকাররা একটু বুদ্ধি খাটিয়ে জেইলব্রেক করলেই AI এই নিয়ম ভেঙে ফেলতে পারে।

তাহলে উপায়?

সবচেয়ে নিরাপদ উপায় হলো ব্যাকএন্ড কোডে Deterministic Filter বা ACL Sensor ব্যবহার করা।

এর মাধ্যমে রিকোয়েস্ট সরাসরি ব্লক করে দেওয়া যায়।


### ৮. মেন্টাল модель: ফুটবল খেলা

চলো পুরো বিষয়টা একটা সহজ খেলার নিয়মের সাথে মিলিয়ে নিই।

মনে করো, এটা একটা ফুটবল খেলা!

এখানে Guides বা `AGENTS.md` হলো বাউন্ডারি লাইন আর প্লেয়ারদের গাইডবুক।

প্লেয়াররা ভালো করেই জানে বল লাইনের বাইরে গেলে থ্রো-ইন হবে, আর কীভাবে ফাউল এড়াতে হবে।

তাহলে Sensors কী?

সেন্সর হলো মাঠের রেফারি!

রেফারি কিন্তু প্লেয়ারের মনের ভালো ইচ্ছা দেখতে যাবে না।

প্লেয়ার ফাউল করলেই রেফারি সাথে সাথে বাঁশি বাজিয়ে খেলা থামিয়ে দেবে।

আর নিয়ম ভাঙলে হলুদ কার্ড দেখিয়ে নিয়ম মানতে বাধ্য করবে!


### ৯. মিনি প্রজেক্ট: ক্যাসকেড সেন্সর পাইপলাইন

চলো এবার পাইথনে স্ক্র্যাচ থেকে একটা ৩-ধাপের ক্যাসকেড সেন্সর পাইপলাইন ডিজাইন করে ফেলি।

```python
import subprocess
import json

# ১. মক LLM-as-a-Judge ইভালুয়েটর
def llm_judge_sentiment(response_text):
    # পোলাইটনেস এবং বাংলায় টোন Quality জাজ
    if "তুই" in response_text or "খারাপ" in response_text:
        return {"pass": False, "reason": "Language is impolite."}
    return {"pass": True}

# ২. ক্যাসকেড সেন্সর পাইপলাইন
def run_cascade_sensors(code_response, text_response):
    print("Starting Cascade Sensor Evaluation...\n")
    
    # ধাপ ১: সস্তা সিমান্টিক লিন্ট চেক
    print("Step 1: Running Semantic Lint Check...")
    if len(code_response) < 10:
        print("[FAIL] Code is too short or empty!\n")
        return False
    print("Step 1 Pass ✓\n")
    
    # ধাপ ২: ইউনিট Test সিমুলেশন
    print("Step 2: Running Unit Tests...")
    if "error" in code_response.lower():
        print("[FAIL] Unit Tests compilation error!\n")
        return False
    print("Step 2 Pass ✓\n")
    
    # ধাপ ৩: দামি LLM-as-a-Judge রান
    print("Step 3: Running LLM-as-a-Judge Evaluation...")
    judge_res = llm_judge_sentiment(text_response)
    if not judge_res["pass"]:
        print(f"[FAIL] LLM Judge rejected: {judge_res['reason']}\n")
        return False
    print("Step 3 Pass ✓\n")
    
    print("[ALL SENSORS PASSED] Response is certified for Production! ")
    return True

# ৩. মক Test রান
print("--- TEST 1: Impolite Response Attack ---")
run_cascade_sensors("print('Success')", "তুই তো একটা খারাপ ছেলে।")

print("\n--- TEST 2: Valid Secure Response ---")
run_cascade_sensors("print('Success')", "প্রিয় কাস্টমার, তোমার পেমেন্ট সফল হয়েছে।")
```

#### কোডটি কীভাবে কাজ করছে?

চলো কোডের মূল বিষয়গুলো সহজে বুঝে নিই।

এখানে Input হিসেবে আমরা কী দিচ্ছি?

আমরা দিচ্ছি AI-এর তৈরি করা কোড আর চ্যাটের রেসপন্স টেক্সট।

আর Output হিসেবে কী পাচ্ছি?

তিনটি সেন্সর পার হয়ে আসার পর কোড আর টোনের সিকিউরিটি স্ট্যাটাস পাচ্ছি।

এটি কেন এত দারুণ কাজ করে?

কারণ এটি সস্তা থেকে দামি সেন্সরগুলো ক্রমানুসারে রান করে।

যার ফলে আমাদের Latency আর API খরচ দুটোই অনেক কমে যায়।

তুমি এটি কখন ব্যবহার করবে?

যখনই কোনো AI এজেন্টের আউটপুট প্রোডাকশনে পাঠানোর আগে ভ্যালিডেট করতে চাও।


### ১০. ইন্টারভিউয়ের কিছু প্রশ্ন

#### Beginner level

**প্রশ্ন:** 'Agent = Model + Harness' বলতে আসলে কী বোঝায়?

**উত্তর:** একটা LLM একা স্রেফ একটা Token Predictor Engine হিসেবে কাজ করে।

কিন্তু তাকে প্রোডাকশন-রেডি এজেন্ট বানাতে হলে তার চারপাশে সিকিউরিটি, মেমরি আর ভ্যালিডেশন গেটওয়ে তৈরি করতে হয়।

এই পুরো সিস্টেমটাকেই বলা হয় Harness।

#### Intermediate level

**প্রশ্ন:** প্রজেক্টের রুট ডিরেক্টরিতে `AGENTS.md` রাখার সুবিধা কী?

**উত্তর:** এটি প্রজেক্টের টেক স্ট্যাক, কোডিং নিয়ম আর নিষেধাজ্ঞাগুলো এক জায়গায় গুছিয়ে রাখে।

Cursor বা Claude Code-এর মতো টুলগুলো রান হওয়ার সময় এই ফাইলটি নিজে নিজেই পড়ে নেয়।

এর ফলে কোনো ভুল বোঝাবুঝি ছাড়াই সঠিক নিয়মে কোড জেনারেট করা সম্ভব হয়।

#### Advanced level

**প্রশ্ন:** প্রোডাকশনে Latency আর খরচ কমাতে Cascade Flow কীভাবে সাজাবে?

**উত্তর:** প্রথমে সবচেয়ে ফাস্ট আর সস্তা Computational Sensor (যেমন লিন্টার) রান করতে হবে।

সেটি পাস করলে দ্বিতীয় ধাপে Unit Tests রান করতে হবে।

আর সবশেষে সাবজেক্টিভ চেকের জন্য দামি LLM-as-a-Judge রান করতে হবে।

শুরুর কোনো ধাপে ভুল ধরা পড়লে পরের দামি স্টেপগুলো আর রান হয় না, ফলে খরচ ও সময় দুটোই বাঁচে।


### ১১. চ্যাপ্টার সামারি

তো এই চ্যাপ্টারে আমরা কী কী শিখলাম?

প্রথমত, প্রোডাকশনে AI সিস্টেম নিরাপদ রাখার জন্য Harness Engineering অত্যন্ত জরুরি।

দ্বিতীয়ত, `AGENTS.md` হলো প্রজেক্টের কন্সটিটিউশনাল রুল বুক।

দ্বিতীয়ত, Cascade Sensors ব্যবহার করে আমরা খুব সহজেই Latency আর খরচ কমিয়ে ফেলতে পারি।

আর সবশেষে মনে রেখো, বেশিরভাগ এন্টারপ্রাইজ AI প্রজেক্ট কিন্তু Harness-এর দুর্বলতার কারণেই ফেইল করে!


### ১২. সামনে কী আসছে?

দারুণ! হারনেস ইঞ্জিনিয়ারিং তো শিখে গেলাম।

পরের চ্যাপ্টারে আমরা দেখবো এজেন্টের চোখের মতো কাজ করা **Chapter 22: AI Observability & Monitoring**।

সেখানে আমরা LangSmith, Phoenix আর OpenTelemetry দিয়ে খরচ আর Latency ট্র্যাক করা শিখবো।

তো রেডি তো?

**Chapter 21 শেষ।**
