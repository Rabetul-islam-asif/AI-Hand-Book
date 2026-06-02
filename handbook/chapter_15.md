# Chapter 15: Supervised Fine-Tuning (SFT) & Dataset Preparation



ধরো, তোমার হাতে একটা বেস Model আছে। সে অনেক কিছু জানে, কিন্তু কথা বলে একদম নিজের মতো করে। তুমি চাচ্ছো সে তোমার কাস্টমারদের সাথে মিষ্টি বাংলায় কথা বলুক, বা JSON Format-এ Output দিক। সেটা শেখাবে কীভাবে? সেটাই হলো Supervised Fine-Tuning (SFT)।

মজার ব্যাপার হলো— অনেকে ভাবে Fine-Tuning মানে মডেলকে নতুন তথ্য শেখানো। ভুল! নতুন ফ্যাক্টস শেখাতে চাইলে RAG ব্যবহার করো। Fine-Tuning হলো মডেলকে **"কীভাবে কথা বলবে"** সেটা শেখানোর জন্য। এই তফাতটা না বুঝলে তুমি শুধু শুধু GPU কস্ট পুড়িয়ে ফেলবে।

তো চলো দেখি কীভাবে Instruction Dataset (Alpaca, ShareGPT formats) তৈরি করতে হয়, কখন RAG বনাম Fine-Tuning বেছে নিতে হয়, আর SFT Training Pipeline কীভাবে কাজ করে। এটা বুঝলে পরের চ্যাপ্টারের LoRA/QLoRA আর RLHF সব পানির মতো সহজ লাগবে। Deal?



### ১. Hook: ডাক্তারকে নতুন বই পড়ানো বনাম তার আচরণের প্রেসক্রিপশন পরিবর্তন

কল্পনা করো, তোমার সামনে একজন খুব দক্ষ এমবিবিএস ডাক্তার বসে আছেন।
* **RAG (Open-Book):** ডাক্তার হৃদরোগের নতুন আবিষ্কৃত একটি সার্জারি রুল বা পলিসি জানো না। তুমি তার টেবিলের ওপর সেই নতুন রিসার্চ পেপার বা বই খুলে দিলে। ডাক্তার পেপারের ৩ নম্বর পৃষ্ঠা দেখে perfect সার্জারি প্রসিডিউরটি বুঝে তোমাকে বুঝিয়ে দিলে। 

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

* **Fine-Tuning (SFT):** ডাক্তার সব মেডিকেল বই জানো, কিন্তু তিনি কথা বলো খুব অভদ্র ও কর্কশ ভাষায়। তুমি চাচ্ছেন তিনি যেন সবসময় রোগীদের সাথে নরম বাংলায় ও পোলাইট Personaয় কথা বলো। তুমি টেবিলে বই খুলে দিলে তার আচরণ পরিবর্তন হবে না! তার আচরণ পরিবর্তন করতে হলে তোমাকে তাকে কয়েক মাস Custom বিহেভিয়ার ট্রেনিং (Fine-Tuning) দিতে হবে যাতে তার মস্তিষ্কের কথা বলার টোন ও স্টাইল সম্পূর্ণ বদলে যায়।

আরএজি এবং Fine-Tuning-এর মূল তফাতটি এখানেই। 
* মডেলকে কোনো Dynamic বা রিয়েল-টাইম ফ্যাক্টস দিতে হলে **RAG** সেরা।
* মডেলকে নির্দিষ্ট টোন, স্টাইল বা Custom Output Format (যেমন: JSON/SQL জেনারেট করা) শেখাতে হলে **Fine-Tuning** ই একমাত্র সমাধান।


### ২. Core Concepts: Supervised Fine-Tuning ও Data স্ট্রাকচার

#### ক. When to Fine-Tune vs. RAG (সিদ্ধান্ত গ্রহণ গাইডলাইন)
Architectural ডিসিশন টেবিল:

| Criteria | RAG (Retrieval-Augmented) | Fine-Tuning (SFT) |
| :--- | :--- | :--- |
| **মূল লক্ষ্য** | External রিয়েল-টাইম ফ্যাক্টস ও ইনফরমেশন দেওয়া | নির্দিষ্ট টোন, স্টাইল বা Format (JSON/SQL) শেখানো |
| **Data আপডেট** | instant (Vector ডাটাবেসে File পুশ করলেই হয়) | ধীর (আবার Training রান করতে হয়) |
| **Hallucination** | খুব কম (সোর্স পেজের রেফারেন্স থাকে) | মাঝারি (Model নিজে বানিয়ে লিখতে পারে) |
| **Compute খরচ** | কম (শুধুমাত্র Inference ও Vector Search কস্ট) | উচ্চ (GPU Training কস্ট) |

#### খ. Supervised Fine-Tuning (SFT)
SFT হলো মডেলকে প্রচুর পরিমাণে Instruction-Response (Instruction-Response) জোড়া দেখিয়ে ট্রেইন করা।
* **Mechanism:** মডেলকে আমরা ১ হাজার থেকে ১ লাখ Custom বাংলা কথোপকথনের স্যাম্পল দেখাই: `"User: [Question] -> Assistant: [ Bengali customized answer]"`।
* **Loss Optimization:** ট্রেনিং লুপে Model যখন Custom উত্তরের সাথে ম্যাচ করতে ভুল Token Predict করে, Loss ক্যালকুলেট করে Backpropagation-এর মাধ্যমে Model-এর Weights Modify করা হয়।

#### গ. Dataset Formats (Dataset Formatস)

##### ১. Alpaca Format (একক Instruction)
এটি সবচেয়ে কমন ও সরল Format। প্রতিটি Data নোডে ৩টি কিওয়ার্ড থাকে:
* `instruction`: ইউজার কী টাস্ক দিয়েছে।
* `input`: টাস্কের সাথে যদি কোনো অতিরিক্ত Context থাকে (অপশনাল)।
* `output`: AI কী উত্তর দেবে।
```json
{
  "instruction": "নিচের বাক্যটি বাংলায় অনুবাদ করো।",
  "input": "I love AI engineering.",
  "output": "আমি AI ইঞ্জিনিয়ারিং ভালোবাসি।"
}
```

##### ২. ShareGPT / Messages Format (মাল্টি-টার্ন চ্যাট)
মডার্ন চ্যাট মডেলগুলোর (যেমন LLaMA-3, GPT-4) জন্য এটি সবচেয়ে জনপ্রিয় Format। এটি ইউজারের সাথে মাল্টি-টার্ন Conversation Simulate করে:
```json
{
  "conversations": [
    {"from": "human", "value": "বিকাশ পিন লক হলে কী করব?"},
    {"from": "gpt", "value": "তোমার পিন লক হলে দয়া করে *247# ডায়াল করে সেলফ-রিসেট করো।"}
  ]
}
```

🧠 Remember

Dataset প্রিপারেশনের সময় সর্বদা **Data Quality**-কে **Data Quantity** এর ওপরে স্থান দাও। ১০ হাজার আজেবাজে Data-এর চেয়ে ১ হাজার হাই-Quality নির্ভুল টোনড Data মডেলকে অনেক বেশি অপ্টিমাইজড করতে পারে। একেই বলে **"Less is More"** রুল।


### ৩. Visual Explanation: SFT ট্রেনিং Matrix Loop

এসএফটি ট্রেনিংয়ের সময় Model কীভাবে শুধু Assistant Token-এর ওপর Loss ক্যালকুলেট করে তা নিচে Diagramের মাধ্যমে ভিজ্যুয়ালাইজ করো:

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

* **Loss Masking:** ট্রেনিংয়ের সময় আমরা ইউজারের কোশ্চেনের Token-এর ওপর Loss ক্যালকুলেট করি না (Masked with -100 index)। Model কেবল Assistant বা জিপিটি-র উত্তর Prediction-এ ভুল করলে Gradient Backpropagate হয়।


### ৪. Real World Example: Cursor-এর `.cursorrules` Custom টোন টিউনিং

Cursor যখন তোমার Project স্পেসিফিক নিয়মে Code লেখে:

1. **System Prompt Alignment:** তারা তাদের ওপেন-সোর্স বেস মডেলকে (যেমন LLaMA) হাজার হাজার Coding কনভেনশন এবং Project রুলস Instruction Dataset দিয়ে Fine-Tuning (SFT) করেছে।
2. **Behavior Control:** এর ফলে মডেলটি তোমার Project-এর `.cursorrules` File রিড করে Instantly তোমার টোন ও স্টাইল বুঝতে পারে এবং তোমার স্পেসিফিক Format-এ Code Produce করে।


