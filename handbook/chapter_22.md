# Chapter 22: Model Context Protocol (MCP) — The USB-C of AI

---

নোকিয়ার চার্জার দিয়ে কি স্যামসাং চার্জ হতো?

হতো না! প্রতিটা ফোনের জন্য ছিল আলাদা চার্জার।

AI-এর Tool Calling-এও ঠিক একই সমস্যা ছিল।

Claude-এর জন্য লেখা Tool ওদিকে OpenAI-তে চলে না, আবার Gemini-তে গিয়ে হয় অন্য Format!

প্রতিবার নতুন করে Code লেখো। কী এক বিশৃঙ্খলা!

মজার ব্যাপার হলো, এই বিশৃঙ্খলার সমাধানই হলো MCP!

সহজ কথায়, এটা হলো AI-এর USB-C ক্যাবল।

Anthropic এটা তৈরি করেছে ঠিকই, কিন্তু এটা সম্পূর্ণ open standard।

তুমি একবার একটা MCP Server বানিয়ে ফেলো, ব্যস!

যেকোনো AI Host— যেমন Claude, Cursor বা Gemini— সবাই সেটা সরাসরি কানেক্ট করতে পারবে।

সহজেই তোমার Tools আর Resources রিড করে ফেলবে। কোনো আলাদা Integration Code লেখাই লাগবে না।

তো চলো দেখি MCP-র তিনটা পিলার Resources, Prompts আর Tools কী, JSON-RPC 2.0 কীভাবে কাজ করে, আর কীভাবে নিজের custom MCP Server ডিজাইন করতে হয়।

কী, শুরু করা যাক? Deal?


### ১. চার্জারের ঝামেলা বনাম এক ক্যাবল

একটু পেছনের কথা ভাবো তো।

আগেকার দিনে নোকিয়া, স্যামসাং বা সনি এরিকসন ফোনের কথা মনে আছে?

প্রতিটা ফোনের জন্য আলাদা আলাদা চার্জার লাগতো!

কারো চিকন পিন, কারো মোটা পিন, আবার কারো চ্যাপ্টা পিন।

একটার চার্জার দিয়ে অন্য ফোনে কোনোভাবেই চার্জ দেওয়া যেতো না।

Developer হিসেবে প্রতিটি AI Model-এ আলাদা করে Custom Coding করে Tool Calling জোড়া দেওয়াও ঠিক এই রকম ঝামেলার ছিল।

![Proprietary Connectors vs. Unified Model Context Protocol (MCP)](/diagrams/proprietary_vs_mcp.png)


আর এখন?

এখন এসেছে USB-C ক্যাবল।

তুমি ল্যাপটপ, ফোন বা ট্যাবলেট—যেকোনো কিছুতেই এই একটা ক্যাবল গুজে দিয়ে চার্জ করতে পারো।

এমনকি Data-ও শেয়ার করতে পারো।

MCP হলো AI জগতের সেই USB-C Standard।

এটি একবার Data আর Tools-কে সবার সামনে তুলে ধরে।

![MCP Host Diagram](/diagrams/MCP host.jpeg)

আর যেকোনো LLM Host ও Client সেই Data অনায়াসে রিড আর প্রসেস করতে পারে।


### ২. MCP-র মূল তিনটি পিলার

MCP মূলত Client-Server Architecture-এর ওপর দাঁড়িয়ে কাজ করে।

সহজ কথায়, এর মূল স্তম্ভ বা পিলার তিনটি।

চলো প্রশ্ন-উত্তরের মাধ্যমে সহজে বুঝে নিই এগুলো আসলে কী।

**প্রশ্ন:** MCP Host বা Client কী?

**উত্তর:** এটা হলো যেকোনো AI Application বা Editor যা এই প্রোটোকল সাপোর্ট করে।

যেমন ধরো Cursor, Claude Desktop App বা তোমার নিজের বানানো কোনো LLM App।

এই Client সরাসরি Server-কে বলে, "তোমার কাছে কী কী Tool আর Resource আছে, চলো তার একটা লিস্ট দাও তো!"

**প্রশ্ন:** তাহলে MCP Server কী?

**উত্তর:** এটি তোমার লোকাল Computer বা ক্লাউড সার্ভারে চলতে থাকা একটি ছোট Process।

এর কাজ হলো Data আর Tool-কে সবার সামনে তুলে ধরা।

