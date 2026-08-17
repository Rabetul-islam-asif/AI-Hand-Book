# Chapter 10: Blueprint 1 — Autonomous Coding Agent (কোডিং এজেন্ট আর্কিটেকচার)

---

Devin, Claude Code, কিংবা Cursor Composer কীভাবে পুরো কোডবেস স্ক্যান করে, বাগ খুঁজে বের করে, কোড লিখে, টেস্ট রান করে এবং স্বয়ংক্রিয়ভাবে PR রেডি করে?

এটি কোনো ব্ল্যাক ম্যাজিক নয়; এটি একটি সুনির্দিষ্ট **৫-স্টেপ অটোনোমাস কোডিং আর্কিটেকচার**।

এই চ্যাপ্টারে আমরা একটি প্রোডাকশন-গ্রেড অটোনোমাস কোডিং এজেন্টের সম্পূর্ণ ব্লুপ্রিন্ট ও ইমপ্লিমেন্টেশন ডিকনস্ট্রাক্ট করব।

---

## ১. The 5-Stage Coding Agent Pipeline (৫-ধাপের কোডিং ইঞ্জিন)

[VISUAL]
Title: End-to-End Autonomous Coding & Self-Healing Architecture
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       AUTONOMOUS CODING AGENT PIPELINE                      │
│                                                                             │
│  ┌───────────────────────┐       ┌───────────────────────┐                  │
│  │ 1. WORKSPACE SCANNER  │──────►│ 2. REASONING & PLAN   │                  │
│  │  • ripgrep / AST parse│       │  • Task decomposition │                  │
│  │  • File tree index    │       │  • Edit strategy      │                  │
│  └───────────────────────┘       └───────────┬───────────┘                  │
│                                              │                              │
│                                  ┌───────────▼───────────┐                  │
│                                  │ 3. SURGICAL DIFF EDIT │                  │
│                                  │  • Exact string match │                  │
│                                  │  • Unified diff patch │                  │
│                                  └───────────┬───────────┘                  │
│                                              │                              │
│                                  ┌───────────▼───────────┐                  │
│               ┌──────────────────┤ 4. TEST RUNNER (BASH) │                  │
│               │ (Test Failed)    │  • pytest / npm test  │                  │
│               │ Self-Heal Loop   └───────────┬───────────┘                  │
│               ▼                              │ (Test Passed)                │
│  ┌───────────────────────┐       ┌───────────▼───────────┐                  │
│  │ 5. ERROR DIAGNOSIS    │       │   GIT COMMIT & PR     │                  │
│  │  • Read stderr trace  │       │  • Clean git diff     │                  │
│  │  • Retry diff edit    │       │  • Auto PR summary    │                  │
│  └───────────────────────┘       └───────────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ২. The 3 Essential Tools of a Coding Agent

একটি কোডিং এজেন্টের মাত্র ৩টি শক্তিশালী টুল লাগে:
1. `grep_search / find_files`: কোডবেসের ভেতর ফাংশন বা টেক্সট সার্চ করা।
2. `view_file`: নির্দিষ্ট লাইনের ফাইল কনটেন্ট রিড করা।
3. `replace_file_content`: পুরো ফাইল রি-রাইট না করে নির্দিষ্ট ব্লক সার্জিক্যাল রিপ্লেস করা।

---

## ৩. Implementation: Minimal Self-Healing Coding Agent

