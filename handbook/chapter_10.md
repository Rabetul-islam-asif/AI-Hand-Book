# Chapter 10: Reasoning Models — Chain of Thought, R1 & o3


তুমি কি কখনো ভেবেছো — ChatGPT-র মতো পুরনো Model-গুলোকে যখন কোনো জটিল Math বা Coding-এর ধাঁধা জিজ্ঞেস করা হতো, তারা কেন সাথে সাথে ভুলভাল উত্তর দিয়ে বসতো?

আসলে তারা প্রশ্নের প্রথম শব্দটা দেখার সাথে সাথেই পরের শব্দটা কী হবে তা Predict করা শুরু করতো।

মানুষের মতো গভীরভাবে চিন্তা করে উত্তর দেওয়ার কোনো সুযোগ তাদের ছিল না।

এইখানেই জন্ম Reasoning Model-এর — যেমন OpenAI o1/o3, DeepSeek R1।

তো চলো এই Chapter-এ AI-এর এই দুর্দান্ত মাইলফলক — Reasoning Model-এর ভেতরের কাজ আর Logic খুব সহজে বুঝে নিই।

চলো শুরু করা যাক একটা সহজ উদাহরণ দিয়ে — চোখের পলকে উত্তর দেওয়া বনাম খাতার কোণায় খসড়া করার গল্প।



## ১. চোখের পলকে উত্তর বনাম খাতায় খসড়া করা

তোমার সামনে দুটি Math Problem দেওয়া হলো।

**প্রশ্ন ১:** $2 + 2 = ?$

তুমি চোখের পলকে উত্তর দেবে — $4$।

কোনো চিন্তা লাগেনি। মস্তিষ্ক Automatically উত্তর দিয়ে দিলো।

এটাকে বলে System 1 Thinking — দ্রুত, Subconscious, Instant।

**প্রশ্ন ২:** $23 \times 47 = ?$

এবার কী হলো?

চট করে উত্তর দিতে পারবে না। তোমাকে একটা কাগজ-কলম নিয়ে বসতে হবে।

ধাপে ধাপে হিসাব করতে হবে:

  * $20 \times 47 = 940$
  * $3 \times 47 = 141$
  * $940 + 141 = 1081$

এটা হলো System 2 Thinking — ধীর, Analytical, Logical।

![System 1 vs. System 2 Reasoning Architectures](/diagrams/system1_vs_system2.png)


তাহলে পুরনো GPT Model-গুলো কোন ক্যাটাগরিতে পড়ে?

সবগুলোই ছিল System 1 Thinking চালিত।

প্রশ্ন দেওয়া মাত্রই Token বাই Token উত্তর বলে দেওয়া শুরু।

কিন্তু **OpenAI o1/o3** আর **DeepSeek R1** — এরা প্রথমবারের মতো AI-তে ভালোভাবে System 2 Thinking নিয়ে এসেছে।

এরা সরাসরি উত্তর দেয় না।

এরা Background-এ একটা Invisible Scratchpad-এ Chain of Thought জেনারেট করে।

নিজের ভুল নিজে যাচাই করে।

তারপর Final উত্তর Produce করে।


## ২. Reasoning Engine-এর ভেতরে কী চলে?

### System 1 বনাম System 2

System 1 কী?

এটা তোমার Subconscious মন।

Language Model যখন Random Chatting করে বা কবিতা লেখে — সে Token বাই Token চোখের পলকে Generate করে যায়।

কোনো গভীর চিন্তা নেই। Instant Output।

System 2 কী?

এটা তোমার সচেতন মন।

জটিল Coding Bug Fix করা, Custom Architecture Design করা, Advanced Math Solve করা — এসব কাজে AI Model-কে তার Attention Process-কে একটা Reasoning Loop-এ আবদ্ধ রাখতে হয়।

ধীরে ধীরে ভেবে ভেবে উত্তর দিতে হয়।


### Chain of Thought — চিন্তার শিকল

![Chain of Thought Diagram](/diagrams/chain_of_thought.png)

Chain of Thought মানে কী?

AI-কে কোনো Problem এক লাইনে Solve করতে না বলে তাকে ধাপে ধাপে Process ভাঙতে বাধ্য করা।

এটা কীভাবে কাজ করে?

খুব সহজ একটা Trick আছে।

Prompt-এর শেষে শুধু `"Let's think step by step"` — এই চারটা শব্দ যোগ করো।

ব্যস, Model-এর Accuracy ৩০% পর্যন্ত Boost হতে পারে।

কেন কাজ করে?

কারণ Model তার নিজের Generate করা আগের Logical Step পড়ে পরের Logical Step Predict করে।

এতে তার Attention Head Focused থাকে।

ভুল করার সম্ভাবনা কমে।


🧠 Remember

