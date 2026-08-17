# Chapter 1: AI Agent Architecture & Cognitive Loops (এজেন্টের ভিত্তি ও কগনিটিভ লুপ)

---

তোমার চ্যাটবটকে বলো, *"আমার সার্ভারে মেমোরি লিক হচ্ছে, ফিক্স করে দাও।"* 

সে কী করবে? 

সে হয়তো কিছু থিওরিটিক্যাল টিপস দেবে: *"htop দিয়ে চেক করুন, কোড প্রোফাইলার চালান..."* — ব্যস! 

তোমাকে নিজে টার্মিনাল খুলতে হবে, লগ দেখতে হবে, কোড এডিট করতে হবে এবং সার্ভার রিস্টার্ট দিতে হবে। এখানে তুমি হলে AI-এর জন্য একজন **কপি-পেস্ট ড্রাইভার**।

কিন্তু একটি **Autonomous AI Agent** কী করে?

সে নিজে SSH দিয়ে সার্ভারে ঢুকবে, `htop` ও লগ ফাইল স্ক্যান করবে, মেমোরি লিকের কারণ খুঁজে কোডে প্যাচ বসাবে, টেস্ট রান করবে এবং তোমাকে বলবে: *"Memory leak fixed on PID 4120. Memory consumption dropped from 94% to 22%."*

চ্যাটবট যেখানে শুধু **Passive Text Generator**, সেখানে AI Agent হলো **Goal-Driven Autonomous Worker**।

---

## ১. The Core Anatomy of an AI Agent (এজেন্টের মূল অঙ্গসংস্থান)

একটি AI Agent কেবল একটি লার্জ ল্যাঙ্গুয়েজ মডেল (LLM) নয়। এটি একটি পূর্ণাঙ্গ কগনিটিভ সিস্টেম।

[VISUAL]
Title: Full Anatomy of an Autonomous AI Agent System
```
┌─────────────────────────────────────────────────────────────────────────┐
│                           AI AGENT SYSTEM                               │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    BRAIN: Foundation Model (LLM)                  │  │
│  │           (Reasoning, Instruction Following, Decision Making)     │  │
│  └─────────────────────────────────┬─────────────────────────────────┘  │
│                                    │                                    │
│        ┌───────────────────────────┼───────────────────────────┐        │
│        ▼                           ▼                           ▼        │
│  ┌───────────┐               ┌───────────┐               ┌───────────┐  │
│  │  PLANNING │               │   MEMORY  │               │   TOOLS   │  │
│  │  & REASON │               │  (Context │               │ (Web, API,│  │
│  │ (ReAct,   │               │   Vector, │               │  Bash, DB,│  │
│  │  Tree-of- │               │ Episodic) │               │   Files)  │  │
│  │  Thought) │               │           │               │           │  │
│  └─────┬─────┘               └─────┬─────┘               └─────┬─────┘  │
│        │                           │                           │        │
│        └───────────────────────────┼───────────────────────────┘        │
│                                    ▼                                    │
│                    ┌───────────────────────────────┐                    │
│                    │    ACTION & EXECUTION LOOP    │                    │
│                    │ (Tool Invocation -> Observe)  │                    │
│                    └───────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────────────┘
```

1. **Brain (Core LLM):** সিদ্ধান্ত গ্রহণকারী ইঞ্জিন (যেমন Claude 3.7 Sonnet, DeepSeek R1, GPT-4o)।
2. **Planning & Reasoning:** জটিল সমস্যাকে ছোট সাব-টাস্কে ভাগ করা এবং ট্র্যাক রাখা।
3. **Memory Systems:** আগের স্টেপে কী ঘটেছিল এবং অতীতের সেশন থেকে কী শেখা গেছে তা সংরক্ষণ করা।
4. **Tool Use & Action:** পরিবেশের সাথে ইন্টারঅ্যাক্ট করার ক্ষমতা (Bash রান করা, SQL কুয়েরি করা, ফাইল রাইট করা)।

---

## ২. The ReAct Pattern: Reasoning + Acting

২০০২ সালে প্রিন্সটন ও গুগলের গবেষকরা **ReAct (Reasoning + Acting)** ফ্রেমওয়ার্ক প্রস্তাব করেন। এটিই আধুনিক এজেন্টের মূল ভিত্তি।

