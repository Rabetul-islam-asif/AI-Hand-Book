# Chapter 21: Harness Engineering — Constitutional Guides & Evaluator Sensors



তোমার কাছে দুনিয়ার সবচেয়ে শক্তিশালী Engine আছে। কিন্তু সেই Engine-কে চাকার ওপর বসিয়ে ব্রেক ছাড়া, স্টিয়ারিং ছাড়া হাইওয়েতে ছেড়ে দিলে কী হবে? ক্র্যাশ। AI-এর ক্ষেত্রেও ঠিক তাই। মজার ব্যাপার হলো— ৬৫% এন্টারপ্রাইজ AI Project ফেইল করে Model-এর দোষে না, বরং তার চারপাশের Harness ভাঙা থাকায়।

সহজ কথায়, **Agent = Model + Harness**। Model হলো Engine, আর Harness হলো স্টিয়ারিং, ব্রেক, সিটবেল্ট— মানে `AGENTS.md` দিয়ে Constitutional Guide সেট করা, Linter আর Unit Test দিয়ে Deterministic Sensor বসানো, আর LLM-as-a-Judge দিয়ে সাবজেক্টিভ টোন চেক করা। এগুলো ছাড়া তোমার AI এজেন্ট প্রোডাকশনে গিয়ে Server ক্র্যাশ করবে, ওয়ালেট ড্রেইন করবে।

তো চলো দেখি কীভাবে `AGENTS.md` কনফিগার করতে হয়, Probabilistic বনাম Deterministic গার্ডরেইলের তফাত কী, আর Cascade Sensor Pipeline কীভাবে ডিজাইন করতে হয়। এটা বুঝলে পরের চ্যাপ্টারের Observability, Tracing আর প্রোডাকশন Blueprint সব ক্লিয়ার হয়ে যাবে।



### ১. Hook: শক্তিশালী ইঞ্জিনের রেসিং কার বনাম নিরাপত্তা বেষ্টনী

কল্পনা করো, তুমি বাজারে আসা সর্বকালের সবচেয়ে শক্তিশালী রেসিং কারের Engine (যেমন: V12 Twin-Turbo) তোমার গ্যারেজে আনলেন। এটি তোমার বেস AI Model (LLM)।
* **The Mess (Engine একা নিরুপায়):** তুমি স্রেফ চাকা ও ইঞ্জিনের ওপর সিট বসিয়ে হাইওয়েতে স্পিড তুলে দিলে। গাড়িটি সেকেন্ডে ৩০০ কিমি বেগে ছুটলো, কিন্তু তোমার গাড়িতে কোনো স্টিয়ারিং হুইল নেই, কোনো ব্রেক নেই, কোনো সিটবেল্ট নেই এবং এয়ারব্যাগও নেই! প্রথম বাঁকেই গাড়িটি ক্র্যাশ করে তোমাকে পঙ্গু করে দেবে।

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

* **The Flagship Car (Agent = Model + Harness):** তুমি ইঞ্জিনের চারপাশে শক্তিশালী চেসিস, perfect স্টিয়ারিং (Guides), ডিস্ক ব্রেক (Sensors), এবং ড্যাশবোর্ড স্ক্রিন (Observability) ফিট করে একটি প্রফেশনাল স্পোর্টস কার তৈরি করলে। 

সিনিয়র AI Engineer ও ইভোলিউশন Architect **Mitchell Hashimoto** (Co-founder of HashiCorp) ২০২৬ সালে AI স্পেসে এই perfect Equation-টা প্রতিষ্ঠা করো: **Agent = Model + Harness**। 
* **Model** হলো স্রেফ Engine (Token in, token out)।
* **Harness** হলো ওরিজিনাল Code-এর চারপাশের নিরাপত্তা ও কন্ট্রোল বডি, যা তোমার প্রডাক্টটিকে প্রোডাকশন-রেডি করে।


### ২. Core Concepts: হারনেস Architecture-এর তিন স্তর

