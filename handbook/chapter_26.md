# Chapter 26: Blueprint 3 — Agentic CLI Code Writer with Auto-Test Healing

---

### Chapter Goal
এই চ্যাপ্টারের মূল লক্ষ্য হলো একটি খুব শক্তিশালী সায়েন্স-ফিকশন লেভেলের AI এজেন্ট Ecosystem নিজের হাতে তৈরি করা। আমরা রিঅ্যাক্ট (ReAct: Reason + Act) Pattern ব্যবহার করে এমন একটি কমান্ড-লাইন অটোমেটিক Code রাইটার এজেন্ট (Agentic CLI Code Writer) দাঁড় করাবো, যা ইউজারের ইন্সট্রাকশন শুনে তোমার লোকাল Computeারে Code File তৈরি করবে, নিজেই টার্মিনালে Test স্ক্রিপ্ট রান করবে এবং Test ফেইল করলে ডাইনামিকালি Error বা ট্র্যাকিং Log রিড করে Automatically Code এডিট বা সেলফ-হিলিং (Auto-Test Healing) সম্পন্ন করবে।

### Why Should I Care?
পুরনো ধাঁচের চ্যাটবট শুধু Code লিখে চ্যাটবক্সে শো করতে পারে। কিন্তু সেই কোডে কোনো সিনট্যাক্স Error আছে কি না বা রিয়েল ডিপেনডেন্সি ক্র্যাশ করছে কি না, তা চ্যাটবট নিজে রান না করে জানতে পারে না। Devin বা Cursor Agent-এর মতো revolutionary AI কো-পাইলট System গড়ার পেছনের মূল বিষয় হলো এই সেলফ-Testing ও হিলিং Loop। একজন AI Engineer হিসেবে এজেন্ট Loop Architecture রপ্ত করতে পারলে তুমি যেকোনো সাধারণ সফটওয়্যারকে স্বয়ংক্রিয় AI এজেন্টে convert করতে পারবে।

### Big Picture
এটি আমাদের বাস্তব Project Blueprint লেয়ারের তৃতীয় এবং সবচেয়ে অ্যাডভান্সড কাইন্ডের ফ্ল্যাগশিপ মাইলফলক। আগের চ্যাপ্টারগুলোতে আমরা থিওরিটিক্যাল টুল কলিং, Function স্কিমাস এবং Conditional Loop শিখেছি। এই চ্যাপ্টারে আমরা সেগুলোকে Practical ডকার বা লোকাল কমান্ড এক্সিকিউট পাইপলাইনে রূপ দেবো।

---

### ১. The Problem: অন্ধ কোডারের ছটফটানি ও Error হিলিং

একটি সাধারণ AI যখন Code জেনারেট করে:
```python
# AI Generated code
import request  # Oops! It should be 'requests' with an 's'
```
ইউজার যখন Code রান করতে যাও, স্ক্রিনে বড় লাল Error আসে: `ModuleNotFoundError: No module named 'request'`। ইউজারকে আবার সেই Error কপি করে AI-তে পেস্ট করতে হয়। এই বারবার কপি-পেস্ট করা ডেভেলপারের মূল্যবান সময় নষ্ট করে।

#### প্রোডাকশন সলিউশন: রিঅ্যাক্ট এজেন্ট Loop (Reason + Act Loop with Auto-Healing)
আমাদের সেলফ-হিলিং এজেন্ট Loop নিচের ৪টি সিকোয়েনশিয়াল ধাপে Loop আকারে কাজ করে:
1. **Think (পরিকল্পনা):** এলএলএম Prompt Analysis করে ডিসিশন নেয় কোন Library বা Code লিখতে হবে।
2. **Write (অ্যাকশন ১):** এজেন্ট তার ওন Custom Code রাইটিং টুল ব্যবহার করে লোকাল Computeারে `app.py` এবং একটি `test_app.py` File তৈরি করে।
3. **Execute Test (অ্যাকশন ২):** এজেন্ট লোকাল টার্মিনালে সাব-প্রসেস রান করে Test কমান্ডটি এক্সিকিউট করে: `pytest test_app.py`।
4. **Self-Heal (পর্যবেক্ষণ ও ভুল fix):** Test যদি ফেইল করে, এজেন্ট কিন্তু হাল ছাড়ে না। সে টেস্টের Output ও লাল Error লগটি সরাসরি রিড করে তার ব্রেইনে ফিড করে এবং তার Code fix করে আবার নতুন করে লেখে। Test ১০০% পাস হওয়া না পর্যন্ত এই Loop বারবার চলতে থাকে।

