# Chapter 5: State Machines & Resumable Workflows (স্টেট মেশিন ও পজেবল ওয়ার্কফ্লো)

---

একটি সাধারণ পাইথন স্ক্রিপ্টে এজেন্টকে `while True:` লুপে চালানো যায়। কিন্তু যদি সার্ভার ক্র্যাশ করে, মেমোরি শেষ হয়ে যায় বা ইউজারকে ৩ দিন পর এসে বাকি কাজ শেষ করতে হয়— তখন কী হবে?

একটি লুপ-বেসড এজেন্ট শুরু থেকে আবার রান করবে এবং আগের সব টোকেন ও কম্পিউট নষ্ট হবে!

এন্টারপ্রাইজ-গ্রেড AI এজেন্ট কখনোই সাধারণ লুপে চলে না; এটি চলে **Graph-Based Deterministic State Machines**-এর ওপর।

---

## ১. Graph State Machine Architecture (স্টেট গ্রাফ আর্কিটেকচার)

[VISUAL]
Title: Cyclic Graph State Machine with Checkpointing & Human Breakpoints
```
                 ┌───────────────────────────┐
                 │       START / INPUT       │
                 └─────────────┬─────────────┘
                               │
                 ┌─────────────▼─────────────┐
                 │     NODE: Research & Plan │
                 └─────────────┬─────────────┘
                               │ 💾 Checkpoint #1 Saved
                 ┌─────────────▼─────────────┐
                 │      NODE: Code Generator │◄─────────────────┐
                 └─────────────┬─────────────┘                  │
                               │ 💾 Checkpoint #2 Saved         │
                 ┌─────────────▼─────────────┐                  │ (Tests Failed)
                 │      NODE: Test Runner    │                  │ Self-Correction Edge
                 └─────────────┬─────────────┘                  │
                               │                                │
                       [Conditional Edge]                       │
                        /              \                        │
             (Tests Pass)              (Tests Fail)─────────────┘
                  │
        ┌─────────▼─────────┐
        │  PAUSE: Wait for  │ ──► [Human approves via UI]
        │   Human Approval  │ 💾 Checkpoint #3 Saved
        └─────────┬─────────┘
                  │
        ┌─────────▼─────────┐
        │ NODE: Deploy to S3│
        └─────────┬─────────┘
                  │
        ┌─────────▼─────────┐
        │        END        │
        └───────────────────┘
```

একটি স্টেট মেশিনের ৪টি মূল উপাদান:
1. **State:** সম্পূর্ণ ওয়ার্কফ্লোর সেন্ট্রাল ডাটা অবজেক্ট (TypedDict / Pydantic).
2. **Nodes:** পৃথক পৃথক ফাংশন বা সাব-এজেন্ট (যেমন: `research_node`, `coder_node`).
3. **Edges:** নোডের মধ্যবর্তী সংযোগ পথ (Fixed বা Conditional Router).
4. **Checkpointer:** প্রতিটি নোড শেষ হওয়ার পর সম্পূর্ণ স্টেট ডাটাবেসে সেভ করা।

---

## ২. Typed State & Checkpointing Implementation

### পাইথনে মিনিমাল স্টেট মেশিন প্যাটার্ন:

```python
from typing import TypedDict, List, Annotated
import operator
import json

# ১. সেন্ট্রাল স্টেট ডেফিনিশন
class AgentState(TypedDict):
    task: str
    plan: List[str]
    code_generated: str
    test_results: str
    status: str
    iteration_count: int

# ২. স্টেট নোডসমূহ
def planner_node(state: AgentState) -> dict:
    plan = ["Step 1: Write SQL Schema", "Step 2: Generate CRUD API"]
    return {"plan": plan, "status": "planned"}

def coder_node(state: AgentState) -> dict:
    code = "def get_users(): return db.query()"
    return {
        "code_generated": code, 
        "iteration_count": state["iteration_count"] + 1
    }

def tester_node(state: AgentState) -> dict:
    # রান টেস্ট
    passed = state["iteration_count"] >= 2 # ডেমো টেস্ট সিমুলেশন
    result = "PASS" if passed else "FAIL: SyntaxError on line 12"
    return {"test_results": result}

# ৩. কন্ডিশনাল রাউটার এজ
def route_after_test(state: AgentState) -> str:
    if state["test_results"] == "PASS":
        return "human_approval"
    if state["iteration_count"] > 3:
        return "failed_abort"
    return "coder_node" # লুপ ব্যাক
```

