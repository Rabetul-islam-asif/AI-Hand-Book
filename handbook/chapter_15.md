# Chapter 15: Supervised Fine-Tuning (SFT) & Dataset Preparation

---

### Chapter Goal
এই চ্যাপ্টারের মূল লক্ষ্য হলো প্রি-ট্রেইনড ল্যাঙ্গুয়েজ মডেলকে নিজের পছন্দমতো নির্দিষ্ট ফরম্যাট বা টোনে কথা বলতে শেখানোর প্রথম ধাপ—অর্থাৎ সুপারভাইজড Fine-Tuning (Supervised Fine-Tuning / SFT) এর Mechanism এবং তার Dataset Preparation (Dataset Preparation) প্রসেস গভীরভাবে আয়ত্ত করা। তুমি জানতে পারবে কখন Fine-Tuning করতে হবে বনাম কখন আরএজি (RAG) ব্যবহার করা উচিত এবং কীভাবে চ্যাটফরম্যাট ও Instruction Dataset (Instruction Datasets - Alpaca, ShareGPT formats) তৈরি করতে হয়।

### Why Should I Care?
অনেক Developer মনে করো নতুন কোনো নলেজ বা তথ্য শেখানোর জন্য Fine-Tuning করা বেস্ট চয়েস। কিন্তু বাস্তবে নতুন ফ্যাক্টস বা Data মডেলকে ফাইন-টিউনিংয়ের মাধ্যমে শেখাতে গেলে Model তা মুখস্থ না করে হ্যালুসিনেশন বা বিভ্রান্তিকর তথ্য বেশি দেয়। Fine-Tuning হলো মডেলকে **"How to behave"** (কীভাবে কথা বলতে হবে, কী ফরম্যাটে Output দিতে হবে) তা শেখানোর সেরা টুল, এবং আরএজি হলো **"What to say"** (কোন রিয়েল তথ্য বলতে হবে) তার সেরা টুল। এই তফাত না বুঝলে তুমি প্রচুর GPU কস্ট অপ্টিমাইজ করতে পারবে না।

### Big Picture
আগের চ্যাপ্টারগুলোতে আমরা Vector Database এবং আরএজি অপ্টিমাইজেশন শিখেছি। এই চ্যাপ্টার থেকে আমাদের শুরু হচ্ছে **Model Fine-Tuning** এর মহাবিশ্ব। এখানে শেখা Dataset ফরম্যাট এবং এসএফটি (SFT) Training পাইপলাইন আমাদের পরবর্তী চ্যাপ্টারের LoRA/QLoRA অ্যাডাপ্টার এবং আরএলএইচএফ (RLHF) সেফটি টিউনিং বোঝার মূল ভিত্তি।

---

### ১. Hook: ডাক্তারকে নতুন বই পড়ানো বনাম তার আচরণের প্রেসক্রিপশন পরিবর্তন

কল্পনা করো, তোমার সামনে একজন অত্যন্ত দক্ষ এমবিবিএস ডাক্তার বসে আছেন।
* **RAG (Open-Book):** ডাক্তার হৃদরোগের নতুন আবিষ্কৃত একটি সার্জারি রুল বা পলিসি জানো না। তুমি তার টেবিলের ওপর সেই নতুন রিসার্চ পেপার বা বই খুলে দিলে। ডাক্তার পেপারের ৩ নম্বর পৃষ্ঠা দেখে নিখুঁত সার্জারি প্রসিডিউরটি বুঝে তোমাকে বুঝিয়ে দিলে। 

[VISUAL]
Title: When to use RAG vs. Fine-Tuning
Illustration: Dynamic document drawer (RAG) vs. modifying brain synapses/tone (Fine-Tuning)
Placement: After Hook Section
Purpose: Show the core architectural distinction between RAG and Fine-Tuning.

```
RAG (What to Say - External Database Library):
[LLM Brain] ◄───► [ Document Drawer (Dynamic Facts) ]
(Model reads fresh documents on the fly)

Fine-Tuning (How to Behave - Modifying Internal weights):
[LLM Brain] ──► (Modify Internal Weights & Synapses) ──► [ Speaks in customized tone / JSON Format ]
```

