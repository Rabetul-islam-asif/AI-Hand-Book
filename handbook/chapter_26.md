# Chapter 26: Blueprint 3 — Agentic CLI Code Writer with Auto-Test Healing

---

তুমি কি কখনো ভেবেছো — সায়েন্স-ফিকশন সিনেমার মতো এমন একটা AI Agent বানানো কি সত্যিই সম্ভব?

যে নিজে নিজে Code লিখবে, নিজে নিজেই সেটা Terminal-এ Run করে Test করবে।

আর যদি কোনো ভুল বা Bug থাকে, তবে নিজেই সেই Error Log পড়ে Code ঠিক করে নেবে!

শুনে অবিশ্বাস্য মনে হলেও, এটাই সত্যি।

Devin বা Cursor Agent-এর মতো আধুনিক AI Tool-গুলোর আসল ম্যাজিক কিন্তু এখানেই। একে আমরা বলি Self-Testing এবং Auto-Healing Loop।

তো চলো, এই চ্যাপ্টারে আমরা এমনই একটা রোমাঞ্চকর Pattern নিজের হাতে ডিজাইন করে ফেলি!

আমরা ব্যবহার করবো ReAct এবং Auto-Test Healing।

আমরা দেখবো কীভাবে ইউজার থেকে কমান্ড নিয়ে ফাইল তৈরি করা যায়, লোকাল কম্পিউটারে pytest দিয়ে টেস্ট করা যায়, আর টেস্ট ফেইল করলে ভুল শুধরে নেওয়া যায়।

চলো, শুরু করা যাক! Deal?


### ১. আসল সমস্যাটা কোথায়?

ধরো, একটা সাধারণ AI-কে তুমি কোড লিখতে বললে। 

সে হয়তো এমন একটা কোড বানিয়ে দিল:

```python
# AI Generated code
import request  # Oops! It should be 'requests' with an 's'
```

কিন্তু রান করার সাথে সাথে স্ক্রিনে বড় বড় লাল অক্ষরে একটা Error চলে এলো:

`ModuleNotFoundError: No module named 'request'`

এখন তুমি কী করবে?

নিশ্চয়ই সেই Error কপি করে আবার AI-এর চ্যাটে পেস্ট করবে। 

AI সেটা দেখে কোড ঠিক করে দেবে। তুমি আবার রান করবে।

এই যে বারবার কপি-পেস্ট করা, এটা কি বিরক্তিকর নয়? 

আমাদের মূল্যবান সময় নষ্ট করার জন্য এটাই যথেষ্ট।

তাহলে এর সমাধান কী?

এখানেই আসে ReAct Agent Loop এবং Auto-Healing।

আমাদের এই সেলফ-হিলিং সিস্টেমটি মূলত চারটি ধাপে একটা লুপের মতো কাজ করে:

প্রথম ধাপ হলো **Think**। 

এখানে LLM প্রথমে চিন্তা করে সিদ্ধান্ত নেয় যে তাকে ঠিক কী করতে হবে। কোন লাইব্রেরি বা কোড লিখতে হবে।

দ্বিতীয় ধাপ হলো **Write**। 

সিদ্ধান্ত নেওয়ার পর এজেন্ট তার নিজস্ব টুল ব্যবহার করে কম্পিউটারে `app.py` এবং `test_app.py` ফাইল তৈরি করে।

তৃতীয় ধাপ হলো **Execute Test**। 

কোড লেখা শেষ হলে এজেন্ট টার্মিনালে `pytest test_app.py` কমান্ডটি রান করে।

চতুর্থ ধাপ হলো **Self-Heal**। 

যদি টেস্ট ফেইল করে, এজেন্ট কিন্তু থেমে যায় না। 

সে টেস্টের আউটপুট আর লাল Error লগ সরাসরি রিড করে নিজের ব্রেইনে নিয়ে নেয়। 

এরপর ভুলগুলো ঠিক করে কোডটি আবার নতুন করে লেখে। 

আর টেস্ট ১০০% পাস না হওয়া পর্যন্ত এই লুপ চলতেই থাকে! 

দারুণ না?

