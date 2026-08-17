# Chapter 21: Tool Calling & Function Integration

একটু ভেবে দেখো তো— তোমার AI Model দুনিয়ার সব থিওরি জানে।

কিন্তু সে কি তোমার Database পড়তে পারে?

উঁহু, পারে না।

আজকের আবহাওয়া কেমন, সেটা কি সে জানে?

জানে না।

এমনকি একটা bKash ট্রানজ্যাকশনও সে চেক করতে পারে না।

কারণ, সে আসলে সম্পূর্ণ অন্ধ! তার কোনো হাত-পা নেই।

এই হাত-পা দেওয়ার জাদুকরী উপায়টাই হলো Tool Calling।

এখানে তুমি একটা JSON Schema দিয়ে একটা Contract বানাবে।

AI সেটা পড়ে বুঝবে কোন Function রান করতে হবে আর কী Parameter দিতে হবে।

তারপর তোমার ব্যাকএন্ড Code বাকি কাজটুকু করে ফেলবে।

সবসময় মনে রাখবে— AI কিন্তু নিজে কোনো API কল করে না।

সে শুধু সিদ্ধান্ত নেয়, আর কাজটা করে তোমার নিজের লেখা Code।

তো চলো দেখি, কীভাবে এই JSON Schema ডিজাইন করতে হয়।

আমরা আরও শিখবো Tool Calling Loop-এর ৪টা সহজ ধাপ আর Parallel Tool Calling হ্যান্ডেল করার উপায়।

এটা শিখে নিলে পরের চ্যাপ্টারের Model Context Protocol (MCP) বোঝা তোমার জন্য একদম সহজ হয়ে যাবে। Deal?


## ১. বিজ্ঞানী আর রোবোটিক আর্ম

ধরো, একটা বন্ধ রুমে পৃথিবীর সবচেয়ে বুদ্ধিমান বিজ্ঞানী বসে আছেন।

এই বিজ্ঞানী হলেন আমাদের LLM।

তিনি সব থিওরি আর বইয়ের কথা জানেন।

কিন্তু সমস্যা হলো, তার হাত-পা নড়াচড়া করতে পারে না।

তিনি নিজের চেয়ার থেকে উঠতে পারেন না, এমনকি একটা কলমও ধরতে পারেন না!

তাহলে এই বিজ্ঞানী বাইরের পৃথিবীর সাথে কীভাবে কাজ করবেন?

খুব সহজ! বিজ্ঞানীকে সাহায্য করার জন্য তুমি রুমে একটা Custom রোবোটিক আর্ম বা Tools সেটআপ করে দিলে।

![LLM Tool Use Decision Loop](/diagrams/tool_use_decision_loop.png)


বিজ্ঞানী যখনই কোনো কাজ করতে চান, তিনি মুখে একটা নিখুঁত Instruction দেন।

যেমন তিনি বললেন: "সিলিন্ডার থেকে ৫ গ্রাম লিকুইড নিয়ে টেস্টটিউব বি-তে ঢালো।"

এই Instruction-টাই হলো আমাদের JSON Schema Contract।

তোমার ব্যাকএন্ড System বা রোবটের কন্ট্রোলার সেই নির্দেশটি Receive করে।

তারপর সে নিজে কাজটি করে বিজ্ঞানীকে জানায়: "টেস্টটিউব বি-তে ৫ গ্রাম লিকুইড ঢালা হয়েছে।"

বিজ্ঞানী সেই Result দেখে তার পরের কাজ শুরু করেন।

AI Tool Calling ঠিক এভাবেই কাজ করে।

মনে রাখবে, LLM কিন্তু নিজে কোনো API কল বা Database কোয়েরি করতে পারে না।

সে শুধু তোমার System-কে গাইড করে যে কোন Function-টি কী Parameter দিয়ে রান করাতে হবে।


## ২. JSON Schema ও Tool Calling Loop

টুল কলিং কীভাবে কাজ করে জানো?

এর পেছনে মূলত দুইটা বড় জিনিস থাকে।

চলো সহজ কথায় বুঝে নিই।

প্রথমটা হলো JSON Schema Contract।

এটা আবার কী?

যখন আমরা AI-কে বলি আমাদের কাছে কী কী টুল আছে, তখন তাকে একটা ফর্ম পূরণ করে দিতে হয়।

