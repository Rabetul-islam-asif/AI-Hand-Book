# Chapter 21: Harness Engineering — Constitutional Guides & Evaluator Sensors

---

### Chapter Goal
এই চ্যাপ্টারের মূল লক্ষ্য হলো মডার্ন এআই ইঞ্জিনিয়ারিংয়ের সবচেয়ে অ্যাডভান্সড ডোমেইন—অর্থাৎ হারনেস ইঞ্জিনিয়ারিং (Harness Engineering - `Agent = Model + Harness`) এবং তার ইভালুয়েটর সেন্সর (Evaluator Sensors) মেকানিজম ক্র্যাক করা। আপনি জানতে পারবেন কীভাবে প্রজেক্ট রুট ফাইলে `AGENTS.md` ব্যবহার করে এজেন্টের কন্সটিটিউশনাল বাউণ্ডারি সেট করা হয় এবং প্রোবাবিলিস্টিক (Probabilistic) ও ডিটারমিনিস্টিক (Deterministic) গার্ডরেইলের টেকনিক্যাল সমন্বয় ঘটিয়ে এন্টারপ্রাইজ-গ্রেড স্ট্যাবল সিস্টেম আর্কিটেক্ট করতে হয়।

### Why Should I Care?
বাস্তবে দেখা গেছে, **৬৫% এন্টারপ্রাইজ এআই প্রোজেক্টের ফেইলিউরের কারণ মডেলের দুর্বলতা নয়; বরং হারনেস ডিফেক্ট (Harness Defect)।** ডেভেলপাররা মনে করেন জিপিটি-৫ আসলে তাদের চ্যাটবটের এরর ঠিক হবে, কিন্তু তাদের ভেতরের ফাইল রিডার বা কোড ভ্যালিডেটর সেন্সর ভাঙা থাকার কারণে এআই প্রতিনিয়ত ভুল ডিসিশন নেয়। কড়া ইভালুয়েশন ও সেন্সর সিস্টেম ডিজাইন করা আপনার প্রডাক্টকে ১০০% নির্ভরযোগ্য করবে।

### Big Picture
আগের চ্যাপ্টারগুলোতে আমরা টুল কলিং ও ইউনিভার্সাল এমসিপি (MCP) স্ট্যান্ডার্ড শিখেছি। এই চ্যাপ্টার থেকে আমাদের শুরু হচ্ছে **Production AI Systems** এর কোর পার্ট। এখানে শেখা হারনেস আর্কিটেকচার আমাদের পরবর্তী চ্যাপ্টারের অবজারভেবিলিটি (Tracing, LangSmith), সিকিউরিটি ও কস্ট অপ্টিমাইজেশন এবং কমপ্লিট প্রডাক্ট ব্লুপ্রিন্ট দাঁড় করানোর মূল ভিত্তি।

---

### ১. Hook: শক্তিশালী ইঞ্জিনের রেসিং কার বনাম নিরাপত্তা বেষ্টনী

কল্পনা করুন, আপনি বাজারে আসা সর্বকালের সবচেয়ে শক্তিশালী রেসিং কারের ইঞ্জিন (যেমন: V12 Twin-Turbo) আপনার গ্যারেজে আনলেন। এটি আপনার বেস এআই মডেল (LLM)।
* **The Mess (ইঞ্জিন একা নিরুপায়):** আপনি স্রেফ চাকা ও ইঞ্জিনের ওপর সিট বসিয়ে হাইওয়েতে স্পিড তুলে দিলেন। গাড়িটি সেকেন্ডে ৩০০ কিমি বেগে ছুটলো, কিন্তু আপনার গাড়িতে কোনো স্টিয়ারিং হুইল নেই, কোনো ব্রেক নেই, কোনো সিটবেল্ট নেই এবং এয়ারব্যাগও নেই! প্রথম বাঁকেই গাড়িটি ক্র্যাশ করে আপনাকে পঙ্গু করে দেবে।