একটি Custom হারনেস Engine মূলত ৩টি নিরাপত্তা স্তরের সমন্বয়ে গঠিত:

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
* **AGENTS.md:** এটি একটি ওপেন ইন্ডাস্ট্রি Standard (August 2025)। আমরা Project-এর রুট ফাইলে এই ফাইলটি রাখি। প্রোটোকল Server বা এডিটর (যেমন: Cursor, Claude Code) রান হওয়ার সময় অটো-রিড করে Project-এর Coding কনভেনশন, টেক স্ট্যাক এবং কড়া নিষেধাজ্ঞা (`DO NOT` rules) জেনে নেয়।

#### খ. Layer 2: Context & States (Data সোর্সিং)
এজেন্ট প্রতি Iteration-এ কী Data দেখবে তা অপ্টিমাইজ করা। এটি Context রট (Context Rot - পুরনো বা মিসম্যাচড Data) থেকে সিস্টেমকে রক্ষা করে।

#### গ. Layer 3: Sensors (প্রতিরক্ষা ব্যবস্থা)
এজেন্ট যখন কোনো অ্যাকশন বা Code Output Produce করে, সেটি রিয়েল ইউজারের কাছে যাওয়ার আগে কঠোর Test গেট Validation পার হতে হয়।
* **Computational Sensors:** লিন্টার, টাইপ চেকার বা ইউনিট Test। এগুলো **Deterministic** (১০০% পাস অথবা ফেইল, কোনো AI দ্বিধা নেই)।
* **LLM-as-a-Judge:** চ্যাট টোন, সাবজেক্টিভ মিনিং বা বাংলায় কথার শালীনতা ইভালুয়েশন করার জন্য Custom লাইটওয়েট জাজ Model (যেমন: GPT-4o-mini) ডিক্লেয়ার করা।

 Remember

**Probabilistic Guide (Constitutional instructions)** = Model রুলস ফলো করার চেষ্টা করে (সাধারণত ৭০% সময়)।  
**Deterministic Sensor (Linter/Tests/ACL)** = System রুলস মানতে বাধ্য করে (১০০% সময়)।  
নিরাপত্তা ও Data ইন্টিগ্রিটির জন্য ক্রুশিয়াল রুলস সবসময় **Deterministic Sensor** লেয়ারে Implement করা আবশ্যক।


### ৩. Visual Explanation: Validation Loop এবং Error ফিডব্যাক

এজেন্ট যখন কোনো Code লিখে ডিক্লেয়ার করে সে সাকসেসফুল হয়েছে, কিন্তু সেন্সর দেখে সিন্ট্যাক্স ভাঙা, তখন কীভাবে Validation Loop কাজ করে:

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


### ৪. Real World Example: Claude Code-এর বিল্ট-ইন হারনেস Engine

অ্যানথ্রপিকের ফ্ল্যাগশিপ সিএলআই এডিটর **Claude Code** যেভাবে তোমার কোডবেস প্রোটেক্ট করে:

1. **Constitutional Alignment:** এটি ওপেন হওয়ার সময় তোমার Project-এর `CLAUDE.md` এবং `AGENTS.md` রিড করে।
2. **Deterministic Safety:** তুমি যখন Code চেঞ্জ করতে বলো, সে Code লিখে সেভ করে এবং ব্যাকগ্রাউন্ডে Automatically তোমার Project-এর `pnpm test` বা `npm run lint` সেন্সর রান করে। Test ফেইল করলে সে নিজে থেকেই Error ডিটেক্ট করে Code রি-রাইট করে ফিক্স করে।


### ৫. Developer Perspective: Project রুট `AGENTS.md` Configuration

💻 Developer View

ইন্ডাস্ট্রি Standard Custom `AGENTS.md` টেমপ্লেট File যা তোমার ওএস-এ Deploy করতে হবে:

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


### ৬. Production Perspective: Sensor Pruning & Optimization

 Production Reality

