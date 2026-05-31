# Chapter 19: Tool Calling & Function Integration

---

### Chapter Goal
এই চ্যাপ্টারের মূল লক্ষ্য হলো অন্ধ এআই মডেলকে চোখ ও হাত দেওয়ার প্রধান গেটওয়ে—অর্থাৎ টুল কলিং (Tool Calling) এবং ফাংশনাল ইন্টিগ্রেশন (Function Integration) এর কোডিং আর্কিটেকচার সম্পূর্ণ আয়ত্ত করা। আপনি জানতে পারবেন কীভাবে JSON Schema ব্যবহার করে এআই-এর সাথে একটি নিখুঁত ডেটা কনট্র্যাক্ট (Contract) ডিজাইন করা হয়, এআই কীভাবে ডায়নামিকালি সঠিক আর্গুমেন্ট প্রেডিক্ট করে এবং আপনার ব্যাকএন্ড কোড কীভাবে সেই এআই-এর রিকোয়েস্ট এক্সেকিউট করে চ্যাটলুপ সম্পন্ন করে।

### Why Should I Care?
লার্জ ল্যাঙ্গুয়েজ মডেল (LLM) একা কিন্তু সম্পূর্ণ অন্ধ। সে আপনার ডাটাবেস পড়তে পারে না, ইউজারকে মেসেজ পাঠাতে পারে না এবং আজকের আবহাওয়া কেমন তাও জানে না। আপনার ব্যাকএন্ডের ডাটাবলিং ক্ষমতা এবং থার্ড-পার্টি এপিআই (যেমন: bKash, Pathao APIs) মডেলে ইন্টিগ্রেট করতে হলে আপনাকে টুল কলিং জানতে হবে। এটি এআই চ্যাট ইন্টারফেসকে একটি ডায়নামিক এন্টারপ্রাইজ প্রডাক্টে রূপান্তর করার এক নম্বর হাতিয়ার।

### Big Picture
আগের চ্যাপ্টারে আমরা এআই এজেন্টের থিওরি এবং ReAct লুপের বেসিক শিখেছি। এই চ্যাপ্টারে আমরা সেই এজেন্ট ইঞ্জিনের আসল হার্ডওয়্যার—অর্থাৎ কীভাবে টুলস ডিজাইন করতে হয় এবং কোডে কীভাবে সেই লুপ ঘুরবে তার ফিজিক্যাল ইমপ্লিমেন্টেশন সম্পূর্ণ করব। এটি আমাদের পরবর্তী চ্যাপ্টারের বিশ্বমানের ওপেন-স্ট্যান্ডার্ড **Model Context Protocol (MCP)** বোঝার কোর ফাউন্ডেশন।

---

### ১. Hook: হাত-পাহীন বিজ্ঞানীর জন্য একটি রোবোটিক আর্ম

কল্পনা করুন, একটি রুমের ভেতর পৃথিবীর সবচেয়ে বুদ্ধিমান বিজ্ঞানী বসে আছেন (LLM)। সে সব থিওরি ও বই জানে, কিন্তু তার হাত ও পা অবশ। সে নিজের চেয়ার থেকে উঠতে পারে না, এমনকি কলমও ধরতে পারে না।
* **The Interface:** বিজ্ঞানীকে সাহায্য করার জন্য আপনি রুমে একটি কাস্টম রোবোটিক আর্ম বা হাত (Tools) সেটআপ করলেন।

[VISUAL]
Title: LLM Tool Use Decision Loop
Illustration: Separation between LLM's brain thinking and the client environment's arm executing
Placement: After Hook Section
Purpose: Show that the LLM only decides, while the client code executes.

```
┌────────────────────────────────────────────────────────┐
│                      CLIENT ENVIRONMENT                │
│                                                        │
│   [ Scientist / LLM ] ──► (Generates JSON: "use arm")  │
│            ▲                          │                │
│            │                          ▼                │
│   [ Receives Result ] ◄── [ Executes: Robot Arm ]      │
└────────────────────────────────────────────────────────┘
```

