# Chapter 18: AI Agents — From Chatbots to Autonomous Workers



তোমার চ্যাটবটকে বলো, *"আমার Project-এর বাগ ফিক্স করে দাও।"* কী করবে সে? উত্তর দেবে: *"এইভাবে ফিক্স করতে পারো..."* — ব্যস, এইটুকুই। তুমি নিজে Code কপি করবে, পেস্ট করবে, Error আসলে আবার তাকে দেখাবে। তুমি হলে কপি-পেস্ট ড্রাইভার!

কিন্তু ধরো, AI নিজেই পুরো কোডবেস রিড করলো, নিজেই বাগ খুঁজে বের করলো, Code লিখলো, Test রান করলো, ফেইল হলে নিজেই ফিক্স করলো— আর শেষে বললো, *"কাজ শেষ, PR রেডি।"* এটাই হলো AI Agent। চ্যাটবট থেকে Autonomous Worker-এ উত্তরণ। এটাই এখন গ্লোবাল টেক ইন্ডাস্ট্রির সবচেয়ে হট ট্রেন্ড।

তো চলো দেখি ReAct Pattern (Think → Act → Observe) কীভাবে কাজ করে, Planning আর Self-Correction Loop কীভাবে Implement করতে হয়। এটা বুঝলে পরের চ্যাপ্টারের Tool Calling, MCP Protocol আর Harness Engineering— সব জায়গায় তুমি কমফোর্টেবল থাকবে।



### ১. Hook: বাচাল ডিকটেশন সহকারী বনাম দায়িত্বশীল কর্মী

কল্পনা করো, তুমি তোমার Companyর জন্য একজন নতুন Developer হায়ার করলে।
* **Chatbot Mode (inactive সহকারী):** সে তোমার পাশে বসে আছে। তুমি বললে, `"জাভাস্ক্রিপ্টের এই কোডটা পাইথনে কনভার্ট করে দাও।"` সে সাথে সাথে কনভার্ট করে দিল। তুমি আবার কপি করে ফাইলে রাখলেন, রান করে দেখলে Error এসেছে। তুমি আবার এররটি তাকে দেখালেন, সে ফিক্সড করে দিল। তুমি কপি-পেস্ট ড্রাইভার হিসেবে কাজ করছো, সে কেবল Instruction ফলো করছে।

[VISUAL]
Title: Conversational Chatbot vs. Autonomous AI Agent
Illustration: Static back-and-forth conversational loop vs. continuous recursive goal-oriented tool loop
Placement: After Hook Section
Purpose: Show the paradigm shift from message-driven bots to autonomous goal-driven loops.

```
Traditional Chatbot (Static Message Loop):
User ──► [ Prompt ] ──► [ Chatbot Response ] ──► User (Copy-paste driver)

Autonomous AI Agent (Continuous Agentic Loop):
User ──► [ Set Goal: "Fix payment bug" ] ──► [ Think ] ──► [ Act (Run Tool/Code) ] ──► [ Observe (Test fails) ] ──► [ Loop: Self-Correct ] ──► Done!
```

* **Agent Mode (Autonomous Worker):** তুমি তাকে গোল দিয়ে বললে, `"পেমেন্ট গেটওয়েতে ট্রানজ্যাকশন Error আসছে, ফিক্স করে দাও।"` সে নিজে সম্পূর্ণ কোডবেস রিড করল, লগে গিয়ে Error পিনপয়েন্ট করল, Custom ফিক্স লিখল, লোকাল Test রান করল, Error আসলে নিজে নিজেই Code রি-রাইট করে ফিক্স করে সম্পূর্ণ সাকসেসফুল হওয়ার পর তোমাকে বলল, `"কাজ শেষ, পিআর (PR) রেডি।"`

AI এজেন্ট হলো এই দায়িত্বশীল কর্মী। সে কেবল ওয়ার্ড Predict করে না; সে নিজের কাজের ফলাফল ট্র্যাক করে Loop চালিয়ে গোল এচিভ করে।

---

### ২. Core Concepts: Agentic Loop ও রিঅ্যাক্ট Pattern

একটি Custom AI এজেন্ট মূলত ৪টি প্রধান উপাদানের সমন্বয়ে গঠিত:

[VISUAL]
Title: Four Pillars of AI Agent Architecture
Illustration: High-quality flowchart mapping Profiling, Planning, Tools, and Memory
Placement: After Core Concepts section
Purpose: Visually define the structural blocks of an AI Agent.

