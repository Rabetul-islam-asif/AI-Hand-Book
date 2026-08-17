# Chapter 20: AI Agents — From Chatbots to Autonomous Workers

---

তোমার চ্যাটবটকে বলো, *"আমার Project-এর বাগ ফিক্স করে দাও।"* 

কী করবে সে? 

উত্তর দেবে: *"এইভাবে ফিক্স করতে পারো..."* — ব্যস, এইটুকুই। 

তুমি নিজে Code কপি করবে, পেস্ট করবে, Error আসলে আবার তাকে দেখাবে। 

এখানে তুমি হলে স্রেফ একজন কপি-পেস্ট ড্রাইভার!

কিন্তু ধরো, AI নিজেই পুরো কোডবেস রিড করলো, নিজেই বাগ খুঁজে বের করলো, Code লিখলো, Test রান করলো, ফেইল হলে নিজেই ফিক্স করলো— 

আর শেষে বললো, *"কাজ শেষ, PR রেডি।"* 

এটাই হলো AI Agent! চ্যাটবট থেকে Autonomous Worker-এ উত্তরণ। 

মজার ব্যাপার হলো, এটাই এখন গ্লোবাল টেক ইন্ডাস্ট্রির সবচেয়ে হট ট্রেন্ড।

তো চলো দেখি ReAct Pattern (Think → Act → Observe) কীভাবে কাজ করে, Planning আর Self-Correction Loop কীভাবে Implement করতে হয়। 

সহজ কথায়, এটা বুঝলে পরের চ্যাপ্টারের Tool Calling, MCP Protocol আর Harness Engineering— সব জায়গায় তুমি দারুণ কমফোর্টেবল থাকবে। Deal?


## ১. বাচাল সহকারী বনাম দায়িত্বশীল কর্মী

ধরো, তুমি তোমার কোম্পানির জন্য একজন নতুন Developer হায়ার করলে।

এখন এই ডেমো ডেভেলপার মূলত দুইভাবে কাজ করতে পারে।

প্রথমটি হলো Chatbot Mode বা ইনঅ্যাক্টিভ সহকারী।

এখানে সে কেমন আচরণ করবে?

ধরো, তুমি তাকে বললে, `"JavaScript-এর এই Code-টা Python-এ Convert করে দাও।"`

সে সাথে সাথে Convert করে দিল।

কিন্তু তুমি যখন সেটা ফাইলে রান করলে, দেখলে একটা Error এসেছে।

তখন কী হবে?

তুমি আবার সেই Error কপি করে তাকে দেখালে। সে সেটা ফিক্স করে দিল।

খেয়াল করেছ? এখানে তুমি নিজেই কপি-পেস্ট ড্রাইভার হিসেবে কাজ করছ, আর সে শুধু তোমার Instruction ফলো করছে।

![Conversational Chatbot vs. Autonomous AI Agent](/diagrams/agent_vs_chatbot.png)


তাহলে Agent Mode বা Autonomous Worker কী জিনিস?

এখানে তুমি তাকে একটা Goal দিয়ে বলবে, `"Payment Gateway-তে Transaction Error আসছে, ফিক্স করে দাও।"`

তারপর সে কী করবে?

সে নিজে সম্পূর্ণ Codebase রিড করবে।

নিজে নিজেই Log-এ গিয়ে Error খুঁজে বের করবে।

তারপর একটা Custom ফিক্স লিখবে।

এখানেই শেষ নয়, সে লোকাল Test রান করবে。

যদি কোনো Error আসে, সে ঘাবড়ে যাবে না। নিজে নিজেই Code রি-রাইট করে ফিক্স করবে।

আর সবশেষে কাজ সফলভাবে শেষ করে তোমাকে এসে বলবে, `"কাজ শেষ, PR রেডি।"`

কেমন হতো বলো তো?

এটাই হলো AI Agent। একজন দায়িত্বশীল কর্মী।

সে কেবল Word Predict করে বসে থাকে না।

সে নিজের কাজের ফলাফল নিজে ট্র্যাক করে। একটা Loop চালিয়ে সে তার Target বা Goal পূরণ করে ছাড়ে।


## ২. Agentic Loop ও ReAct Pattern

একটি Custom AI Agent আসলে কী কী উপাদান নিয়ে তৈরি হয়?

সহজ কথায়, এর পেছনে ৪টি প্রধান পিলার বা উপাদান থাকে।