[VISUAL]
Title: Agentic Self-Healing Loop Flowchart
Illustration: Loop cycle between LLM Generator, Write File, Run Subprocess pytest, Catch Failure, Feedback Error, and rewrite
Placement: After Hook Section
Purpose: Provide architectural mapping of the self-correcting agent loop.

```
          ┌────────────────────────────────────────┐
          ▼                                        │
    ┌───────────┐       ┌────────────┐             │
    │  Think     │ ────►│ Act:       │             │
    │   (LLM)   │       │ Write Code │             │
    └───────────┘       └────────────┘             │ (If test fails,
          ▲                    │                   │  feed error back)
          │                    ▼                   │
          │             ┌────────────┐             │
          │             │  Run       │             │
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


### ২. মূল কনসেপ্টগুলো কী কী?

এই চমৎকার সিস্টেমটি বানাতে আমাদের কিছু বেসিক জিনিস বুঝতে হবে।

প্রথমেই জানা দরকার, **ReAct Framework** আসলে কী?

সহজ কথায়, এটা হলো এজেন্টের চিন্তা ও কাজ করার একটা ফ্রেমওয়ার্ক। 

যেমন ধরো, এজেন্টের মাথায় প্রথমে আসবে একটি **Thought** বা চিন্তা: 

"আমি একটি যোগ করার ফাংশন লিখতে চাই। প্রথমে আমার ফাইল তৈরি করা দরকার।"

চিন্তা করার পর আসবে **Action** বা কাজ:

সে কোড লেখার জন্য `write_file_to_disk` নামের ফাংশনটি কল করবে।

কাজ শেষ হলে আসবে **Observation** বা পর্যবেক্ষণ:

সে দেখবে টেস্ট রান করার পর কী রেজাল্ট এলো। টেস্ট পাস করলে সে সিদ্ধান্ত নেবে, "আমার কাজ সফল হয়েছে, এবার লুপ শেষ করা যাক।"

তাহলে এজেন্ট লোকাল কমান্ড কীভাবে রান করে?

পাইথনের `subprocess` মডিউল ব্যবহার করে এজেন্ট এই কমান্ডগুলো রান করার ক্ষমতা পায়।

কিন্তু একটা বড়সড় বিপদের কথা মাথায় রাখতে হবে।

লোকাল কম্পিউটারে সরাসরি এজেন্টের কোড রান করা কি নিরাপদ?

একেবারেই না! এটা চরম বিপজ্জনক হতে পারে।

ধরো, কোনো কারণে এজেন্ট ভুল করে বা কোনো ক্ষতিকর প্রম্পটের কারণে পুরো হার্ডডিস্ক ডিলিট করার কমান্ড দিয়ে বসলো!

যেমন: `rm -rf /` বা `rd /s /q c:\`।

তাহলে তো সর্বনাশ হয়ে যাবে!

এই জন্য প্রোডাকশনে কাজ করার সময় সবসময় কোড রান করার জন্য একটি ডকার কন্টেইনার বা Docker Sandbox ব্যবহার করা উচিত।

এতে এজেন্টের কোড একটি আলাদা সুরক্ষিত জায়গায় রান হবে এবং তোমার আসল সিস্টেম থাকবে একদম নিরাপদ।


### ৩. ডকার স্যান্ডবক্সের কাজ

চলো দেখি প্রোডাকশনে কীভাবে এটা কাজ করে:

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


### ৪. বাস্তব জীবনের উদাহরণ

ধরো, একটি বড় সফটওয়্যার কোম্পানির সিস্টেমে একটি সিকিউরিটি বাগ পাওয়া গেল।

তখন AI এজেন্ট কীভাবে কাজ করবে?

প্রথমে এজেন্ট নিজে থেকেই Source Code ফাইলটি রিড করবে এবং ডকার স্যান্ডবক্সে কোড প্যাচ করে নেবে।

কোড প্যাচ করার পর সে তার সিকিউরিটি Regression Test রান করবে। 

উদ্দেশ্য হলো, এই পরিবর্তনের ফলে অন্য কোনো sistem বা সিস্টেম ডাউন হয়েছে কি না তা পরীক্ষা করা।

যদি টেস্টে দেখা যায় ইউজার লগইন ফেইল করছে, তাহলে এজেন্ট কিন্তু থেমে থাকবে না।

সে সাথে সাথে কোডটি আবার Modify করে টেস্ট পাস করাবে।

আর সব শেষে নিমিষেই গিটহাবে একটি Pull Request সাবমিট করে দেবে!

পুরো কাজটাই হবে অটোমেটিকভাবে।


### ৫. চলো কোড লিখে ফেলি!

💻 Developer View

চলো, পাইথনে একটি সম্পূর্ণ রানিং সেলফ-হিলিং এজেন্ট লুপ স্ক্র্যাচ থেকে তৈরি করি। 

এটি ফেইল করা টেস্ট কেসগুলো নিজে নিজেই সমাধান করে ফেলবে!

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
            
        print(f"[ Action] Writing generated code to {TARGET_FILE}...")
        with open(TARGET_FILE, "w", encoding="utf-8") as f:
            f.write(agent_code)
            
        # Test রান ও পর্যবেক্ষণ
        test_passed, test_log = run_pytest()
        
        if test_passed:
            print("\n[ SUCCESS] All tests passed! Agent has successfully healed and written the perfect code!")
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


### ৬. প্রোডাকশন ও সিকিউরিটি পলিসি

 Production Reality

প্রোডাকশন লেভেলে যখন তুমি ইউজারদের জন্য কোড এডিটিং সিস্টেম ডেপ্লয় করবে, তখন কিছু গুরুত্বপূর্ণ সিকিউরিটি পলিসি মেনে চলা দরকার।

যেমন ধরো, **Resource Limiting** বা রিসোর্স লিমিট করা কেন জরুরি?

কোনো ইউজার যদি প্রম্পটে একটি ইনফিনিটি লুপ কোড লিখে তোমার সার্ভারে রান করায়, তবে কিন্তু তোমার CPU ক্র্যাশ করবে। 

তাই প্রতিটি সাব-প্রসেস রান করার সময় অবশ্যই `timeout=10.0` প্যারামিটার ব্যবহার করতে হবে। 

এতে ১০ সেকেন্ডের বেশি কোড চললে তা সাথে সাথে বন্ধ হয়ে যাবে।

আরেকটি বিষয় হলো **Read-only Filesystem**।

এজেন্টের স্যান্ডবক্স ডিরেক্টরি ছাড়া অন্য কোনো ফোল্ডারে যেন সে রিড বা রাইট করতে না পারে, সেটা নিশ্চিত করতে হবে।


### ৭. সাধারণ কিছু ভুল

🔴 Common Mistake

**ভুল ধারণা:** এজেন্টের সোর্স কোডে `eval()` বা `exec()` ফাংশন ব্যবহার করে রানিং পাইথনের ভেতর ডাইনামিকালি কোড রান করা ঠিক আছে।

**বাস্তবতা:** এটি পাইথনের সবচেয়ে বড় সিকিউরিটি লিক! 

এর ফলে তোমার রানিং পাইথন প্রসেসের সম্পূর্ণ মেমোরি হ্যাক হয়ে যেতে পারে। 

তাই বুদ্ধিমানের কাজ হলো কোড সবসময় আলাদা ফাইলে সেভ করে সাব-প্রসেস হিসেবে রান করানো।


### ৮. একটি সহজ তুলনা

আমাদের সেলফ-হিলিং এজেন্টকে তুমি একজন পাইপ ফিটার বা মিস্ত্রির সাথে তুলনা করতে পারো। 

আর টেস্ট রানার হলো তার সেই খিটখিটে অ্যাসিস্ট্যান্ট, যে পাইপের ভেতরে জল ঢেলে লিক খোঁজে। 

যখনই লিক পাওয়া যায়, অ্যাসিস্ট্যান্ট চেঁচিয়ে বলে লিকটা ঠিক কোথায় হয়েছে।

আর মিস্ত্রি সাথে সাথে ওয়েল্ডিং করে পাইপ একদম পারফেক্ট করে দেয়!


### ৯. একটি মিনি প্রজেক্ট

চলো, পাইথনে প্র্যাক্টিক্যালি কোড করে দেখি কীভাবে কোনো ইনফিনিটি লুপে আটকে যাওয়া স্ক্রিপ্টকে টাইমার দিয়ে কিল করতে হয়।

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
    print("\n[ SECURED] Process took more than 3 seconds. TimeoutExpired triggered!")
    print("The infinite loop was successfully KILLED to save CPU resources!")
```