```python
import subprocess
import os

class CodingAgent:
    def __init__(self, workspace_path: str):
        self.workspace = workspace_path

    def run_tests(self) -> tuple[bool, str]:
        """Runs the pytest suite in the workspace."""
        res = subprocess.run(
            ["pytest", "-q"],
            cwd=self.workspace,
            capture_output=True,
            text=True
        )
        return (res.returncode == 0, res.stdout + "\n" + res.stderr)

    def apply_diff(self, file_path: str, target_chunk: str, replacement_chunk: str) -> bool:
        """Surgically replaces a specific code block in a file."""
        full_path = os.path.join(self.workspace, file_path)
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        if target_chunk not in content:
            return False
            
        new_content = content.replace(target_chunk, replacement_chunk, 1)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True

    def self_heal_loop(self, max_retries: int = 3):
        for attempt in range(max_retries):
            passed, output = self.run_tests()
            if passed:
                print(" All tests passed! Ready for git commit.")
                return True
                
            print(f" Test failed on attempt {attempt+1}. Feeding trace to LLM...")
            # LLM-কে এরর লগ ও ফাইল দিয়ে ফিক্স চাওয়া
            patch = self.llm_generate_patch(output)
            self.apply_diff(patch["file"], patch["target"], patch["replacement"])
            
        print(" Self-healing failed after max retries.")
        return False
```

---
Developer Perspective
কখনোই কোডিং এজেন্টকে দিয়ে সম্পূর্ণ ফাইল ওভাররাইট করাবে না (`write_entire_file`). পুরো ফাইল ওভাররাইট করলে মডেল প্রায়শই মাঝখানের কমেন্ট, ইম্পোর্ট বা টাইপ ডেফিনিশন ড্রপ করে দেয়। সবসময় **Surgical Diff Tool** ব্যবহার করো যা শুধুমাত্র নির্দিষ্ট ৩-১০ লাইন খুঁজে প্রতিস্থাপন করে।

---
Production Reality
কোডিং এজেন্টের নিরাপত্তার জন্য Git হলো পরম বন্ধু। কোড এডিট শুরু করার আগে এজেন্ট স্বয়ংক্রিয়ভাবে একটি নতুন আইসোলেটেড ব্রাঞ্চ বা ওয়ার্কট্রি তৈরি করবে (`git checkout -b ai-fix-123`). কাজ শেষে সব টেস্ট পাস করলে একটি ক্লিন `git diff` সহ পিআর বানাবে, যাতে কোনো অবস্থাতেই মেইন প্রোডাকশন ব্রাঞ্চ নষ্ট না হয়।

---
Common Mistake
টার্মিনালে কোনো কমান্ড ঝুলিয়ে রাখা (যেমন `npm start` বা ডেভ সার্ভার যা কোনোদিন শেষ হয় না)। এজেন্টের সব ব্যাশ কমান্ডে কঠোর **Timeout (যেমন 15-30s)** থাকতে হবে, নয়তো পুরো এজেন্ট প্রসেস হ্যাং হয়ে থাকবে।

---

## Interview Flashcards

#### Beginner Level
* **প্রশ্ন:** একটি Autonomous Coding Agent কীভাবে কাজ করে?
* **উত্তর:** কোডিং এজেন্ট কোডবেস স্ক্যান করে বাগ খুঁজে বের করে, সার্জিক্যাল ডিফ দিয়ে কোড প্যাচ করে, টার্মিনালে অটোমেটেড টেস্ট রান করে এবং কোনো এরর আসলে নিজে নিজেই কোড শুধরে টেস্ট পাস করায়।

#### Intermediate Level
* **প্রশ্ন:** পুরো ফাইল রি-রাইটের চেয়ে Surgical Diff কেন উন্নত?
* **উত্তর:** পুরো ফাইল রি-রাইট করতে প্রচুর টোকেন খরচ হয় এবং মডেল ভুলে পুরানো কোড বা কমেন্ট ডিলিট করে দিতে পারে। Surgical Diff শুধু নির্দিষ্ট লাইন প্রতিস্থাপন করায় এটি দ্রুত, সস্তা এবং নিরাপদ।

#### Advanced Level
* **প্রশ্ন:** এজেন্টে Self-Healing Loop কীভাবে কাজ করে?
* **উত্তর:** টেস্ট ফেইল করলে টেস্ট রানারের STDERR স্ট্যাকট্রেসকে ফিডব্যাক হিসেবে এজেন্টের স্ক্র্যাচপ্যাডে পাঠানো হয়। এজেন্ট ট্রেস দেখে নতুন হাইপোথিসিস তৈরি করে কোড সংশোধন করে আবার টেস্ট চালায়।
