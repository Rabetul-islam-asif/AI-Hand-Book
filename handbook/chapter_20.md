# Chapter 20: Model Context Protocol (MCP) — The USB-C of AI

---

### Chapter Goal
এই চ্যাপ্টারের মূল লক্ষ্য হলো AI টুল এবং Resource ইন্টিগ্রেশনের সবচেয়ে আধুনিক ও বৈপ্লবিক ওপেন-স্ট্যান্ডার্ড—অর্থাৎ Model Context প্রোটোকল (Model Context Protocol / MCP) এর Mechanism এবং তার Coding Architecture সম্পূর্ণ আয়ত্ত করা। তুমি জানতে পারবে কীভাবে অ্যানথ্রপিক (Anthropic) এর তৈরি করা এই ইউনিভার্সাল প্রোটোকল AI হোস্ট (যেমন: Claude, Cursor) এবং বিভিন্ন Data সোর্সের মধ্যে একটি কমন কানেকশন ব্রিজ তৈরি করে এবং কীভাবে নিজের কাস্টম **MCP Server** ডেভেলপ ও ডিপ্লয় করতে হয়।

### Why Should I Care?
আগের চ্যাপ্টারে আমরা কাস্টম টুল কলিং শিখেছি। কিন্তু প্রথাগত টুল কলিংয়ের সবচেয়ে বড় সমস্যা হলো এটি Model-স্পেসিফিক (Model-specific)। তুমি যদি Claude (Claude) এর জন্য টুল ডিফাইন করো, সেটি ওপেনএআই (OpenAI) বা Gemini (Gemini)-তে কাজ করবে না। তোমাকে প্রতিটির জন্য আলাদা API ফরম্যাট ও Code লিখতে হবে। **MCP হলো AI-এর জন্য USB-C ক্যাবলের মতো।** তুমি একবার একটি কাস্টম MCP Server তৈরি করলে, যেকোনো AI হোস্ট বা Model সেই একই Server কানেক্ট করে ডাইরেক্ট টুলস ও Resource রিড করতে পারবে। এটি বর্তমান গ্লোবাল AI ইনফ্রাস্ট্রাকচারের সবচেয়ে মডার্ন আর্কিটেকচারাল Pattern।

### Big Picture
আগের চ্যাপ্টারে আমরা কাস্টম টুলস কনট্র্যাক্ট ও JSON স্কিমা ইমপ্লিমেন্টেশন শিখেছি। এই চ্যাপ্টারে আমরা সেই টুল লজিককে একটি বৈশ্বিক প্রোটোকলে রূপান্তর করব। এটি আমাদের পরবর্তী চ্যাপ্টারের এন্টারপ্রাইজ হারনেস ইঞ্জিনিয়ারিং (Harness Engineering), অবজারভেবিলিটি এবং রিয়েল প্রডাক্ট ব্লুপ্রিন্ট দাঁড় করানোর সবচেয়ে আধুনিক ভিত্তি।

---

### ১. Hook: চার্জারের বিশৃঙ্খলা বনাম একটিমাত্র ইউনিভার্সাল ক্যাবল

একটু পেছনের কথা ভাবো তো। 
* **The Old Mess (নন-স্ট্যান্ডার্ড চার্জার):** নোকিয়া, স্যামসাং, সনি এরিকসন—প্রতিটি ফোনের জন্য আলাদা চিকন পিন, মোটা পিন বা চ্যাপ্টা পিনের চার্জার লাগতো। এক চার্জার অন্য ফোনে কাজ করতো না। Developer হিসেবে প্রতিটি AI মডেলে আলাদা কাস্টম Coding করে টুল কলিং জোড়া দেওয়া ছিল ঠিক এই পুরানো চার্জার বিশৃঙ্খলার মতো।

[VISUAL]
Title: Proprietary Tool Connectors vs. Unified MCP USB-C Standard
Illustration: Complex point-to-point lines versus a centralized standard USB-C bridge
Placement: After Hook Section
Purpose: Show the core architectural simplification of MCP.

```
Proprietary Integration (The Old Mess):
Tool A ──► Claude API Format ──► Claude
Tool A ──► OpenAI API Format ──► ChatGPT
Tool A ──► Gemini API Format ──► Gemini

MCP Standard Integration (The USB-C Era ✓):
Tool A ──┐
Tool B ──┼─► [ MCP Server (Standard JSON-RPC) ] ◄──► [ Any LLM Host / Client ]
Tool C ──┘
```