[VISUAL]
Title: Model alone vs. Model + Harness System
Illustration: Heavy high-speed engine vs. fully structured car chassis with dashboard, brakes, and safety systems
Placement: After Hook Section
Purpose: Show that a production Agent is a complete car, not just an engine.

```
Model Alone (High Risk Engine):
[ Massive GPU Engine (LLM) ] ──► (No steering/breaks) ──► Crash / Wallet Drainage 💥

Agent = Model + Harness (Flagship Safe Racing Car ✓):
[ Host Client ] ──► [ Guides (AGENTS.md) ] ──► [ Model Engine ] ──► [ Sensors (Evals) ] ──► Safe Response
```

* **The Flagship Car (Agent = Model + Harness):** আপনি ইঞ্জিনের চারপাশে শক্তিশালী চেসিস, নিখুঁত স্টিয়ারিং (Guides), ডিস্ক ব্রেক (Sensors), এবং ড্যাশবোর্ড স্ক্রিন (Observability) ফিট করে একটি প্রফেশনাল স্পোর্টস কার তৈরি করলেন। 

সিনিয়র এআই ইঞ্জিনিয়ার ও ইভোলিউশন আর্কিটেক্ট **Mitchell Hashimoto** (Co-founder of HashiCorp) ২০২৬ সালে এআই স্পেসে এই নিখুঁত সমীকরণটি প্রতিষ্ঠা করেন: **Agent = Model + Harness**। 
* **Model** হলো স্রেফ ইঞ্জিন (Token in, token out)।
* **Harness** হলো ওরিজিনাল কোডের চারপাশের নিরাপত্তা ও কন্ট্রোল বডি, যা আপনার প্রডাক্টটিকে প্রোডাকশন-রেডি করে।

---

### ২. Core Concepts: হারনেস আর্কিটেকচারের তিন স্তর

একটি কাস্টম হারনেস ইঞ্জিন মূলত ৩টি নিরাপত্তা স্তরের সমন্বয়ে গঠিত:

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

#### ক. Layer 1: Guides (সংবিধান)
এজেন্টকে গাইড করার জন্য আগে থেকে ডিফাইন করা রুল বুক।
* **AGENTS.md:** এটি একটি ওপেন ইন্ডাস্ট্রি স্ট্যান্ডার্ড (August 2025)। আমরা প্রোজেক্টের রুট ফাইলে এই ফাইলটি রাখি। প্রোটোকল সার্ভার বা এডিটর (যেমন: Cursor, Claude Code) রান হওয়ার সময় অটো-রিড করে প্রজেক্টের কোডিং কনভেনশন, টেক স্ট্যাক এবং কড়া নিষেধাজ্ঞা (`DO NOT` rules) জেনে নেয়।

#### খ. Layer 2: Context & States (ডাটা সোর্সিং)
এজেন্ট প্রতি ইটারেশনে কী ডেটা দেখবে তা অপ্টিমাইজ করা। এটি কনটেক্সট রট (Context Rot - পুরনো বা মিসম্যাচড ডেটা) থেকে সিস্টেমকে রক্ষা করে।

#### গ. Layer 3: Sensors (প্রতিরক্ষা ব্যবস্থা)
এজেন্ট যখন কোনো অ্যাকশন বা কোড আউটপুট প্রডিউস করে, সেটি রিয়েল ইউজারের কাছে যাওয়ার আগে কঠোর টেস্ট গেট ভ্যালিডেশন পার হতে হয়।
* **Computational Sensors:** লিন্টার, টাইপ চেকার বা ইউনিট টেস্ট। এগুলো **Deterministic** (১০০% পাস অথবা ফেইল, কোনো এআই দ্বিধা নেই)।
* **LLM-as-a-Judge:** চ্যাট টোন, সাবজেক্টিভ মিনিং বা বাংলায় কথার শালীনতা ইভালুয়েশন করার জন্য কাস্টম লাইটওয়েট জাজ মডেল (যেমন: GPT-4o-mini) ডিক্লেয়ার করা।

