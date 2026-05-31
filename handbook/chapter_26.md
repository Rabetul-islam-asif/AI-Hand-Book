# Chapter 26: Blueprint 3 — Agentic CLI Code Writer with Auto-Test Healing

---

### Chapter Goal
এই চ্যাপ্টারের মূল লক্ষ্য হলো একটি অত্যন্ত শক্তিশালী সায়েন্স-ফিকশন লেভেলের এআই এজেন্ট ইকোসিস্টেম স্বহস্তে তৈরি করা। আমরা রিঅ্যাক্ট (ReAct: Reason + Act) প্যাটার্ন ব্যবহার করে এমন একটি কমান্ড-লাইন অটোমেটিক কোড রাইটার এজেন্ট (Agentic CLI Code Writer) দাঁড় করাবো, যা ইউজারের ইন্সট্রাকশন শুনে তোমার লোকাল কম্পিউটারে কোড ফাইল তৈরি করবে, নিজেই টার্মিনালে টেস্ট স্ক্রিপ্ট রান করবে এবং টেস্ট ফেইল করলে ডাইনামিকালি এরর বা ট্র্যাকিং লগ রিড করে অটোমেটিক্যালি কোড এডিট বা সেলফ-হিলিং (Auto-Test Healing) সম্পন্ন করবে।

### Why Should I Care?
গতানুগতিক চ্যাটবট শুধু কোড লিখে চ্যাটবক্সে শো করতে পারে। কিন্তু সেই কোডে কোনো সিনট্যাক্স এরর আছে কি না বা রিয়েল ডিপেনডেন্সি ক্র্যাশ করছে কি না, তা চ্যাটবট নিজে রান না করে জানতে পারে না। Devin বা Cursor Agent-এর মতো বৈপ্লবিক এআই কো-পাইলট সিস্টেম গড়ার পেছনের মূল রহস্য হলো এই সেলফ-টেস্টিং ও হিলিং লুপ। একজন এআই ইঞ্জিনিয়ার হিসেবে এজেন্ট লুপ আর্কিটেকচার রপ্ত করতে পারলে তুমি যেকোনো সাধারণ সফটওয়্যারকে স্বয়ংক্রিয় এআই এজেন্টে রূপান্তর করতে পারবে।

### Big Picture
এটি আমাদের বাস্তব প্রোজেক্ট ব্লুপ্রিন্ট লেয়ারের তৃতীয় এবং সবচেয়ে অ্যাডভান্সড কাইন্ডের ফ্ল্যাগশিপ মাইলফলক। আগের চ্যাপ্টারগুলোতে আমরা থিওরিটিক্যাল টুল কলিং, ফাংশন স্কিমাস এবং কন্ডিশনাল লুপ শিখেছি। এই চ্যাপ্টারে আমরা সেগুলোকে প্র্যাক্টিক্যাল ডকার বা লোকাল কমান্ড এক্সিকিউট পাইপলাইনে রূপ দেবো।

---

### ১. The Problem: অন্ধ কোডারের ছটফটানি ও এরর হিলিং

একটি সাধারণ এআই যখন কোড জেনারেট করে:
```python
# AI Generated code
import request  # Oops! It should be 'requests' with an 's'
```
ইউজার যখন কোড রান করতে যাও, স্ক্রিনে বড় লাল এরর আসে: `ModuleNotFoundError: No module named 'request'`। ইউজারকে আবার সেই এরর কপি করে এআই-তে পেস্ট করতে হয়। এই অনবরত কপি-পেস্ট করা ডেভেলপারের মূল্যবান সময় নষ্ট করে।