* **The USB-C Standard (MCP):** এখন বাজারে এলো USB-C ক্যাবল। তুমি ল্যাপটপ, ফোন, ট্যাবলেট—যেকোনো ডিভাইসে একটিমাত্র ক্যাবল প্লাগ-ইন করে চার্জ ও Data শেয়ার করতে পারো। 

Model Context প্রোটোকল (MCP) হলো AI-এর সেই **USB-C** স্ট্যান্ডার্ড। এটি একবার Data বা টুলস এক্সপোজ করে এবং যেকোনো এলএলএম হোস্ট ও ক্লায়েন্ট সেই Data রিড ও প্রসেস করতে পারে।

---

### ২. Core Concepts: এমসিপি প্রোটোকলের তিন স্তম্ভ

Model Context Protocol (MCP) মূলত **Client-Server Architecture** এর ওপর ভিত্তি করে কাজ করে। এর তিনটি প্রধান স্তম্ভ রয়েছে:

#### ক. MCP Host (Client)
যেকোনো AI Application বা এডিটর যা প্রোটোকলটি সাপোর্ট করে (যেমন: Claude Desktop App, Cursor, Zed Editor, or your custom LLM app)। ক্লায়েন্ট সার্ভারকে বলে: *"তোমার কাছে কী কী টুল বা Resource আছে তার লিস্ট দাও।"*

#### খ. MCP Server
এটি তোমার লোকাল কম্পিউটার বা ক্লাউড সার্ভারে চলা একটি ছোট প্রসেস যা Data এবং টুল এক্সপোজ করে। এটি ক্লায়েন্টের সাথে **JSON-RPC 2.0** প্রোটোকল ব্যবহার করে স্টাইলিশ উপায়ে কমিউনিকেট করে (Over `stdio` or `Server-Sent Events - SSE`)।

#### গ. The Three Pillars of MCP (তিনটি প্রধান Resource টাইপ)

1. **Resources (উৎস):** AI রিড করতে পারে এমন যেকোনো Data। যেমন: তোমার ডকার File, Postgres Database টেবিল বা কাস্টম ওয়েব পেজ কনটেন্ট।
2. **Prompts (Prompt টেমপ্লেট):** আগে থেকে ডিজাইন করা System Prompt বা ইউজার গাইড।
3. **Tools (Function):** AI এক্সেকিউট করতে পারে এমন কাস্টম Code। যেমন: File রাইটার, ব্যাশ রানার বা কাস্টম Database কোয়েরিয়ার।

[VISUAL]
Title: Internals of an MCP Connection
Illustration: Bidirectional JSON-RPC messages passing through stdio pipe
Placement: Under Core Concepts section
Purpose: Visually demonstrate the clean JSON-RPC handshake of MCP.

```
Host (Client: Cursor / Claude Desktop)
       │
       ├─► Request:  {"jsonrpc": "2.0", "method": "tools/list", "id": 1} ──┐
       │                                                                   │ (stdio / SSE Pipe)
       │                                                                   ▼
       └◄─ Response: {"jsonrpc": "2.0", "result": {"tools": [...]}, "id": 1} ◄── MCP Server
```

🧠 Remember

**MCP is Open Source!**  
অ্যানথ্রপিক এটি তৈরি করলেও এটি সম্পূর্ণ ওপেন স্ট্যান্ডার্ড। Gemini বা জিপিটি ডেভেলপাররাও এই একই প্রোটোকল ফ্রেমওয়ার্ক ব্যবহার করে কাস্টম আরএজি ও এজেন্ট কোডবেস ইন্টিগ্রেট করতে পারো।

---

### ৩. Real World Example: Cursor-এর গ্লোবাল টুল ইন্টিগ্রেশন

Cursor বা Claude Desktop-এ যখন তুমি কাস্টম Feature File Search করতে চান:

1. **MCP Connect:** এডিটরটি ব্যাকগ্রাউন্ডে তোমার কম্পিউটারে রেজিস্টার্ড থাকা `filesystem-mcp-server` কানেক্ট করে।
2. **Directory Map:** এমসিপি সার্ভারটি উইন্ডোজ ওএস-এর পাথ রিড করে Resource হিসেবে Vector ম্যাপ হোস্ট ক্লায়েন্টকে পাস করে।
3. **Auto Search:** AI হোস্টটি সেই Resource এনালাইসিস করে সরাসরি তোমার কম্পিউটারের ফাইলে Code চেঞ্জ ও ব্যাশ Test রান করতে পারে, যা আগে প্রতিটি মডেলে আলাদা স্ক্রিপ্ট ছাড়া অসম্ভব ছিল।