[VISUAL]
Title: Agentic Self-Healing Loop Flowchart
Illustration: Loop cycle between LLM Generator, Write File, Run Subprocess pytest, Catch Failure, Feedback Error, and rewrite
Placement: After Hook Section
Purpose: Provide architectural mapping of the self-correcting agent loop.

```
          ┌────────────────────────────────────────┐
          ▼                                        │
    ┌───────────┐       ┌────────────┐             │
    │🧠  Think  │ ────► │ 🛠️ Act:    │             │
    │   (LLM)   │       │ Write Code │             │
    └───────────┘       └────────────┘             │ (If test fails,
          ▲                    │                   │  feed error back)
          │                    ▼                   │
          │             ┌────────────┐             │
          │             │ 💻 Run     │             │
          │             │ Pytest     │             │
          │             └────────────┘             │
          │                    │                   │
          │                    ▼                   │
          │             /────────────\             │
          │            /   Does it    \            │
          └───────────┤    Pass?       ├───────────┘
                       \              /
                        \────────────/
                               │ Yes
                               ▼
                        [ Done & Saved! ]
```

---

### ২. Core Concepts: এজেন্ট ইঞ্জিনের মূল ভিত্তি

#### ক. The ReAct Framework (রিঅ্যাক্ট ফ্রেমওয়ার্ক)
রিঅ্যাক্ট হলো AI এজেন্টের মনস্তাত্ত্বিক ফ্রেমওয়ার্ক:
* **Thought (চিন্তা):** *"আমি একটি Mathematical ক্যালকুলেটর Function লিখতে চাই। প্রথমে আমার ফাইলটি রাইট করা উচিত।"*
* **Action (কাজ):** Custom Function কল করা (যেমন `write_file_to_disk`).
* **Observation (পর্যবেক্ষণ):** টার্মিনাল রান করার পর দেখা গেল Test সাকসেসফুল। এজেন্টের সিদ্ধান্ত: *"আমার কাজ সফল হয়েছে, এবার আমি Loop ক্লোজ করতে পারি।"*