#### প্রোডাকশন সলিউশন: রিঅ্যাক্ট এজেন্ট লুপ (Reason + Act Loop with Auto-Healing)
আমাদের সেলফ-হিলিং এজেন্ট লুপ নিচের ৪টি সিকোয়েনশিয়াল ধাপে লুপ আকারে কাজ করে:
1. **Think (পরিকল্পনা):** এলএলএম প্রম্পট অ্যানালাইসিস করে ডিসিশন নেয় কোন লাইব্রেরি বা কোড লিখতে হবে।
2. **Write (অ্যাকশন ১):** এজেন্ট তার ওন কাস্টম কোড রাইটিং টুল ব্যবহার করে লোকাল কম্পিউটারে `app.py` এবং একটি `test_app.py` ফাইল তৈরি করে।
3. **Execute Test (অ্যাকশন ২):** এজেন্ট লোকাল টার্মিনালে সাব-প্রসেস রান করে টেস্ট কমান্ডটি এক্সিকিউট করে: `pytest test_app.py`।
4. **Self-Heal (পর্যবেক্ষণ ও ভুল সংশোধন):** টেস্ট যদি ফেইল করে, এজেন্ট কিন্তু হাল ছাড়ে না। সে টেস্টের আউটপুট ও লাল এরর লগটি সরাসরি রিড করে তার ব্রেইনে ফিড করে এবং তার কোড সংশোধন করে আবার নতুন করে লেখে। টেস্ট ১০০% পাস হওয়া না পর্যন্ত এই লুপ অনবরত চলতে থাকে।

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
রিঅ্যাক্ট হলো এআই এজেন্টের মনস্তাত্ত্বিক ফ্রেমওয়ার্ক:
* **Thought (চিন্তা):** *"আমি একটি ম্যাথমেটিক্যাল ক্যালকুলেটর ফাংশন লিখতে চাই। প্রথমে আমার ফাইলটি রাইট করা উচিত।"*
* **Action (কাজ):** কাস্টম ফাংশন কল করা (যেমন `write_file_to_disk`).
* **Observation (পর্যবেক্ষণ):** টার্মিনাল রান করার পর দেখা গেল টেস্ট সাকসেসফুল। এজেন্টের সিদ্ধান্ত: *"আমার কাজ সফল হয়েছে, এবার আমি লুপ ক্লোজ করতে পারি।"*