Inference-এর স্পিড বুস্ট করার জন্য প্রোডাকশন হারনেস ইঞ্জিনে **Sensor Pruning** নিশ্চিত করতে হয়।

* **Sensor Order (সস্তা বনাম ব্যয়বহুল):** 
  সব সেন্সর একই সাথে রান করা প্রোডাকশন Latency ও কস্ট বাড়ায়। এর সমাধান হলো **Cascade Flow**:
  1. প্রথমে সবচেয়ে সস্তা এবং ফাস্ট **Computational Sensor** (যেমন: Linter - <১ মিলি-সেকেন্ড) রান করা।
  2. লিন্টার পাস করলে **Unit Tests** (<৫ সেকেন্ড) রান করা।
  3. সব পাস করলে final সাবজেক্টিভ চেক করতে সবচেয়ে দামি ও ধীরগতির **LLM-as-a-Judge** (<১ সেকেন্ড) রান করা।
  এর ফলে ফাস্ট ফেইলিউর অপ্টিমাইজড থাকে।


### ৭. Common Mistakes

🔴 Common Mistake

**ভুল ধারণা:** Prompt-এর ভেতর `"কখনোই পিন Code ডিসক্লোজ করবে না"` লিখে রাখলেই AI প্রোডাকশনে পিন সিকিউর রাখবে।

**বাস্তবতা:** Prompt Instruction হলো **Probabilistic** (প্রায়ই হ্যাকারদের Custom জেইলব্রেক Prompt-এর কাছে এটি হেরে যায়)। সিকিউরিটি-ক্রিটিক্যাল Data প্রটেক্ট করতে হলে Prompt-এর পাশাপাশি ব্যাকএন্ড কোডে **Deterministic Filter/ACL Sensor** দিয়ে রিকোয়েস্ট হার্ড ব্লক করা বাধ্যতামূলক।


### ৮. Mental Model: ফুটবল খেলার রেফারী ও বাউন্ডারি লাইন

হারনেস ও সেন্সর Mechanism-এর মেন্টাল Model:

* **Guides (AGENTS.md) = বাউন্ডারি লাইন ও প্লেয়ার গাইডবুক:**
  প্লেয়াররা জানে বল সীমানার বাইরে গেলে থ্রো-ইন হবে, এবং কীভাবে ফাউল এড়াতে হবে।
* **Sensors = রেফারি (The Judge):**
  রেফারি প্লেয়ারের মনের ভালো ইচ্ছা বোঝে না। প্লেয়ার যদি ফাউল করে বা বল লাইনের বাইরে মারেন, রেফারি সাথে সাথে বাঁশি বাজিয়ে খেলা থামিয়ে দেয় (Deterministic Action)। ভুল করলে রেফারি হলুদ কার্ড দেখিয়ে নিয়ম মানতে বাধ্য করে (Validation/Retry)।


### ৯. Mini Project: পাইথনে স্ক্র্যাচ থেকে একটি মাল্টি-স্টেপ ক্যাসকেড সেন্সর পাইপলাইন

চলো পাইথনে Custom পাইপলাইন ব্যবহার করে একটি প্রোডাকশন-গ্রেড ৩-ধাপের ক্যাসকেড সেন্সর (Computational -> Unit -> LLM-as-a-Judge) System ডিজাইন করি।

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

#### Code Breakdown:
* **Input:** AI-এর জেনারেট করা Code ও চ্যাট Response টেক্সট।
* **Output:** ক্যাসকেড ফিল্টারিংয়ের মাধ্যমে Code ও টোনের নিরাপত্তা Validation রেজাল্ট।
* **Why it works:** সস্তা থেকে দামি (Cascade) অর্ডারিং নিশ্চিত করে Latency ও API কস্ট মিনিমাইজ করে সাকসেসফুল ফিল্টারিং সম্পন্ন করেছে।
* **When to use:** AI এজেন্টের প্রোডাকশন গেটওয়ে ভ্যালিডেট করার জন্য।


### ১০. Interview Questions