---

### ৪. Developer Perspective: পাইথনে কাস্টম এমসিপি Server ডিজাইন

💻 Developer View

পাইথনে অ্যানথ্রপিকের অফিশিয়াল `mcp` SDK ব্যবহার করে একটি সম্পূর্ণ কাস্টম এমসিপি Server তৈরি করে টুল রেজিস্টার করার রিয়েল ও গোল্ড স্ট্যান্ডার্ড প্রোডাকশন Code:

```python
# Custom MCP Server using Python SDK
# Prerequisites: pip install mcp
from mcp.server.fastmcp import FastMCP

# ১. MCP Server অবজেক্ট তৈরি করো
mcp_server = FastMCP("WhatsMonk-Database-MCP")

# ২. কাস্টম এমসিপি টুল রেজিস্টার করো (Decorators make it easy!)
@mcp_server.tool()
def get_user_status(user_id: str) -> str:
    """গ্রাহকের স্ট্যাটাস Database থেকে চেক করো।
    
    Args:
        user_id: গ্রাহকের ইউনিক আইডি, যেমন: 'user_123'
    """
    # মক Database Data
    db = {"user_123": "Active / Gold VIP", "user_999": "Suspended"}
    return db.get(user_id, "User not found")

# ৩. কাস্টম এমসিপি Resource রেজিস্টার করো (Static Data/Logs)
@mcp_server.resource("logs://app.log")
def get_app_logs() -> str:
    """System Error লগের শেষ ৫টি লাইন রিড করো।"""
    return "Error 404 on /payment\nDatabase connection timeout\n"

# ৪. Server রান করো (Over stdio standard)
if __name__ == "__main__":
    mcp_server.run()
```

---

### ৫. Production Perspective: JSON-RPC over stdio Security

🏭 Production Reality

প্রোডাকশন সিস্টেমে এমসিপি Server ডিপ্লয় করার সময় সবচেয়ে ক্রুশিয়াল ফোকাস এরিয়া হলো **Host Process Isolation**।

* **The Security Threat:** যেহেতু এমসিপি Server সাধারণত `stdio` (Standard Input/Output) পাইপ ব্যবহার করে হোস্টের রুট পারমিশনে উইন্ডোজ ওএস কমান্ড বা ব্যাশ রান করে, তাই একটি ক্ষতিকর AI Prompt জেইলব্রেকের মাধ্যমে এমসিপি Server হ্যাক করে তোমার পুরো ওএস ড্যামেজ করে দিতে পারে।
* **সমাধান:** প্রোডাকশনে ডিরেক্ট লোকাল হোস্ট রান না করে এমসিপি সার্ভারকে সর্বদা আইসোলেটেড **Docker Container**-এ রান করানো হয় এবং শুধুমাত্র স্পেসিফিক ডিরেক্টরি পারমিশন ভলিউম মাউন্ট করে এক্সেস দেওয়া হয়, যা ওএস-এর নিরাপত্তা ১০০% প্রটেক্ট করে।

---

### ৬. Common Mistakes

🔴 Common Mistake

**ভুল ধারণা:** এমসিপি Server Code লেখার পর প্রতিবার AI Model পরিবর্তন করার সময় Server Code আবার নতুন করে AI মডেলে রেজিস্টার করতে হয়।

**বাস্তবতা:** এমসিপি Server সম্পূর্ণ স্বায়ত্তশাসিত। ক্লায়েন্ট বা হোস্ট এডিটর (যেমন: Cursor) যখন তোমার ওএস-এর `mcpConfig.json` রিড করে রান হয়, সে নিজে থেকেই সার্ভারকে কুয়্যারি করে তার এভেলেবল টুলস অটো-ডিসকভার (Auto-discover) করে নেয়। তোমার AI Code ফাইলে কোনো ম্যানুয়াল ইন্টিগ্রেশন করতে হয় না।

---

### ৭. Mental Model: ইউএসবি হাব ও মাউস-কিবোর্ড