এটি Client-এর সাথে JSON-RPC 2.0 ব্যবহার করে দারুণ উপায়ে কথা বলে।

এই কথা বলার মাধ্যম হতে পারে `stdio` अथवा `Server-Sent Events - SSE`।

**প্রশ্ন:** MCP-র মূল তিনটি Resource টাইপ কী কী?

**উত্তর:** চলো একে একে জেনে নিই:

প্রথমটি হলো **Resources**।

এটি হলো যেকোনো Data, যা AI পড়তে পারে।

যেমন ধরো তোমার Docker File, Postgres Database-এর টেবিল অথবা কোনো কাস্টম ওয়েব পেজের কনটেন্ট।

দ্বিতীয়টি হলো **Prompts**।

সহজ কথায়, এটি আগে থেকে তৈরি করে রাখা System Prompt বা ইউজার গাইড।

আর তৃতীয়টি হলো **Tools**।

এটি হলো কাস্টম Code, যা AI চালাতে পারে।

যেমন File Writer, Bash Runner বা Database Query করার Tool।

![MCP Connection Handshake (JSON-RPC stdio/SSE)](/diagrams/mcp_json_rpc_handshake.png)


 Remember

**MCP কিন্তু সম্পূর্ণ Open Source!**

Anthropic এটি তৈরি করলেও এটি সবার জন্য উন্মুক্ত।

Gemini বা GPT-এর ডেভেলপাররাও চাইলে এই একই ফ্রেমওয়ার্ক ব্যবহার করতে পারবে।

নিজেদের কাস্টম RAG আর Agent Code-এর সাথে সহজেই কানেক্ট করা যাবে।


### ৩. বাস্তবে এর একটা উদাহরণ দেখি

ধরো, তুমি Cursor বা Claude Desktop-এ কাস্টম উপায়ে কোনো File Search করতে চাও।

তখন ব্যাকগ্রাউন্ডে ঠিক কী ঘটে?

চলো গল্পটা জেনে নিই।

প্রথমে Cursor ব্যাকগ্রাউন্ডে তোমার Computer-এ আগে থেকে রেজিস্টার করা `filesystem-mcp-server` ফাইলে কানেক্ট করে।

কানেক্ট করার পর, MCP Server তোমার ওএস-এর পাথ রিড করে।

তারপর সেই Resource-এর ম্যাপ AI Host-কে পাঠিয়ে দেয়।

সবশেষে, AI Host সেই Resource দেখে সরাসরি তোমার কম্পিউটারের ফাইলে Code পরিবর্তন করতে পারে।

এমনকি Bash Test-ও রান করতে পারে!

ভাবা যায়? আগে প্রতিটা মডেলে আলাদা স্ক্রিপ্ট ছাড়া এই কাজ করা অসম্ভব ছিল!


### ৪. পাইথনে নিজের Custom MCP Server বানানো
Developer Perspective

পাইথনে Anthropic-এর অফিশিয়াল `mcp` SDK ব্যবহার করে কীভাবে একটি কাস্টম MCP Server তৈরি করা যায়?

চলো একটা প্রোডাকশন গ্রেড Code দেখে নিই:

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


### ۵. Security এবং Production টিপস
Production Reality

প্রোডাকশন সিস্টেমে MCP Server ডেপ্লয় করার সময় আমাদের সিকিউরিটির দিকে কড়া নজর রাখতে হবে।

এখানে সবচেয়ে গুরুত্বপূর্ণ বিষয় হলো Host Process Isolation।

চলো একটা সহজ প্রশ্ন-উত্তরের মাধ্যমে ঝুঁকি আর এর সমাধানটা বুঝে নিই।

**প্রশ্ন:** এখানে সিকিউরিটির মূল ভয়টা আসলে কী?

**উত্তর:** সাধারণত MCP Server আমাদের `stdio` পাইপ ব্যবহার করে কাজ করে।

এর মানে হলো এটি হোস্টের রুট পারমিশন নিয়ে ওএস-এর ভেতরে কমান্ড রান করতে পারে।

এখন কোনো ক্ষতিকর Prompt যদি AI-কে জেইলব্রেক বা হ্যাক করে ফেলে, তবে সে সরাসরি ওএস-এর বারোটা বাজিয়ে দিতে পারে!

**প্রশ্ন:** তাহলে এর সমাধান কী?