🧠 Remember

**Probabilistic Guide (Constitutional instructions)** = মডেল রুলস ফলো করার চেষ্টা করে (সাধারণত ৭০% সময়)।  
**Deterministic Sensor (Linter/Tests/ACL)** = সিস্টেম রুলস মানতে বাধ্য করে (১০০% সময়)।  
নিরাপত্তা ও ডেটা ইন্টিগ্রিটির জন্য ক্রুশিয়াল রুলস সবসময় **Deterministic Sensor** লেয়ারে ইমপ্লিমেন্ট করা আবশ্যক।

---

### ৩. Visual Explanation: ভ্যালিডেশন লুপ এবং এরর ফিডব্যাক

এজেন্ট যখন কোনো কোড লিখে ডিক্লেয়ার করে সে সাকসেসফুল হয়েছে, কিন্তু সেন্সর দেখে সিন্ট্যাক্স ভাঙা, তখন কীভাবে ভ্যালিডেশন লুপ কাজ করে:

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

---

### ৪. Real World Example: Claude Code-এর বিল্ট-ইন হারনেস ইঞ্জিন

অ্যানথ্রপিকের ফ্ল্যাগশিপ সিএলআই এডিটর **Claude Code** যেভাবে আপনার কোডবেস প্রোটেক্ট করে:

1. **Constitutional Alignment:** এটি ওপেন হওয়ার সময় আপনার প্রজেক্টের `CLAUDE.md` এবং `AGENTS.md` রিড করে।
2. **Deterministic Safety:** আপনি যখন কোড চেঞ্জ করতে বলেন, সে কোড লিখে সেভ করে এবং ব্যাকগ্রাউন্ডে অটোমেটিক্যালি আপনার প্রোজেক্টের `pnpm test` বা `npm run lint` সেন্সর রান করে। টেস্ট ফেইল করলে সে নিজে থেকেই এরর ডিটেক্ট করে কোড রি-রাইট করে ফিক্স করে।

---

### ৫. Developer Perspective: প্রজেক্ট রুট `AGENTS.md` কনফিগারেশন

💻 Developer View

ইন্ডাস্ট্রি স্ট্যান্ডার্ড কাস্টম `AGENTS.md` টেমপ্লেট ফাইল যা আপনার ওএস-এ ডিপ্লয় করতে হবে:

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

---

### ৬. Production Perspective: Sensor Pruning & Optimization

🏭 Production Reality

ইনফারেন্সের স্পিড বুস্ট করার জন্য প্রোডাকশন হারনেস ইঞ্জিনে **Sensor Pruning** নিশ্চিত করতে হয়।

* **Sensor Order (সস্তা বনাম ব্যয়বহুল):** 
  সব সেন্সর একই সাথে রান করা প্রোডাকশন ল্যাটেন্সি ও কস্ট বাড়ায়। এর সমাধান হলো **Cascade Flow**:
  1. প্রথমে সবচেয়ে সস্তা এবং ফাস্ট **Computational Sensor** (যেমন: Linter - <১ মিলি-সেকেন্ড) রান করা।
  2. লিন্টার পাস করলে **Unit Tests** (<৫ সেকেন্ড) রান করা।
  3. সব পাস করলে চূড়ান্ত সাবজেক্টিভ চেক করতে সবচেয়ে দামি ও ধীরগতির **LLM-as-a-Judge** (<১ সেকেন্ড) রান করা।
  এর ফলে ফাস্ট ফেইলিউর অপ্টিমাইজড থাকে।

---

### ৭. Common Mistakes

🔴 Common Mistake

**ভুল ধারণা:** প্রম্পটের ভেতর `"কখনোই পিন কোড ডিসক্লোজ করবে না"` লিখে রাখলেই এআই প্রোডাকশনে পিন সিকিউর রাখবে।