এমসিপি প্রোটোকলের মেন্টাল Model:

**"MCP Server = একটি ইউএসবি হাব (USB Hub)"**

[VISUAL]
Title: USB Hub analogy of MCP architecture
Illustration: Visual representation of multiple accessories plugging into one USB Hub connected to a PC
Placement: Under Mental Model section
Purpose: Create an intuitive map for MCP dynamic discovery.

```
  [ Keyboard ] ──┐
  [ Mouse    ] ──┼─► [ USB Hub (MCP Server) ] ◄──► [ PC/Host (Any LLM Client) ]
  [ Printer  ] ──┘
```

ভাবো তোমার কম্পিউটারটি হলো AI হোস্ট (Claude/Cursor)। তুমি কম্পিউটারে আলাদা কাস্টম পোর্ট বানাতে চান না। 
* **The Hub:** তুমি একটি ইউনিভার্সাল ইউএসবি হাব (MCP Server) কম্পিউটারে কানেক্ট করলে। 
* **The Discovery:** এখন তুমি হাবে মাউস, কিবোর্ড বা প্রিন্টার (Tools/Resources) যাই প্লাগ-ইন করো না কেন, কম্পিউটার সাথে সাথে অটো-ডিটেক্ট করে সেগুলো ড্রাইভার ছাড়া চালাতে পারে। তোমাকে কম্পিউটারের মাদারবোর্ড চেঞ্জ করতে হয় না।

---

### ৮. Mini Project: পাইথনে কাস্টম JSON-RPC ২.০ এমসিপি কমিউনিকেশন সিমুলেটর

চলো পাইথনে কোনো কাস্টম Library ছাড়া স্ক্র্যাচ থেকে একটি এমসিপি সার্ভারের ইন্টারনাল `stdio JSON-RPC` প্রোটোকল হ্যান্ডশেক ও টুল এক্সেকিউশন Loop ডেভেলপ করি।

```python
import json

# ১. লোকাল এমসিপি টুলস রেজিস্ট্রি
mcp_tools_registry = {
    "list_dir": {
        "name": "list_dir",
        "description": "লিস্ট ডিরেক্টরি Files।"
    }
}

# ২. কাস্টম JSON-RPC ২.০ প্রোটোকল পার্সার
def handle_mcp_json_rpc(request_json):
    try:
        req = json.loads(request_json)
        
        # JSON-RPC standard validations
        if "jsonrpc" not in req or req["jsonrpc"] != "2.0":
            return json.dumps({"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": None})
            
        method = req["method"]
        req_id = req.get("id")
        
        # ৩. list_tools মেথড হ্যান্ডলার (Discovery Phase)
        if method == "tools/list":
            result = {"tools": list(mcp_tools_registry.values())}
            return json.dumps({"jsonrpc": "2.0", "result": result, "id": req_id})
            
        # ৪. call_tool মেথড হ্যান্ডলার (Execution Phase)
        elif method == "tools/call":
            tool_name = req["params"]["name"]
            if tool_name == "list_dir":
                # মক রেজাল্ট
                res = {"status": "success", "files": ["app.py", "package.json"]}
                return json.dumps({"jsonrpc": "2.0", "result": res, "id": req_id})
                
        return json.dumps({"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": req_id})
        
    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": f"Parse error: {str(e)}"}, "id": None})

# ৫. মক Test হ্যান্ডশেক (Discovery & Call Simulation)
print("--- STAGE 1: Host requests Tools List (Discovery) ---")
req_list = '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
res_list = handle_mcp_json_rpc(req_list)
print(res_list)

print("\n--- STAGE 2: Host executes 'list_dir' Tool ---")
req_call = '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "list_dir"}, "id": 2}'
res_call = handle_mcp_json_rpc(req_call)
print(res_call)
```

#### Code Breakdown:
* **Input:** AI হোস্টের পাঠানো স্ট্যান্ডার্ড JSON-RPC ২.০ টেক্সট রিকোয়েস্ট।
* **Output:** প্রোটোকল মেনে সঠিক রিদম ও ফরম্যাটে জেনারেট হওয়া এমসিপি Response।
* **Why it works:** JSON-RPC স্ট্যান্ডার্ড মেনে ডিক্লেয়ার্ড মেথড ও আইডি বাইন্ডিং সফলভাবে ভৌত প্রোটোকল সিমুলেট করেছে।
* **When to use:** কাস্টম এমসিপি প্রোটোকল ও স্টুডিও পাইপলাইন স্ক্র্যাচ থেকে ডেভেলপ ও Debug করার জন্য।