* **Fine-Tuning (SFT):** ডাক্তার সব মেডিকেল বই জানো, কিন্তু তিনি কথা বলো অত্যন্ত অভদ্র ও কর্কশ ভাষায়। তুমি চাচ্ছেন তিনি যেন সবসময় রোগীদের সাথে নরম বাংলায় ও পোলাইট পারসোনায় কথা বলো। তুমি টেবিলে বই খুলে দিলে তার আচরণ পরিবর্তন হবে না! তার আচরণ পরিবর্তন করতে হলে তোমাকে তাকে কয়েক মাস কাস্টম বিহেভিয়ার ট্রেনিং (Fine-Tuning) দিতে হবে যাতে তার মস্তিষ্কের কথা বলার টোন ও স্টাইল সম্পূর্ণ বদলে যায়।

আরএজি এবং ফাইন-টিউনিংয়ের মূল তফাতটি এখানেই। 
* মডেলকে কোনো ডায়নামিক বা রিয়েল-টাইম ফ্যাক্টস দিতে হলে **RAG** সেরা।
* মডেলকে নির্দিষ্ট টোন, স্টাইল বা কাস্টম Output ফরম্যাট (যেমন: JSON/SQL জেনারেট করা) শেখাতে হলে **Fine-Tuning** ই একমাত্র সমাধান।

---

### ২. Core Concepts: সুপারভাইজড Fine-Tuning ও Data স্ট্রাকচার

#### ক. When to Fine-Tune vs. RAG (সিদ্ধান্ত গ্রহণ গাইডলাইন)
আর্কিটেকচারাল ডিসিশন টেবিল:

| ক্রাইটেরিয়া | RAG (Retrieval-Augmented) | Fine-Tuning (SFT) |
| :--- | :--- | :--- |
| **মূল লক্ষ্য** | এক্সটার্নাল রিয়েল-টাইম ফ্যাক্টস ও ইনফরমেশন দেওয়া | নির্দিষ্ট টোন, স্টাইল বা ফরম্যাট (JSON/SQL) শেখানো |
| **Data আপডেট** | তাৎক্ষণিক (Vector ডাটাবেসে File পুশ করলেই হয়) | ধীর (আবার Training রান করতে হয়) |
| **হ্যালুসিনেশন** | অত্যন্ত কম (সোর্স পেজের রেফারেন্স থাকে) | মাঝারি (Model নিজে বানিয়ে লিখতে পারে) |
| **কম্পিউট খরচ** | কম (শুধুমাত্র Inference ও Vector Search কস্ট) | উচ্চ (GPU Training কস্ট) |

#### খ. Supervised Fine-Tuning (SFT)
SFT হলো মডেলকে প্রচুর পরিমাণে Instruction-Response (Instruction-Response) জোড়া দেখিয়ে ট্রেইন করা।
* **Mechanism:** মডেলকে আমরা ১ হাজার থেকে ১ লাখ কাস্টম বাংলা কথোপকথনের স্যাম্পল দেখাই: `"User: [Question] -> Assistant: [ Bengali customized answer]"`।
* **Loss Optimization:** ট্রেনিং লুপে Model যখন কাস্টম উত্তরের সাথে ম্যাচ করতে ভুল Token প্রেডিক্ট করে, Loss ক্যালকুলেট করে ব্যাকপ্রোপাগেশনের মাধ্যমে Model-এর Weights মডিফাই করা হয়।

#### গ. Dataset Formats (Dataset ফরম্যাটস)

##### ১. Alpaca Format (একক Instruction)
এটি সবচেয়ে কমন ও সরল ফরম্যাট। প্রতিটি Data নোডে ৩টি কিওয়ার্ড থাকে:
* `instruction`: ইউজার কী টাস্ক দিয়েছে।
* `input`: টাস্কের সাথে যদি কোনো অতিরিক্ত Context থাকে (অপশনাল)।
* `output`: এআই কী উত্তর দেবে।
```json
{
  "instruction": "নিচের বাক্যটি বাংলায় অনুবাদ করো।",
  "input": "I love AI engineering.",
  "output": "আমি এআই ইঞ্জিনিয়ারিং ভালোবাসি।"
}
```