### ১০. ইন্টারভিউতে কেমন প্রশ্ন হতে পারে?

#### Beginner Level

**প্রশ্ন:** ReAct Loop বলতে কী বোঝায়?

**উত্তর:** এটি এজেন্টের কাজ করার একটি বিশেষ ফ্রেমওয়ার্ক। 

এখানে সে প্রথমে চিন্তা বা পরিকল্পনা করে (Reasoning), তারপর সেই অনুযায়ী কাজ করে (Acting)। 

সবশেষে কাজের ফলাফল দেখে সিদ্ধান্ত নেয় পরবর্তী পদক্ষেপ কী হবে।

#### Intermediate Level

**প্রশ্ন:** সেলফ-হিলিং এজেন্টে `timeout` প্যারামিটার দেওয়া কেন জরুরি?

**উত্তর:** AI অনেক সময় ভুল কোড লিখে ইনফিনিটি লুপ তৈরি করে ফেলতে পারে। 

সেটি টার্মিনালে চললে পুরো সার্ভার ক্র্যাশ করতে পারে। 

`timeout` দিলে নির্দিষ্ট সময় পর প্রসেসটি নিজে থেকেই বন্ধ হয়ে যায়, যা সার্ভারকে রক্ষা করে।

#### Advanced Level

**প্রশ্ন:** ডকার স্যান্ডবক্স ব্যবহারের প্রয়োজনীয়তা কী?