![The Four Pillars of AI Agent Architecture](/diagrams/four_pillars_agent.png)


চলো এই ৪টি পিলার সহজে বুঝে নিই।

প্রথম পিলারটি হলো Profiling & Persona।

এটা কী?

এজেন্টকে একটা নির্দিষ্ট রোল দিয়ে দেওয়া। যেমন: `"You are a Senior Security Auditor"`。

এই রোল বা পরিচয়টাই ঠিক করে দেয় সে কীভাবে Decision নেবে বা কী কী Tool ব্যবহার করবে।

দ্বিতীয় পিলারটি হলো Planning ও ReAct Pattern।

এখানে এজেন্ট কীভাবে কাজ করবে তার পরিকল্পনা করে।

এজন্য সবচেয়ে জনপ্রিয় Pattern হলো ReAct (Reason + Act)。

এটি কীভাবে কাজ করে?

ধরো, পুরো প্রক্রিয়াটি কয়েকটি ধাপে ঘটে:

১. Thought: AI প্রথমে নিজে চিন্তা করে এনালাইসিস করে, *"আমার এখন Customer-এর Transaction ID আর Status জানা দরকার।"*

২. Action: এরপর সে একটা নির্দিষ্ট Tool বা Function কল করে। যেমন: `check_payment_status(trx_id="1234")`。

৩. Observation: এবার সে টুলের Output দেখে বা পর্যবেক্ষণ করে। যেমন: `{"status": "failed", "error": "insufficient funds"}`。

৪. Thought: সে টুলের Output দেখে আবার চিন্তা করে সিদ্ধান্ত নেয়, *"যেহেতু Balance কম, তাই Customer-কে রিচার্জ করতে বলতে হবে।"*

৫. Final Action: সবশেষে সে Customer-কে মেসেজ পাঠায়।

মজার ব্যাপার হলো, পুরো জিনিসটা খুব সিম্পল, তাই না?

তৃতীয় পিলারটি হলো Memory।

![Memory and State Management Diagram](/diagrams/memory and state management.png)

এজেন্টের স্মৃতিশক্তি কেমন হতে পারে?

সাধারণত দুই ধরনের।

প্রথমটি হলো Working Memory।

এটি হচ্ছে বর্তমান সেশনের Chat History বা Messages array।

আর দ্বিতীয়টি হলো Semantic Memory।

এটি হলো Vector database-এ সেভ থাকা Customer Profile বা কোনো Custom Information, যা অনেকদিন মনে রাখতে হয়।

চতুর্থ পিলারটি হলো Tools।

এগুলোকে এজেন্টের হাত-পা বলতে পারো।

কারণ AI তো নিজে ব্রাউজার বা Database এক্সেস করতে পারে না।

তাই আমরা তাকে API, CLI বা Bash কমান্ড রান করার জন্য কিছু Custom Function বা Tool যুক্ত করে দিই।

🧠 Remember

**Agent = LLM + Tools + Loop**

মনে রেখো, Agent নিজে কোনো নতুন Engineering টেকনোলজি নয়।

এটি হলো LLM-এর চারপাশে একটা Custom Loop আর Tool Integration করে তৈরি করা একটি চমৎকার System।


## ৩. Self-Correction Loop

একটি Agent যখন কোনো কাজ ফেইল করে, তখন সে নিজে নিজে কীভাবে সেটা ফিক্স করে?

চলো নিচের Diagram-টি থেকে এই Self-Correction Flow দেখে নিই:

![Agentic Self-Correction Loop (Code Healing)](/diagrams/agent_self_correction.png)



## ४. Claude Code ও Devin কীভাবে কাজ করে?

আজকাল গ্লোবাল টেক জায়ান্টদের তৈরি করা Claude Code বা Devin-এর মতো টুলের কথা আমরা প্রায়ই শুনি।

কিন্তু এগুলো একটা পুরো Codebase নিজে নিজে কীভাবে Modify করে?

পুরো প্রক্রিয়াটি ঘটে মাত্র তিনটি ধাপে।

প্রথমধাপ হলো System Parsing।

এখানে Agent প্রথমে পুরো GitHub Repository-র Directory Structure রিড করে একটি ডাইনামিক File Map তৈরি করে নেয়।

দ্বিতীয় ধাপ হলো ReAct Execution Loop।

সে কাস্টম Bash কমান্ড এবং File Reader টুল ব্যবহার করে কোডে প্রয়োজনীয় পরিবর্তন আনে। 