### ৫. Developer Perspective: Hugging Face `Dataset` লোড ও প্রিপারেশন Code

💻 Developer View

Developer হিসেবে পাইথনে `datasets` Library ব্যবহার করে Custom Alpaca Format-এর Dataset লোড, Tokenize এবং প্রিপেয়ার করার রিয়েল মেথড:

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


### ৬. Production Perspective: Data Anonymization (Data Anonymization)

🏭 Production Reality

Fine-Tuning-এর Dataset রেডি করার সময় এন্টারপ্রাইজ প্রোডাকশনে সবচেয়ে জটিল সিকিউরিটি অডিট হলো **PII (Personally Identifiable Information) Leakage** রোধ করা।

* **The Risk:** Customার চ্যাটের লাইভ Log থেকে যদি তুমি সরাসরি নাম, ইমেইল, ফোন নাম্বার বা বিকাশ ট্রানজ্যাকশন আইডি দিয়ে Model ট্রেইন করে ফেলেন, তবে Model-এর ভেতরের Weights-এ সেই secret Data এনকোড হয়ে যাবে। পরবর্তীতে Prompt হ্যাক বা র্যান্ডম চ্যাটিংয়ে Model সেই secret Customার Data অন্য ইউজারের সামনে ফাস (Leak) করে দেবে।
* **সমাধান:** প্রোডাকশন Dataset পাইপলাইনে ট্রেইনিংয়ের আগে ডেটাকে strictly **Anonymize** করতে হয় (যেমন: স্পেশাল Regular Expression বা পাইথন `presidio` Library ব্যবহার করে ফোন নাম্বারকে `<PHONE>` এবং নামকে `<NAME>` দিয়ে মাস্ক করা)।


### ৭. Common Mistakes

🔴 Common Mistake

**ভুল ধারণা:** Fine-Tuning-এর ডেটাসেটে ব্যাকরণ বা তথ্যের ভুল থাকলেও সমস্যা নেই, Model নিজে থেকেই তা ঠিক করে নেবে।

**বাস্তবতা:** Model Fine-Tuning-এর সময় তোমার ডেটাসেটে যা পাবে, সে হুবহু সেই স্টাইল ও তথ্যই হুবহু অনুকরণ করবে। তোমার ডেটাসেটে বানান ভুল থাকলে ফাইন-টিউনড Model-ও প্রোডাকশনে বানান ভুল Produce করবে। তাই Dataset ক্লিন রাখা Fine-Tuning-এর সবচেয়ে গুরুত্বপূর্ণ কাজ।


### ৮. Mental Model: অ্যাক্টিং স্কুলে ভর্তি করা

Fine-Tuning বনাম আরএজি-র মেন্টাল Model:

* **RAG = Memory কার্ড রিডার (External Memory Source):**
  Model-এর ব্রেইনে নতুন কোনো পরিবর্তন হয় না। তুমি তাকে একটি External Memory ড্রাইভ প্লাগ-ইন করে দিলে, সে কেবল রিড করে Output দিল।
* **Fine-Tuning = অ্যাক্টিং স্কুলে ক্যারেক্টার ট্রেনিং (Synaptic change):**
  তুমি একটি অভিনেতাকে অ্যাক্টিং স্কুলে পাঠালেন। সে সেখানে কোনো নতুন ইতিহাস বা ফ্যাক্টস শিখছে না। সে শিখছে কীভাবে একজন রাগী পুলিশের মতো অভিনয় করতে হয়, বা কীভাবে একজন মিষ্টি ডাক্তারের Persona ধারণ করে কথা বলতে হয়।


### ৯. Mini Project: পাইথনে Custom Alpaca Dataset জেনারেটর ও সিকিউরিটি পিআইআই ফিল্টার