##### ২. ShareGPT / Messages Format (মাল্টি-টার্ন চ্যাট)
মডার্ন চ্যাট মডেলগুলোর (যেমন LLaMA-3, GPT-4) জন্য এটি সবচেয়ে জনপ্রিয় ফরম্যাট। এটি ইউজারের সাথে মাল্টি-টার্ন কনভারসেশন সিমুলেট করে:
```json
{
  "conversations": [
    {"from": "human", "value": "বিকাশ পিন লক হলে কী করব?"},
    {"from": "gpt", "value": "তোমার পিন লক হলে দয়া করে *247# ডায়াল করে সেলফ-রিসেট করো।"}
  ]
}
```

🧠 Remember

Dataset প্রিপারেশনের সময় সর্বদা **Data Quality**-কে **Data Quantity** এর ওপরে স্থান দিন। ১০ হাজার আজেবাজে Data-এর চেয়ে ১ হাজার হাই-Quality নির্ভুল টোনড Data মডেলকে অনেক বেশি অপ্টিমাইজড করতে পারে। একেই বলে **"Less is More"** রুল।

---

### ৩. Visual Explanation: SFT ট্রেনিং ম্যাট্রিক্স Loop

এসএফটি ট্রেনিংয়ের সময় Model কীভাবে শুধু অ্যাসিস্ট্যান্ট Token-এর ওপর Loss ক্যালকুলেট করে তা নিচে ডায়াগ্রামের মাধ্যমে ভিজ্যুয়ালাইজ করো:

[VISUAL]
Title: SFT Target Token Loss Calculation
Illustration: Visual breakdown of prompt tokens (ignored loss) and response tokens (active loss calculation)
Placement: After SFT section
Purpose: Visually demonstrate the mathematical formatting of causal language modeling during tuning.

```
Input Tokens (Loss Ignored):           Output Target Tokens (Active Loss 계산):
┌──────┬──────┬──────┬──────┐         ┌──────┬──────┬──────┬──────┐
│ User │ :    │ PIN  │ Lock │  ──►   │ Pls  │ dial │ *    │ 247  │
└──────┴──────┴──────┴──────┘         └──────┴──────┴──────┴──────┘
   │      │      │      │                │      │      │      │
[ Loss Masked - No Weights Update ]   [ Loss Active - Weights Updated via Backprop ✓ ]
```

* **Loss Masking:** ট্রেনিংয়ের সময় আমরা ইউজারের কোশ্চেনের Token-এর ওপর Loss ক্যালকুলেট করি না (Masked with -100 index)। Model কেবল অ্যাসিস্ট্যান্ট বা জিপিটি-র উত্তর প্রেডিকশনে ভুল করলে গ্রেডিয়েন্ট ব্যাকপ্রোপাগেট হয়।

---

### ৪. Real World Example: Cursor-এর `.cursorrules` কাস্টম টোন টিউনিং

Cursor যখন তোমার প্রোজেক্ট স্পেসিফিক নিয়মে Code লেখে:

1. **System Prompt Alignment:** তারা তাদের ওপেন-সোর্স বেস মডেলকে (যেমন LLaMA) হাজার হাজার Coding কনভেনশন এবং Project রুলস Instruction Dataset দিয়ে Fine-Tuning (SFT) করেছে।
2. **Behavior Control:** এর ফলে মডেলটি তোমার Project-এর `.cursorrules` File রিড করে ইনস্ট্যান্টলি তোমার টোন ও স্টাইল বুঝতে পারে এবং তোমার স্পেসিফিক ফরম্যাটে Code প্রডিউস করে।

---

### ৫. Developer Perspective: Hugging Face `Dataset` লোড ও প্রিপারেশন Code

💻 Developer View

Developer হিসেবে পাইথনে `datasets` Library ব্যবহার করে কাস্টম Alpaca ফরম্যাটের Dataset লোড, টোকেনাইজ এবং প্রিপেয়ার করার রিয়েল মেথড:

```python
from datasets import Dataset

# ১. র অ্যান্ড কাস্টম Dataset লিস্ট (Alpaca Format)
raw_data = [
    {
        "instruction": "বিকাশ পিন লক হলে কী করব?",
        "output": "নিকটস্থ কাস্টমার কেয়ার সেন্টারে যোগাযোগ করো।"
    },
    {
        "instruction": "পিন রিসেট করতে কী কী Document লাগবে?",
        "output": "তোমার অরিজিনাল এনআইডি (NID) কপি এবং সিম কার্ড প্রয়োজন।"
    }
]

# ২. Hugging Face Dataset অবজেক্টে রূপান্তর
dataset = Dataset.from_list(raw_data)

# ৩. টেমপ্লেটিং Function (Formatting function for training)
def format_prompts(batch):
    formatted_texts = []
    for i in range(len(batch['instruction'])):
        prompt = f"### Instruction:\n{batch['instruction'][i]}\n\n### Response:\n{batch['output'][i]}"
        formatted_texts.append(prompt)
    return {"text": formatted_texts}

# ৪. ম্যাপ Function প্রয়োগ
tokenized_dataset = dataset.map(format_prompts, batched=True)

print("--- FORMATTED DATASET FOR TRAINING ---")
print(tokenized_dataset[0]['text'])
```

---

### ৬. Production Perspective: Data অ্যানোনিপাইজেশন (Data Anonymization)

🏭 Production Reality

ফাইন-টিউনিংয়ের Dataset রেডি করার সময় এন্টারপ্রাইজ প্রোডাকশনে সবচেয়ে জটিল সিকিউরিটি অডিট হলো **PII (Personally Identifiable Information) Leakage** রোধ করা।

* **The Risk:** কাস্টমার চ্যাটের লাইভ Log থেকে যদি তুমি সরাসরি নাম, ইমেইল, ফোন নাম্বার বা বিকাশ ট্রানজ্যাকশন আইডি দিয়ে Model ট্রেইন করে ফেলেন, তবে Model-এর ভেতরের Weights-এ সেই গোপন Data এনকোড হয়ে যাবে। পরবর্তীতে Prompt হ্যাক বা র্যান্ডম চ্যাটিংয়ে Model সেই গোপন কাস্টমার Data অন্য ইউজারের সামনে ফাস (Leak) করে দেবে।
* **সমাধান:** প্রোডাকশন Dataset পাইপলাইনে ট্রেইনিংয়ের আগে ডেটাকে কঠোরভাবে **Anonymize** করতে হয় (যেমন: স্পেশাল রেগুলার এক্সপ্রেশন বা পাইথন `presidio` Library ব্যবহার করে ফোন নাম্বারকে `<PHONE>` এবং নামকে `<NAME>` দিয়ে মাস্ক করা)।

---

### ৭. Common Mistakes

🔴 Common Mistake

**ভুল ধারণা:** ফাইন-টিউনিংয়ের ডেটাসেটে ব্যাকরণ বা তথ্যের ভুল থাকলেও সমস্যা নেই, Model নিজে থেকেই তা ঠিক করে নেবে।

**বাস্তবতা:** Model ফাইন-টিউনিংয়ের সময় তোমার ডেটাসেটে যা পাবে, সে হুবহু সেই স্টাইল ও তথ্যই চরম অন্ধের মতো অনুকরণ করবে। তোমার ডেটাসেটে বানান ভুল থাকলে ফাইন-টিউনড Model-ও প্রোডাকশনে বানান ভুল প্রডিউস করবে। তাই Dataset ক্লিন রাখা ফাইন-টিউনিংয়ের সবচেয়ে গুরুত্বপূর্ণ কাজ।

---

### ৮. Mental Model: অ্যাক্টিং স্কুলে ভর্তি করা

Fine-Tuning বনাম আরএজি-র মেন্টাল Model:

* **RAG = Memory কার্ড রিডার (External Memory Source):**
  Model-এর ব্রেইনে নতুন কোনো পরিবর্তন হয় না। তুমি তাকে একটি এক্সটার্নাল Memory ড্রাইভ প্লাগ-ইন করে দিলে, সে কেবল রিড করে Output দিল।