তারপর আক্রান্ত Test ফাইলগুলো রান করে দেখে।

তৃতীয় ধাপ হলো Healing on Failures।

যদি রান করার সময় Test ফেইল করে, সে কিন্তু ভয় পেয়ে পিছিয়ে যায় না!

বরং সে Test Error Log নিজে নিজে রিড করে। 

এরপর Auto-heal পদ্ধতিতে কোডটি Modify করে ফেলে।

কাজটি সফলভাবে শেষ হওয়ার পর সে নিজেই একটা Merge Request বা PR তৈরি করে দেয়।


## ৫. Python-এ স্ক্র্যাচ থেকে Agentic Loop
Developer Perspective

একজন Developer হিসেবে তুমি কি কোনো কাস্টম লাইব্রেরি (যেমন LangChain বা CrewAI) ছাড়া কোড লিখতে চাও? 

চলো দেখি কীভাবে শুধু Python ব্যবহার করে স্ক্র্যাচ থেকে একটা খাঁটি ReAct Loop এবং কাস্টম Agent System ডিজাইন করা যায়:

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


## ৬. Infinite Loop ও Safety Gates
Production Reality

যখন তুমি Agentic AI-কে প্রোডাকশনে Deploy করবে, তখন সবচেয়ে বড় ভয়ের কারণ কী হতে পারে?

সবচেয়ে বিপজ্জনক সমস্যাটি হলো Infinite Loop এবং VRAM Blow-up।

এই Infinite Loop আসলে কী?

ধরো, Agent কোনো একটা বাগ ফিক্স করার চেষ্টা করছে। 

সে বারবার একই ভুল কোড লিখছে আর Test ফেইল করছে। 

এর ফলে সে অনবরত API কল করতে থাকবে। 

দেখা যাবে মাত্র ১০ মিনিটে সে হাজার হাজার ডলারের API বিল বা Token কস্ট বানিয়ে ফেলেছে! 

এতে কোম্পানির অনেক বড় আর্থিক ক্ষতি হতে পারে।

তাহলে এর সমাধান কী?

এর সমাধান হলো প্রোডাকশন হারনেস ইঞ্জিনে strictly **Max Iterations Limit** সেট করা। 

যেমন: সর্বোচ্চ ১০ বার Loop ঘুরবে, এরপর থেমে যাবে। 

একই সাথে বিপজ্জনক টুল (যেমন: `rm -rf` বা `git push --force`) কল করার আগে **Human-in-the-loop (HITL)** গেটওয়ে সচল রাখা হয়। 

ফলে তোমার অনুমতি ছাড়া সে কোনো বড় বা ক্ষতিকর কমান্ড রান করতে পারবে না।


## ৭. Common Mistakes
Common Mistake

আমরা অনেকেই ভাবি, চ্যাটবটের মতো এজেন্টকেও যেকোনো সাধারণ ওপেন-এন্ডেড চ্যাট Prompt দিয়ে সরাসরি প্রোডাকশনে ছেড়ে দেওয়া যায়।

কিন্তু এটা কি আসলেই ঠিক?

একদমই নয়! 

কারণ এজেন্ট অনেক বেশি probabilistic বা সম্ভাবনা-ভিত্তিক। 

তাই তাকে সবসময় সঠিক পথে রাখতে কড়া **Constitutional Guides (AGENTS.md)** এবং Input-Output Validation লেয়ার ব্যবহার করা জরুরি। 

নাহলে এজেন্ট ভুলভাল কমান্ড রান করে তোমার পুরো Server Data ক্র্যাশ করে দিতে পারে!


## ৮. ভ্যাকুয়াম ক্লিনার রোবট

AI Agent-কে আমরা সহজে কীভাবে কল্পনা করতে পারি?

এর সবচেয়ে দারুণ মেন্টাল Model হলো একটি ঘরের ভ্যাকুয়াম ক্লিনার রোবট।

![Robot Vacuum Cleaner Analogy of Autonomous Agents](/diagrams/vacuum_cleaner_analogy.png)


ধরো, তুমি তাকে ঘরের Rules আর Boundary সেট করে দিলে। 

তারপর শুধু একটা লক্ষ্য দিলে: `"ঘর পরিষ্কার করো"`। 

সে নিজে নিজে পুরো ঘরের নকশা মেপে নেবে, যাকে আমরা বলি Planning। 