এই ফর্মটাই হলো JSON Schema Format।

এখানে টুলের সব ডিটেইলস লেখা থাকে।

যেমন, AI যখন কোনো Parameter তৈরি করবে, তার বানান কী হবে বা টাইপ কী হবে— সেটা এই Schema থেকেই সে জানতে পারে।

যেমন এই কোডটা দেখো:

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

টুল আর প্রোপার্টির Description পড়েই AI সিদ্ধান্ত নেয় কখন কোন টুল কল করতে হবে।

এখানে যদি তুমি অস্পষ্ট কিছু লেখো, যেমন শুধু "Get balance", তাহলে AI কনফিউজড হয়ে যাবে।

সে ভুলভাল Parameter তৈরি করে তোমার পুরো System ক্র্যাশ করিয়ে দিতে পারে!

এবার আসি দ্বিতীয় জিনিসে— Tool Execution Loop বা আমাদের কাজের ফ্লো।

ব্যাকএন্ড Developer হিসেবে তোমাকে ৪টি ধাপ মেনে চলতে হবে।

চলো ঝটপট ধাপগুলো দেখে নিই:

![Tool Calling Loop Diagram](/diagrams/tool_calling_loop.png)





## ৩. একসাথে অনেক টুল চালানো বা Parallel Calling

ধরো, ইউজার একটা মেসেজে একসাথে দুইটা কাজ করতে চাইল।

তখন AI কী করবে?

সে কি একটা একটা করে করবে?

না! সে একই সাথে দুইটা Parallel Tool Request তৈরি করতে পারে।

নিচের ডায়াগ্রামটি দেখলে একদম পরিষ্কার হয়ে যাবে:

![Parallel Tool Call Resolution](/diagrams/parallel_tool_call_resolution.png)



## ৪. বাস্তবে যেমন দেখায়: bKash পেমেন্ট ভেরিফিকেশন

চলো একটা বাস্তব উদাহরণ দেখি।

ধরো, একজন bKash Customer চ্যাটে এসে বলল: "আমি টাকা পাঠিয়েছি কিন্তু অ্যাড হয়নি, ট্রানজ্যাকশন TRX999।"

তখন পর্দার আড়ালে কী ঘটে?

প্রথমেই AI তার কাছে থাকা সব টুলের লিস্ট চেক করে।

সে দেখে `check_bkash_transaction` নামে একটা টুল আছে।

তার Description পড়ে সে বুঝে নেয় যে এটাই রিয়েল-টাইম Data চেক করার জন্য পারফেক্ট টুল।

এরপর AI একটা JSON Object তৈরি করে ফেলে: `{"trx_id": "TRX999"}`।

এবার তোমার ব্যাকএন্ড Code এই JSON দেখে bKash API কল করে।

সেখান থেকে ট্রানজ্যাকশন স্ট্যাটাস "Success" আর অ্যামাউন্ট "500 BDT" নিয়ে AI-কে ফেরত দেয়।

সবশেষে AI সব তথ্য পেয়ে কাস্টমারকে মিষ্টি করে বাংলায় উত্তর দেয়:

"ধন্যবাদ! তোমার ৫০০ টাকার পেমেন্টটি ভেরিফাই করা হয়েছে এবং অ্যাকাউন্টে যোগ করা হয়েছে।"


## ৫. কোডিংয়ের পালা: Custom Tool Executor তৈরি
Developer Perspective

এবার চলো একটু কোড দেখা যাক।

একজন Developer হিসেবে তুমি কীভাবে পাইথনে Anthropic API ব্যবহার করে টুল কলিং হ্যান্ডল করবে?

নিচে তার একটি প্রোডাকশন লেভেলের পাইথন কোড দেওয়া হলো:

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


## ৬. প্রোডাকশন লাইফে ভ্যালিডেশনের গুরুত্ব
Production Reality

বাস্তবে যখন AI কাজ করে, সে কিন্তু মাঝে মাঝে ভুল আর্গুমেন্ট টাইপ তৈরি করে ফেলে।

যেমন ধরো, `threshold_ms`-এর জায়গায় সে একটা String `"500ms"` পাঠিয়ে দিল।

তখন কী সমস্যা হতে পারে?

এই ভুল Parameter যদি সরাসরি তোমার Database বা Function-এ চলে যায়, তবে পুরো Application ক্র্যাশ করবে!

