# Chapter 17: Supervised Fine-Tuning (SFT) & Dataset Preparation

---

ধরো, তোমার হাতে একটা বেস Model আছে।

সে অনেক কিছু জানে, কিন্তু কথা বলে একদম নিজের মতো করে।

তুমি চাচ্ছো সে তোমার কাস্টমারদের সাথে মিষ্টি বাংলায় কথা বলুক, বা JSON Format-এ Output দিক।

সেটা শেখাবে কীভাবে?

সেটাই হলো Supervised Fine-Tuning (SFT)।

মজার ব্যাপার হলো— অনেকে ভাবে Fine-Tuning মানে মডেলকে নতুন তথ্য শেখানো। ভুল!

নতুন ফ্যাক্টস শেখাতে চাইলে RAG ব্যবহার করো।

Fine-Tuning হলো মডেলকে **"কীভাবে কথা বলবে"** সেটা শেখানোর জন্য।

এই তফাতটা না বুঝলে তুমি শুধু শুধু GPU কস্ট পুড়িয়ে ফেলবে।

तो চলো দেখি কীভাবে Instruction Dataset (Alpaca, ShareGPT formats) তৈরি করতে হয়, কখন RAG বনাম Fine-Tuning বেছে নিতে হয়, আর SFT Training Pipeline কীভাবে কাজ করে।

এটা বুঝলে পরের চ্যাপ্টারের LoRA/QLoRA আর RLHF সব পানির মতো সহজ লাগবে। Deal?


## ১. ডাক্তার বনাম তার আচরণ

কল্পনা করো, তোমার সামনে একজন খুব দক্ষ ডাক্তার বসে আছেন।

ধরো, তিনি হৃদরোগের নতুন আবিষ্কৃত একটি সার্জারি রুল বা পলিসি জানেন না।

এখন তুমি কী করবে?

খুব সহজ! তুমি তার টেবিলের ওপর সেই নতুন রিসার্চ পেপার বা বই খুলে দিলে।

ডাক্তার পেপারের ৩ নম্বর পৃষ্ঠা দেখে নিখুঁত সার্জারি প্রসিডিউরটি বুঝে তোমাকে বুঝিয়ে দিলেন।

এটাই হলো RAG। অনেকটা Open-Book পরীক্ষার মতো।

![When to use RAG vs. Fine-Tuning](/diagrams/when_to_use_rag_vs_finetuning.png)

কিন্তু এবার ধরো অন্য একটা পরিস্থিতি।

ডাক্তার সব মেডিকেল বই জানেন, কিন্তু তিনি কথা বলেন খুব অভদ্র ও কর্কশ ভাষায়।

তুমি চাও তিনি যেন রোগীদের সাথে নরম বাংলায় ও পোলাইট Persona-য় কথা বলেন।

এখন টেবিলে নতুন বই খুলে দিলে কি তার আচরণ পরিবর্তন হবে?

একদমই না!

তার আচরণ বদলাতে হলে তাকে কয়েক মাস Custom বিহেভিয়ার ট্রেনিং দিতে হবে।

যাতে তার মস্তিষ্কের কথা বলার টোন ও স্টাইল সম্পূর্ণ বদলে যায়।

এই ট্রেনিংটাই হলো Fine-Tuning বা SFT।

RAG এবং Fine-Tuning-এর মূল তফাতটি ঠিক এখানেই।

সহজ কথায়, মডেলকে কোনো Dynamic বা রিয়েল-টাইম ডাটা দিতে হলে RAG ব্যবহার করবে।

আর মডেলকে নির্দিষ্ট টোন, স্টাইল বা Custom Output Format যেমন JSON বা SQL শেখাতে হলে Fine-Tuning-ই একমাত্র পথ। Deal?


## ২. Supervised Fine-Tuning এবং Data স্ট্রাকচার

### কখন Fine-Tune করবে আর কখন RAG?

চলো সিদ্ধান্ত নেওয়ার জন্য একটি Decision Table দেখে নিই:

| Criteria | RAG (Retrieval-Augmented) | Fine-Tuning (SFT) |
| :--- | :--- | :--- |
| **মূল লক্ষ্য** | External রিয়েল-টাইম ফ্যাক্টস ও ইনফরমেশন দেওয়া | নির্দিষ্ট টোন, স্টাইল বা Format (JSON/SQL) শেখানো |
| **Data আপডেট** | instant (Vector ডাটাবেসে File পুশ করলেই হয়) | ধীর (আবার Training রান করতে হয়) |
| **Hallucination** | খুব কম (সোর্স পেজের রেফারেন্স থাকে) | মাঝারি (Model নিজে বানিয়ে লিখতে পারে) |
| **Compute খরচ** | কম (শুধুমাত্র Inference ও Vector Search কস্ট) | উচ্চ (GPU Training কস্ট) |

### Supervised Fine-Tuning কী?

SFT আসলে কী?

সহজ কথায়, এটি হলো মডেলকে প্রচুর পরিমাণে Instruction-Response জোড়া দেখিয়ে ট্রেইন করা।

এর Mechanism কী?

মডেলকে আমরা ১ হাজার থেকে ১ লাখ কাস্টম বাংলা কথোপকথনের স্যাম্পল দেখাই।

যেমন: `User: [Question] -> Assistant: [Bengali customized answer]`।

ট্রেনিংয়ের সময় Loss Optimization কীভাবে হয়?

মডেল যখন কাস্টম উত্তরের সাথে ম্যাচ করতে ভুল Token Predict করে, তখন Loss Calculate করা হয়।

তারপর Backpropagation-এর মাধ্যমে Model-এর Weights পরিবর্তন বা Modify করা হয়।

### Dataset Format

#### Alpaca Format

এটি সবচেয়ে সহজ এবং সরল Format।

এখানে প্রতিটি Data নোডে ৩টি কিওয়ার্ড থাকে।

কী কী সেগুলো?

প্রথমটি হলো `instruction`, অর্থাৎ ইউজার কী টাস্ক দিয়েছে।

দ্বিতীয়টি `input`, যা টাস্কের সাথে কোনো অতিরিক্ত Context দিতে ব্যবহার করা হয়। এটি অপশনাল।

আর শেষটি হলো `output`, অর্থাৎ AI কী উত্তর দেবে।

```json
{
  "instruction": "নিচের বাক্যটি বাংলায় অনুবাদ করো।",
  "input": "I love AI engineering.",
  "output": "আমি AI ইঞ্জিনিয়ারিং ভালোবাসি।"
}
```

#### ShareGPT Format

মডার্ন চ্যাট মডেলগুলোর জন্য এটি সবচেয়ে জনপ্রিয় Format।

এটি ইউজারের সাথে মাল্টি-টার্ন Conversation তৈরি করে।

```json
{
  "conversations": [
    {"from": "human", "value": "বিকাশ পিন লক হলে কী করব?"},
    {"from": "gpt", "value": "তোমার পিন লক হলে দয়া করে *247# ডায়াল করে সেলফ-রিসেট করো।"}
  ]
}
```

🧠 Remember

Dataset তৈরি করার সময় সর্বদা Data Quality-কে Data Quantity-এর চেয়ে বেশি গুরুত্ব দেবে।

১০ হাজার আজেবাজে Data-এর চেয়ে ১ হাজার হাই-Quality নির্ভুল Data মডেলকে অনেক ভালো বানাতে পারে।

একেই বলে "Less is More" রুল।


## ৩. SFT Training Loop

এসএফটি ট্রেনিংয়ের সময় Model কীভাবে শুধু Assistant Token-এর ওপর Loss Calculate করে, চলো নিচে তা দেখে নিই:

![SFT Target Token Loss Calculation](/diagrams/sft_target_token_loss_calculation.png)

ট্রেনিংয়ের সময় আমরা কিন্তু ইউজারের প্রশ্নের Token-এর ওপর Loss Calculate করি না।

একে -100 index দিয়ে Mask করা হয়।

মডেল কেবল Assistant-এর উত্তর Prediction-এ ভুল করলে Weights আপডেট হয়।


## ৪. Real World Example: Cursor ও .cursorrules

Cursor যখন তোমার Project-এর স্পেসিফিক নিয়মে Code লেখে, তখন আসলে কী ঘটে?

প্রথমত, তারা তাদের ওপেন-সোর্স বেস মডেলকে হাজার হাজার Coding কনভেনশন এবং Project রুলস দিয়ে Fine-Tuning করেছে।