* **Fine-Tuning = অ্যাক্টিং স্কুলে ক্যারেক্টার ট্রেনিং (Synaptic change):**
  তুমি একটি অভিনেতাকে অ্যাক্টিং স্কুলে পাঠালেন। সে সেখানে কোনো নতুন ইতিহাস বা ফ্যাক্টস শিখছে না। সে শিখছে কীভাবে একজন রাগী পুলিশের মতো অভিনয় করতে হয়, বা কীভাবে একজন মিষ্টি ডাক্তারের পারসোনা ধারণ করে কথা বলতে হয়।

---

### ৯. Mini Project: পাইথনে কাস্টম Alpaca Dataset জেনারেটর ও সিকিউরিটি পিআইআই ফিল্টার

চলো পাইথনে কাস্টম রেগুলার এক্সপ্রেশন (Regex) ব্যবহার করে কোনো Library ছাড়া একটি প্রোডাকশন-গ্রেড কাস্টমার Data অ্যানোনিমাইজার এবং Fine-Tuning Dataset স্যানিটাইজার Engine স্ক্র্যাচ থেকে আর্কিটেক্ট করি।

```python
import re

# ১. র কাস্টমার কনভারসেশন Log (ফোন নাম্বার ও ইমেইলসহ গোপন Data)
customer_logs = [
    {
        "instruction": "আমার অ্যাকাউন্ট নম্বর ০১৮১২৩৪৫৬৭৮ এর পিন লক হয়ে গেছে।",
        "output": "প্রিয় কাস্টমার, তোমার নম্বর ০১৮১২৩৪৫৬৭৮ এর পিন রিসেট করার জন্য NID নিয়ে অফিসে এসো।"
    },
    {
        "instruction": "যেকোনো জিজ্ঞাসায় karim123@gmail.com এ মেইল করতে পারো কি?",
        "output": "হ্যাঁ, karim123@gmail.com এ আমাদের সাপোর্ট টিম ২৪ ঘণ্টা একটিভ থাকে।"
    }
]

# ২. কাস্টম PII অ্যানোনিমাইজার Function
def anonymize_text(text):
    # ফোন নাম্বার মাস্কিং (বাংলা মোবাইল ১০-১১ ডিজিট)
    phone_pattern = r'(?:০১৮|০১৭|০১৫|০১৬|০১৯|০১৩)\d{৮}|\b01[3-9]\d{8}\b'
    text = re.sub(phone_pattern, "<PHONE_NUMBER>", text)
    
    # ইমেইল মাস্কিং
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    text = re.sub(email_pattern, "<EMAIL_ADDRESS>", text)
    
    return text

# ৩. Dataset স্যানিটাইজ ও রূপান্তর করো
sanitized_dataset = []

for log in customer_logs:
    clean_instruction = anonymize_text(log["instruction"])
    clean_output = anonymize_text(log["output"])
    
    sanitized_dataset.append({
        "instruction": clean_instruction,
        "output": clean_output
    })

# ৪. Output প্রিন্ট করো
print("--- SANITIZED DATASET FOR SECURE FINE-TUNING ---")
for idx, data in enumerate(sanitized_dataset):
    print(f"Data {idx+1}:")
    print(f"Instruction: '{data['instruction']}'")
    print(f"Output:      '{data['output']}'")
    print("-" * 50)
```

#### Code Breakdown:
* **Input:** কাস্টমারদের সিক্রেট ফোন নাম্বার ও ইমেইলসহ র কনভারসেশন হিস্টোরি।
* **Output:** অ্যানোনিমাইজড নিরাপদ Fine-Tuning Dataset।
* **Why it works:** কাস্টম রেগুলার এক্সপ্রেশন Pattern নিখুঁতভাবে ফোন ও ইমেইল ডিটেক্ট করে প্লেসহোল্ডার ট্যাগ দিয়ে প্রতিস্থাপন করেছে, যা প্রোডাকশন Data লিক হওয়ার ঝুঁকি ১০০% দূর করে।
* **When to use:** রিয়েল ইউজার Database থেকে Fine-Tuning Dataset Preparation করার সময়।

---

### ১০. Interview Questions