**উত্তর:** সমাধান খুব সহজ।

প্রোডাকশনে সরাসরি লোকাল হোস্টে এটি রান না করে সবসময় isolated Docker Container ব্যবহার করতে হবে।

সেখানে শুধুমাত্র প্রয়োজনীয় ডিরেক্টরির পারমিশন ভলিউম মাউন্ট করে এক্সেস দিতে হবে।

এতে ওএস-এর নিরাপত্তা একশভাগ নিশ্চিত করা সম্ভব।


### ৬. কিছু সাধারণ ভুল ধারণা
Common Mistake

**ভুল ধারণা:**

MCP Server বানানোর পর প্রতিবার AI Model চেঞ্জ করার সময় কি সার্ভারের কোডও নতুন করে মডেলে রেজিস্টার করতে হবে?

**বাস্তবতা:**

একেবারেই না! MCP Server সম্পূর্ণ আলাদাভাবে নিজের মতো চলে।

তোমার Cursor বা Claude-এর মতো Host এডিটরগুলো যখন ওএস-এর `mcpConfig.json` রিড করে চালু হয়, তখন সে নিজে থেকেই সার্ভারের কাছে জানতে চায় কী কী Tool আছে।

অর্থাৎ, সে নিজেই অটো-ডিসকভার করে নেয়।

তোমাকে ম্যানুয়ালি কোনো কোড লিখে জোড়াতালি দিতে হবে না।


### ৭. মনের ভেতর ছবি এঁকে নেওয়া

চলো বোঝার সুবিধার্থে একটা সহজ তুলনা করি।

**"MCP Server = একটি USB Hub"**

![Analogy: MCP Server = USB Hub](/diagrams/mcp_usb_hub_analogy.png)


ধরে নাও তোমার কম্পিউটারটি হলো AI Host (যেমন Claude বা Cursor)।

তুমি তো আর কম্পিউটারে প্রতিটা ডিভাইসের জন্য আলাদা আলাদা পোর্ট বানাতে যাবে না, তাই না?

তুমি শুধু একটি সাধারণ USB Hub (অর্থাৎ MCP Server) কম্পিউটারে কানেক্ট করে দিলে।

এবার তুমি সেই হাবে মাউস, কিবোর্ড বা প্রিন্টার যা-ই লাগাও না কেন, কম্পিউটার নিজে থেকেই তা চিনে নেবে।

তোমাকে কম্পিউটারের ভেতরের মাদারবোর্ড নিয়ে একটুও মাথা ঘামাতে হবে না!


### ৮. ছোট প্রজেক্ট: JSON-RPC ২.০ সিমুলেশন

চলো পাইথনে কোনো কাস্টম লাইব্রেরি ছাড়াই একদম শুরু থেকে একটি MCP সার্ভারের ভেতরের `stdio JSON-RPC` প্রোটোকল হ্যান্ডশেক ও টুল এক্সেকিউশন সিমুলেট করি।

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

চলো কোডের খুঁটিনাটি বিষয়গুলো সহজ প্রশ্ন-উত্তরের মাধ্যমে জেনে নিই।

**প্রশ্ন:** এই কোডে Input আর Output হিসেবে কী ব্যবহার করা হয়েছে?

**উত্তর:** Input হলো AI Host-এর পাঠানো একদম সাধারণ JSON-RPC 2.0 টেক্সট রিকোয়েস্ট।

আর Output হলো প্রোটোকল মেনে জেনারেট হওয়া সঠিক MCP Response।

**প্রশ্ন:** এই পুরো সিস্টেমটা কীভাবে নিখুঁতভাবে কাজ করছে?

**উত্তর:** কারণ এটি JSON-RPC Standard মেনে চলছে।

এর ফলে মেথড আর আইডি বাইন্ডিং খুব সুন্দরভাবে প্রোটোকল সিমুলেট করতে পেরেছে।

**প্রশ্ন:** এটি আমরা কখন এবং কেন ব্যবহার করবো?

**উত্তর:** যখন তুমি নিজের কোনো MCP প্রোটোকল স্ক্র্যাচ থেকে বানাতে চাও, তখন এটি খুব কাজে দেবে।

বিশেষ করে লাইনের ভেতর কী ঘটছে তা Debug করার জন্য এটি অসাধারণ এক উপায়।


