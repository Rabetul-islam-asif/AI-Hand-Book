# Chapter 19: Tool Calling & Function Integration

---

### Chapter Goal
এই চ্যাপ্টারের মূল লক্ষ্য হলো অন্ধ AI মডেলকে চোখ ও হাত দেওয়ার প্রধান গেটওয়ে— মানে টুল কলিং (Tool Calling) এবং ফাংশনাল Integration (Function Integration) এর Coding Architecture সম্পূর্ণ আয়ত্ত করা। তুমি জানতে পারবে কীভাবে JSON Schema ব্যবহার করে AI-এর সাথে একটি perfect Data কনট্র্যাক্ট (Contract) ডিজাইন করা হয়, AI কীভাবে Dynamically সঠিক আর্গুমেন্ট Predict করে এবং তোমার ব্যাকএন্ড Code কীভাবে সেই AI-এর রিকোয়েস্ট এক্সেকিউট করে চ্যাটলুপ সম্পন্ন করে।

### Why Should I Care?
লার্জ Language Model (LLM) একা কিন্তু সম্পূর্ণ অন্ধ। সে তোমার Database পড়তে পারে না, ইউজারকে মেসেজ পাঠাতে পারে না এবং আজকের আবহাওয়া কেমন তাও জানে না। তোমার ব্যাকএন্ডের ডাটাবলিং ক্ষমতা এবং থার্ড-পার্টি API (যেমন: bKash, Pathao APIs) মডেলে Integrate করতে হলে তোমাকে টুল কলিং জানতে হবে। এটি AI চ্যাট ইন্টারফেসকে একটি Dynamic এন্টারপ্রাইজ প্রডাক্টে convert করার এক নম্বর হাতিয়ার।

### Big Picture
আগের চ্যাপ্টারে আমরা AI এজেন্টের থিওরি এবং ReAct Loop-এর বেসিক শিখেছি। এই চ্যাপ্টারে আমরা সেই এজেন্ট ইঞ্জিনের আসল হার্ডওয়্যার— মানে কীভাবে টুলস ডিজাইন করতে হয় এবং কোডে কীভাবে সেই Loop ঘুরবে তার ফিজিক্যাল Implementation সম্পূর্ণ করব। এটি আমাদের পরের chapter-এর বিশ্বমানের ওপেন-Standard **Model Context Protocol (MCP)** বোঝার কোর ফাউন্ডেশন।

---

### ১. Hook: হাত-পাহীন বিজ্ঞানীর জন্য একটি রোবোটিক আর্ম

কল্পনা করো, একটি রুমের ভেতর পৃথিবীর সবচেয়ে বুদ্ধিমান বিজ্ঞানী বসে আছেন (LLM)। সে সব থিওরি ও বই জানে, কিন্তু তার হাত ও পা অবশ। সে নিজের চেয়ার থেকে উঠতে পারে না, এমনকি কলমও ধরতে পারে না।
* **The Interface:** বিজ্ঞানীকে সাহায্য করার জন্য তুমি রুমে একটি Custom রোবোটিক আর্ম বা হাত (Tools) সেটআপ করলে।

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

* **The Workflow:** বিজ্ঞানী যখনই কোনো জটিল কাজ করতে চান, তিনি মুখের কথায় রোবটের জন্য একটি perfect Instruction তৈরি করো: `"সিলিন্ডার থেকে ৫ গ্রাম লিকুইড এ নিয়ে টেস্টটিউব বি-তে ঢালো"` (JSON Schema Contract)। তোমার ব্যাকঅ্যান্ড System বা রোবটের কন্ট্রোলার সেই নির্দেশটি Receive করে নিজে কাজটি করে বিজ্ঞানীকে বলে: `"টেস্টটিউব বি-তে ৫ গ্রাম লিকুইড যুক্ত করা হয়েছে"` (Observation/Result)। বিজ্ঞানী সেই রেজাল্ট নিয়ে আবার তার পরবর্তী গবেষণা শুরু করো।

AI টুল কলিং ঠিক এই প্রসেসে কাজ করে। **এলএলএম নিজে কোনো API কল বা Database কোয়েরি করতে পারে না।** সে শুধু তোমার সিস্টেমকে গাইড করে কোন ফাংশনটি কী Parameter দিয়ে রান করতে হবে।

---

### ২. Core Concepts: JSON স্কিমা এবং টুল কলিং Loop