একে বলে System Prompt Alignment।

দ্বিতীয়ত, এর ফলে মডেলটি তোমার প্রজেক্টের `.cursorrules` ফাইলটি পড়া মাত্রই তোমার টোন এবং স্টাইল বুঝে ফেলে।

সে অনুযায়ী একদম নিখুঁত Code তৈরি করে দেয়।


## ৫. Developer Perspective: Dataset লোড করা

💻 Developer View

ডেভলপার হিসেবে পাইথনে `datasets` লাইব্রেরি ব্যবহার করে কাস্টম Alpaca Format-এর Dataset লোড করার উপায়টি চলো দেখে নিই।

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


## ৬. Production Perspective: Data Anonymization

🏭 Production Reality

Dataset রেডি করার সময় সবচেয়ে বড় সিকিউরিটি রিস্ক হলো PII Leakage বা ব্যক্তিগত তথ্য ফাস হয়ে যাওয়া।

PII কী?

এটি হলো Personally Identifiable Information, যেমন মানুষের নাম, ফোন নাম্বার, ইমেইল ইত্যাদি।

এর ঝুঁকি বা Risk কী?

লাইভ চ্যাট Log থেকে যদি সরাসরি ফোন নাম্বার বা ইমেইল দিয়ে Model ট্রেইন করে ফেলো, তবে সেই তথ্য Model-এর ব্রেইনে সেভ হয়ে যাবে।

পরবর্তীতে চ্যাট করার সময় Model সেই গোপন তথ্য অন্য কারও সামনে ফাস করে দিতে পারে!

তাহলে এর সমাধান কী?

খুব সহজ, ট্রেইনিংয়ের আগে ডেটাকে Anonymize বা মাস্ক করে ফেলতে হবে।

যেমন Regular Expression বা `presidio` লাইব্রেরি ব্যবহার করে ফোন নাম্বারকে `<PHONE>` এবং নামকে `<NAME>` দিয়ে বদলে দেওয়া।


## ৭. Common Mistakes

🔴 Common Mistake

ভুল ধারণা:

ডেটাসেটে ব্যাকরণ বা তথ্যের ভুল থাকলেও সমস্যা নেই, Model নিজে নিজেই সব ঠিক করে নেবে।

বাস্তবতা:

Model কিন্তু ট্রেইনিং ডেটাসেটের স্টাইল হুবহু অনুকরণ করে।

তাই ডেটাসেটে বানান ভুল থাকলে ফাইন-টিউনড Model-ও ভুল বানানই জেনারেট করবে।

এজন্য Dataset সবসময় একদম পরিষ্কার ও নির্ভুল রাখতে হবে।


## ৮. Mental Model: অ্যাক্টিং স্কুল

RAG এবং Fine-Tuning-এর পার্থক্য বোঝার জন্য একটি সহজ Mental Model ব্যবহার করা যাক।

RAG হলো অনেকটা Memory কার্ড রিডার-এর মতো।

এখানে Model-এর ব্রেইনে কোনো পরিবর্তন হয় না।

তুমি তাকে একটা External Memory ড্রাইভ কানেক্ট করে দিলে, সে শুধু রিড করে উত্তর দিল।

আর Fine-Tuning হলো অ্যাক্টিং স্কুলে ক্যারেক্টার ট্রেনিং নেওয়ার মতো।

তুমি একজন অভিনেতাকে অ্যাক্টিং স্কুলে পাঠালে সে কিন্তু নতুন কোনো ইতিহাস বা তথ্য শিখছে না।

সে শুধু শিখছে কীভাবে একজন মিষ্টি স্বভাবের ডাক্তারের মতো অভিনয় করতে হয় বা কথা বলতে হয়।


## ৯. Mini Project: Custom Dataset এবং PII Filter

চলো পাইথনে Regex ব্যবহার করে কোনো লাইব্রেরি ছাড়াই একটি কাস্টম Data Anonymizer তৈরি করে ফেলি।

এর মাধ্যমে আমরা সহজেই Fine-Tuning ডেটাসেট থেকে গোপন তথ্য ফিল্টার করতে পারব।

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

এখানে Input হিসেবে আমরা কী দিচ্ছি?