#### খ. Executing Subprocesses in Python (লোকাল কমান্ড রান করার লজিক)
এজেন্টকে কমান্ড রান করার ক্ষমতা দিতে পাইথনের `subprocess` মডিউল ব্যবহার করা হয়।
* **নিরাপত্তা সতর্কীকরণ (Sandbox Warning):** প্রোডাকশন লেভেলে এজেন্টকে তোমার লোকাল উইন্ডোজ বা ম্যাক Computeারে সরাসরি ডিরেক্ট কমান্ড রান করতে দেওয়া চরম বিপজ্জনক! কোনো ম্যালিসিয়াস Prompt-এর কারণে এজেন্ট পুরো হার্ডডিস্ক Format বা ডিলিট করার কমান্ড (`rm -rf /` বা `rd /s /q c:\`) চালিয়ে দিতে পারে। তাই সবসময় এই এজেন্টগুলোকে একটি আইসোলেটেড ডকার কন্টেইনার (Docker Sandbox Context) বা ভার্চুয়াল মেশিনে রান করানো আবশ্যক।

---

### ৩. Visual Explanation: ডকার স্যান্ডবক্স আইসোলেশন লেয়ার

প্রোডাকশনে কীভাবে এজেন্ট রান করাতে হয় তা দেখে নাও:

```
[ ইউজার Prompt ] ──► [ AI Agent Engine (LLM) ]
                             │
                             ▼ (Restricted Execution API)
                ┌───────────────────────────────────┐
                │       DOCKER SANDBOX ENGINE       │
                │  - No Network Access              │
                │  - Locked Directory               │
                │  - Auto-terminate in 10 seconds   │
                │                                   │
                │  [ app.py ] ──► [ Run Pytest ]    │
                └───────────────────────────────────┘
```

---

### ৪. Real World Example: স্বয়ংক্রিয় AI সিকিউরিটি প্যাচিং

একটি বড় Software Companyর ডাটাবেসে একটি সিকিউরিটি ভালনারেবিলিটি বা বাগ পাওয়া গেল:
1. AI এজেন্ট স্বয়ংক্রিয়ভাবে সোর্স Code-এর ফাইলটি রিড করে ডকার স্যান্ডবক্সে Code প্যাচ করে।
2. প্যাচ করার পর সে তার সিকিউরিটি Regression Test রান করে দেখে কোনো System ডাউন হয়েছে কি না।
3. টেস্টে যদি দেখা যায় ইউজার লগইন ফেইল করছে, এজেন্ট সাথে সাথে কোডটি আবার রোলব্যাক করে বা Modify করে Test পাস করিয়ে নিমিষেই গিটহাবে পিআর (Pull Request) সাবমিট করে দেয়।

---

### ৫. Developer Perspective: CLI Code Writer with Auto-Test Healing সম্পূর্ণ পাইপলাইন Implementation

💻 Developer View

চলো পাইথনে একটি সম্পূর্ণ রানিং, Custom সেলফ-হিলিং এজেন্ট Loop স্ক্র্যাচ থেকে ডিজাইন করি যা ফেইলড পাইথন টেস্টকে নিজে নিজেই হিল বা রিসলভ করবে।

```python
import os
import subprocess
import time
from openai import OpenAI

# ১. এনভায়রনমেন্ট ও ক্লায়েন্ট সেটআপ
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
client = OpenAI()

# টার্গেট Code File-এর পাথ
TARGET_FILE = "calculator.py"
TEST_FILE = "test_calculator.py"

# ২. কাস্টম পাইটেস্ট File প্রিপারেশন
# আমরা এজেন্টের কাজ Test করার জন্য কড়া Test ফাইলটি আগেই লিখে রাখছি
TEST_CODE = """
import pytest
from calculator import add

def test_add_positive():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, -1) == -2

def test_add_string_handling():
    # এটি হলো এজেন্টের জন্য একটি ফাঁদ বা এজ কেস!
    # এজেন্টকে স্ট্রিং Input আসলে ValueError থ্রো করতে হবে
    with pytest.raises(ValueError):
        add("2", 3)
"""

with open(TEST_FILE, "w", encoding="utf-8") as f:
    f.write(TEST_CODE)

# ৩. লোকাল পাইটেস্ট সাব-প্রসেস এক্সিকিউটর টুল
def run_pytest():
    print("[💻 Terminal] Executing: pytest test_calculator.py ...")
    # Run pytest and capture standard output & errors
    result = subprocess.run(["pytest", TEST_FILE], capture_output=True, text=True)
    return result.returncode == 0, result.stdout

# ৪. এজেন্ট ব্রেইন Loop উইথ Auto-Healing
def run_self_healing_agent():
    print("\n--- Starting Agentic Auto-Test Healing Loop ---")
    
    # এজেন্টের জন্য ট্র্যাকিং Prompt
    system_prompt = f"""
    You are an expert python developer who writes clean code.
    Your goal is to write code in a file named '{TARGET_FILE}' to make all tests in '{TEST_FILE}' pass.
    
    You must ONLY return the raw, clean python code. Do not include markdown wraps or explanations.
    """
    
    conversation_history = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Please write the 'add' function in {TARGET_FILE} to handle simple additions and raise ValueError if inputs are not numeric."}
    ]
    
    max_iterations = 4
    for iteration in range(1, max_iterations + 1):
        print(f"\n[🔄 Iteration {iteration}/{max_iterations}] Agent is thinking...")
        
        # এলএলএম কল
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation_history,
            temperature=0.2 # low temperature for deterministic code
        )
        agent_code = response.choices[0].message.content.strip()
        
        # মার্কডাউন Code ব্লক ট্রিম করো যদি এলএলএম ভুল করে দিয়ে দেয়
        if agent_code.startswith("```python"):
            agent_code = agent_code[9:-3].strip()
        elif agent_code.startswith("```"):
            agent_code = agent_code[3:-3].strip()
            
        print(f"[📝 Action] Writing generated code to {TARGET_FILE}...")
        with open(TARGET_FILE, "w", encoding="utf-8") as f:
            f.write(agent_code)
            
        # Test রান ও পর্যবেক্ষণ
        test_passed, test_log = run_pytest()
        
        if test_passed:
            print("\n[🎉 SUCCESS] All tests passed! Agent has successfully healed and written the perfect code!")
            print("--- FINAL CODE ---")
            print(agent_code)
            break
        else:
            print(f"\n[🔴 FAILURE] Test failed in iteration {iteration}!")
            # Error লগটি কনভারসেশন হিস্টোরিতে ফিড করো অটো-হিলিংয়ের জন্য
            feedback = f"""
            The code you wrote failed the tests. Here is the pytest execution log and traceback:
            
            {test_log}
            
            Analyze the traceback, find the bugs (syntax errors or missing constraints), fix them, and rewrite the code.
            """
            print("Feeding error log back to AI brain for self-correction...")
            conversation_history.append({"role": "assistant", "content": agent_code})
            conversation_history.append({"role": "user", "content": feedback})
            
            # হালকা রিফ্রেশ টাইম
            time.sleep(2)
            
    else:
        print("\n[🛑 ABORTED] Agent reached maximum iteration limit without passing tests.")