* **The Workflow:** বিজ্ঞানী যখনই কোনো জটিল কাজ করতে চান, তিনি মুখের কথায় রোবটের জন্য একটি নিখুঁত ইনস্ট্রাকশন তৈরি করেন: `"সিলিন্ডার থেকে ৫ গ্রাম লিকুইড এ নিয়ে টেস্টটিউব বি-তে ঢালো"` (JSON Schema Contract)। আপনার ব্যাকঅ্যান্ড সিস্টেম বা রোবটের কন্ট্রোলার সেই নির্দেশটি রিসিভ করে নিজে কাজটি করে বিজ্ঞানীকে বলে: `"টেস্টটিউব বি-তে ৫ গ্রাম লিকুইড যুক্ত করা হয়েছে"` (Observation/Result)। বিজ্ঞানী সেই রেজাল্ট নিয়ে আবার তার পরবর্তী গবেষণা শুরু করেন।

এআই টুল কলিং ঠিক এই প্রসেসে কাজ করে। **এলএলএম নিজে কোনো এপিআই কল বা ডেটাবেস কোয়েরি করতে পারে না।** সে শুধু আপনার সিস্টেমকে গাইড করে কোন ফাংশনটি কী প্যারামিটার দিয়ে রান করতে হবে।

---

### ২. Core Concepts: JSON স্কিমা এবং টুল কলিং লুপ

একটি পূর্ণাঙ্গ টুল কলিং মেকানিজম মূলত ৩টি উপাদানের সমন্বয়ে গঠিত:

#### ক. The JSON Schema Contract (টুল ডিফাইন করার চুক্তিপত্র)
আমরা যখন এআই-কে বলি আমাদের কাছে অমুক অমুক টুল আছে, তখন আমরা তাকে একটি নির্দিষ্ট JSON Schema ফরম্যাটে টুলের প্রোপার্টি ডিফাইন করে দিই। এটি এআই-কে ডিক্টেট করে সে প্যারামিটারের স্পেলিং বা টাইপ কী জেনারেট করবে।

```json
{
  "name": "get_customer_balance",
  "description": "গ্রাহকের ওয়ালেট ব্যালেন্স চেক করো।",
  "parameters": {
    "type": "object",
    "properties": {
      "customer_id": {
        "type": "string",
        "description": "গ্রাহকের ইউনিক আইডি, যেমন: 'bK-1234'"
      }
    },
    "required": ["customer_id"]
  }
}
```

🧠 Remember

**Description is Code!**  
টুলের ডেসক্রিপশন এবং প্রোপার্টির ডেসক্রিপশন মূলত এআই রিড করে সিদ্ধান্ত নেয় কখন কোন টুল কল করতে হবে। ডেসক্রিপশন অস্পষ্ট হলে (যেমন: শুধু `"Get balance"` লিখলে) এআই ভুলভাল প্যারামিটার জেনারেট করে সিস্টেম ক্র্যাশ করবে।

#### খ. The Tool Execution Loop (কোড ফ্লো)
রিয়েল কোড ফ্লো-তে ব্যাকএন্ড ডেভেলপার হিসেবে আপনাকে ৪টি ধাপ মেইনটেইন করতে হয়:

[VISUAL]
Title: 4-Step Tool Calling Iteration
Illustration: Step 1 Prompt -> Step 2 LLM requests Tool -> Step 3 Local Exec -> Step 4 Inject Result
Placement: After Tool Execution Loop
Purpose: Visually map the bidirectional network hops of function calling.