---

## ৩. Time-Travel Debugging & Resumability

স্টেট মেশিনে **Checkpointing** থাকার কারণে ২টি ম্যাজিক্যাল সুবিধা পাওয়া যায়:

1. **Long-Running Resumability:** এজেন্ট হয়তো কোড লিখে স্টেপ ৩-এ এসে থেমে গেল এবং ইউজারকে ইমেইল পাঠাল। ইউজার ২ দিন পর লিংকে ক্লিক করে অ্যাপ্রুভ করলে এজেন্ট একদম স্টেপ ৪ থেকে শুরু করতে পারবে।
2. **Time-Travel Debugging:** প্রোডাকশনে কোনো বাগ আসলে ডেভেলপার স্টেপ ২-এর পুরনো চেকপয়েন্টে ফিরে গিয়ে স্টেট ডাটা মডিফাই করে আবার রান করতে পারে।

---
Developer Perspective
স্টেট অবজেক্টকে সবসময় **Immutable** বা রিডিউসার প্যাটার্নে হ্যান্ডেল করা উচিত। সরাসরি `state["messages"].append(msg)` না করে `operator.add` রিডিউসার ব্যবহার করো। এতে কনকারেন্ট নোডগুলো স্টেট ওভাররাইট না করে নিরাপদে মার্জ করতে পারে।

---
Production Reality
প্রোডাকশন চেকপয়েন্টার হিসেবে কখনো ইন-মেমোরি ডিকশনারি ব্যবহার করবে না। Redis বা PostgreSQL-ভিত্তিক চেকপয়েন্টার (`PostgresSaver`) ব্যবহার করতে হবে। যখন কুবারনেটিসের পড রিস্টার্ট নেবে বা ক্লাউড অটোস্কেলিং হবে, তখন ডাটাবেস থেকে স্টেট লোড করে এজেন্ট নিরবচ্ছিন্নভাবে চলতে থাকবে।

---
Common Mistake
স্টেট অবজেক্টের ভেতর ফাইল হ্যান্ডলার, ডাটাবেস কার্সর বা নেটওয়ার্ক সকেট অবজেক্ট স্টোর করা। স্টেটকে সবসময় **JSON-Serializable** (Strings, Dictionaries, Lists, Ints) রাখতে হবে, নয়তো চেকপয়েন্টার ডাটাবেসে সেভ করতে গিয়ে `TypeError: Object not JSON serializable` এরর দেবে।

---

## Interview Flashcards

#### Beginner Level
* **প্রশ্ন:** এজেন্টে State Machine কেন ব্যবহার করা হয়?
* **উত্তর:** সাধারণ কোড লুপ ক্র্যাশ করলে সব ডাটা হারিয়ে যায়। State Machine একটি স্ট্রাকচার্ড গ্রাফ তৈরি করে যেখানে প্রতিটি স্টেপের স্টেট ডাটাবেসে সেভ থাকে। ফলে জটিল মাল্টি-স্টেপ টাস্ক নিরাপদ, পজেবল ও প্রেডিক্টেবল হয়।

#### Intermediate Level
* **প্রশ্ন:** এজেন্টে "Human-in-the-Loop" বা ব্রেকপয়েন্ট কীভাবে কাজ করে?
* **উত্তর:** স্টেট গ্রাফে নির্দিষ্ট নোডের আগে (যেমন টাকা পাঠানো বা ফাইল ডিলিট করার আগে) একটি ব্রেকপয়েন্ট বসানো হয়। স্টেট মেশিন সেখানে এসে স্টেট সেভ করে এক্সিকিউশন পজ করে দেয় এবং মানুষের অনুমোদনের পর পরবর্তী নোডে যায়।

#### Advanced Level
* **প্রশ্ন:** Time-Travel Debugging কী?
* **উত্তর:** টাইম-ট্রাভেল ডিবাগিং হলো চেকপয়েন্ট হিস্ট্রি ব্যবহার করে এজেন্টের অতীত কোনো স্টেটের স্ন্যাপশটে ফিরে যাওয়া, ইনপুট বা প্রম্পট পরিবর্তন করা এবং সেখান থেকে পুনরায় এক্সিকিউশন চালিয়ে ফলাফল পরীক্ষা করা।