---

### ৯. Interview Questions

#### Beginner
1. **প্রশ্ন:** প্রথাগত Model-স্পেসিফিক টুল কলিংয়ের তুলনায় Model Context প্রোটোকল (MCP) এর প্রধান বৈপ্লবিক সুবিধা কী?
   * **উত্তর:** প্রথাগত টুল কলিং Model-স্পেসিফিক (যেমন: ক্লডের জন্য লেখা Code জিপিটি-তে চলে না)। কিন্তু MCP হলো একটি ওপেন-স্ট্যান্ডার্ড ইউনিভার্সাল প্রোটোকল, যা একবার Server তৈরি করলে যেকোনো AI হোস্ট বা এডিটর (Claude Desktop, Cursor, etc.) ডাইরেক্ট ড্রাইভার ছাড়াই টুল ডিসকভার ও কল করতে পারে।

#### Intermediate
2. **প্রশ্ন:** MCP প্রোটোকলের তিনটি প্রধান স্তম্ভ (Three Pillars) কোনগুলো এবং এদের কাজ কী?
   * **উত্তর:** প্রথমত, **Resources** (রিড-অনলি Data যেমন ওএস File, Database)। দ্বিতীয়ত, **Prompts** (System Prompt টেমপ্লেট)। তৃতীয়ত, **Tools** (AI এক্সেকিউট করতে পারে এমন কাস্টম ব্যাশ বা Database Function)।

#### Advanced
3. **প্রশ্ন:** এন্টারপ্রাইজ প্রোডাকশনে stdio-ভিত্তিক MCP Server ডিপ্লয় করার প্রধান সিকিউরিটি থ্রেট কী এবং এর স্ট্যান্ডার্ড মিটিগেশন স্ট্র্যাটেজি ব্যাখ্যা করো।
   * **উত্তর:** প্রধান থ্রেট হলো Prompt ইনজেকশন অ্যাটাকের মাধ্যমে হ্যাকার হোস্ট ক্লায়েন্টকে হ্যাক করে stdio পাইপ ব্যবহার করে ওএস রুট কমান্ড রান করিয়ে Server Data ক্র্যাশ করতে পারে। এর মিটিগেশন হলো এমসিপি সার্ভারকে ডিরেক্ট লোকাল ওএস-এ রান না করে আইসোলেটেড **Docker Sandbox**-এ রান করানো এবং শুধুমাত্র রিড-অনলি ভলিউম মাউন্ট করে পারমিশন লিমিট করা।

---

### ১০. Chapter Summary
* **MCP** হলো AI টুল ও Data ইন্টিগ্রেশনের ওপেন-স্ট্যান্ডার্ড ইউনিভার্সাল চার্জার (USB-C)।
* **Resources**, **Prompts**, এবং **Tools** এমসিপি কানেকশনের মূল তিনটি চালিকাশক্তি।
* **JSON-RPC 2.0** প্রোটোকল stdio পাইপের সাহায্যে হোস্ট ও Server হ্যান্ডশেক সম্পন্ন করে।
* প্রোডাকশন লেভেলে Data সেফটি নিশ্চিত করতে **Docker Isolation** ব্যবহার করা আবশ্যিক।

---

### ১১. What's Next
দারুণ! আমরা সফলভাবে পার্ট ৯ এর এজেন্টিক AI, টুল কলিং ও ইউনিভার্সাল এমসিপি প্রোটোকলের রোমাঞ্চকর অধ্যায় সম্পন্ন করেছি। পরবর্তী চ্যাপ্টার থেকে আমাদের শুরু হচ্ছে AI প্রোডাকশন ইঞ্জিনিয়ারিংয়ের সবচেয়ে অ্যাডভান্সড অধ্যায়: **Part 10 — Production AI Systems এর Chapter 21: Harness Engineering — Constitutional Guides & Evaluator Sensors**। কীভাবে সিনিয়র AI ইঞ্জিনিয়াররা AI এজেন্টের চারপাশে কড়া লিন্টার, `AGENTS.md` ও Validation সেন্সর আর্কিটেক্ট করো, তা আমরা বিস্তারিত শিখব।

---
**Chapter 20 সমাপ্ত।**