কাস্টমারদের গোপন ফোন নাম্বার ও ইমেইলসহ র চ্যাট হিস্টোরি।

Output হিসেবে কী পাচ্ছি?

PII ফিল্টার করা একদম নিরাপদ Fine-Tuning Dataset।

এটি কীভাবে কাজ করছে?

আমাদের Custom Regex Pattern খুব সহজেই ফোন এবং ইমেইল খুঁজে বের করে ট্যাগ দিয়ে বদলে দিচ্ছে।

এর ফলে আমাদের প্রোডাকশন ডেটা লিক হওয়ার কোনো সম্ভাবনাই থাকছে না।

আমরা এটি কখন ব্যবহার করব?

রিয়েল ইউজার ডেটা ব্যবহার করে Fine-Tuning Dataset রেডি করার সময়।


## ১০. Interview Questions

### Beginner

**প্রশ্ন:** কখন RAG বনাম Fine-Tuning-এর মধ্যে সঠিক Architectural সিদ্ধান্ত নিতে হবে?

**উত্তর:** যখন প্রজেক্টের লক্ষ্য রিয়েল-টাইম এবং নির্ভুল Factual তথ্য দেওয়া, তখন RAG সেরা চয়েস।

আর যখন লক্ষ্য Model-কে নির্দিষ্ট টোন বা Custom Output Format (যেমন JSON বা SQL) শেখানো, তখন Fine-Tuning একমাত্র সমাধান।

### Intermediate

**প্রশ্ন:** Fine-Tuning Dataset তৈরির সময় PII Masking কেন আবশ্যক?

**উত্তর:** PII মাস্কিং না করলে কাস্টমারের গোপন ফোন নাম্বার বা ইমেইল চিরতরে Model-এর ব্রেইনে সেভ হয়ে যাবে।

পরবর্তীতে Prompt হ্যাকিংয়ের মাধ্যমে AI সেই গোপন ডাটা সবার সামনে ফাস করে দিতে পারে।

এটি একটি বড় সিকিউরিটি লিক ঘটাবে।

### Advanced

**প্রশ্ন:** SFT ট্রেনিংয়ের সময় Loss Calculation-এ কেন Target Prompt Masking বা Index -100 ব্যবহার করা হয়?

**উত্তর:** SFT ট্রেনিংয়ে আমাদের মূল লক্ষ্য হলো সঠিক উত্তর দিতে শেখানো।

ইউজার কী প্রশ্ন করবে তার ওপর মডেলের কোনো হাত নেই।

Prompt Token-এর ওপর Loss Calculate করলে মেমরি ও Gradient Optimization নষ্ট হয়।

টার্গেট মাস্কিং চেইন রুলকে শুধুমাত্র Assistant Response-এর ওপর Weights আপডেট করতে সাহায্য করে।


## Chapter Summary

চলো সংক্ষেপে পুরো চ্যাপ্টারটি রিভিশন দিয়ে নিই:

SFT হলো মডেলের আচরণ ও কথা বলার টোন পরিবর্তন করার মূল গাণিতিক পদ্ধতি।

মনে রাখবে, RAG হলো রিয়েল-টাইম ডাটার রাজা, আর Fine-Tuning হলো Format ও Persona-র রাজা।

আমরা ডেটাসেট তৈরির জন্য Alpaca এবং ShareGPT—এই দুটি জনপ্রিয় Format ব্যবহার করি।

আর হ্যাঁ, প্রোডাকশন ডেটাসেট তৈরির সময় PII Masking করা কিন্তু একদম বাধ্যতামুলক!


## What's Next?

দারুণ! আমরা Supervised Fine-Tuning-এর মূল বিষয়গুলো শিখে ফেলেছি।

পরের চ্যাপ্টারে আমরা এই প্রসেসকে আরও সহজ ও কম খরচে করার ম্যাজিক শিখব।

চলো তাহলে দেখে নিই: **Chapter 18: Parameter-Efficient Fine-Tuning (LoRA & QLoRA)**।

কম খরচে কীভাবে ল্যাপটপেই বড় মডেল ফাইন-টিউন করা যায়, সেটাই দেখব সেখানে। Deal?

**Chapter 17 শেষ।**