### ৯. ইন্টারভিউতে যেসব প্রশ্ন আসতে পারে

চলো ইন্টারভিউতে সচরাচর জিজ্ঞেস করা কিছু গুরুত্বপূর্ণ প্রশ্ন দেখে নিই।

#### Beginner লেভেল

**প্রশ্ন:**

আগের সাধারণ Tool Calling-এর চেয়ে MCP-র মূল সুবিধা কী?

**উত্তর:**

আগে প্রতিটা Model-এর জন্য আলাদা আলাদা কোড লিখতে হতো। যেমন Claude-এর কোড GPT-তে চলতো না।

কিন্তু MCP হলো একটি Universal প্রোটোকল।

একবার Server বানিয়ে ফেললে যেকোনো AI Host (যেমন Claude Desktop বা Cursor) সরাসরি তা ব্যবহার করতে পারে।

#### Intermediate লেভেল

**প্রশ্ন:**

MCP-র তিনটি প্রধান পিলার কী কী এবং এগুলো কী কাজ করে?

**উত্তর:**

প্রথমটি হলো **Resources**, যা রিড-অনলি ডেটা হিসেবে কাজ করে (যেমন কোনো ফাইল বা ডেটাবেস)।

দ্বিতীয়টি হলো **Prompts**, যা আগে থেকে লিখে রাখা System Prompt টেমপ্লেট।

আর তৃতীয়টি হলো **Tools**, যা AI হোস্ট সরাসরি রান করতে পারে (যেমন কোনো স্ক্রিপ্ট বা ডেটাবেস কোয়েরি)।

#### Advanced লেভেল

**প্রশ্ন:**

stdio-ভিত্তিক MCP Server চালানোর সময় সিকিউরিটির সবচেয়ে বড় ঝুঁকি কী এবং কীভাবে তা এড়ানো যায়?

**উত্তর:**

সবচেয়ে বড় ভয় হলো Prompt Injection অ্যাটাক।

হ্যাকাররা চাইলে ক্ষতিকর Prompt দিয়ে stdio পাইপের মাধ্যমে ওএস-এর রুট কমান্ড রান করিয়ে নিতে পারে।

এর সমাধান হলো, সরাসরি ওএস-এ সার্ভার রান না করে Isolated Docker Sandbox ব্যবহার করা।

সেখানে শুধুমাত্র রিড-অনলি ভলিউম মাউন্ট করে অ্যাক্সেস দিতে হবে।


### ১০. সংক্ষেপে চ্যাপ্টারের মূল কথা

চলো পুরো চ্যাপ্টারটা এক নজরে ঝালিয়ে নেওয়া যাক।

**প্রশ্ন:** সংক্ষেপে MCP জিনিসটা আসলে কী?

**উত্তর:** এটি হলো AI Tool আর Data কানেক্ট করার একদম সহজ এক Universal চার্জার।

**প্রশ্ন:** MCP কানেকশনের মূল ভিত্তি কী?

**উত্তর:** এর মূল তিনটি শক্তি হলো Resources, Prompts আর Tools।

**প্রশ্ন:** হোস্ট আর সার্ভার একে অপরের সাথে কথা বলে কীভাবে?

**উত্তর:** তারা JSON-RPC 2.0 প্রোটোকল আর stdio পাইপ ব্যবহার করে নিজেদের ভেতর Handshake করে।

**প্রশ্ন:** প্রোডাকশনে কাজ করার সময় কোন বিষয়টিতে সবচেয়ে বেশি জোর দিতে হবে?

**উত্তর:** ডেটার নিরাপত্তা নিশ্চিত করতে অবশ্যই Docker Isolation ব্যবহার করতে হবে।


### ১১. সামনে কী আসছে?

পরবর্তী চ্যাপ্টারেই আমরা প্রবেশ করছি AI প্রোডাকশন সিস্টেমের দারুণ এক জগতে!

সেখানে আমরা শিখবো Harness Engineering, Constitutional Guides আর Validation Sensors-এর মতো সব দারুণ জিনিস।

আমরা দেখবো কীভাবে AI এজেন্টের চারপাশ নিরাপদ রাখতে কড়া লিন্টার আর ভ্যালিডেশন সেন্সর আর্কিটেক্ট করতে হয়।

তো চলো, পরের চ্যাপ্টারে চলে যাই!

**Chapter 22 শেষ।**