কাজ করতে গিয়ে সে যদি কোনো আসবাবপত্রে ধাক্কা খায় বা বাধা পায়, সে কিন্তু ঘাবড়ে কান্নাকা্টি শুরু করবে না! 

সে তার Sensor দিয়ে ব্যাকট্র্যাক করবে এবং অন্য পথ খুঁজে নিয়ে কাজ সম্পন্ন করবে। 

সবশেষে নিজেই চার্জারে ফিরে যাবে, যা হলো Self-correction ও Completion-এর চমৎকার উদাহরণ।


## ৯. Mini Project: কাস্টম এডিটিং AI Agent

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

এখানে আসলে কী ঘটল?

চলো কোডের মূল বিষয়গুলো সহজে বুঝে নিই।

এখানে Input হিসেবে কী দেওয়া হয়েছে?

ভুল Syntax-সহ একটি কাস্টম Python কোড কন্টেন্ট।

তাহলে Output-এ কী পাওয়া গেল?

Subprocess থেকে Error Detection Log রিড করে কাস্টম Self-correction এবং সফলভাবে কাজ শেষ করার বার্তা।

কিন্তু এটি কীভাবে কাজ করল?

খুব সহজ! 

এজেন্টের ভেতরে থাকা `run_tests` ফিডব্যাক লুপটি ভুল খুঁজে পেয়ে কোড হিলিং লেয়ারে সিগন্যাল পাঠিয়েছে।

আর এটি আমরা কখন ব্যবহার করব?

কাস্টম Coding Assistant এবং নিজে নিজে ভুল সংশোধন করতে পারে এমন AI Automation Agent তৈরি করতে তুমি এই প্যাটার্নটি ব্যবহার করতে পারো।


## ১০. Multi-Agent Systems ও Agent-to-Agent (A2A) কমিউনিকেশন

এখন পর্যন্ত আমরা একটি এজেন্টের একা একা কাজ করার ক্ষমতা দেখেছি। 

নন-ট্রিভিয়াল জটিল সিস্টেমে যখন কাজের জটিলতা অনেক বেড়ে যায়, তখন কি একটা এআই দিয়ে সব কাজ করানো সম্ভব?

হয়তো সম্ভব, কিন্তু রেজাল্ট ভালো হবে না। খিচুড়ি পেকে যাওয়ার সম্ভাবনা অনেক বেশি!

তাই আমরা একটার বদলে অনেকগুলো ছোট ছোট স্পেশালিস্ট এজেন্টের একটি টিম বা **Multi-Agent System** ব্যবহার করি।

![Multi-Agent System Diagram](/diagrams/multy_agent_system.png)

যেমন ধরো:
*   **Research Agent:** সে শুধু ইন্টারনেটে তথ্য খোঁজার কাজে পারদর্শী।
*   **Coding Agent:** সে শুধু কোড লেখার কাজ ভালো বোঝে।
*   **Executive Agent:** সে কাজের গুণগত মান যাচাই করে ইউজারের সাথে যোগাযোগ রাখে।

প্রতিটি এজেন্ট কিন্তু স্বাধীন এবং তাদের নিজের নিজস্ব লক্ষ্য (Goal) রয়েছে।

### A2A (Agent-to-Agent): এজেন্টদের দলগত চ্যাট

তাহলে এই এজেন্টরা নিজেদের মধ্যে কাজ কীভাবে ভাগ করে নেয়?

সেটার জন্য আমাদের প্রয়োজন **A2A (Agent-to-Agent) Communication**। 

![Agent-to-Agent Communication Diagram](/diagrams/A2A.png)

সহজ কথায়, এটা হলো টিমের সব স্পেশালিস্টদের একটা চ্যাট গ্রুপ বা গ্রুপ চ্যাট। 

এখানে কোনো হিউম্যান ড্রাইভার বা মানুষের হস্তক্ষেপ ছাড়াই এজেন্টরা নিজেদের মধ্যে কথা বলে, ফাইল পাস করে, আর নেগোশিয়েট করে কাজ শেষ করে ফেলে।

যেমন— Executive Agent রিকোয়েস্ট পেয়ে প্রথমে Research Agent-কে বলে ডাটা এনে দিতে। 

সে ডাটা এনে দিলে Coding Agent-কে বলে কোড লিখতে। 

এভাবে ব্যাকগ্রাউন্ডে নিজেরা চ্যাট করে পুরো টাস্ক সফলভাবে ডেলিভারি করে!