```
Step 1: User says: "আমার TRX999 ব্যালেন্স কত?" ──► [ Prompt sent to LLM ]
                                                            │
                                                            ▼
Step 2: LLM returns structured JSON request ◄───────────────┘
        (e.g. stop_reason = "tool_use", call = "check_balance")
                                                            │
                                                            ▼
Step 3: Your server executes local function: check_balance("TRX999") ──► Returns database result
                                                                              │
                                                                              ▼
Step 4: Server sends database result back to LLM ──► LLM outputs final friendly text response ✓
```

---

### ৩. Visual Explanation: মাল্টি-টুল প্যারালাল কলিং

এআই যদি একই ইউজার মেসেজে একাধিক কাজ করতে চায়, তবে সে একই রেসপন্সে একাধিক প্যারালাল টুল রিকোয়েস্ট জেনারেট করে:

[VISUAL]
Title: Parallel Tool Call Resolution
Illustration: Single LLM response splitting into 2 local tool execution paths and re-converging in the next turn
Placement: After parallel calling explanation
Purpose: Ground how systems handle multiple queries like "compare weather in Dhaka and Tokyo".

```
User Query: "Compare prices of Product A and Product B"
  │
  ▼
[ LLM response: stop_reason = "tool_use" ]
  ├── Tool Call 1: check_price(product="A") ──► Local Exec A ──┐
  │                                                            ├──► [ Merge Results ] ──► Final LLM Answer
  └── Tool Call 2: check_price(product="B") ──► Local Exec B ──┘
```

---

### ৪. Real World Example: bKash চ্যাট পেমেন্ট ভেরিফিকেশন

bKash কাস্টমার যখন চ্যাটে এসে বলে, `"আমি টাকা পাঠিয়েছি কিন্তু অ্যাড হয়নি, ট্রানজ্যাকশন TRX999"`:

1. **Tool Match:** মডেলটি তার ওপরে রেজিস্টার্ড থাকা `check_bkash_transaction` টুলের ডেসক্রিপশন পড়ে বোঝে এটি রিয়েল-টাইম ডাটা চেক করার পারফেক্ট টুল।
2. **JSON Argument Generation:** মডেলটি JSON অবজেক্ট জেনারেট করে: `{"trx_id": "TRX999"}`।
3. **Execution:** bKash কাস্টম ব্যাকঅ্যান্ড এপিআই কল করে ট্রানজ্যাকশন স্ট্যাটাস `"Success"` এবং এমাউন্ট `"500 BDT"` মেপে মডেলকে রেসপন্স দেয়।
4. **Friendly Response:** মডেল কাস্টমারকে মিষ্টি বাংলায় বলে: `"ধন্যবাদ, আপনার ৫০০ টাকার পেমেন্টটি সফলভাবে ভেরিফাইড হয়েছে এবং অ্যাকাউন্টে যোগ করা হয়েছে।"`

---

### ৫. Developer Perspective: PyTorch / Python standard SDK তে কাস্টম টুল এক্সিকিউটর

💻 Developer View

ডেভেলপার হিসেবে পাইথনে অ্যানথ্রপিক (Anthropic Claude API) স্ট্যান্ডার্ড ব্যবহার করে একটি সম্পূর্ণ টুল কলিং ইভেন্ট হ্যান্ডলার ইমপ্লিমেন্ট করার রিয়েল ও গোল্ড স্ট্যান্ডার্ড প্রোডাকশন কোড:

```python
import json

# ১. লোকাল পাইথন ফাংশন (টুল ইমপ্লিমেন্টেশন)
def get_slow_queries(threshold_ms: int):
    # মক ডাটাবেস এরর লগ চেক
    return {"status": "success", "queries_found": 3, "slowest_query": "SELECT * FROM users"}

# ২. টুল স্কিমা ডিকশনারি
tools_schema = [
    {
        "name": "get_slow_queries",
        "description": "ডাটাবেসের স্লো কোয়েরি লগ চেক করো।",
        "input_schema": {
            "type": "object",
            "properties": {
                "threshold_ms": {
                    "type": "integer",
                    "description": "স্লো কোয়েরির সময়সীমা মিলি-সেকেন্ডে।"
                }
            },
            "required": ["threshold_ms"]
        }
    }
]

# ৩. মক এআই রেসপন্স হ্যান্ডলার (Simulating stop_reason='tool_use')
def handle_ai_response(response_obj):
    if response_obj["stop_reason"] == "tool_use":
        tool_use_block = response_obj["content"][0]
        tool_name = tool_use_block["name"]
        arguments = tool_use_block["input"]
        
        print(f"AI requested tool: '{tool_name}' with arguments: {arguments}")
        
        # ৪. লোকাল ফাংশন ডায়নামিক কলিং
        if tool_name == "get_slow_queries":
            result = get_slow_queries(threshold_ms=arguments["threshold_ms"])
            print(f"Local Execution Result: {result}")
            
            # ৫. রেসপন্স রিম্যাপ করে পরবর্তী টার্নের জন্য প্রিপেয়ার করুন
            tool_result_message = {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_block["id"],
                        "content": json.dumps(result)
                    }
                ]
            }
            return tool_result_message

# মক এআই রেসপন্স ডেটা
mock_response = {
    "stop_reason": "tool_use",
    "content": [
        {
            "id": "toolu_xyz123",
            "name": "get_slow_queries",
            "input": {"threshold_ms": 500}
        }
    ]
}

handle_ai_response(mock_response)
```

---

### ৬. Production Perspective: JSON Validation & Schema Guard

🏭 Production Reality

ইনফারেন্সে এআই মাঝে মাঝে কড়া JSON Schema কনট্র্যাক্ট ভেঙে ভুল আর্গুমেন্ট টাইপ (যেমন: `threshold_ms` এর জায়গায় স্ট্রিং `"500ms"`) জেনারেট করে ফেলে। 

* **The Risk:** এই ভুল প্যারামিটার সরাসরি আপনার ডাটাবেস বা থার্ড-পার্টি ফাংশনে পাস করলে অ্যাপ্লিকেশন এরর বা ডাটাবেস এক্সেপশন ক্র্যাশ করবে।
* **সমাধান:** প্রোডাকশন ব্যাকঅ্যান্ডে এআই-এর জেনারেট করা আর্গুমেন্ট সরাসরি ফাংশনে পাস করার আগে কঠোরভাবে **Pydantic** বা **Zod (TypeScript)** দিয়ে টাইপ ভ্যালিডেশন চেক করা বাধ্যতামূলক। যদি ভ্যালিডেশন ফেল করে, সিস্টেম সাথে সাথে এআই-কে এরর ফিডব্যাক পাঠিয়ে আবার ট্রাই করতে বাধ্য করে (Self-correction loop)।

---

### ৭. Common Mistakes

🔴 Common Mistake

**ভুল ধারণা:** এআই যখন টুল ব্যবহার করে, সে নিজে থেকেই ইন্টারনেটে গিয়ে আপনার থার্ড-পার্টি এপিআই কল করে ডিরেক্ট ডেটা রিসিভ করে।

**বাস্তবতা:** এআই প্রসেস লাইফসাইকেলে কোনো নেটওয়ার্ক রিকোয়েস্ট করতে পারে না। সে শুধু টেক্সট জেনারেট করে। এপিআই-এর সম্পূর্ণ নেটওয়ার্ক কল, অথেনটিকেশন এবং সিকিউরিটি টোকেন হ্যান্ডেল করার দায়িত্ব আপনার ব্যাকএন্ড কোডের। এআই শুধুমাত্র ডিসিশন মেকার।

---

### ৮. Mental Model: ব্যাংকের টেলার ও ম্যানেজার

টুল কলিং কনসেপ্টের মেন্টাল মডেল:

* **LLM = অভিজ্ঞ ম্যানেজার (The Decision Maker):**
  ম্যানেজার ব্যাংকের ভল্ট বা ক্যাশ কাউন্টার নিজে স্পর্শ করতে পারেন না। তিনি সিদ্ধান্ত নেন কাকে লোন দেওয়া হবে এবং কার অ্যাকাউন্ট চেক করা দরকার।
* **Your Code = ক্যাশিয়ার বা টেলার (The Executor):**
  ম্যানেজার যখন চিরকুটে লিখে ক্যাশিয়ারকে বলেন: `"রহিমের অ্যাকাউন্টের ব্যালেন্স মেপে আমাকে জানাও"`, ক্যাশিয়ার কম্পিউটারে কোয়েরি করে ব্যালেন্স মেপে ম্যানেজারকে আবার চিরকুট ফেরত দেয়। ম্যানেজার সেই চিরকুট পড়ে চূড়ান্ত এপ্রুভাল সিগনেচার দেন।

---

### ৯. Mini Project: পাইথনে স্ক্র্যাচ থেকে একটি কাস্টম উইন্ডোজ কমান্ড এক্সিকিউশন সিকিউর এজেন্ট

চলুন পাইথনে কাস্টম JSON Schema ভ্যালিডেটর ব্যবহার করে একটি মিনি সেফ-কমান্ড রানার এজেন্ট তৈরি করি, যা এআই-এর আর্গুমেন্ট চেক করে শুধুমাত্র নিরাপদ উইন্ডোজ ফাইল লিস্টার টুল এক্সেকিউট করতে পারে।

```python
import os
import json

# ১. লোকাল নিরাপদ ডিরেক্টরি লিস্টার টুল
def list_directory_contents(path):
    # পাথ ট্রাভার্সাল হ্যাকিং এড়াতে সেফটি গার্ড
    if ".." in path or path.startswith("/") or path.startswith("\\"):
        return {"status": "error", "message": "Access Denied. Path traversal detected!"}
    
    if os.path.exists(path):
        return {"status": "success", "files": os.listdir(path)}
    return {"status": "error", "message": "Directory not found."}

# ২. কাস্টম JSON Schema ভ্যালিডেটর ও রানার
def secure_tool_executor(tool_name, arguments_json):
    try:
        args = json.loads(arguments_json)
        
        # ৩. প্যারামিটার স্কিমা ভ্যালিডেশন
        if "path" not in args or not isinstance(args["path"], str):
            return {"status": "error", "message": "Invalid arguments. 'path' must be a string."}
            
        if tool_name == "list_dir":
            result = list_directory_contents(args["path"])
            return result
        return {"status": "error", "message": "Unknown tool name."}
        
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON format."}

# ৪. মক টেস্ট রান (প্রোডাকশন গ্রেড টেস্ট)
print("--- TEST 1: Safe Path Execution ---")
safe_res = secure_tool_executor("list_dir", '{"path": "."}')
print(safe_res)

print("\n--- TEST 2: Hack Attempt (Path Traversal) ---")
hack_res = secure_tool_executor("list_dir", '{"path": "../../../"}')
print(hack_res)
```

#### Code Breakdown:
* **Input:** এআই-এর জেনারেট করা কাস্টম JSON আর্গুমেন্ট টেক্সট।
* **Output:** পাথের নিরাপত্তা ও স্কিমা চেক করে সঠিক ডিরেক্টরি লিস্ট বা হ্যাক ব্লক এলার্ট।
* **Why it works:** `..` ট্রাভার্সাল প্যাটার্ন ডিটেক্টর ডিরেক্টরি এক্সেস ব্লক করেছে, যা হোস্ট ও এস ও (OS) সিকিউরিটি ১০০% গ্যারান্টি দেয়।
* **When to use:** প্রোডাকশন হারনেস ইঞ্জিনে কাস্টম ব্যাশ (Bash) বা ওএস টুল সেভলি এক্সিকিউট করার জন্য।

---

### ১০. Interview Questions