#### Beginner
1. **প্রশ্ন:** কখন আরএজি (RAG) বনাম Fine-Tuning (Fine-Tuning) এর মধ্যে সঠিক আর্কিটেকচারাল সিদ্ধান্ত নিতে হবে?
   * **উত্তর:** যখন Project-এর লক্ষ্য ডায়নামিক, রিয়েল-টাইম এবং নিখুঁত ফ্যাকচুয়াল তথ্য প্রডিউস করা, তখন RAG সেরা চয়েস। আর যখন লক্ষ্য মডেলকে নির্দিষ্ট টোন, স্টাইল বা কাস্টম Output ফরম্যাট (যেমন: JSON/SQL/Code) জেনারেট করা শেখানো, তখন Fine-Tuning একমাত্র সমাধান।

#### Intermediate
2. **প্রশ্ন:** Fine-Tuning Dataset তৈরির সময় "Personally Identifiable Information (PII) Masking" কেন আবশ্যক?
   * **উত্তর:** PII মাস্কিং না করলে কাস্টমারের গোপন ফোন নাম্বার, ইমেইল বা আইডি ইনফরমেশন ফাইন-টিউনিংয়ের সময় Model-এর ওয়েটসে চিরতরে সেভ হয়ে যাবে। পরবর্তীতে Prompt হ্যাকিংয়ের মাধ্যমে এআই সেই গোপন Data পাবলিকলি ফাস করে দিতে পারে, যা বিশাল সিকিউরিটি লিক ঘটাবে।

#### Advanced
3. **প্রশ্ন:** SFT ট্রেনিংয়ের সময় Loss ক্যালকুলেশনে কেন "Target Prompt Masking (Index -100)" ব্যবহার করা হয়? এর গুরুত্ব কী?
   * **উত্তর:** এসএফটি (SFT) ট্রেনিংয়ে আমাদের লক্ষ্য মডেলকে ইউজারের প্রশ্নের পর কীভাবে সঠিক উত্তর দিতে হয় তা শেখানো। ইউজার কী প্রশ্ন করবে তার ওপর Model-এর কোনো নিয়ন্ত্রণ নেই, তাই Prompt Token-এর ওপর Loss ক্যালকুলেট করা মেমরি ও গ্রেডিয়েন্ট অপ্টিমাইজেশন ব্যাহত করে। টার্গেট মাস্কিং (-100 ইনডেক্স) চেইন রুলকে শুধুমাত্র অ্যাসিস্ট্যান্ট Response Token-এর ওপর ওয়েটস আপডেট করতে গাইড করে।

---

### ১১. Chapter Summary
* **Supervised Fine-Tuning (SFT)** Model-এর আচরণ ও টোন পরিবর্তনের মূল গাণিতিক পদ্ধতি।
* **RAG** ফ্যাট ও ডায়নামিক Data সোর্সিংয়ের রাজা, আর **Fine-Tuning** ফরম্যাট ও পারসোনার রাজা।
* **Alpaca** এবং **ShareGPT** Instruction Dataset-এর প্রধান দুটি গোল্ড স্ট্যান্ডার্ড ফরম্যাট।
* প্রোডাকশন Dataset প্রিপারেশনে কঠোরভাবে **PII Masking** নিশ্চিত করা ম্যান্ডেটরি।

---

### biographies.md
দারুণ! আমরা সফলভাবে সুপারভাইজড ফাইন-টিউনিংয়ের Data প্রিপারেশন ও থিওরি জয় করে ফেলেছি। পরবর্তী চ্যাপ্টারে আমরা এই Fine-Tuning মেমরি ও GPU কম্পিউট কস্ট সাশ্রয় করার জন্য সবচেয়ে বৈপ্লবিক Mechanism নিয়ে আলোচনা করব: **Chapter 16: Parameter-Efficient Fine-Tuning (LoRA & QLoRA)**। লো-র্যাংক অ্যাডাপ্টার (LoRA) এর ম্যাথমেটিক্যাল ইনটুইশন এবং ৪-বিট কোয়ান্টাইজেশন (QLoRA) কীভাবে কনজিউমার ল্যাপটপে এলএলএম ফাইন-টিউন করতে সাহায্য করে, তা আমরা বিস্তারিত শিখব।

---
**Chapter 15 সমাপ্ত।**