## ১১. Interview Questions

চলো এবার ইন্টারভিউয়ের জন্য কিছু গুরুত্বপূর্ণ প্রশ্ন এবং তাদের উত্তরগুলো একনজরে দেখে নিই।

### Beginner Level

**প্রশ্ন:** সাধারণ Chatbot আর AI Agent-এর মধ্যে মূল পার্থক্য কী?

**উত্তর:** Chatbot শুধু মেসেজ ফ্লোতে ইউজারের প্রশ্নের ওয়ান-শট উত্তর দেয়। কাজ শেষ হলে তার ভূমিকাও শেষ। 

কিন্তু AI Agent স্বাধীনভাবে কোনো Goal পাওয়ার পর নিজে নিজে চিন্তা করে (Think), কাজ করে (Act) এবং ফলাফল পর্যবেক্ষণ করে (Observe)। 

সে ভুল হলে নিজে নিজে ফিক্স করে লক্ষ্য অর্জন না হওয়া পর্যন্ত কাজ চালিয়ে যায়।

### Intermediate Level

**প্রশ্ন:** Agentic AI-তে ReAct ডিজাইন Pattern কীভাবে কাজ করে?

**উত্তর:** ReAct হলো Reasoning ও Acting-এর সমন্বয়। 

এটি প্রতিটি ধাপে এজেন্টকে প্রথমে চিন্তা (Thought) করতে সাহায্য করে যে সে কী করতে চায়। 

এরপর সে একটি Custom Tool (Action) রান করে এবং টুলের Output পর্যবেক্ষণ (Observation) করে পরবর্তী সিদ্ধান্ত নেওয়ার লুপটি সচল রাখে।

### Advanced Level

**প্রশ্ন:** প্রোডাকশনে একটি স্বাধীন Coding Agent-এর Infinite Loop এবং Wallet Drainage-এর ঝুঁকি কীভাবে কমানো যায়?

**উত্তর:** এটি প্রতিহত করতে ব্যাকএন্ড হারনেস ইঞ্জিনে কঠোরভাবে **Max Iterations Limit** (যেমন: ৫ বা ১০ বারের বেশি Loop ঘুরবে না) এবং **Max Token/Cost Budget Limit** সেট করে দেওয়া হয়। 

একই সাথে যেকোনো ক্ষতিকর বা হাই-রিস্ক কমান্ড এক্সিকিউট করার আগে **Human-in-the-loop (HITL)** কনফার্মেশন গেটওয়ে সচল রাখা হয়। 

ফলে ইউজারের সরাসরি অনুমতি ছাড়া সে কোনো টুল রান করতে পারে না।


## ১২. Chapter Summary

এই অধ্যায়ে আমরা চমৎকার কিছু জিনিস শিখলাম!

প্রথমত, AI Agent হলো নির্দিষ্ট কোনো Goal পূরণ করার জন্য ডিজাইন করা একটি স্বাধীন বা Independent AI System।

দ্বিতীয়ত, ReAct Pattern তার থিংক (Think), অ্যাক্ট (Act) এবং অবজারভেশন (Observe) লুপের মাধ্যমে এজেন্টের সিদ্ধান্ত নেওয়া গাইড করে।

তৃতীয়ত, Self-Correction-এর মাধ্যমে এজেন্ট কোনো ভুল বা ফেইল হওয়া টেস্ট লগ নিজে রিড করে তা ফিক্স করতে পারে।

সবশেষে, প্রোডাকশন সিস্টেমে AI এজেন্টকে সুরক্ষিত ও নিরাপদ রাখতে HITL Gateways এবং Iteration Bounds সেট করা একদম বাধ্যতামূলক!


## ১৩. What's Next?

দারুণ! আমরা AI Agent-এর মূল ভিত্তি আর Self-Correction Loop বেশ ভালোভাবে বুঝে ফেলেছি।

পরের চ্যাপ্টারে আমরা এজেন্টের হাত-পা বা অ্যাকশন লেয়ার নিয়ে কথা বলব।

আমাদের পরবর্তী বিষয়: **Chapter 21: Tool Calling & Function Integration**!

সেখানে আমরা শিখব কীভাবে AI নিজে কাস্টম API কল করে চমৎকার সব কাজ করে ফেলে। 

পরের চ্যাপ্টারে দেখা হচ্ছে, Deal?

**Chapter 20 শেষ।**