লুপটি তিনটি চক্রে আবর্তিত হয়:
$$\text{Thought} \longrightarrow \text{Action} \longrightarrow \text{Observation} \longrightarrow \text{Thought}$$

```
                ┌──────────────────────────────┐
                │   User Goal / Problem Input  │
                └──────────────┬───────────────┘
                               │
                ┌──────────────▼───────────────┐
         ┌─────►│  THOUGHT: What should I do?  │
         │      └──────────────┬───────────────┘
         │                     │
         │      ┌──────────────▼───────────────┐
         │      │  ACTION: Call specific Tool  │
         │      └──────────────┬───────────────┘
         │                     │
         │      ┌──────────────▼───────────────┐
         │      │  OBSERVATION: Tool Output    │
         │      └──────────────┬───────────────┘
         │                     │
         └──────── (Goal achieved? No)
                               │ (Yes)
                ┌──────────────▼───────────────┐
                │  FINAL ANSWER / Deliverable  │
                └──────────────────────────────┘
```

### পাইথনে মিনিমাল ReAct লুপ ইমপ্লিমেন্টেশন:

```python
import json

class SimpleReActAgent:
    def __init__(self, llm_client, tools):
        self.llm = llm_client
        self.tools = {t.name: t for t in tools}
        self.scratchpad = []

    def run(self, user_goal: str, max_steps: int = 6):
        prompt = f"Goal: {user_goal}\nAvailable Tools: {list(self.tools.keys())}\n"
        
        for step in range(max_steps):
            full_context = prompt + "\n".join(self.scratchpad) + "\nThought:"
            response = self.llm.generate(full_context)
            
            # মডেলের রেসপন্স থেকে Thought এবং Action এক্সট্রাক্ট করা
            thought, action_name, action_input = self.parse_response(response)
            self.scratchpad.append(f"Thought: {thought}")
            
            if action_name == "FINISH":
                return action_input # কাজ শেষ
            
            # টুল এক্সিকিউট করা
            tool = self.tools.get(action_name)
            if not tool:
                observation = f"Error: Tool '{action_name}' not found."
            else:
                observation = tool.execute(action_input)
                
            self.scratchpad.append(f"Action: {action_name}({action_input})")
            self.scratchpad.append(f"Observation: {observation}")
            
        return "Failed: Maximum steps exceeded without achieving goal."
```

---

## ৩. Advanced Planning: Plan-and-Solve & Reflection

একক ReAct লুপ অনেক সময় জটিল মাল্টি-স্টেপ প্রজেক্টে বিভ্রান্ত হয়ে যায়। এজন্য উন্নত এজেন্ট আর্কিটেকচারে **Plan-and-Solve** এবং **Reflection Loops** ব্যবহার করা হয়।

### ক. Plan-and-Solve (Planner + Executor)
1. **Planner Agent:** প্রথমে সম্পূর্ণ কাজের একটি রৈখিক বা ট্রি-স্ট্রাকচার্ড ব্লুপ্রিন্ট তৈরি করে (যেমন Step 1 to Step 5)।
2. **Executor Agent:** প্রতিটি স্টেপ ধরে কাজ সম্পন্ন করে।
3. **Replanner:** যদি কোনো স্টেপে এরর আসে, প্ল্যানার তৎক্ষণাৎ অবশিষ্ট প্ল্যান রি-রাইট করে।

### খ. Self-Correction / Reflection Loop
এজেন্ট কোড বা উত্তর তৈরি করার পর সরাসরি ইউজারের কাছে দেয় না। একটি ক্রিটিক (Critic) সাব-এজেন্ট সেটি নিরীক্ষা করে:
* *"কোডটি কি টেস্ট পাস করেছে?"*
* *"এতে কোনো সিকিউরিটি ভলনারেবিলিটি আছে?"*
* ফেইল করলে এরর মেসেজ ফিডব্যাক আকারে নিয়ে রি-জেনারেট করে।