# --- ৫. RUN THE AGENT ---
# Ensure pytest is installed in your python environment before running: pip install pytest
# run_self_healing_agent()
```

---

### VI. Production Perspective: স্যান্ডবক্সিং ও সিকিউরিটি পলিসি

🏭 Production Reality

প্রোডাকশন লেভেলে যখন তুমি গ্রাহকদের জন্য Code এডিটিং System ডেপ্লয় করবে, তখন তোমাকে নিচের কড়া সিকিউরিটি Architecture মেনে চলতে হবে:

* **Resource Limiting (Compute লকিং):** কোনো হ্যাকার যদি Promptে একটি ইনফিনিটি Loop Code লিখে তোমার সার্ভারে Test রান করায়, তবে তোমার CPU ক্র্যাশ করবে। তাই প্রতিটি সাব-প্রসেস এক্সিকিউশনে অবশ্যই `timeout=10.0` Parameter ব্যবহার করতে হবে যাতে ১০ সেকেন্ডের বেশি কোনো স্ক্রিপ্ট চললে তা সাথে সাথে কিল হয়ে যায়।
* **Read-only Filesystem:** এজেন্টের স্যান্ডবক্স ডিরেক্টরি ছাড়া অন্য কোনো সিস্টেমে রিড বা রাইট অ্যাক্সেস থাকা যাবে না।

---

### VII. Common Mistakes

🔴 Common Mistake

**ভুল ধারণা:** এজেন্টের সোর্স কোডে `eval()` বা `exec()` Function ব্যবহার করে রানিং পাইথনের ভেতর ডাইনামিকালি AI জেনারেটেড Code এক্সিকিউট করা।

**বাস্তবতা:** `eval()` ব্যবহার করা পাইথনের সবচেয়ে বড় সিকিউরিটি লিকেজ। এর ফলে রানিং পাইথন প্রসেসের সম্পূর্ণ Memory ও ভেরিয়েবল AI স্ক্রিপ্ট ডাইনামিকালি ম্যানিপুলেট বা হ্যাক করে ফেলতে পারে। Code সবসময় সম্পূর্ণ আলাদা ফাইলে সেভ করে সাব-প্রসেস হিসেবে হোস্ট করাই একমাত্র প্রোডাকশন-গ্রেড সিদ্ধান্ত।

---

### VIII. Mental Model: অভিজ্ঞ মিস্ত্রি ও তার সহকারী

সেলফ-হিলিং এজেন্টের মেন্টাল Model:

**"আমাদের সেলফ-হিলিং এজেন্ট হলো একজন মিস্ত্রি যে পাইপ বসায়। আর Test রানার হলো সেই খিটখিটে Assistant যে বারবার পাইপের ভেতরে জল ঢেলে (Test cases) লিক খোঁজে। যখনই লিক পাওয়া যায়, Assistant চেঁচিয়ে বলে লিক কোথায়, আর মিস্ত্রি সাথে সাথে প্লাস্টার বা ওয়েল্ডিং করে পাইপ perfect করে দেয়।"**

---

### IX. Mini Project: পাইথনে Custom সাব-প্রসেস টাইমআউট ট্র্যাপার

চলো পাইথনে Code করে Practically দেখি কীভাবে কোনো কমান্ড বা AI স্ক্রিপ্ট ইনফিনিটি লুপে আটকে গেলে তাকে টাইমার দিয়ে কিল করতে হয়।

```python
import subprocess

# ১. কাল্পনিক ইনফিনিটি Loop স্ক্রিপ্ট যা CPU খেয়ে ফেলবে
infinite_loop_code = """
import time
print("Starting infinite computation loop...")
while True:
    time.sleep(0.5)
"""

with open("infinite_trap.py", "w", encoding="utf-8") as f:
    f.write(infinite_loop_code)

# ২. টাইমআউট দিয়ে সাব-প্রসেস ট্র্যাপ ও কিল Mechanism
try:
    print("Running process with 3-second timeout trap...")
    # Timeout strictly locked at 3 seconds
    result = subprocess.run(["python", "infinite_trap.py"], capture_output=True, text=True, timeout=3.0)