একটি পুরো টুল কলিং Mechanism মূলত ৩টি উপাদানের সমন্বয়ে গঠিত:

#### ক. The JSON Schema Contract (টুল ডিফাইন করার চুক্তিপত্র)
আমরা যখন AI-কে বলি আমাদের কাছে অমুক অমুক টুল আছে, তখন আমরা তাকে একটি নির্দিষ্ট JSON Schema Format-এ টুলের প্রোপার্টি ডিফাইন করে দিই। এটি AI-কে ডিক্টেট করে সে Parameter-এর স্পেলিং বা টাইপ কী জেনারেট করবে।

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
টুলের ডেসক্রিপশন এবং প্রোপার্টির ডেসক্রিপশন মূলত AI রিড করে সিদ্ধান্ত নেয় কখন কোন টুল কল করতে হবে। ডেসক্রিপশন অস্পষ্ট হলে (যেমন: শুধু `"Get balance"` লিখলে) AI ভুলভাল Parameter জেনারেট করে System ক্র্যাশ করবে।

#### খ. The Tool Execution Loop (Code ফ্লো)
রিয়েল Code ফ্লো-তে ব্যাকএন্ড Developer হিসেবে তোমাকে ৪টি ধাপ মেইনটেইন করতে হয়:

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

### ৩. Visual Explanation: মাল্টি-টুল Parallel কলিং

AI যদি একই ইউজার মেসেজে একাধিক কাজ করতে চায়, তবে সে একই রেসপন্সে একাধিক Parallel টুল রিকোয়েস্ট জেনারেট করে:

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

bKash Customার যখন চ্যাটে এসে বলে, `"আমি টাকা পাঠিয়েছি কিন্তু অ্যাড হয়নি, ট্রানজ্যাকশন TRX999"`:

1. **Tool Match:** মডেলটি তার ওপরে রেজিস্টার্ড থাকা `check_bkash_transaction` টুলের ডেসক্রিপশন পড়ে বোঝে এটি রিয়েল-টাইম Data চেক করার পারফেক্ট টুল।
2. **JSON Argument Generation:** মডেলটি JSON অবজেক্ট জেনারেট করে: `{"trx_id": "TRX999"}`।
3. **Execution:** bKash Custom ব্যাকঅ্যান্ড API কল করে ট্রানজ্যাকশন স্ট্যাটাস `"Success"` এবং এমাউন্ট `"500 BDT"` মেপে মডেলকে Response দেয়।
4. **Friendly Response:** Model Customারকে মিষ্টি বাংলায় বলে: `"ধন্যবাদ, তোমার ৫০০ টাকার পেমেন্টটি ভালোভাবে Verifyড হয়েছে এবং অ্যাকাউন্টে যোগ করা হয়েছে।"`

---

### ৫. Developer Perspective: PyTorch / Python standard SDK তে Custom টুল এক্সিকিউটর

💻 Developer View

Developer হিসেবে পাইথনে অ্যানথ্রপিক (Anthropic Claude API) Standard ব্যবহার করে একটি সম্পূর্ণ টুল কলিং ইভেন্ট হ্যান্ডলার Implement করার রিয়েল ও গোল্ড Standard প্রোডাকশন Code:

```python
import json

# ১. লোকাল পাইথন Function (টুল ইমপ্লিমেন্টেশন)
def get_slow_queries(threshold_ms: int):
    # মক Database Error Log চেক
    return {"status": "success", "queries_found": 3, "slowest_query": "SELECT * FROM users"}

# ২. টুল স্কিমা ডিকশনারি
tools_schema = [
    {
        "name": "get_slow_queries",
        "description": "Database-এর স্লো কোয়েরি Log চেক করো।",
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

# ৩. মক AI Response হ্যান্ডলার (Simulating stop_reason='tool_use')
def handle_ai_response(response_obj):
    if response_obj["stop_reason"] == "tool_use":
        tool_use_block = response_obj["content"][0]
        tool_name = tool_use_block["name"]
        arguments = tool_use_block["input"]
        
        print(f"AI requested tool: '{tool_name}' with arguments: {arguments}")
        
        # ৪. লোকাল Function ডায়নামিক কলিং
        if tool_name == "get_slow_queries":
            result = get_slow_queries(threshold_ms=arguments["threshold_ms"])
            print(f"Local Execution Result: {result}")
            
            # ৫. Response রিম্যাপ করে পরবর্তী টার্নের জন্য প্রিপেয়ার করো
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

# মক AI Response Data
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

Inferenceে AI মাঝে মাঝে কড়া JSON Schema কনট্র্যাক্ট ভেঙে ভুল আর্গুমেন্ট টাইপ (যেমন: `threshold_ms` এর জায়গায় স্ট্রিং `"500ms"`) জেনারেট করে ফেলে। 

* **The Risk:** এই ভুল Parameter সরাসরি তোমার Database বা থার্ড-পার্টি ফাংশনে পাস করলে Application Error বা Database এক্সেপশন ক্র্যাশ করবে।
* **সমাধান:** প্রোডাকশন ব্যাকঅ্যান্ডে AI-এর জেনারেট করা আর্গুমেন্ট সরাসরি ফাংশনে পাস করার আগে strictly **Pydantic** বা **Zod (TypeScript)** দিয়ে টাইপ Validation চেক করা বাধ্যতামূলক। যদি Validation ফেল করে, System সাথে সাথে AI-কে Error ফিডব্যাক পাঠিয়ে আবার ট্রাই করতে বাধ্য করে (Self-correction loop)।

---

### ৭. Common Mistakes

🔴 Common Mistake

**ভুল ধারণা:** AI যখন টুল ব্যবহার করে, সে নিজে থেকেই ইন্টারনেটে গিয়ে তোমার থার্ড-পার্টি API কল করে ডিরেক্ট Data Receive করে।

**বাস্তবতা:** AI প্রসেস লাইফসাইকেলে কোনো নেটওয়ার্ক রিকোয়েস্ট করতে পারে না। সে শুধু টেক্সট জেনারেট করে। API-এর সম্পূর্ণ নেটওয়ার্ক কল, অথেনটিকেশন এবং সিকিউরিটি Token হ্যান্ডেল করার দায়িত্ব তোমার ব্যাকএন্ড Code-এর। AI শুধুমাত্র ডিসিশন মেকার।

---

### ৮. Mental Model: ব্যাংকের টেলার ও ম্যানেজার

টুল কলিং কনসেপ্টের মেন্টাল Model:

* **LLM = অভিজ্ঞ ম্যানেজার (The Decision Maker):**
  ম্যানেজার ব্যাংকের ভল্ট বা ক্যাশ কাউন্টার নিজে স্পর্শ করতে পারো না। তিনি সিদ্ধান্ত নেন কাকে লোন দেওয়া হবে এবং কার অ্যাকাউন্ট চেক করা দরকার।
* **Your Code = ক্যাশিয়ার বা টেলার (The Executor):**
  ম্যানেজার যখন চিরকুটে লিখে ক্যাশিয়ারকে বলো: `"রহিমের অ্যাকাউন্টের ব্যালেন্স মেপে আমাকে জানাও"`, ক্যাশিয়ার Computeারে কোয়েরি করে ব্যালেন্স মেপে ম্যানেজারকে আবার চিরকুট ফেরত দেয়। ম্যানেজার সেই চিরকুট পড়ে final এপ্রুভাল সিগনেচার দেন।

---

### ৯. Mini Project: পাইথনে স্ক্র্যাচ থেকে একটি Custom উইন্ডোজ কমান্ড এক্সিকিউশন সিকিউর এজেন্ট

চলো পাইথনে Custom JSON Schema ভ্যালিডেটর ব্যবহার করে একটি মিনি সেফ-কমান্ড রানার এজেন্ট তৈরি করি, যা AI-এর আর্গুমেন্ট চেক করে শুধুমাত্র নিরাপদ উইন্ডোজ File লিস্টার টুল এক্সেকিউট করতে পারে।

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
        
        # ৩. Parameter স্কিমা Validation
        if "path" not in args or not isinstance(args["path"], str):
            return {"status": "error", "message": "Invalid arguments. 'path' must be a string."}
            
        if tool_name == "list_dir":
            result = list_directory_contents(args["path"])
            return result
        return {"status": "error", "message": "Unknown tool name."}
        
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON format."}

# ৪. মক Test রান (প্রোডাকশন গ্রেড Test)
print("--- TEST 1: Safe Path Execution ---")
safe_res = secure_tool_executor("list_dir", '{"path": "."}')
print(safe_res)

print("\n--- TEST 2: Hack Attempt (Path Traversal) ---")
hack_res = secure_tool_executor("list_dir", '{"path": "../../../"}')
print(hack_res)
```