**বাস্তবতা:** প্রম্পট ইনস্ট্রাকশন হলো **Probabilistic** (প্রায়ই হ্যাকারদের কাস্টম জেইলব্রেক প্রম্পটের কাছে এটি হেরে যায়)। সিকিউরিটি-ক্রিটিক্যাল ডেটা প্রটেক্ট করতে হলে প্রম্পটের পাশাপাশি ব্যাকএন্ড কোডে **Deterministic Filter/ACL Sensor** দিয়ে রিকোয়েস্ট হার্ড ব্লক করা বাধ্যতামূলক।

---

### ৮. Mental Model: ফুটবল খেলার রেফারী ও বাউন্ডারি লাইন

হারনেস ও সেন্সর মেকানিজমের মেন্টাল মডেল:

* **Guides (AGENTS.md) = বাউন্ডারি লাইন ও প্লেয়ার গাইডবুক:**
  প্লেয়াররা জানে বল সীমানার বাইরে গেলে থ্রো-ইন হবে, এবং কীভাবে ফাউল এড়াতে হবে।
* **Sensors = রেফারি (The Judge):**
  রেফারি প্লেয়ারের মনের ভালো ইচ্ছা বোঝে না। প্লেয়ার যদি ফাউল করে বা বল লাইনের বাইরে মারেন, রেফারি সাথে সাথে বাঁশি বাজিয়ে খেলা থামিয়ে দেয় (Deterministic Action)। ভুল করলে রেফারি হলুদ কার্ড দেখিয়ে নিয়ম মানতে বাধ্য করে (Validation/Retry)।

---

### ৯. Mini Project: পাইথনে স্ক্র্যাচ থেকে একটি মাল্টি-স্টেপ ক্যাসকেড সেন্সর পাইপলাইন

চলুন পাইথনে কাস্টম পাইপলাইন ব্যবহার করে একটি প্রোডাকশন-গ্রেড ৩-ধাপের ক্যাসকেড সেন্সর (Computational -> Unit -> LLM-as-a-Judge) সিস্টেম ডিজাইন করি।

```python
import subprocess
import json

# ১. মক LLM-as-a-Judge ইভালুয়েটর
def llm_judge_sentiment(response_text):
    # পোলাইটনেস এবং বাংলায় টোন কোয়ালিটি জাজ
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
    
    # ধাপ ২: ইউনিট টেস্ট সিমুলেশন
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
    
    print("[ALL SENSORS PASSED] Response is certified for Production! 🎉")
    return True

# ৩. মক টেস্ট রান
print("--- TEST 1: Impolite Response Attack ---")
run_cascade_sensors("print('Success')", "তুই তো একটা খারাপ ছেলে।")

print("\n--- TEST 2: Valid Secure Response ---")
run_cascade_sensors("print('Success')", "প্রিয় কাস্টমার, আপনার পেমেন্ট সফল হয়েছে।")
```

#### Code Breakdown:
* **Input:** এআই-এর জেনারেট করা কোড ও চ্যাট রেসপন্স টেক্সট।
* **Output:** ক্যাসকেড ফিল্টারিংয়ের মাধ্যমে কোড ও টোনের নিরাপত্তা ভ্যালিডেশন রেজাল্ট।
* **Why it works:** সস্তা থেকে দামি (Cascade) অর্ডারিং নিশ্চিত করে ল্যাটেন্সি ও এপিআই কস্ট মিনিমাইজ করে সাকসেসফুল ফিল্টারিং সম্পন্ন করেছে।
* **When to use:** এআই এজেন্টের প্রোডাকশন গেটওয়ে ভ্যালিডেট করার জন্য।

---

### ১০. Interview Questions

#### Beginner
1. **প্রশ্ন:** সিনিয়র এআই আর্কিটেক্টদের তৈরি করা "Agent = Model + Harness" সমীকরণের মূল তাৎপর্য কী?
   * **উত্তর:** লার্জ ল্যাঙ্গুয়েজ মডেল (LLM) একা শুধুমাত্র একটি স্ট্যাটিস্টিক্যাল ইঞ্জিন (Token Predictor)। এটিকে একটি প্রোডাকশন-রেডি নির্ভরযোগ্য স্বয়ংক্রিয় এজেন্টে রূপান্তর করতে তার চারপাশে কোডের যে সিকিউরিটি, মেমরি, অবজারভেবিলিটি এবং ডেসিশন গেটওয়ে তৈরি করা হয়, তাকেই **Harness** বলে।