#### Beginner
1. **প্রশ্ন:** এআই টুল কলিং প্রসেসে JSON Schema-র গুরুত্ব কী?
   * **উত্তর:** JSON Schema হলো এআই এবং ব্যাকএন্ড ফাংশনের মধ্যকার একটি ডেটা কনট্র্যাক্ট (Contract)। এটি পড়ে এআই নিখুঁতভাবে সিদ্ধান্ত নেয় ফাংশনে কী টাইপের (যেমন: স্ট্রিং, ইনটেজার) প্যারামিটার এবং কী স্পেলিংয়ের আর্গুমেন্ট জেনারেট করতে হবে, যা কোড ক্র্যাশ হওয়া রোধ করে।

#### Intermediate
2. **প্রশ্ন:** এআই যখন একই রেসপন্সে একাধিক প্যারালাল টুল কল রিকোয়েস্ট করে, তখন ব্যাকএন্ডে কীভাবে তা হ্যান্ডেল করা উচিত?
   * **উত্তর:** ব্যাকএন্ডে রিসিভ করা প্রতিটি টুল কল অবজেক্টের জন্য লুপ চালিয়ে আলাদা থ্রেড বা অ্যাসিনক্রোনাসলি (`async/await`) ফাংশনগুলো রান করতে হবে। সবগুলোর রেজাল্ট আলাদা আলাদা ইউনিক `tool_use_id` ট্যাগ দিয়ে মেসেজ এরে-তে প্যাক করে পরবর্তী টার্নে এআই-কে ফিড করতে হবে।

#### Advanced
3. **প্রশ্ন:** এআই-এর জেনারেট করা আর্গুমেন্ট সরাসরি লোকাল ডাটাবেস ফাংশনে পাস করার প্রোডাকশন রিস্কগুলো কী কী এবং এর বেস্ট প্র্যাকটিস সমাধান কী?
   * **উত্তর:** প্রধান রিস্ক হলো টাইপ মিসম্যাচ এবং কাস্টম কোড ইনজেকশন/পাথ ট্রাভার্সাল হ্যাকিং। এর সমাধান হলো সরাসরি প্যারামিটার পাস না করে প্রথমে **Pydantic** বা **Zod** এর মতো কড়া স্কিমা ভ্যালিডেটর রান করা এবং ইনপুট স্যানিটাইজেশন ফিল্টার নিশ্চিত করার পর শুধুমাত্র ক্লিন ডেটা লোকাল ডাটাবেসে সাবমিট করা।

---

### ১১. Chapter Summary
* **Tool Calling** অন্ধ এআই মডেলকে এক্সটার্নাল এপিআই ও ডাটাবেস রিড করার ক্ষমতা দেয়।
* **JSON Schema** এআই-এর প্যারামিটার জেনারেশন গাইড করার একমাত্র রুল বুক।
* **Parallel Calling** একই ইউজার মেসেজে একাধিক কাস্টম এপিআই কাজ সম্পাদন বুস্ট করে।
* প্রোডাকশন সিকিউরিটি নিশ্চিত করতে **Strict Argument Validation** করা বাধ্যতামূলক।

---

### ১২. What's Next
দারুণ! আমরা সফলভাবে টুল কলিং এবং ফাংশনাল ইন্টিগ্রেশন প্রসেস জয় করে ফেলেছি। পরবর্তী চ্যাপ্টারে আমরা এই টুলের ইউনিভার্সাল স্ট্যান্ডার্ড প্রোটোকল নিয়ে আলোচনা করব: **Chapter 20: Model Context Protocol (MCP) — The USB-C of AI**। অ্যানথ্রপিকের তৈরি করা মডার্ন এমসিপি (MCP) প্রোটোকল কীভাবে এআই টুল ও রিসোর্সের বৈশ্বিক কানেকশন সহজ করে, তা আমরা বিস্তারিত শিখব।

---
**Chapter 19 সমাপ্ত।**