#### Code Breakdown:
* **Input:** AI-এর জেনারেট করা Custom JSON আর্গুমেন্ট টেক্সট।
* **Output:** পাথের নিরাপত্তা ও স্কিমা চেক করে সঠিক ডিরেক্টরি লিস্ট বা হ্যাক ব্লক এলার্ট।
* **Why it works:** `..` ট্রাভার্সাল Pattern ডিটেক্টর ডিরেক্টরি এক্সেস ব্লক করেছে, যা হোস্ট ও এস ও (OS) সিকিউরিটি ১০০% গ্যারান্টি দেয়।
* **When to use:** প্রোডাকশন হারনেস ইঞ্জিনে Custom ব্যাশ (Bash) বা ওএস টুল সেভলি এক্সিকিউট করার জন্য।

---

### ১০. Interview Questions

#### Beginner
1. **প্রশ্ন:** AI টুল কলিং প্রসেসে JSON Schema-র গুরুত্ব কী?
   * **উত্তর:** JSON Schema হলো AI এবং ব্যাকএন্ড Function-এর মধ্যকার একটি Data কনট্র্যাক্ট (Contract)। এটি পড়ে AI perfectly সিদ্ধান্ত নেয় ফাংশনে কী টাইপের (যেমন: স্ট্রিং, ইনটেজার) Parameter এবং কী স্পেলিংয়ের আর্গুমেন্ট জেনারেট করতে হবে, যা Code ক্র্যাশ হওয়া রোধ করে।

#### Intermediate
2. **প্রশ্ন:** AI যখন একই রেসপন্সে একাধিক Parallel টুল কল রিকোয়েস্ট করে, তখন ব্যাকএন্ডে কীভাবে তা হ্যান্ডেল করা উচিত?
   * **উত্তর:** ব্যাকএন্ডে Receive করা প্রতিটি টুল কল অবজেক্টের জন্য Loop চালিয়ে আলাদা থ্রেড বা Asynchronousলি (`async/await`) ফাংশনগুলো রান করতে হবে। সবগুলোর রেজাল্ট আলাদা আলাদা ইউনিক `tool_use_id` ট্যাগ দিয়ে মেসেজ এরে-তে প্যাক করে পরবর্তী টার্নে AI-কে ফিড করতে হবে।

#### Advanced
3. **প্রশ্ন:** AI-এর জেনারেট করা আর্গুমেন্ট সরাসরি লোকাল Database ফাংশনে পাস করার প্রোডাকশন রিস্কগুলো কী কী এবং এর বেস্ট প্র্যাকটিস সমাধান কী?
   * **উত্তর:** প্রধান রিস্ক হলো টাইপ মিসম্যাচ এবং Custom Code ইনজেকশন/পাথ ট্রাভার্সাল হ্যাকিং। এর সমাধান হলো সরাসরি Parameter পাস না করে প্রথমে **Pydantic** বা **Zod** এর মতো কড়া স্কিমা ভ্যালিডেটর রান করা এবং Input Sanitizeেশন ফিল্টার নিশ্চিত করার পর শুধুমাত্র ক্লিন Data লোকাল ডাটাবেসে সাবমিট করা।

---

### ১১. Chapter Summary
* **Tool Calling** অন্ধ AI মডেলকে External API ও Database রিড করার ক্ষমতা দেয়।
* **JSON Schema** AI-এর Parameter জেনারেশন গাইড করার একমাত্র রুল বুক।
* **Parallel Calling** একই ইউজার মেসেজে একাধিক Custom API কাজ সম্পাদন বুস্ট করে।
* প্রোডাকশন সিকিউরিটি নিশ্চিত করতে **Strict Argument Validation** করা বাধ্যতামূলক।

---

### ১২. What's Next
দারুণ! আমরা ভালোভাবে টুল কলিং এবং ফাংশনাল Integration প্রসেস শেষ করে ফেলেছি। পরের chapter-এ আমরা এই টুলের ইউনিভার্সাল Standard প্রোটোকল নিয়ে আলোচনা করব: **Chapter 20: Model Context Protocol (MCP) — The USB-C of AI**। অ্যানথ্রপিকের তৈরি করা মডার্ন এমসিপি (MCP) প্রোটোকল কীভাবে AI টুল ও Resource-এর বৈশ্বিক কানেকশন সহজ করে, তা আমরা বিস্তারিত শিখব।

---
**Chapter 19 শেষ।**