```
┌────────────────────────────────────────────────────────┐
│                      AI AGENT ENGINE                   │
│                                                        │
│   ┌──────────────────┐          ┌──────────────────┐   │
│   │    PROFILING     │          │     PLANNING     │   │
│   │ (Identity/Role)  │          │ (MCTS / ReAct)   │   │
│   └────────┬─────────┘          └────────┬─────────┘   │
│            │                             │             │
│            ▼                             ▼             │
│   ┌──────────────────┐          ┌──────────────────┐   │
│   │      MEMORY      │          │      TOOLS       │   │
│   │(Working/Semantic)│          │ (API/CLI/Bash)   │   │
│   └──────────────────┘          └──────────────────┘   │
└────────────────────────────────────────────────────────┘
```

#### ক. Profiling & Persona (ভূমিকা ও পরিচয়)
এজেন্টকে একটি নির্দিষ্ট রোলে আবদ্ধ করা (যেমন: `"You are a Senior Security Auditor"`)। এটি তার ডিসিশন মেকিং বা টুল ব্যবহারের প্রোফাইল গাইড করে।

#### খ. Planning & The ReAct Pattern (পরিকল্পনা)
এজেন্ট কীভাবে চিন্তা করে অ্যাকশন নেবে, তার জন্য সবচেয়ে সফল ও Standard Pattern হলো **ReAct (Reason + Act)**।
* **Thought (চিন্তা):** AI প্রথমে এনালাইসিস করে: *"এই মুহূর্তে আমার Customারের ট্রানজ্যাকশন আইডি ও স্ট্যাটাস জানা প্রয়োজন।"*
* **Action (কাজ):** সে একটি স্পেসিফিক টুল বা Function কল করে: `check_payment_status(trx_id="1234")`।
* **Observation (পর্যবেক্ষণ):** সে টুলের Output দেখে: `{"status": "failed", "error": "insufficient funds"}`।
* **Thought (পরবর্তী চিন্তা):** সে অবজারভেশন রিড করে সিদ্ধান্ত নেয়: *"যেহেতু ব্যালেন্স কম ছিল, Customারকে পোলাইটলি ব্যালেন্স রিচার্জ করতে বলতে হবে।"*
* **Final Action:** সে Customারকে মেসেজ পাঠায়।

#### গ. Memory (স্মৃতিশক্তি)
* **Working Memory (Short-term):** বর্তমান সেশনের মেসেজ হিস্টোরি (Messages array)।
* **Semantic Memory (Long-term):** Vector ডাটাবেসে সেভ থাকা Customার প্রোফাইল বা Custom ইনফরমেশন।

#### ঘ. Tools (অস্ত্রাগার)
এজেন্টের হাত-পা। AI নিজে ব্রাউজার বা Database এক্সেস করতে পারে না। আমরা তাকে API, CLI, বা Bash কমান্ড রান করার Custom Function বা টুল জোড়া দিয়ে দেই।

🧠 Remember

**Agent = LLM + Tools + Loop**  
এজেন্ট নিজে কোনো নতুন Engineerিং টেকনোলজি নয়; এটি হলো লার্জ Language Model-এর চারপাশে Custom Loop ও টুল Integration করে তৈরি করা একটি স্বয়ংক্রিয় System।

---

### ৩. Visual Explanation: Agentic রিফ্লেকশন (Self-Correction) Loop

এজেন্ট যখন কোনো ব্যর্থ টাস্ক নিজে নিজে fix করে, সেই সেলফ-কারেকশন ফ্লো নিচে Diagramের মাধ্যমে ভিজ্যুয়ালাইজ করো:

[VISUAL]
Title: Agentic Self-Correction Loop
Illustration: Cyclic flow of Think -> Act -> Test Fails -> Reflection -> Update Plan -> Success
Placement: After Reflection Section
Purpose: Show the robustness of self-evaluating agents.

```
       [ Goal: "Compile code" ]
                   │
                   ▼
               [ Think ]
                   │
                   ▼
         [ Act: Write Code ]
                   │
                   ▼
        [ Observe: Test Fails! ]
                   │
                   ▼
       [ Reflection & Re-plan ] ──► (Incorporate error log and self-correct)
                   │
                   ▼
     [ Act 2: Fix Code & Run Test ] ──► [ Success ✓ ]
```

---

### ৪. Real World Example: Claude Code ও Devin-এর স্বয়ংক্রিয় বাগ ফিক্সিং

গ্লোবাল টেক জায়ান্টদের তৈরি করা **Claude Code** বা **Devin** কীভাবে একটি পুরো কোডবেস Modify করে:

1. **System Parsing:** এজেন্ট প্রথমে পুরো গিটহাব রিপোজিটরির ডিরেক্টরি স্ট্রাকচার রিড করে একটি ডাইনামিক File ম্যাপ তৈরি করে।
2. **ReAct Execution Loop:** সে Custom ব্যাশ (Bash) কমান্ড এবং File রিডার টুল ব্যবহার করে Code চেঞ্জ করে এবং আক্রান্ত Test ফাইলগুলো রান করে।
3. **Healing on Failures:** Test ফেইল করলে সে ভয়ে পিছিয়ে যায় না। Test Error Log নিজে রিড করে সেলফ-অ্যারর হিলিং (Auto-heal) Mechanism-এ Code Modify করে সাকসেসফুল হওয়ার পর মার্জ রিকোয়েস্ট ক্রিয়েট করে।

---

### ৫. Developer Perspective: পাইথনে স্ক্র্যাচ থেকে একটি সম্পূর্ণ Agentic Loop Implementation

💻 Developer View

Developer হিসেবে পাইথনে কোনো Custom Library (যেমন LangChain বা CrewAI) ছাড়া একটি খাঁটি ReAct Loop এবং Custom এজেন্ট System যেভাবে ডিজাইন করতে হয়:

```python
import time

# ১. এজেন্টের জন্য এভেলেবল কাস্টম টুল
def check_bkash_payment(trx_id):
    # মক Database চেক
    database = {"TRX999": "Failed due to insufficient balance", "TRX111": "Success"}
    return database.get(trx_id, "Transaction ID not found")

# ২. এজেন্ট Prompt (ReAct format)
system_prompt = """
You are WhatsMonk's customer support agent.
Solve the customer query by thinking step-by-step and calling tools.

Available Tools:
- check_bkash_payment(trx_id): Returns payment status.

Follow this exact format in every loop turn:
Thought: Describe what you need to do.
Action: tool_name(arguments)
Observation: (You will receive this from the system)
... (Repeat until you have the final answer)
Final Answer: State the final response to the user.
"""

# ৩. এজেন্ট রান Loop (The Agentic Loop Engine)
def run_agent(user_query, trx_id):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Query: {user_query}, Trx: {trx_id}"}
    ]
    
    max_turns = 3
    print("Agentic Loop Started...\n")
    
    # সিমুলেটেড কাস্টম এজেন্ট থিংকিং Loop
    # (বাস্তবে প্রতি লুপে LLM call হয়, এখানে আমরা ম্যাপিং দেখাচ্ছি)
    print("Turn 1:")
    print("Thought: I need to check the bKash payment status for transaction ID.")
    print("Action: check_bkash_payment('TRX999')")
    
    # টুল এক্সিকিউশন (Observation)
    observation = check_bkash_payment("TRX999")
    print(f"Observation: {observation}\n")
    
    print("Turn 2:")
    print("Thought: The payment failed because of insufficient balance. I should inform the customer.")
    print("Final Answer: প্রিয় গ্রাহক, তোমার TRX999 পেমেন্টটি অপর্যাপ্ত ব্যালেন্সের কারণে ব্যর্থ হয়েছে। দয়া করে রিচার্জ করে আবার চেষ্টা করো।")
    
    print("\nAgentic Loop Completed successfully! ✓")

run_agent("আমার পেমেন্ট আটকে গেছে কেন?", "TRX999")
```

---

### ৬. Production Perspective: Infinite Loop Protection & Safety Gates

 Production Reality

Agentic AI প্রোডাকশনে Deploy করার সময় সবচেয়ে বিপজ্জনক বিপদ হলো **Infinite Loop / VRAM Blow-up**।

* **Infinite Loop:** এজেন্ট যখন কোনো একটি বাগ ফিক্স করতে গিয়ে বারবার একই ভুল Code লেখে এবং Test ফেইল করে, সে বারবার API কল করতে থাকে। ১০ মিনিটে সে হাজার হাজার ডলারের API বিল বা Token কস্ট জেনারেট করে Companyর বড় আর্থিক ক্ষতি করতে পারে।
* **সমাধান:** প্রোডাকশন হারনেস ইঞ্জিনে strictly **Max Iterations Limit** (যেমন: সর্বোচ্চ ১০ বার Loop ঘুরবে) সেট করা থাকে। একই সাথে ডেসট্রাকটিভ বা বিপজ্জনক টুল (যেমন: `rm -rf` বা `git push --force`) কল করার আগে **Human-in-the-loop (HITL)** গেটওয়ে সচল রাখা হয়, যা ডেভেলপারের অনুমতি ছাড়া কমান্ড রান করে না।