except subprocess.TimeoutExpired:
    print("\n[🚨 SECURED] Process took more than 3 seconds. TimeoutExpired triggered!")
    print("The infinite loop was successfully KILLED to save CPU resources!")
```

---

### X. Interview Questions

#### Beginner
1. **প্রশ্ন:** AI এজেন্টের প্রসঙ্গে "Reason + Act (ReAct)" Loop বলতে কী বোঝায়?
   * **উত্তর:** ReAct হলো এজেন্টের এমন একটি কাজের ধারা যেখানে সে প্রথমে চিন্তা বা পরিকল্পনা করে (Reason/Thought), এরপর সেটির ওপর ভিত্তি করে একটি কাজ সম্পন্ন করে (Act/Action), এবং কাজের রেজাল্ট দেখে পর্যবেক্ষণ করে (Observation) সিদ্ধান্ত নেয় লক্ষ্য অর্জিত হয়েছে কি না।

#### Intermediate
2. **প্রশ্ন:** কেন সেলফ-হিলিং এজেন্টে জেনারেটেড Code রান করার সময় `timeout` Parameter দেওয়া খুব জরুরি?
   * **উত্তর:** AI Code লেখার সময় অনেক সময় ভুল করে ইনফিনিটি Loop জেনারেট করে ফেলতে পারে যা টার্মিনালে রান করলে CPU ১০০% এনগেজ করে পুরো Server ক্র্যাশ করিয়ে দেবে। `timeout` Parameter দিলে নির্দিষ্ট সময় (যেমন ১০ সেকেন্ড) পর প্রসেসটি অটো-টার্মিনেট বা কিল হয়, যা System Resource সেভ করে।

#### Advanced
3. **প্রশ্ন:** প্রোডাকশনে Devin বা Cursor-এর মতো Code জেনারেটর এজেন্ট ডিজাইনে "Docker Sandbox Container" এর প্রয়োজনীয়তা Math-এর ও Architectural দিক থেকে ব্যাখ্যা করো।
   * **উত্তর:** AI বা ম্যালিসিয়াস Prompt যদি লোকাল ওএসে সরাসরি অ্যাক্সেস পায়, সে তোমার Computeারের সব পার্সোনাল File রিড করতে পারে বা ক্ষতিকর কমান্ড রান করে Database মুছে দিতে পারে। ডকার স্যান্ডবক্স কন্টেইনার একটি আলাদা লাইটওয়েট ভার্চুয়াল ফাইলসিস্টেম তৈরি করে যার সাথে লোকাল ওএসের কোনো Memory বা নেটওয়ার্ক শেয়ার থাকে না। ফলে এজেন্ট ডকারের ভেতরে কোনো ক্ষতি করলেও কন্টেইনারটি বন্ধ করার সাথে সাথে Database ও System রিবুট হয়ে ফ্রেশ স্টেটে ফিরে আসে, যা লোকাল ওএসকে ১০০% সিকিউর রাখে।

---

### XI. Chapter Summary
* **ReAct Framework** এজেন্টকে মানুষের মতো ধাপে ধাপে চিন্তা ও অ্যাকশন নেওয়ার ক্ষমতা দেয়।
* **Auto-Test Healing** ভুল Error Log রিড করে স্বয়ংক্রিয়ভাবে Code বাগ fix করে।
* প্রোডাকশন AI এজেন্ট ডিজাইনের প্রধান শর্ত হলো **Strict Security Isolation (Docker Sandbox)**।

---

### XII. What's Next
আমরা Deep Learning ও AI Ecosystem-এর কঠিনতম ও রোমাঞ্চকর এজেন্ট Loop Architecture ভালোভাবে শেষ করেছি। পরের chapter-এ আমরা প্রবেশ করতে যাচ্ছি আমাদের ফাইনাল বা শেষ টেকনিক্যাল Project Blueprintে: **Part 11 — Building Real AI Products এর Chapter 27: Blueprint 4 — Production AI SaaS with Rate Limiting & Usage Billing**। কীভাবে একটি বিশ্বমানের AI সফটওয়্যারকে Subscription বা পেইড সার্ভিসে convert করে Redis রেট-লিমিটিং, API Token ব্যবহার ট্র্যাকিং এবং স্ট্রাইপ (Stripe) ইউসেজ-বেসড বিলিং Integration করা হয়, তা আমরা বিশদ Source Code ও Architecture দিয়ে নিজের হাতে ডিজাইন করবো।

---
**Chapter 26 শেষ।**