#### Intermediate
2. **প্রশ্ন:** প্রজেক্ট রুট ফাইলে `AGENTS.md` রাখার আর্কিটেকচারাল সুবিধা কী কী?
   * **উত্তর:** এটি প্রজেক্টের টেক স্ট্যাক, কোডিং কনভেনশন এবং নিষেধাজ্ঞাগুলো ওয়ান-প্লেসে ডিক্লেয়ার করে। Cursor বা Claude Code এর মতো মডার্ন এজেন্টগুলো রান হওয়ার সময় এই ফাইল অটো-রিড করে কোনো ওওএম বা হ্যালুসিনেশন ফাটল ছাড়াই কোম্পানির নির্দিষ্ট কোডিং স্ট্যান্ডার্ড মেনে অটো-কোড জেনারেট করতে পারে।

#### Advanced
3. **প্রশ্ন:** প্রোডাকশনে ল্যাটেন্সি এবং কম্পিউট কস্ট অপ্টিমাইজ করতে ইভালুয়েশন সেন্সরগুলোর অর্ডারিং বা "Cascade Flow" কীভাবে ডিজাইন করা উচিত?
   * **উত্তর:** ক্যাসকেড ফ্লো-তে প্রথমে সবচেয়ে দ্রুত এবং সস্তা **Computational Sensor** (যেমন: Linter, Regex - <১ মিলি-সেকেন্ড) রান করতে হবে। সেটি পাস করলে সেকেন্ডারি **Unit Tests/tsc** (<৫ সেকেন্ড) এবং সবশেষে ডমিন্যান্ট চেক করতে সবচেয়ে দামি ও ধীরগতির **LLM-as-a-Judge** (<১ সেকেন্ড) রান করা উচিত। এতে শুরুর কোনো ধাপে এরর ডিটেক্ট হলে দামি এপিআই কল এড়িয়ে ইনস্ট্যান্ট ফাস্ট ফেইলিউর অপ্টিমাইজড থাকে।

---

### ১১. Chapter Summary
* **Harness Engineering** প্রোডাকশনে এআই প্রডাক্টের নিরাপত্তা ও স্থায়িত্বের গোল্ড স্ট্যান্ডার্ড।
* **AGENTS.md** প্রজেক্টের কন্সটিটিউশনাল রুলস ও কনভেনশন ডিক্লেয়ার করার ইউনিভার্সাল ফাইল।
* **Cascade Sensors** সস্তা থেকে দামি ক্রমানুসারে এআই আউটপুট স্ক্যান করে ল্যাটেন্সি বাঁচায়।
* প্রোডাকশন এন্টারপ্রাইজে ৬৫% এআই ফেইলিউর স্রেফ **Harness Defect**-এর কারণে ঘটে।

---

### ১২. What's Next
দারুণ! আমরা সফলভাবে হারনেস ইঞ্জিনিয়ারিং ও নিরাপত্তা সেন্সরের কোর আর্কিটেকচার জয় করে ফেলেছি। পরবর্তী চ্যাপ্টারে আমরা এই প্রোডাকশন সিস্টেমের উইন্ডো বা চোখের মেকানিজম নিয়ে আলোচনা করব: **Chapter 22: AI Observability & Monitoring**। ল্যাংস্মিথ (LangSmith), ফিনিক্স এবং ওপেন-টেলিমেন্ট্রি কীভাবে এজেন্টিক লুপের প্রতি মিলি-সেকেন্ডের এপিআই খরচ ও ল্যাটেন্সি ট্র্যাক করে, তা আমরা বিস্তারিত শিখব।

---
**Chapter 21 সমাপ্ত।**