---

### ७. Common Mistakes

🔴 Common Mistake

**ভুল ধারণা:** চ্যাটবটের মতো এজেন্টকেও যেকোনো সাধারণ ওপেন-এন্ডেড চ্যাট Prompt দিয়ে ডাইরেক্ট প্রোডাকশনে ছেড়ে দেওয়া যায়।

**বাস্তবতা:** এজেন্ট খুবprobabilistic। তাকে ডাইনামিকলি সঠিক পথে রাখতে কড়া **Constitutional Guides (AGENTS.md)** এবং Input-Output Validation লেয়ার ব্যবহার করা বাধ্যতামূলক। অন্যথায় এজেন্ট ভুল কমান্ড রান করে Server Data ক্র্যাশ করে দিতে পারে।

---

### ৮. Mental Model: স্বায়ত্তশাসিত রোবট ভ্যাকুয়াম ক্লিনার

AI এজেন্টের মেন্টাল Model:

**"AI Agent = ঘরের কোন কোণায় ময়লা আছে তা নিজে খুঁজে পরিষ্কার করার ভ্যাকুয়াম ক্লিনার রোবট"**

[VISUAL]
Title: Robot Vacuum Cleaner Analogy of AI Agents
Illustration: High-quality ASCII showing robot mapping rooms, bumping to obstacles, and adjusting paths
Placement: Under Mental Model
Purpose: Ground the autonomous navigation feedback loop.

```
  [ Goal: Clean Room ] ──► [ Sense Obstacle / Test Fail ] ──► [ Adjust Path / Self-Correct ]
                                      ▲                                     │
                                      └─────────────────────────────────────┘
```

তুমি তাকে ঘরের রুলস ও বাউন্ডারি ট্যাগ করে দিয়ে শুধু একটি লক্ষ্য দিলে: `"ঘর পরিষ্কার করো"`। সে নিজে পুরো ঘরের নকশা মেপে নেয় (Planning)। সে আসবাবপত্রে ধাক্কা খেলে বা বাধা পেলে বিভ্রান্ত হয়ে কান্নাকা্টি করে না। সে তার সেন্সর দিয়ে ব্যাকট্র্যাক করে অন্য পথে এগিয়ে কাজ সম্পন্ন করে চার্জে ফিরে যায় (Self-correction & Completion)।

---

### ৯. Mini Project: পাইথনে স্ক্র্যাচ থেকে একটি Custom File এডিটিং AI এজেন্ট উইথ ব্যাকট্র্যাকিং

চলো পাইথনে Custom সেলফ-কারেকশন Loop ব্যবহার করে একটি মিনি এজেন্ট স্ক্র্যাচ থেকে তৈরি করি, যা ফাইলে ভুল Code লিখলে Automatically Error রিড করে ব্যাকট্র্যাক করে Code ফিক্স করতে পারে।

```python
import subprocess
import os

# ১. কাস্টম রাইটার ও Test এজেন্ট
class CodeAgent:
    def __init__(self):
        self.filename = "C:\\Users\\user\\.gemini\\antigravity\\brain\\d18b6320-548d-4c78-80c0-d11b5a5704b7\\scratch\\temp_agent_code.py"
        
    def write_code(self, code_content):
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(code_content)
            
    def run_tests(self):
        # পাইথন Code সিনট্যাক্স রান Test
        result = subprocess.run(["python", self.filename], capture_output=True, text=True)
        return result.returncode, result.stderr

    def heal_code(self):
        print("Agent writing initial code with syntax error...")
        # ভুল সিনট্যাক্স Code (Missing closing bracket)
        self.write_code("print('Hello World'") 
        
        # Loop চালিয়ে Error ডিটেক্ট ও ফিক্স করো
        for turn in range(3):
            code, err = self.run_tests()
            if code == 0:
                print("\n[SUCCESS] Code compiled successfully! Agent task done.")
                break
            else:
                print(f"\n[ERROR DETECTED] Turn {turn+1}: {err.strip()}")
                print("Agent reflecting and self-correcting the code...")
                # সঠিক সিনট্যাক্স Code দিয়ে রিপ্লেস
                self.write_code("print('Hello World')")
        
        # ক্লিনআপ
        if os.path.exists(self.filename):
            os.remove(self.filename)

agent = CodeAgent()
agent.heal_code()
```