Reasoning Model-এর মূল শক্তি হলো তার **Scratchpad Tokens**।

এই Token-গুলো Background-এ Compute হয়।

User-কে শুধু Final উত্তর দেখানো হয়।

তবে API ব্যবহার করলে এই Thinking Token-গুলোর জন্যও তোমাকে Pay করতে হবে।


### Reinforcement Learning আর DeepSeek R1

DeepSeek R1 একটা দারুণ জিনিস দেখিয়েছে।

কড়া তাত্ত্বিক গণিত ছাড়াই Reinforcement Learning ব্যবহার করে Model-কে Reasoning শেখানো সম্ভব।

কীভাবে?

তিনটা ধাপে।

**ধাপ ১ — Cold Start Data:**

প্রথমে কিছু হাজার High-Quality Chain of Thought Data দিয়ে Model-কে Fine-Tuning করা হয়।

এটাকে বলে SFT — Supervised Fine-Tuning।

**ধাপ ২ — RL Loop (পুরস্কার ও শাস্তি):**

এরপর Model-কে হাজার হাজার Problem Solve করতে দেওয়া হয়।

Model সঠিক উত্তর দিলে Reward পায়।

Chain of Thought-এ Logical ভুল করলে বা ভুল উত্তর দিলে Penalty পায়।

**ধাপ ৩ — Self-Correction:**

এই Trial ও Error Loop-এর মাধ্যমে Model নিজে নিজেই শেখে।

ভুল পথে হাঁটা শুরু করলে সাথে সাথে Backtrack করে সঠিক Track-এ ফিরে আসতে হয়।


## ৩. Monte Carlo Search Tree — Model কীভাবে সেরা পথ বাছে?

Reasoning Model-গুলো যখন কোনো জটিল দাবার চাল বা Coding Option বাছে — তারা Background-এ একটা Search Tree তৈরি করে।

ব্যাপারটা কী?

ধরো, একটা Problem Solve করতে তিনটা পথ আছে — Step A, Step B, Step C।

Model প্রতিটা পথের Value Score মেপে দেখে।

![Monte Carlo Tree Search (MCTS) in Reasoning](/diagrams/monte_carlo_tree_search_mcts_in_reasoning.png)

এখন Model দেখলো — Step B থেকে Step B2-তে গেলে Problem Solve হওয়ার সম্ভাবনা ৯২%।

আর Step A-তে গেলে মাত্র ১৫%।

তখন কী করবে?

Model সাথে সাথে Step A বাদ দিয়ে Step B-এর Chain ধরে এগিয়ে যাবে।

এটাই Monte Carlo Tree Search-এর মূল আইডিয়া।


## ৪. বাস্তব উদাহরণ — Cursor Agent-এর Bug Fixing

Cursor বা Devin যখন তোমার Repository-তে একটা জটিল Dependency Bug Fix করে — তখন কী ঘটে?

**Step 1 — System 2 চালু হয়:**

Agent দেখে সাধারণ Conditional Fix কাজ করছে না।

তখন সে তার Reasoning Mode On করে।

**Step 2 — Scratchpad Loop:**

Background Thinking Token-এ সে Analysis করে:

*"প্রথমে package.json Read করি... উমম, এখানে Prisma Version ৪.২। কিন্তু schema.prisma-তে Type Define করা ৫.০-এর। তাহলে কি Type Mismatch? হ্যাঁ! Let's run a migration..."*

**Step 3 — Self-Correction:**

Migration Run করতে গিয়ে Error আসলো।

কিন্তু Agent বিভ্রান্ত হয় না।

সে Error Log Scan করে বলে:

*"Migrate Fail করেছে কারণ Database Port Conflict। Let's check Docker..."*

**Step 4 — Final Action:**

Docker Port Fix করে Bug Resolve করে তোমাকে Solution Propose করে।

লক্ষ্য করো — পুরো Process-এ Agent নিজেই ভুল ধরেছে, নিজেই ঠিক করেছে।

এটাই Reasoning Model-এর আসল শক্তি।


## ৫. Developer View — নিজের Computer-এ DeepSeek R1 চালানো

💻 Developer View

Developer হিসেবে তুমি নিজের Computer-এ Ollama ব্যবহার করে DeepSeek-R1 Locally Run করতে পারো।

আর তার Chain of Thought Backend Script-এ Trap করতে পারো।

কীভাবে?