---
Developer Perspective
চ্যাটবটের কনটেক্সট উইন্ডো আর এজেন্টের কনটেক্সট উইন্ডোর ব্যবহারে বিশাল পার্থক্য রয়েছে। এজেন্টের স্ক্র্যাচপ্যাডে প্রতি স্টেপের `Tool Output` জমতে থাকে। যদি কোনো টুল ১০,০০০ লাইনের লগ রিটার্ন করে, তা সরাসরি এজেন্টের কনটেক্সটে পুশ করলে কনটেক্সট ব্লাস্ট হবে এবং টোকেন খরচ আকাশচুম্বী হবে। তাই প্রতিটি টুলের আউটপুট প্রি-প্রসেস ও ট্রাঙ্কেট করে মূল সামারিটুকু এজেন্টের স্ক্র্যাচপ্যাডে দিতে হবে।

---
Production Reality
প্রোডাকশনে আনসুপারভাইজড রিঅ্যাক্ট লুপ সবচেয়ে বড় যে সমস্যার মুখোমুখি হয় তা হলো **Infinite Action Loops**। যেমন: ফাইল রিড করতে গিয়ে `File Not Found` এরর এলো, এজেন্ট আবার একই কমান্ড রান করলো, আবার এরর এলো। প্রোডাকশন এজেন্ট সিস্টেমে কঠোর **Max Iteration Limit** (যেমন max 10 steps), **Loop Detection Algorithm** (আগের ৩টি অ্যাকশন হুবহু একই কি না), এবং **Timeout Circuit Breakers** বসানো বাধ্যতামূলক।

---
Common Mistake
অনেক ডেভেলপার এজেন্ট তৈরি করতে গিয়ে মডেলকে সরাসরি পাইথন বা ব্যাশ কোড রান করার পূর্ণ অনুমতি দিয়ে দেন কোনো স্যান্ডবক্সিং ছাড়া। প্রোডাকশনে এটি চরম বিপজ্জনক। কোনো হ্যালুসিনেশনের কারণে মডেল `rm -rf /` অথবা ডাটাবেস ড্রপ করে দিতে পারে। এজেন্টের সমস্ত টুল এক্সেকিউশন ডকার কন্টেইনার বা ফায়ারওয়াল-যুক্ত আইসোলেটেড স্যান্ডবক্সে চালাতে হবে।

---

## Interview Flashcards

#### Beginner Level
* **প্রশ্ন:** AI Chatbot এবং AI Agent-এর মধ্যে মৌলিক পার্থক্য কী?
* **উত্তর:** চ্যাটবট মূলত প্যাসিভ, টেক্সট ইনপুট পেয়ে টেক্সট প্রেডিক্ট করে থেমে যায়। আর AI Agent হলো গোল-ড্রিভেন এবং স্বয়ংক্রিয়; সে লক্ষ্য অর্জনের জন্য প্ল্যান তৈরি করে, বাহ্যিক টুল ব্যবহার করে (যেমন ব্রাউজার, ব্যাশ, ডাটাবেস), ভুল হলে নিজে শুধরে নেয় এবং কাজ সম্পন্ন করে।

#### Intermediate Level
* **প্রশ্ন:** ReAct প্যাটার্ন কীভাবে এজেন্টের হ্যালুসিনেশন কমায়?
* **উত্তর:** ReAct মডেলে ইন্টারনাল মেমোরির ওপর নির্ভর করার বদলে প্রতিটি সিদ্ধান্তের আগে "Thought" তৈরি করে এবং রিয়েল-টাইম এনভায়রনমেন্ট থেকে "Action"-এর মাধ্যমে "Observation" সংগ্রহ করে। ফলে ফ্যাক্ট ও বাস্তব ডেটার ওপর ভিত্তি করে এজেন্ট সিদ্ধান্ত নেয়।

#### Advanced Level
* **প্রশ্ন:** এজেন্টে Infinite Loop বন্ধ করার জন্য প্রোডাকশনে কী কী মেকানিজম ব্যবহার করা হয়?
* **উত্তর:** ১. হার্ড স্টেপ লিমিট (যেমন Max 10-15 steps), ২. হ্যাশ-বেসড স্টেট হিস্ট্রি ট্র্যাকিং (একই Action ও Input বারবার ঘটলে ইন্টারাপ্ট করা), ৩. টোকেন ও কস্ট বাজেট ক্যাপ এবং ৪. রিপ্ল্যানার ফলব্যাক ট্রিগার।