#### Beginner
1. **প্রশ্ন:** সিনিয়র AI Architectদের তৈরি করা "Agent = Model + Harness" Equationের মূল তাৎপর্য কী?
   * **উত্তর:** লার্জ Language Model (LLM) একা শুধুমাত্র একটি স্ট্যাটিস্টিক্যাল Engine (Token Predictor)। এটিকে একটি প্রোডাকশন-রেডি নির্ভরযোগ্য স্বয়ংক্রিয় এজেন্টে convert করতে তার চারপাশে Code-এর যে সিকিউরিটি, মেমরি, অবজারভেবিলিটি এবং ডেসিশন গেটওয়ে তৈরি করা হয়, তাকেই **Harness** বলে।

#### Intermediate
2. **প্রশ্ন:** Project রুট ফাইলে `AGENTS.md` রাখার Architectural সুবিধা কী কী?
   * **উত্তর:** এটি Project-এর টেক স্ট্যাক, Coding কনভেনশন এবং নিষেধাজ্ঞাগুলো ওয়ান-প্লেসে ডিক্লেয়ার করে। Cursor বা Claude Code এর মতো মডার্ন এজেন্টগুলো রান হওয়ার সময় এই File অটো-রিড করে কোনো ওওএম বা Hallucination ফাটল ছাড়াই Companyর নির্দিষ্ট Coding Standard মেনে অটো-Code জেনারেট করতে পারে।

#### Advanced
3. **প্রশ্ন:** প্রোডাকশনে Latency এবং Compute কস্ট অপ্টিমাইজ করতে ইভালুয়েশন সেন্সরগুলোর অর্ডারিং বা "Cascade Flow" কীভাবে ডিজাইন করা উচিত?
   * **উত্তর:** ক্যাসকেড ফ্লো-তে প্রথমে সবচেয়ে দ্রুত এবং সস্তা **Computational Sensor** (যেমন: Linter, Regex - <১ মিলি-সেকেন্ড) রান করতে হবে। সেটি পাস করলে সেকেন্ডারি **Unit Tests/tsc** (<৫ সেকেন্ড) এবং সবশেষে ডমিন্যান্ট চেক করতে সবচেয়ে দামি ও ধীরগতির **LLM-as-a-Judge** (<১ সেকেন্ড) রান করা উচিত। এতে শুরুর কোনো ধাপে Error ডিটেক্ট হলে দামি API কল এড়িয়ে ইনস্ট্যান্ট ফাস্ট ফেইলিউর অপ্টিমাইজড থাকে।


### ১১. Chapter Summary
* **Harness Engineering** প্রোডাকশনে AI প্রডাক্টের নিরাপত্তা ও স্থায়িত্বের গোল্ড Standard।
* **AGENTS.md** Project-এর কন্সটিটিউশনাল রুলস ও কনভেনশন ডিক্লেয়ার করার ইউনিভার্সাল File।
* **Cascade Sensors** সস্তা থেকে দামি ক্রমানুসারে AI Output স্ক্যান করে Latency বাঁচায়।
* প্রোডাকশন এন্টারপ্রাইজে ৬৫% AI ফেইলিউর স্রেফ **Harness Defect**-এর কারণে ঘটে।


### ১২. What's Next
দারুণ! আমরা ভালোভাবে হারনেস Engineerিং ও নিরাপত্তা সেন্সরের কোর Architecture শেষ করে ফেলেছি। পরের chapter-এ আমরা এই প্রোডাকশন সিস্টেমের Window বা চোখের Mechanism নিয়ে আলোচনা করব: **Chapter 22: AI Observability & Monitoring**। ল্যাংস্মিথ (LangSmith), ফিনিক্স এবং ওপেন-টেলিমেন্ট্রি কীভাবে Agentic Loop-এর প্রতি মিলি-সেকেন্ডের API খরচ ও Latency ট্র্যাক করে, তা আমরা বিস্তারিত শিখব।

**Chapter 21 শেষ।**