তাহলে এর সমাধান কী?

এর জন্য তোমাকে ব্যাকএন্ডে একটা Guard বা ভ্যালিডেটর রাখতে হবে।

কোড রান করার আগে Pydantic বা Zod দিয়ে টাইপ ভ্যালিডেশন চেক করা একদম বাধ্যতামূলক।

যদি ভ্যালিডেশন ফেল করে, তাহলে তোমার System সাথে সাথে AI-কে একটি Error মেসেজ পাঠিয়ে বলবে আবার চেষ্টা করতে।

একে আমরা বলি Self-correction Loop।


## ৭. কিছু সাধারণ ভুল ধারণা
Common Mistake

অনেকেরই একটা বড় ভুল ধারণা থাকে।

তারা মনে করে, AI নিজে নিজেই ইন্টারনেটে গিয়ে থার্ড-পার্টি API কল করে ডাটা নিয়ে আসে।

কিন্তু আসলে কি তাই?

একেবারেই না!

বাস্তবতা হলো, AI নিজে কোনো নেটওয়ার্ক রিকোয়েস্ট করতে পারে না।

সে শুধু টেক্সট জেনারেট করতে পারে।

সব নেটওয়ার্ক কল, অথেনটিকেশন আর সিকিউরিটি হ্যান্ডেল করার দায়িত্ব তোমার ব্যাকএন্ড কোডের।

AI এখানে শুধুই সিদ্ধান্ত নেয়, সে কোনো কাজ নিজে করে না।


## ৮. সহজ মেন্টাল মডেল: ব্যাংকের ম্যানেজার ও ক্যাশিয়ার

টুল কলিংয়ের পুরো ব্যপারটা বুঝতে একটা সহজ মেন্টাল মডেল ব্যবহার করা যাক।

ভাবো, আমাদের LLM হলো ব্যাংকের একজন অভিজ্ঞ ম্যানেজার।

ম্যানেজার কিন্তু নিজে ক্যাশ কাউন্টারে গিয়ে টাকা গোনেন না বা ভল্ট খোলেন না।

তিনি শুধু সিদ্ধান্ত নেন কাকে লোন দেওয়া হবে আর কার অ্যাকাউন্ট চেক করা দরকার।

আর তোমার ব্যাকএন্ড কোড হলো সেই ব্যাংকের ক্যাশিয়ার।

ম্যানেজার যখন চিরকুটে লিখে ক্যাশিয়ারকে বলেন: "রহিমের ব্যালেন্স কত দেখে জানাও।"

ক্যাশিয়ার তখন কম্পিউটারে ডাটাবেস চেক করে ম্যানেজারকে ব্যালেন্সের হিসাব এনে দেন।

ম্যানেজার সেই হিসাব দেখে ফাইনাল সিদ্ধান্ত নেন।

এখানে ম্যানেজার হলেন Decision Maker, আর ক্যাশিয়ার হলেন Executor।


## ৯. মিনি প্রজেক্ট: একটি সেফ ফাইল লিস্টার এজেন্ট

চলো এবার পাইথনে একটা দারুণ কাজ করি।

আমরা একটা নিরাপদ কমান্ড রানার এজেন্ট তৈরি করব।

এই এজেন্টটি AI-এর দেওয়া আর্গুমেন্ট চেক করবে।

এবং শুধুমাত্র নিরাপদ উইন্ডোজ ফাইল লিস্টার টুল এক্সেকিউট করবে।

কোডটি নিচে দেখে নাও:

```python
import os
import json

# ১. লোকাল নিরাপদ ডিরেক্টরি লিস্টার টুল
def list_directory_contents(path):
    # পাথের ট্রাভার্সাল হ্যাকিং এড়াতে সেফটি গার্ড
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

#### কোডটি কীভাবে কাজ করে?

ইউজার যখন ইনপুট হিসেবে AI-এর তৈরি করা JSON আর্গুমেন্ট পাঠাবে, আমাদের এই কোডটি পাথের সিকিউরিটি আর স্কিমা চেক করে দেখবে।

যদি পাথটি নিরাপদ হয়, তবে সে ফাইলের লিস্ট আউটপুট হিসেবে দেবে।

আর যদি কেউ হ্যাক করার চেষ্টা করে, তবে সাথে সাথে সে এলার্ট দেখাবে।

কারণ, আমাদের কোডে `..` ট্রাভার্সাল ডিটেকশন আছে, যা ওএস সিকিউরিটি নিশ্চিত করে।

তুমি যখন প্রোডাকশনে কোনো কাস্টম ব্যাশ বা ওএস টুল সেভলি রান করাতে চাও, তখন এই কোডটি ব্যবহার করতে পারো।


## ১০. ইন্টারভিউতে কেমন প্রশ্ন হতে পারে?

### বিগিনার লেভেল

**প্রশ্ন:** AI টুল কলিংয়ে JSON Schema-র গুরুত্ব কী?

**উত্তর:** JSON Schema হলো AI আর ব্যাকএন্ড Function-এর মধ্যে একটা ডাটা Contract।

এটি পড়ে AI বুঝতে পারে ফাংশনে কী ধরনের Parameter দিতে হবে।

যেমন, সেটি String হবে নাকি Integer হবে, তা AI এখান থেকে বুঝতে পারে।

এর ফলে কোড ক্র্যাশ করার কোনো সম্ভাবনা থাকে না।

### ইন্টারমিডিয়েট লেভেল

**প্রশ্ন:** AI যখন একই সাথে অনেকগুলো Parallel Tool Call করতে চায়, তখন ব্যাকএন্ডে কীভাবে হ্যান্ডেল করবে?

**উত্তর:** ব্যাকএন্ডে যে কয়টি টুল কল রিকোয়েস্ট আসবে, প্রতিটির জন্য Loop চালিয়ে Asynchronous উপায়ে বা `async/await` দিয়ে ফাংশনগুলো রান করতে হবে।

এরপর সবগুলোর রেজাল্ট আলাদা ইউনিক `tool_use_id` দিয়ে মেসেজ অ্যারেতে প্যাক করে AI-কে ফেরত দিতে হবে।

### অ্যাডভান্সড লেভেল

**প্রশ্ন:** AI-এর তৈরি করা আর্গুমেন্ট সরাসরি লোকাল Database-এ পাঠানোর রিস্ক কী? আর এর বেস্ট প্র্যাকটিস কী?

**উত্তর:** সবচেয়ে বড় রিস্ক হলো টাইপ মিসম্যাচ হওয়া আর সিকিউরিটি হ্যাক হওয়া।

যেমন কেউ কাস্টম কোড ইনজেকশন বা পাথ ট্রাভার্সাল অ্যাটাক করতে পারে।

এর বেস্ট প্র্যাকটিস হলো— সরাসরি ডাটাবেসে ডাটা না পাঠিয়ে প্রথমে Pydantic বা Zod দিয়ে কড়া স্কিমা ভ্যালিডেশন চেক করা।

এবং ইনপুট পুরোপুরি ফিল্টার বা Sanitize করার পর কেবল ক্লিন ডাটা ডাটাবেসে সেভ করা।


## ১১. চ্যাপ্টার সামারি

তাহলে এই চ্যাপ্টারে আমরা কী কী শিখলাম? চলো একবার চোখ বুলিয়ে নিই।

আমরা জানলাম Tool Calling কীভাবে অন্ধ AI-কে বাইরের দুনিয়ার API আর Database পড়ার ক্ষমতা দেয়।

শিখলাম JSON Schema হলো AI-এর জন্য একমাত্র রুল বুক, যা দেখে সে আর্গুমেন্ট তৈরি করে।

আরও বুঝলাম Parallel Calling-এর সাহায্যে একই সাথে একাধিক API-র কাজ করে ফেলা যায়।

আর সবশেষে মনে রাখব, সুরক্ষার জন্য Strict Argument Validation করাটা একদম বাধ্যতামূলক।


## ১২. এরপরে কী?

টুল কলিং তো শিখে গেলাম, এবার তাহলে কী করব?

পরের চ্যাপ্টারে আমরা শিখব টুলের ইউনিভার্সাল স্ট্যান্ডার্ড প্রোটোকল: **Chapter 22: Model Context Protocol (MCP)**।

একে বলা যায় AI-এর USB-C!

অ্যানথ্রপিকের তৈরি এই মডার্ন প্রোটোকল কীভাবে সব AI টুলকে একসাথে কানেক্ট করে, চলো সেটাই দেখে নিই!

**Chapter 21 শেষ।**
