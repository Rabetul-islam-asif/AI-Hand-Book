# Chapter 20: Model Context Protocol (MCP) — The USB-C of AI

---

### Chapter Goal
এই চ্যাপ্টারের মূল লক্ষ্য হলো এআই টুল এবং রিসোর্স ইন্টিগ্রেশনের সবচেয়ে আধুনিক ও বৈপ্লবিক ওপেন-স্ট্যান্ডার্ড—অর্থাৎ মডেল কনটেক্সট প্রোটোকল (Model Context Protocol / MCP) এর মেকানিজম এবং তার কোডিং আর্কিটেকচার সম্পূর্ণ আয়ত্ত করা। আপনি জানতে পারবেন কীভাবে অ্যানথ্রপিক (Anthropic) এর তৈরি করা এই ইউনিভার্সাল প্রোটোকল এআই হোস্ট (যেমন: Claude, Cursor) এবং বিভিন্ন ডেটা সোর্সের মধ্যে একটি কমন কানেকশন ব্রিজ তৈরি করে এবং কীভাবে নিজের কাস্টম **MCP Server** ডেভেলপ ও ডিপ্লয় করতে হয়।

### Why Should I Care?
আগের চ্যাপ্টারে আমরা কাস্টম টুল কলিং শিখেছি। কিন্তু প্রথাগত টুল কলিংয়ের সবচেয়ে বড় সমস্যা হলো এটি মডেল-স্পেসিফিক (Model-specific)। আপনি যদি ক্লড (Claude) এর জন্য টুল ডিফাইন করেন, সেটি ওপেনএআই (OpenAI) বা জেমিনি (Gemini)-তে কাজ করবে না। আপনাকে প্রতিটির জন্য আলাদা এপিআই ফরম্যাট ও কোড লিখতে হবে। **MCP হলো এআই-এর জন্য USB-C ক্যাবলের মতো।** আপনি একবার একটি কাস্টম MCP Server তৈরি করলে, যেকোনো এআই হোস্ট বা মডেল সেই একই সার্ভার কানেক্ট করে ডাইরেক্ট টুলস ও রিসোর্স রিড করতে পারবে। এটি বর্তমান গ্লোবাল এআই ইনফ্রাস্ট্রাকচারের সবচেয়ে মডার্ন আর্কিটেকচারাল প্যাটার্ন।

### Big Picture
আগের চ্যাপ্টারে আমরা কাস্টম টুলস কনট্র্যাক্ট ও JSON স্কিমা ইমপ্লিমেন্টেশন শিখেছি। এই চ্যাপ্টারে আমরা সেই টুল লজিককে একটি বৈশ্বিক প্রোটোকলে রূপান্তর করব। এটি আমাদের পরবর্তী চ্যাপ্টারের এন্টারপ্রাইজ হারনেস ইঞ্জিনিয়ারিং (Harness Engineering), অবজারভেবিলিটি এবং রিয়েল প্রডাক্ট ব্লুপ্রিন্ট দাঁড় করানোর সবচেয়ে আধুনিক ভিত্তি।

---

### ১. Hook: চার্জারের বিশৃঙ্খলা বনাম একটিমাত্র ইউনিভার্সাল ক্যাবল

একটু পেছনের কথা ভাবুন তো। 
* **The Old Mess (নন-স্ট্যান্ডার্ড চার্জার):** নোকিয়া, স্যামসাং, সনি এরিকসন—প্রতিটি ফোনের জন্য আলাদা চিকন পিন, মোটা পিন বা চ্যাপ্টা পিনের চার্জার লাগতো। এক চার্জার অন্য ফোনে কাজ করতো না। ডেভেলপার হিসেবে প্রতিটি এআই মডেলে আলাদা কাস্টম কোডিং করে টুল কলিং জোড়া দেওয়া ছিল ঠিক এই পুরানো চার্জার বিশৃঙ্খলার মতো।

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

* **The USB-C Standard (MCP):** এখন বাজারে এলো USB-C ক্যাবল। আপনি ল্যাপটপ, ফোন, ট্যাবলেট—যেকোনো ডিভাইসে একটিমাত্র ক্যাবল প্লাগ-ইন করে চার্জ ও ডেটা শেয়ার করতে পারেন। 

মডেল কনটেক্সট প্রোটোকল (MCP) হলো এআই-এর সেই **USB-C** স্ট্যান্ডার্ড। এটি একবার ডেটা বা টুলস এক্সপোজ করে এবং যেকোনো এলএলএম হোস্ট ও ক্লায়েন্ট সেই ডেটা রিড ও প্রসেস করতে পারে।

---

### ২. Core Concepts: এমসিপি প্রোটোকলের তিন স্তম্ভ

Model Context Protocol (MCP) মূলত **Client-Server Architecture** এর ওপর ভিত্তি করে কাজ করে। এর তিনটি প্রধান স্তম্ভ রয়েছে:

#### ক. MCP Host (Client)
যেকোনো এআই অ্যাপ্লিকেশন বা এডিটর যা প্রোটোকলটি সাপোর্ট করে (যেমন: Claude Desktop App, Cursor, Zed Editor, or your custom LLM app)। ক্লায়েন্ট সার্ভারকে বলে: *"তোমার কাছে কী কী টুল বা রিসোর্স আছে তার লিস্ট দাও।"*

#### খ. MCP Server
এটি আপনার লোকাল কম্পিউটার বা ক্লাউড সার্ভারে চলা একটি ছোট প্রসেস যা ডেটা এবং টুল এক্সপোজ করে। এটি ক্লায়েন্টের সাথে **JSON-RPC 2.0** প্রোটোকল ব্যবহার করে স্টাইলিশ উপায়ে কমিউনিকেট করে (Over `stdio` or `Server-Sent Events - SSE`)।

#### গ. The Three Pillars of MCP (তিনটি প্রধান রিসোর্স টাইপ)

1. **Resources (উৎস):** এআই রিড করতে পারে এমন যেকোনো ডেটা। যেমন: আপনার ডকার ফাইল, পোস্টগ্রেস ডাটাবেস টেবিল বা কাস্টম ওয়েব পেজ কনটেন্ট।
2. **Prompts (প্রম্পট টেমপ্লেট):** আগে থেকে ডিজাইন করা সিস্টেম প্রম্পট বা ইউজার গাইড।
3. **Tools (ফাংশন):** এআই এক্সেকিউট করতে পারে এমন কাস্টম কোড। যেমন: ফাইল রাইটার, ব্যাশ রানার বা কাস্টম ডাটাবেস কোয়েরিয়ার।

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
অ্যানথ্রপিক এটি তৈরি করলেও এটি সম্পূর্ণ ওপেন স্ট্যান্ডার্ড। জেমিনি বা জিপিটি ডেভেলপাররাও এই একই প্রোটোকল ফ্রেমওয়ার্ক ব্যবহার করে কাস্টম আরএজি ও এজেন্ট কোডবেস ইন্টিগ্রেট করতে পারেন।

---

### ৩. Real World Example: Cursor-এর গ্লোবাল টুল ইন্টিগ্রেশন

Cursor বা Claude Desktop-এ যখন আপনি কাস্টম ফিচার ফাইল সার্চ করতে চান:

1. **MCP Connect:** এডিটরটি ব্যাকগ্রাউন্ডে আপনার কম্পিউটারে রেজিস্টার্ড থাকা `filesystem-mcp-server` কানেক্ট করে।
2. **Directory Map:** এমসিপি সার্ভারটি উইন্ডোজ ওএস-এর পাথ রিড করে রিসোর্স হিসেবে ভেক্টর ম্যাপ হোস্ট ক্লায়েন্টকে পাস করে।
3. **Auto Search:** এআই হোস্টটি সেই রিসোর্স এনালাইসিস করে সরাসরি আপনার কম্পিউটারের ফাইলে কোড চেঞ্জ ও ব্যাশ টেস্ট রান করতে পারে, যা আগে প্রতিটি মডেলে আলাদা স্ক্রিপ্ট ছাড়া অসম্ভব ছিল।

---

### ৪. Developer Perspective: পাইথনে কাস্টম এমসিপি সার্ভার ডিজাইন

💻 Developer View

পাইথনে অ্যানথ্রপিকের অফিশিয়াল `mcp` SDK ব্যবহার করে একটি সম্পূর্ণ কাস্টম এমসিপি সার্ভার তৈরি করে টুল রেজিস্টার করার রিয়েল ও গোল্ড স্ট্যান্ডার্ড প্রোডাকশন কোড:

```python
# Custom MCP Server using Python SDK
# Prerequisites: pip install mcp
from mcp.server.fastmcp import FastMCP

# ১. MCP Server অবজেক্ট তৈরি করুন
mcp_server = FastMCP("WhatsMonk-Database-MCP")

# ২. কাস্টম এমসিপি টুল রেজিস্টার করুন (Decorators make it easy!)
@mcp_server.tool()
def get_user_status(user_id: str) -> str:
    """গ্রাহকের স্ট্যাটাস ডাটাবেস থেকে চেক করো।
    
    Args:
        user_id: গ্রাহকের ইউনিক আইডি, যেমন: 'user_123'
    """
    # মক ডাটাবেস ডাটা
    db = {"user_123": "Active / Gold VIP", "user_999": "Suspended"}
    return db.get(user_id, "User not found")

# ৩. কাস্টম এমসিপি রিসোর্স রেজিস্টার করুন (Static Data/Logs)
@mcp_server.resource("logs://app.log")
def get_app_logs() -> str:
    """সিস্টেম এরর লগের শেষ ৫টি লাইন রিড করো।"""
    return "Error 404 on /payment\nDatabase connection timeout\n"

# ৪. সার্ভার রান করুন (Over stdio standard)
if __name__ == "__main__":
    mcp_server.run()
```