#### খ. Executing Subprocesses in Python (লোকাল কমান্ড রান করার লজিক)
এজেন্টকে কমান্ড রান করার ক্ষমতা দিতে পাইথনের `subprocess` মডিউল ব্যবহার করা হয়।
* **নিরাপত্তা সতর্কীকরণ (Sandbox Warning):** প্রোডাকশন লেভেলে এজেন্টকে তোমার লোকাল উইন্ডোজ বা ম্যাক কম্পিউটারে সরাসরি ডিরেক্ট কমান্ড রান করতে দেওয়া চরম বিপজ্জনক! কোনো ম্যালিসিয়াস প্রম্পটের কারণে এজেন্ট পুরো হার্ডডিস্ক ফরম্যাট বা ডিলিট করার কমান্ড (`rm -rf /` বা `rd /s /q c:\`) চালিয়ে দিতে পারে। তাই সবসময় এই এজেন্টগুলোকে একটি আইসোলেটেড ডকার কন্টেইনার (Docker Sandbox Context) বা ভার্চুয়াল মেশিনে রান করানো আবশ্যক।

---

### ৩. Visual Explanation: ডকার স্যান্ডবক্স আইসোলেশন লেয়ার

প্রোডাকশনে কীভাবে এজেন্ট রান করাতে হয় তা দেখে নাও:

```
[ ইউজার প্রম্পট ] ──► [ AI Agent Engine (LLM) ]
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

### ৪. Real World Example: স্বয়ংক্রিয় এআই সিকিউরিটি প্যাচিং

একটি বড় সফটওয়্যার কোম্পানির ডাটাবেসে একটি সিকিউরিটি ভালনারেবিলিটি বা বাগ পাওয়া গেল:
1. এআই এজেন্ট স্বয়ংক্রিয়ভাবে সোর্স কোডের ফাইলটি রিড করে ডকার স্যান্ডবক্সে কোড প্যাচ করে।
2. প্যাচ করার পর সে তার সিকিউরিটি রিগ্রেশন টেস্ট রান করে দেখে কোনো সিস্টেম ডাউন হয়েছে কি না।
3. টেস্টে যদি দেখা যায় ইউজার লগইন ফেইল করছে, এজেন্ট সাথে সাথে কোডটি আবার রোলব্যাক করে বা মডিফাই করে টেস্ট পাস করিয়ে নিমিষেই গিটহাবে পিআর (Pull Request) সাবমিট করে দেয়।

---

### ৫. Developer Perspective: CLI Code Writer with Auto-Test Healing সম্পূর্ণ পাইপলাইন ইমপ্লিমেন্টেশন

💻 Developer View

চলো পাইথনে একটি সম্পূর্ণ রানিং, কাস্টম সেলফ-হিলিং এজেন্ট লুপ স্ক্র্যাচ থেকে ডিজাইন করি যা ফেইলড পাইথন টেস্টকে নিজে নিজেই হিল বা রিসলভ করবে।

```python
import os
import subprocess
import time
from openai import OpenAI

# ১. এনভায়রনমেন্ট ও ক্লায়েন্ট সেটআপ
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
client = OpenAI()

# টার্গেট কোড ফাইলের পাথ
TARGET_FILE = "calculator.py"
TEST_FILE = "test_calculator.py"

# ২. কাস্টম পাইটেস্ট ফাইল প্রিপারেশন
# আমরা এজেন্টের কাজ টেস্ট করার জন্য কড়া টেস্ট ফাইলটি আগেই লিখে রাখছি
TEST_CODE = """
import pytest
from calculator import add

def test_add_positive():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, -1) == -2

def test_add_string_handling():
    # এটি হলো এজেন্টের জন্য একটি ফাঁদ বা এজ কেস!
    # এজেন্টকে স্ট্রিং ইনপুট আসলে ValueError থ্রো করতে হবে
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

# ৪. এজেন্ট ব্রেইন লুপ উইথ অটো-হিলিং
def run_self_healing_agent():
    print("\n--- Starting Agentic Auto-Test Healing Loop ---")
    
    # এজেন্টের জন্য ট্র্যাকিং প্রম্পট
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
        
        # মার্কডাউন কোড ব্লক ট্রিম করো যদি এলএলএম ভুল করে দিয়ে দেয়
        if agent_code.startswith("```python"):
            agent_code = agent_code[9:-3].strip()
        elif agent_code.startswith("```"):
            agent_code = agent_code[3:-3].strip()
            
        print(f"[📝 Action] Writing generated code to {TARGET_FILE}...")
        with open(TARGET_FILE, "w", encoding="utf-8") as f:
            f.write(agent_code)
            
        # টেস্ট রান ও পর্যবেক্ষণ
        test_passed, test_log = run_pytest()
        
        if test_passed:
            print("\n[🎉 SUCCESS] All tests passed! Agent has successfully healed and written the perfect code!")
            print("--- FINAL CODE ---")
            print(agent_code)
            break
        else:
            print(f"\n[🔴 FAILURE] Test failed in iteration {iteration}!")
            # এরর লগটি কনভারসেশন হিস্টোরিতে ফিড করো অটো-হিলিংয়ের জন্য
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

প্রোডাকশন লেভেলে যখন তুমি গ্রাহকদের জন্য কোড এডিটিং সিস্টেম ডেপ্লয় করবে, তখন তোমাকে নিচের কড়া সিকিউরিটি আর্কিটেকচার মেনে চলতে হবে:

* **Resource Limiting (কম্পিউট লকিং):** কোনো হ্যাকার যদি প্রম্পটে একটি ইনফিনিটি লুপ কোড লিখে তোমার সার্ভারে টেস্ট রান করায়, তবে তোমার সিপিইউ ক্র্যাশ করবে। তাই প্রতিটি সাব-প্রসেস এক্সিকিউশনে অবশ্যই `timeout=10.0` প্যারামিটার ব্যবহার করতে হবে যাতে ১০ সেকেন্ডের বেশি কোনো স্ক্রিপ্ট চললে তা সাথে সাথে কিল হয়ে যায়।
* **Read-only Filesystem:** এজেন্টের স্যান্ডবক্স ডিরেক্টরি ছাড়া অন্য কোনো সিস্টেমে রিড বা রাইট অ্যাক্সেস থাকা যাবে না।

---

### VII. Common Mistakes

🔴 Common Mistake

**ভুল ধারণা:** এজেন্টের সোর্স কোডে `eval()` বা `exec()` ফাংশন ব্যবহার করে রানিং পাইথনের ভেতর ডাইনামিকালি এআই জেনারেটেড কোড এক্সিকিউট করা।

**বাস্তবতা:** `eval()` ব্যবহার করা পাইথনের সবচেয়ে বড় সিকিউরিটি লিকেজ। এর ফলে রানিং পাইথন প্রসেসের সম্পূর্ণ মেমোরি ও ভেরিয়েবল এআই স্ক্রিপ্ট ডাইনামিকালি ম্যানিপুলেট বা হ্যাক করে ফেলতে পারে। কোড সবসময় সম্পূর্ণ আলাদা ফাইলে সেভ করে সাব-প্রসেস হিসেবে হোস্ট করাই একমাত্র প্রোডাকশন-গ্রেড সিদ্ধান্ত।

---

### VIII. Mental Model: অভিজ্ঞ মিস্ত্রি ও তার সহকারী

সেলফ-হিলিং এজেন্টের মেন্টাল মডেল:

**"আমাদের সেলফ-হিলিং এজেন্ট হলো একজন মিস্ত্রি যে পাইপ বসায়। আর টেস্ট রানার হলো সেই খিটখিটে অ্যাসিস্ট্যান্ট যে অনবরত পাইপের ভেতরে জল ঢেলে (Test cases) লিক খোঁজে। যখনই লিক পাওয়া যায়, অ্যাসিস্ট্যান্ট চেঁচিয়ে বলে লিক কোথায়, আর মিস্ত্রি সাথে সাথে প্লাস্টার বা ওয়েল্ডিং করে পাইপ নিখুঁত করে দেয়।"**

---

### IX. Mini Project: পাইথনে কাস্টম সাব-প্রসেস টাইমআউট ট্র্যাপার

চলো পাইথনে কোড করে প্র্যাক্টিক্যালি দেখি কীভাবে কোনো কমান্ড বা এআই স্ক্রিপ্ট ইনফিনিটি লুপে আটকে গেলে তাকে টাইমার দিয়ে কিল করতে হয়।

```python
import subprocess

# ১. কাল্পনিক ইনফিনিটি লুপ স্ক্রিপ্ট যা সিপিইউ খেয়ে ফেলবে
infinite_loop_code = """
import time
print("Starting infinite computation loop...")
while True:
    time.sleep(0.5)
"""

with open("infinite_trap.py", "w", encoding="utf-8") as f:
    f.write(infinite_loop_code)

# ২. টাইমআউট দিয়ে সাব-প্রসেস ট্র্যাপ ও কিল মেকানিজম
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
1. **প্রশ্ন:** এআই এজেন্টের প্রসঙ্গে "Reason + Act (ReAct)" লুপ বলতে কী বোঝায়?
   * **উত্তর:** ReAct হলো এজেন্টের এমন একটি কাজের ধারা যেখানে সে প্রথমে চিন্তা বা পরিকল্পনা করে (Reason/Thought), এরপর সেটির ওপর ভিত্তি করে একটি কাজ সম্পন্ন করে (Act/Action), এবং কাজের রেজাল্ট দেখে পর্যবেক্ষণ করে (Observation) সিদ্ধান্ত নেয় লক্ষ্য অর্জিত হয়েছে কি না।

#### Intermediate
2. **প্রশ্ন:** কেন সেলফ-হিলিং এজেন্টে জেনারেটেড কোড রান করার সময় `timeout` প্যারামিটার দেওয়া অত্যন্ত জরুরি?
   * **উত্তর:** এআই কোড লেখার সময় অনেক সময় ভুল করে ইনফিনিটি লুপ জেনারেট করে ফেলতে পারে যা টার্মিনালে রান করলে সিপিইউ ১০০% এনগেজ করে পুরো সার্ভার ক্র্যাশ করিয়ে দেবে। `timeout` প্যারামিটার দিলে নির্দিষ্ট সময় (যেমন ১০ সেকেন্ড) পর প্রসেসটি অটো-টার্মিনেট বা কিল হয়, যা সিস্টেম রিসোর্স সেভ করে।

#### Advanced
3. **প্রশ্ন:** প্রোডাকশনে Devin বা Cursor-এর মতো কোড জেনারেটর এজেন্ট ডিজাইনে "Docker Sandbox Container" এর প্রয়োজনীয়তা গাণিতিক ও আর্কিটেকচারাল দিক থেকে ব্যাখ্যা করো।
   * **উত্তর:** এআই বা ম্যালিসিয়াস প্রম্পট যদি লোকাল ওএসে সরাসরি অ্যাক্সেস পায়, সে তোমার কম্পিউটারের সব পার্সোনাল ফাইল রিড করতে পারে বা ক্ষতিকর কমান্ড রান করে ডাটাবেস মুছে দিতে পারে। ডকার স্যান্ডবক্স কন্টেইনার একটি আলাদা লাইটওয়েট ভার্চুয়াল ফাইলসিস্টেম তৈরি করে যার সাথে লোকাল ওএসের কোনো মেমোরি বা নেটওয়ার্ক শেয়ার থাকে না। ফলে এজেন্ট ডকারের ভেতরে কোনো ক্ষতি করলেও কন্টেইনারটি বন্ধ করার সাথে সাথে ডাটাবেস ও সিস্টেম রিবুট হয়ে ফ্রেশ স্টেটে ফিরে আসে, যা লোকাল ওএসকে ১০০% সিকিউর রাখে।

---

### XI. Chapter Summary
* **ReAct Framework** এজেন্টকে মানুষের মতো ধাপে ধাপে চিন্তা ও অ্যাকশন নেওয়ার ক্ষমতা দেয়।
* **Auto-Test Healing** ভুল এরর লগ রিড করে স্বয়ংক্রিয়ভাবে কোড বাগ সংশোধন করে।
* প্রোডাকশন এআই এজেন্ট ডিজাইনের প্রধান শর্ত হলো **Strict Security Isolation (Docker Sandbox)**।

---

### XII. What's Next
আমরা ডিপ লার্নিং ও এআই ইকোসিস্টেমের কঠিনতম ও রোমাঞ্চকর এজেন্ট লুপ আর্কিটেকচার সফলভাবে শেষ করেছি। পরবর্তী চ্যাপ্টারে আমরা পদার্পণ করতে যাচ্ছি আমাদের ফাইনাল বা শেষ টেকনিক্যাল প্রোজেক্ট ব্লুপ্রিন্টে: **Part 11 — Building Real AI Products এর Chapter 27: Blueprint 4 — Production AI SaaS with Rate Limiting & Usage Billing**। কীভাবে একটি বিশ্বমানের এআই সফটওয়্যারকে সাবস্ক্রিপশন বা পেইড সার্ভিসে রূপান্তর করে Redis রেট-লিমিটিং, এপিআই টোকেন ব্যবহার ট্র্যাকিং এবং স্ট্রাইপ (Stripe) ইউসেজ-বেসড বিলিং ইন্টিগ্রেশন করা হয়, তা আমরা বিশদ সোর্স কোড ও আর্কিটেকচার দিয়ে স্বহস্তে ডিজাইন করবো।

---
**Chapter 26 সমাপ্ত।**