#### Code Breakdown:
* **Input:** ভুল সিনট্যাক্সসহ Custom পাইথন Code কন্টেন্ট।
* **Output:** সাবপ্রসেস Error ডিটেকশন Log রিড করে এজেন্টের Custom সেলফ-কারেকশন ও সাকসেসফুল কমপ্লিশন।
* **Why it works:** এজেন্টের ভেতরের `run_tests` ফিডব্যাক লুপটি ভুল ডিটেক্ট করে Code হিলিং লেয়ারে সিগন্যাল পাস করেছে।
* **When to use:** Custom Coding Assistant এবং সেলফ-কারেক্টিং AI অটোমেশন এজেন্ট Architect করার জন্য।

---

### ১০. Interview Questions

#### Beginner
1. **প্রশ্ন:** সাধারণ চ্যাটবট এবং AI এজেন্টের (AI Agent) মধ্যে মূল বৈসাদৃশ্য কী?
   * **উত্তর:** চ্যাটবট শুধুমাত্র মেসেজ ফ্লোতে ইউজারের প্রশ্নের ওয়ান-শট উত্তর দেয় এবং কাজ শেষ। কিন্তু AI এজেন্ট স্বায়ত্তশাসিতভাবে একটি গোল পাওয়ার পর নিজে চিন্তা (Think), কাজ (Act), এবং পর্যবেক্ষণ (Observe) Loop চালিয়ে ভুল নিজে fix করে লক্ষ্য অর্জন না হওয়া পর্যন্ত কাজ চালিয়ে যায়।

#### Intermediate
2. **প্রশ্ন:** Agentic AI-তে "ReAct" ডিজাইন Pattern কীভাবে কাজ করে?
   * **উত্তর:** ReAct হলো Reasoning and Acting এর সমন্বয়। এটি এজেন্টকে প্রতিটি ধাপে প্রথমে চিন্তা (Thought) করতে গাইড করে সে কী করতে চায়, তারপর একটি Custom টুল রান করতে (Action) বলে এবং টুলের Output পর্যবেক্ষণ (Observation) করে পরবর্তী ডিসিশন মেকিং Loop alive রাখে।

#### Advanced
3. **প্রশ্ন:** প্রোডাকশনে একটি স্বায়ত্তশাসিত Coding এজেন্টের "Infinite Loop & Wallet Drainage" রিস্ক কীভাবে প্রতিহত করা যায়?
   * **উত্তর:** এটি প্রতিহত করতে ব্যাকঅ্যান্ড হারনেস ইঞ্জিনে strictly **Max Iterations Limit** (যেমন: ৫ বা ১০ বারের বেশি Loop ঘুরবে না) এবং **Max Token/Cost Budget Limit** সেট করে দেওয়া হয়। একই সাথে যেকোনো ডেসট্রাকটিভ বা হাই-রিস্ক কমান্ড এক্সিকিউট করার আগে **Human-in-the-loop (HITL)** কনফার্মেশন গেটওয়ে সচল রাখা হয়, যা ইউজারের ডিরেক্ট পারমিশন ছাড়া টুল রান করে না।

---

### ১১. Chapter Summary
* **AI Agent** হলো নির্দিষ্ট গোল এচিভ করার জন্য ডিজাইন করা স্বায়ত্তশাসিত AI System।
* **ReAct Pattern** থিংক, অ্যাক্ট এবং অবজারভেশন Loop-এর মাধ্যমে এজেন্টের ডিসিশন গাইড করে।
* **Self-Correction** ব্যর্থ Test Log নিজে রিড করে ভুল fixের ক্ষমতা এচিভ করায়।
* প্রোডাকশন সিস্টেমে AI এজেন্টকে সুরক্ষিত রাখতে **HITL Gateways** এবং **Iteration Bounds** সেট করা বাধ্যতামূলক।

---

### ১২. What's Next
দারুণ! আমরা ভালোভাবে AI এজেন্টের কোর ফাউন্ডেশন ও সেলফ-কারেকশন Loop শেষ করে ফেলেছি। পরের chapter-এ আমরা এই এজেন্টের সবচেয়ে গুরুত্বপূর্ণ হাত-পা বা অ্যাকশন লেয়ার নিয়ে আলোচনা করব: **Chapter 19: Tool Calling & Function Integration**। কীভাবে JSON স্কিমা ব্যবহার করে টুল কনট্র্যাক্ট ডিজাইন করা হয় এবং AI কীভাবে Dynamically সঠিক Parameter জেনারেট করে Custom API কল করে, তা আমরা বিস্তারিত শিখব।

---
**Chapter 18 শেষ।**