---

### ৫. Production Perspective: JSON-RPC over stdio Security

🏭 Production Reality

প্রোডাকশন সিস্টেমে এমসিপি সার্ভার ডিপ্লয় করার সময় সবচেয়ে ক্রুশিয়াল ফোকাস এরিয়া হলো **Host Process Isolation**।

* **The Security Threat:** যেহেতু এমসিপি সার্ভার সাধারণত `stdio` (Standard Input/Output) পাইপ ব্যবহার করে হোস্টের রুট পারমিশনে উইন্ডোজ ওএস কমান্ড বা ব্যাশ রান করে, তাই একটি ক্ষতিকর এআই প্রম্পট জেইলব্রেকের মাধ্যমে এমসিপি সার্ভার হ্যাক করে আপনার পুরো ওএস ড্যামেজ করে দিতে পারে।
* **সমাধান:** প্রোডাকশনে ডিরেক্ট লোকাল হোস্ট রান না করে এমসিপি সার্ভারকে সর্বদা আইসোলেটেড **Docker Container**-এ রান করানো হয় এবং শুধুমাত্র স্পেসিফিক ডিরেক্টরি পারমিশন ভলিউম মাউন্ট করে এক্সেস দেওয়া হয়, যা ওএস-এর নিরাপত্তা ১০০% প্রটেক্ট করে।

---

### ৬. Common Mistakes

🔴 Common Mistake

**ভুল ধারণা:** এমসিপি সার্ভার কোড লেখার পর প্রতিবার এআই মডেল পরিবর্তন করার সময় সার্ভার কোড আবার নতুন করে এআই মডেলে রেজিস্টার করতে হয়।

**বাস্তবতা:** এমসিপি সার্ভার সম্পূর্ণ স্বায়ত্তশাসিত। ক্লায়েন্ট বা হোস্ট এডিটর (যেমন: Cursor) যখন আপনার ওএস-এর `mcpConfig.json` রিড করে রান হয়, সে নিজে থেকেই সার্ভারকে কুয়্যারি করে তার এভেলেবল টুলস অটো-ডিসকভার (Auto-discover) করে নেয়। আপনার এআই কোড ফাইলে কোনো ম্যানুয়াল ইন্টিগ্রেশন করতে হয় না।

---

### ৭. Mental Model: ইউএসবি হাব ও মাউস-কিবোর্ড

এমসিপি প্রোটোকলের মেন্টাল মডেল:

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

ভাবুন আপনার কম্পিউটারটি হলো এআই হোস্ট (Claude/Cursor)। আপনি কম্পিউটারে আলাদা কাস্টম পোর্ট বানাতে চান না। 
* **The Hub:** আপনি একটি ইউনিভার্সাল ইউএসবি হাব (MCP Server) কম্পিউটারে কানেক্ট করলেন। 
* **The Discovery:** এখন আপনি হাবে মাউস, কিবোর্ড বা প্রিন্টার (Tools/Resources) যাই প্লাগ-ইন করুন না কেন, কম্পিউটার সাথে সাথে অটো-ডিটেক্ট করে সেগুলো ড্রাইভার ছাড়া চালাতে পারে। আপনাকে কম্পিউটারের মাদারবোর্ড চেঞ্জ করতে হয় না।

---

### ৮. Mini Project: পাইথনে কাস্টম JSON-RPC ২.০ এমসিপি কমিউনিকেশন সিমুলেটর

চলুন পাইথনে কোনো কাস্টম লাইব্রেরি ছাড়া স্ক্র্যাচ থেকে একটি এমসিপি সার্ভারের ইন্টারনাল `stdio JSON-RPC` প্রোটোকল হ্যান্ডশেক ও টুল এক্সেকিউশন লুপ ডেভেলপ করি।