চলো পাইথনে Custom Regular Expression (Regex) ব্যবহার করে কোনো Library ছাড়া একটি প্রোডাকশন-গ্রেড Customার Data Anonymizer এবং Fine-Tuning Dataset Sanitizer Engine স্ক্র্যাচ থেকে Architect করি।

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
* **Input:** Customারদের সিক্রেট ফোন নাম্বার ও ইমেইলসহ র Conversation হিস্টোরি।
* **Output:** Anonymized নিরাপদ Fine-Tuning Dataset।
* **Why it works:** Custom Regular Expression Pattern perfectly ফোন ও ইমেইল ডিটেক্ট করে Placeholder ট্যাগ দিয়ে replace করেছে, যা প্রোডাকশন Data লিক হওয়ার ঝুঁকি ১০০% দূর করে।
* **When to use:** রিয়েল ইউজার Database থেকে Fine-Tuning Dataset Preparation করার সময়।


### ১০. Interview Questions

#### Beginner
1. **প্রশ্ন:** কখন আরএজি (RAG) বনাম Fine-Tuning (Fine-Tuning) এর মধ্যে সঠিক Architectural সিদ্ধান্ত নিতে হবে?
   * **উত্তর:** যখন Project-এর লক্ষ্য Dynamic, রিয়েল-টাইম এবং perfect Factual তথ্য Produce করা, তখন RAG সেরা চয়েস। আর যখন লক্ষ্য মডেলকে নির্দিষ্ট টোন, স্টাইল বা Custom Output Format (যেমন: JSON/SQL/Code) জেনারেট করা শেখানো, তখন Fine-Tuning একমাত্র সমাধান।

#### Intermediate
2. **প্রশ্ন:** Fine-Tuning Dataset তৈরির সময় "Personally Identifiable Information (PII) Masking" কেন আবশ্যক?
   * **উত্তর:** PII মাস্কিং না করলে Customারের secret ফোন নাম্বার, ইমেইল বা আইডি ইনফরমেশন Fine-Tuning-এর সময় Model-এর ওয়েটসে forever সেভ হয়ে যাবে। পরবর্তীতে Prompt হ্যাকিংয়ের মাধ্যমে AI সেই secret Data পাবলিকলি ফাস করে দিতে পারে, যা বিশাল সিকিউরিটি লিক ঘটাবে।

#### Advanced
3. **প্রশ্ন:** SFT ট্রেনিংয়ের সময় Loss ক্যালকুলেশনে কেন "Target Prompt Masking (Index -100)" ব্যবহার করা হয়? এর গুরুত্ব কী?
   * **উত্তর:** এসএফটি (SFT) ট্রেনিংয়ে আমাদের লক্ষ্য মডেলকে ইউজারের প্রশ্নের পর কীভাবে সঠিক উত্তর দিতে হয় তা শেখানো। ইউজার কী প্রশ্ন করবে তার ওপর Model-এর কোনো নিয়ন্ত্রণ নেই, তাই Prompt Token-এর ওপর Loss ক্যালকুলেট করা মেমরি ও Gradient অপ্টিমাইজেশন ব্যাহত করে। টার্গেট মাস্কিং (-100 Index) চেইন রুলকে শুধুমাত্র Assistant Response Token-এর ওপর ওয়েটস আপডেট করতে গাইড করে।


### ১১. Chapter Summary
* **Supervised Fine-Tuning (SFT)** Model-এর আচরণ ও টোন পরিবর্তনের মূল Mathematical method।
* **RAG** ফ্যাট ও Dynamic Data সোর্সিংয়ের রাজা, আর **Fine-Tuning** Format ও Personaর রাজা।
* **Alpaca** এবং **ShareGPT** Instruction Dataset-এর প্রধান দুটি গোল্ড Standard Format।
* প্রোডাকশন Dataset প্রিপারেশনে strictly **PII Masking** ensure করা must।


### biographies.md
দারুণ! আমরা ভালোভাবে Supervised Fine-Tuning-এর Data প্রিপারেশন ও থিওরি শেষ করে ফেলেছি। পরের chapter-এ আমরা এই Fine-Tuning মেমরি ও GPU Compute কস্ট save করার জন্য সবচেয়ে revolutionary Mechanism নিয়ে আলোচনা করব: **Chapter 16: Parameter-Efficient Fine-Tuning (LoRA & QLoRA)**। Low-Rank Adapter (LoRA) এর Mathematical Intuition এবং ৪-বিট Quantization (QLoRA) কীভাবে কনজিউমার ল্যাপটপে এলএলএম ফাইন-টিউন করতে সাহায্য করে, তা আমরা বিস্তারিত শিখব।

**Chapter 15 শেষ।**