```python
import httpx

# ১. Local Ollama Server URL (Ollama locally running DeepSeek-R1 1.5B/8B)
OLLAMA_URL = "http://localhost:11434/api/generate"

# ২. রিজনিং Prompt
prompt = "রহিমের ৫টি কমলা আছে। সে যদুকে ২টি দিল এবং যদু তাকে ১টি আপেল দিল। রহিমের কাছে এখন কয়টি ফল আছে?"

payload = {
    "model": "deepseek-r1:1.5b",
    "prompt": prompt,
    "stream": False
}

# ৩. API রিকোয়েস্ট রান করো
print("AI থিংকিং প্রসেস সচল হচ্ছে (System 2)...")
response = httpx.post(OLLAMA_URL, json=payload, timeout=30.0)
result = response.json()['response']

# ৪. DeepSeek-R1 থিংকিং এবং ফাইনাল অ্যানসার আলাদা করো
# R1 Model তার চেইন অফ থট <think> এবং </think> ট্যাগের ভেতর রিটার্ন করে
thinking_start = result.find("<think>")
thinking_end = result.find("</think>")

if thinking_start != -1 and thinking_end != -1:
    thinking_process = result[thinking_start + 7 : thinking_end].strip()
    final_answer = result[thinking_end + 8 :].strip()
    
    print("\n--- AI THINKING PROCESS (Scratchpad) ---")
    print(thinking_process)
    print("\n--- FINAL ANSWER ---")
    print(final_answer)
```

Code-টা কী করছে?

**Input:** তুমি একটা Bangla Math Problem দিচ্ছো।

**Process:** DeepSeek-R1 `<think>` Tag-এর ভেতরে তার পুরো Thinking Process Return করে।

Script সেটা Parse করে Thinking আর Final Answer আলাদা করে দেখায়।

**Output:** তুমি দেখতে পাবে Model কীভাবে ধাপে ধাপে ভেবেছে, আর শেষ উত্তর কী দিয়েছে।


## ৬. Production-এ Reasoning Model ব্যবহারের হিসাব

🏭 Production Reality

Reasoning Model Production-এ Deploy করার আগে দুটো জিনিস অবশ্যই মাথায় রাখবে।

**Latency:**

সাধারণ Model ৫০০ Millisecond-এ উত্তর দেয়।

কিন্তু Reasoning Model ৫ থেকে ৩০ Second পর্যন্ত Thinking Loop-এ থাকতে পারে।

তাই Chat-এর Frontend-এ অবশ্যই **Streaming UI** আর **Loading State** রাখতে হবে।

নাহলে User মনে করবে App Hang হয়ে গেছে।

**Pricing:**

Thinking Token Generate করতে বেশি Memory আর GPU Compute লাগে।

তাই Reasoning API-এর Cost সাধারণ Generation API-এর চেয়ে ৩ থেকে ৫ গুণ বেশি।

Production-এ Budget Plan করার সময় এটা মাথায় রাখো।


## ৭. Common Mistake

🔴 Common Mistake

**ভুল ধারণা:**

সব ধরনের সাধারণ প্রশ্নের জন্যও Reasoning Model ব্যবহার করা উচিত।

যেমন — "বাংলাদেশের রাজধানী কী?"

**বাস্তবতা:**

এরকম Factual প্রশ্নের জন্য Reasoning Model ব্যবহার করা চরম অপচয়।

Latency বাড়বে। Cost বাড়বে। কিন্তু উত্তরের Quality বাড়বে না।

এসব প্রশ্নের জন্য **Flash/Lite Model** ব্যবহার করো — যেমন Gemini 2.5 Flash বা GPT-4o-mini।

সেটাই Production-Grade সেরা Decision।

সহজ নিয়ম মনে রাখো:

সহজ প্রশ্ন → Fast Model।

জটিল Reasoning → Reasoning Model।


## ৮. Mental Model — অভিজ্ঞ গণিতবিদ

Reasoning Model-কে কীভাবে মনে রাখবে?

**"Reasoning Model = খাতা-কলম হাতে বসা একজন খুব সতর্ক গণিতবিদ"**

তাকে কোনো জটিল প্রশ্ন দিলে সে হুট করে মুখ দিয়ে উত্তর বলে না।

সে তার Drawing খাতায় খসড়া কাটে।

প্রথমে একটা Equation লেখে।

ভুল হলে মুছে আবার লেখে।

সব হিসাব মিলিয়ে একদম শেষে সে Final Decision তোমাকে জানায়।


## ৯. Mini Project — Chain of Thought Prompting Classifier

চলো Python-এ একটা মজার জিনিস করি।

সাধারণ Decoder Model দিয়ে Custom Chain of Thought Emulate করবো।

মানে কী?

GPT-4o-mini বা Gemini Flash — এদের ভেতরে কিন্তু Built-in Reasoning নেই।

কিন্তু আমরা Prompt Engineering দিয়ে তাদেরকে ধাপে ধাপে ভাবতে বাধ্য করতে পারি।

কীভাবে? এই Prompt Template দেখো:

```python
# কাস্টম চেইন অফ থট Prompt টেমপ্লেট
cot_prompt_template = """
You are a senior system architect. Solve the following programming or design problem.

Follow this strict logical path:
1. Under a section named "1. PROBLEM ANALYSIS", break down the constraints and potential edge cases.
2. Under a section named "2. CRITICAL PATHS & FALLBACKS", analyze different architectural approaches and their tradeoffs.
3. Under a section named "3. STEP-BY-STEP SOLUTION", provide the final optimal code or configuration.

Problem:
{user_problem}

Let's solve this logically step by step:
"""

user_query = "আমাদের এমন একটি কাস্টম চ্যাট মেমরি পাইপলাইন ডিজাইন করতে হবে যা একই সাথে দ্রুত (Redis) এবং সাশ্রয়ী (Postgres)।"

formatted_prompt = cot_prompt_template.format(user_problem=user_query)
print("--- GENERATED COT PROMPT FOR PRODUCION ---")
print(formatted_prompt)
```

### Code Breakdown

**Input কী?**

User-এর একটা জটিল Architectural Design Query।

**Output কী?**

একটা Structured Thinking Prompt Template যেটা Model-কে ধাপে ধাপে ভাবতে Force করে।

**কেন কাজ করে?**

কারণ এই Template Model-এর Attention Head-কে Sequential Logical Analysis-এ আবদ্ধ করে।

ফলে Instant Hallucination Block হয়।

**কখন ব্যবহার করবে?**

Production-এ সাধারণ LLM Module দিয়ে জটিল Logical Output দরকার হলে।


## ১০. Interview Questions

### Beginner

**প্রশ্ন:** সাধারণ Language Model আর Reasoning Model-এর মূল পার্থক্য কী?

**উত্তর:** সাধারণ Model প্রশ্ন শোনার সাথে সাথে পরবর্তী Token সরাসরি Predict করে। এটা System 1।

কিন্তু Reasoning Model উত্তর দেওয়ার আগে Background Scratchpad-এ Chain of Thought ব্যবহার করে।

Logically Process ভেঙে Self-Correction করে।

তারপর Final Output দেয়। এটা System 2।

### Intermediate

**প্রশ্ন:** Chain of Thought Prompting কীভাবে AI-এর Accuracy Boost করে?

**উত্তর:** CoT Prompting Model-কে সরাসরি Final উত্তরে লাফ দেওয়ার বদলে মধ্যবর্তী Logical Sub-step Generate করতে বাধ্য করে।

Model যখন তার নিজের Generate করা আগের সঠিক Logic-গুলো Read করে Next Token Predict করে — তার Attention Focus Perfect থাকে।

Math বা Reasoning-এর ভুল কমে যায়।

### Advanced

**প্রশ্ন:** DeepSeek R1 কীভাবে Cold Start Data আর Reinforcement Learning ব্যবহার করে Self-Correction শিখিয়েছে?

**উত্তর:** R1 প্রথমে কিছু High-Quality Chain of Thought Data দিয়ে SFT সম্পন্ন করে।

এরপর RL Loop-এর মাধ্যমে Model-কে ক্রমাগত Problem Solve করতে দেয়।

উত্তরের সঠিকতা আর Logical Flow মেপে Dynamically Reward ও Penalty দেওয়া হয়।

এই Loop-এর মাধ্যমে Model নিজেই Chain of Thought-এর ভেতর ভুল পথ Detect করে Backtracking বা Self-Correction করার ক্ষমতা অর্জন করে।


## ১১. Chapter Summary

* **Reasoning Models** AI-তে System 2 Analytical Thinking Integrate করেছে।
* **Chain of Thought** আর **Scratchpad Tokens** Background-এ ভুল Fix করে Hallucination কমায়।
* **Reinforcement Learning** আর **MCTS** — Reasoning Model-এর Self-Optimization-এর চাবিকাঠি।
* Production-এ **Latency** আর **API Cost** Tradeoff সতর্কভাবে Balance করতে হবে।


## ১২. What's Next?

Reasoning Model-এর চমৎকার জগৎটা আমরা বুঝে ফেললাম।

পরবর্তী চ্যাপ্টারে আমরা শিখবো কীভাবে এই শক্তিশালী লার্জ ল্যাঙ্গুয়েজ মডেলগুলোকে সঠিক নির্দেশনা দিয়ে তাদের সর্বোচ্চ পারফরম্যান্স আদায় করা যায়।

আমরা প্রবেশ করছি প্রম্পট ইঞ্জিনিয়ারিংয়ের দুনিয়ায়!

**Chapter 11: Prompt Engineering Fundamentals — Zero-Shot, Few-Shot & Persona Prompting।**

সেখানে দেখবো কীভাবে সামান্য ইনস্ট্রাকশন আর উদাহরণ বদলে দিয়ে মডেলের রেসপন্স নিখুঁত করা যায়।

**Chapter 10 শেষ।**