```python
import json

# ১. লোকাল এমসিপি টুলস রেজিস্ট্রি
mcp_tools_registry = {
    "list_dir": {
        "name": "list_dir",
        "description": "লিস্ট ডিরেক্টরি ফাইলস।"
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

# ৫. মক টেস্ট হ্যান্ডশেক (Discovery & Call Simulation)
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
* **Input:** এআই হোস্টের পাঠানো স্ট্যান্ডার্ড JSON-RPC ২.০ টেক্সট রিকোয়েস্ট।
* **Output:** প্রোটোকল মেনে সঠিক রিদম ও ফরম্যাটে জেনারেট হওয়া এমসিপি রেসপন্স।
* **Why it works:** JSON-RPC স্ট্যান্ডার্ড মেনে ডিক্লেয়ার্ড মেথড ও আইডি বাইন্ডিং সফলভাবে ভৌত প্রোটোকল সিমুলেট করেছে।
* **When to use:** কাস্টম এমসিপি প্রোটোকল ও স্টুডিও পাইপলাইন স্ক্র্যাচ থেকে ডেভেলপ ও ডিবাগ করার জন্য।

---

### ৯. Interview Questions

#### Beginner
1. **প্রশ্ন:** প্রথাগত মডেল-স্পেসিফিক টুল কলিংয়ের তুলনায় মডেল কনটেক্সট প্রোটোকল (MCP) এর প্রধান বৈপ্লবিক সুবিধা কী?
   * **উত্তর:** প্রথাগত টুল কলিং মডেল-স্পেসিফিক (যেমন: ক্লডের জন্য লেখা কোড জিপিটি-তে চলে না)। কিন্তু MCP হলো একটি ওপেন-স্ট্যান্ডার্ড ইউনিভার্সাল প্রোটোকল, যা একবার সার্ভার তৈরি করলে যেকোনো এআই হোস্ট বা এডিটর (Claude Desktop, Cursor, etc.) ডাইরেক্ট ড্রাইভার ছাড়াই টুল ডিসকভার ও কল করতে পারে।

#### Intermediate
2. **প্রশ্ন:** MCP প্রোটোকলের তিনটি প্রধান স্তম্ভ (Three Pillars) কোনগুলো এবং এদের কাজ কী?
   * **উত্তর:** প্রথমত, **Resources** (রিড-অনলি ডেটা যেমন ওএস ফাইল, ডাটাবেস)। দ্বিতীয়ত, **Prompts** (সিস্টেম প্রম্পট টেমপ্লেট)। তৃতীয়ত, **Tools** (এআই এক্সেকিউট করতে পারে এমন কাস্টম ব্যাশ বা ডাটাবেস ফাংশন)।

#### Advanced
3. **প্রশ্ন:** এন্টারপ্রাইজ প্রোডাকশনে stdio-ভিত্তিক MCP সার্ভার ডিপ্লয় করার প্রধান সিকিউরিটি থ্রেট কী এবং এর স্ট্যান্ডার্ড মিটিগেশন স্ট্র্যাটেজি ব্যাখ্যা করুন।
   * **উত্তর:** প্রধান থ্রেট হলো প্রম্পট ইনজেকশন অ্যাটাকের মাধ্যমে হ্যাকার হোস্ট ক্লায়েন্টকে হ্যাক করে stdio পাইপ ব্যবহার করে ওএস রুট কমান্ড রান করিয়ে সার্ভার ডেটা ক্র্যাশ করতে পারে। এর মিটিগেশন হলো এমসিপি সার্ভারকে ডিরেক্ট লোকাল ওএস-এ রান না করে আইসোলেটেড **Docker Sandbox**-এ রান করানো এবং শুধুমাত্র রিড-অনলি ভলিউম মাউন্ট করে পারমিশন লিমিট করা।

---

### ১০. Chapter Summary
* **MCP** হলো এআই টুল ও ডাটা ইন্টিগ্রেশনের ওপেন-স্ট্যান্ডার্ড ইউনিভার্সাল চার্জার (USB-C)।
* **Resources**, **Prompts**, এবং **Tools** এমসিপি কানেকশনের মূল তিনটি চালিকাশক্তি।
* **JSON-RPC 2.0** প্রোটোকল stdio পাইপের সাহায্যে হোস্ট ও সার্ভার হ্যান্ডশেক সম্পন্ন করে।
* প্রোডাকশন লেভেলে ডেটা সেফটি নিশ্চিত করতে **Docker Isolation** ব্যবহার করা আবশ্যিক।

---

### ১১. What's Next
দারুণ! আমরা সফলভাবে পার্ট ৯ এর এজেন্টিক এআই, টুল কলিং ও ইউনিভার্সাল এমসিপি প্রোটোকলের রোমাঞ্চকর অধ্যায় সম্পন্ন করেছি। পরবর্তী চ্যাপ্টার থেকে আমাদের শুরু হচ্ছে এআই প্রোডাকশন ইঞ্জিনিয়ারিংয়ের সবচেয়ে অ্যাডভান্সড অধ্যায়: **Part 10 — Production AI Systems এর Chapter 21: Harness Engineering — Constitutional Guides & Evaluator Sensors**। কীভাবে সিনিয়র এআই ইঞ্জিনিয়াররা এআই এজেন্টের চারপাশে কড়া লিন্টার, `AGENTS.md` ও ভ্যালিডেশন সেন্সর আর্কিটেক্ট করেন, তা আমরা বিস্তারিত শিখব।

---
**Chapter 20 সমাপ্ত।**