**উত্তর:** AI যদি লোকাল অপারেটিং সিস্টেমে সরাসরি অ্যাক্সেস পায়, তবে সে যেকোনো পার্সোনাল ফাইল রিড করতে পারে বা ক্ষতিকর কমান্ড রান করে ডাটাবেস মুছে দিতে পারে। 

ডকার স্যান্ডবক্স একটি আলাদা ভার্চুয়াল সিস্টেম তৈরি করে, যার সাথে লোকাল মেমোরি বা নেটওয়ার্কের কোনো যোগাযোগ থাকে না। 

এর ফলে এজেন্ট কোনো ক্ষতি করলেও কন্টেইনারটি বন্ধ করলেই সবকিছু আবার আগের মতো ফ্রেশ স্টেটে ফিরে আসে, যা লোকাল সিস্টেমকে ১০০% সিকিউর রাখে।


### ১১. চ্যাপ্টার সামারি

এই চ্যাপ্টারে আমরা চমৎকার কিছু জিনিস শিখলাম:

প্রথমত, ReAct Framework কীভাবে এজেন্টকে মানুষের মতো ধাপে ধাপে চিন্তা করার ক্ষমতা দেয়।

দ্বিতীয়ত, Auto-Test Healing কীভাবে এরর লগ দেখে নিজে নিজেই কোডের বাগ ঠিক করতে পারে।

এবং সবশেষে জানলাম, কেন প্রোডাকশন লেভেলে সিকিউরিটির জন্য ডকার স্যান্ডবক্স ব্যবহার করা উচিত।


### ১২. এরপরে কী?

অভিনন্দন! আমরা চমৎকার একটি এজেন্ট লুপ আর্কিটেকচার সফলভাবে শেষ করেছি। 

পরের চ্যাপ্টারে আমরা আমাদের শেষ প্রোজেক্ট ব্লুপ্রিন্ট তৈরি করতে যাচ্ছি।

সেখানে আমরা দেখবো কীভাবে একটি AI SaaS অ্যাপ্লিকেশনে রেট-লিমিটিং এবং স্ট্রাইপ বিলিং ইন্টিগ্রেট করা যায়।

দেখা হচ্ছে পরের চ্যাপ্টারে! 

**Chapter 26 শেষ।**
