# Chapter 9: The LLM Ecosystem — Decoder-only, Encoder-only & Encoder-Decoder

---

### Chapter Goal
এই চ্যাপ্টারের মূল লক্ষ্য হলো লার্জ ল্যাঙ্গুয়েজ Model (LLM) এবং আধুনিক জেনারেটিভ এআই ইকোসিস্টেমের পূর্ণাঙ্গ শ্রেণীবিন্যাস ম্যাপ করা। আমরা জানবো কীভাবে এনকোডার-অনলি (Encoder-only: BERT), ডিকোডার-অনলি (Decoder-only: GPT/Llama) এবং এনকোডার-ডিকোডার (Encoder-Decoder: T5) Architecture কাজ করে, কেন ডিকোডারের বাজারে একচ্ছত্র আধিপত্য এবং একই সাথে মাল্টি-মোডাল ভিশন (VLM), Image জেনারেশন (Diffusion - Flux, SD) এবং অডিও Model-এর ভেতরের মূল Mechanism ভেঙে দেখবো।

### Why Should I Care?
Developer হিসেবে সব কাজের জন্য জিপিটি-৪ বা Claude-৩ কল করা একটি অপচয় এবং চরম আর্কিটেকচারাল অজ্ঞতা। টেক্সট ক্লাসিফিকেশন বা সেন্টিমেন্ট অ্যানালাইসিসের জন্য একটি মাত্র ১০০ ডলারের BERT Model যা করতে পারে, তার জন্য ৩০০ গুণ বড় জিপিটি Model কল করার কোনো প্রয়োজন নেই। এই চ্যাপ্টারটি পড়লে তুমি এআই ল্যান্ডস্কেপের প্রতিটি ক্যাটাগরির শক্তি ও সীমাবদ্ধতা অনুধাবন করতে পারবে এবং Project-এর রিকোয়ারমেন্ট অনুযায়ী নিখুঁত Model সিলেক্ট করতে পারবে।

### Big Picture
এটি আমাদের প্রথম ৮টি তাত্ত্বিক ও গাণিতিক চ্যাপ্টারের মূল সমাপনী অধ্যায়। এর পর থেকে আমরা সরাসরি Vector Database, আরএজি (RAG), Fine-Tuning এবং প্রোডাকশন এজেন্ট ব্লুপ্রিন্ট গড়ার কাজ শুরু করবো। এই চ্যাপ্টারটি তোমার এআই আর্কিটেক্ট হওয়ার জার্নিতে ইকোসিস্টেমের ফাইনাল ম্যাপ হিসেবে কাজ করবে।

---

### ১. Hook: তিন কারিগরের এক অদ্ভুত গল্প

একটি ভার্চুয়াল রাজপ্রাসাদে তিনজন অত্যন্ত দক্ষ কারিগর আছেন:
1. **প্রথম কারিগর (BERT - The Inspector):** তাকে একটি সম্পূর্ণ বাক্য দিলে সে বাক্যের ডান-বাম, আগে-পরে সব শব্দ স্ক্যান করে মাঝখানের লুকানো বা মুছে যাওয়া শব্দ নিখুঁতভাবে উদ্ধার করতে পারে। সে খুব ভালো গোয়েন্দা বা বিশ্লেষক, কিন্তু নতুন কোনো বাক্য লিখতে পারে না। একে বলে **Encoder-only**।
2. **দ্বিতীয় কারিগর (GPT - The Storyteller):** সে খুব ভালো গল্প লেখক। তাকে শুধু একটি শুরুর শব্দ বা Prompt দিন, সে তার আগের শব্দের স্মৃতি মাথায় রেখে একের পর এক Token জেনারেট করে এক বিশাল উপন্যাস লিখে দিতে পারবে। সে কেবল সামনের দিকে (Autoregressive) তাকাতে পারে। একে বলে **Decoder-only**।
3. **তৃতীয় কারিগর (T5 - The Translator):** সে একটি বাক্য সম্পূর্ণ শুনে তার অর্থ হৃদয়ঙ্গম করে এবং এরপর অন্য ভাষা বা ফরম্যাটে রূপান্তর করে Output দেয়। যেমন বাংলা থেকে ইংরেজি অনুবাদ বা বড় আর্টিকেলের জিস্ট সামারি প্রডিউস করা। একে বলে **Encoder-Decoder**।

[VISUAL]
Title: LLM Architectures Taxonomy
Illustration: Comparison of data direction for Encoder-only (bidirectional), Decoder-only (causal), and Encoder-Decoder (split sequence)
Placement: After Hook Section
Purpose: Instantly differentiate BERT, GPT, and T5 pathways.

```
Encoder-only (BERT - Bidirectional):
[ Token 1 ] ◄───► [ Token 2 ] ◄───► [ Token 3 ]  (Sees everything at once - Good for Extraction)

Decoder-only (GPT - Causal/Autoregressive):
[ Token 1 ] ───► [ Token 2 ] ───► [ Token 3 ] ───► [ Next Token ? ] (Masks future - Good for Generation)

Encoder-Decoder (T5 - Translation Seq2Seq):
[ Input Sequence ] ───► [ Encoder Block ] ───► [ Latent States ] ───► [ Decoder Block ] ───► [ Output Sequence ]
```

---

### ২. Core Concepts: Model পরিবারের অন্দরমহল

#### ক. Encoder-only Models (BERT পরিবার)
* **Mechanism:** এরা **Bidirectional Attention** ব্যবহার করে। অর্থাৎ, প্রতিটি Token বাক্যের বাম ও ডান—উভয় দিকের অন্যান্য সব টোকেনে মনোযোগ দিতে পারে।
* **Training মেথড:** Masked Language Modeling (MLM)—বাক্যের ১৫% শব্দ র্যান্ডমলি মুছে দিয়ে মডেলকে তা প্রেডিক্ট করতে বলা হয়।
* **কখন ব্যবহার করবে:** সেন্টিমেন্ট এনালাইসিস, Search কি-ওয়ার্ড ম্যাচিং, নেমড এন্টিটি রিকগনিশন (NER)।

#### খ. Decoder-only Models (GPT/Llama পরিবার)
* **Mechanism:** এরা **Causal Masked Attention** ব্যবহার করে। অর্থাৎ, কোনো Token তার সামনের বা ভবিষ্যতের কোনো শব্দ রিড করতে পারে না, কেবল তার পূর্বে জেনারেট হওয়া শব্দের দিকে মনোযোগ দিতে পারে।
* **Training মেথড:** Causal Language Modeling (CLM)—পরবর্তী শব্দের নিখুঁত প্রেডিকশন।
* **কখন ব্যবহার করবে:** জেনারেটিভ চ্যাট, Code রাইটিং, ক্রিয়েটিভ রাইটিং। এটিই বর্তমান এআই এজেন্টের মূল ব্রেইন।

#### গ. Encoder-Decoder Models (T5/BART পরিবার)
* **Mechanism:** Input-এর জন্য একটি এনকোডার ম্যাট্রিক্স এবং Output জেনারেশনের জন্য একটি ডিকোডার ম্যাট্রিক্স আলাদা থাকে।
* **কখন ব্যবহার করবে:** টেক্সট সামারাইজেশন, ল্যাঙ্গুয়েজ ট্রান্সলেশন, কাস্টম ফরম্যাট Conversion।

#### ঘ. Multi-modal & Generative AI (মাল্টি-মোডাল মহাবিশ্ব)

##### ১. Vision-Language Models (VLM - যেমন: GPT-4o, Llama 3.2 Vision)
* **Mechanism:** এরা একটি **Vision Encoder** (যেমন CLIP, যা ছবিকে এম্বেডিংস ভেক্টরে রূপান্তর করে) Transformer প্রজেকশন লেয়ার দিয়ে সরাসরি ডিকোডার এলএলএম-এর সাথে জুড়ে দেয়। এর ফলে Model ছবি ও টেক্সটকে একই জ্যামিতিক স্পেসে প্রসেস করতে পারে।

##### ২. Image Generation (Diffusion Models - Flux, Stable Diffusion)
* **Mechanism:** এরা Transformer দিয়ে সরাসরি Image জেনারেট করে না। এরা **Denoising** মেকানিজমে চলে। Model প্রথমে একটি র্যান্ডম নয়েজ (হিজিবিজি Pixel) নেয় এবং ধীরে ধীরে টেক্সট এম্বেডিংসের সাথে মিল রেখে ধাপে ধাপে নয়েজ রিমুভ করে একটি নিখুঁত ছবি প্রডিউস করে।

##### ৩. Audio & Speech Models (যেমন: Whisper)
* **Mechanism:** এরা র অডিও ফ্রিকোয়েন্সিকে স্পেক্ট্রোগ্রাম ইমেজে রূপান্তর করে সিকোয়েন্স টু সিকোয়েন্স Transformer দিয়ে সরাসরি র টেক্সট প্রেডিক্ট করে।

---

### ৩. Visual Explanation: ভিশন ল্যাঙ্গুয়েজ Model-এর প্রজেকশন পাইপলাইন

ভিশন এআই কীভাবে কাজ করে তা দেখলে ম্যাজিক মনে হলেও আসলে তা সাধারণ Vector প্রজেকশন লেয়ার:

```
[ ছবি Input ] ───► [ Vision Encoder (CLIP) ] ───► [ Image Embedding Vector ]
                                                           │
                                                           ▼ (Cross-Attention Projection)
[ Prompt: "ছবিটি বর্ণন করো" ] ──► [ LLM Decoder Block ] ◄─┘
                                   │
                                   ▼
                            "এটি একটি সুন্দর বিড়াল..."
```

---

### ৪. Real World Example: সেন্টিমেন্ট ক্লাসিফায়ার ডিউটি

তোমার একটি ই-কমার্স স্টোর আছে যেখানে কাস্টমাররা অনবরত কমেন্ট করছো:
* **ভুল সিদ্ধান্ত:** প্রতি সেকেন্ডে প্রতিটি কাস্টমার কমেন্টের সেন্টিমেন্ট (Positive / Negative) বের করার জন্য OpenAI-এর GPT-4 API কল করা। এতে তোমার Latency ও বিলিং আকাশে উঠবে।
* **সঠিক সিদ্ধান্ত:** Hugging Face থেকে একটি ১০০ মিলিয়ন Parameter-এর ফ্রী **DeBERTa (Encoder-only)** Model ডাউনলোড করে লোকাল সার্ভারে ডিপ্লয় করা। এটি ১ মিলি-সেকেন্ডে ফ্রীতে ১০০% নিখুঁতভাবে সেন্টিমেন্ট ক্লাসিফাই করে ডাটাবেসে সেভ করবে।

---

### ৫. Developer Perspective: Hugging Face Transformers Library ব্যবহার

💻 Developer View

চলো পাইথনে Hugging Face `transformers` Library ব্যবহার করে লোকাল কম্পিউটারে ৩টি আলাদা ক্যাটাগরির টাস্ক (BERT দিয়ে ক্লাসিফিকেশন, GPT-2 দিয়ে জেনারেশন এবং Whisper দিয়ে অডিও ট্রান্সক্রিপশন) নিমিষেই রান করার Architecture দেখে নিই।

```python
from transformers import pipeline

# ১. ENCODER-ONLY (DeBERTa/BERT for Sentiment Analysis)
print("Loading Sentiment Classifier...")
classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
res_sentiment = classifier("I love this AI Engineering book! It makes math so easy.")
print("Sentiment Result:", res_sentiment)

# ২. DECODER-ONLY (GPT-2 for Text Generation)
print("\nLoading Story Generator...")
generator = pipeline("text-generation", model="gpt2")
res_generator = generator("In the future, AI engineers will", max_length=30, num_return_sequences=1)
print("Generated Text:\n", res_generator[0]['generated_text'])

# ৩. VISION MODEL (Image Classification)
print("\nLoading Object Detector...")
detector = pipeline("image-classification", model="google/vit-base-patch16-224")
# Note: You can pass a local image path or URL here
# res_image = detector("https://example.com/cat.jpg")
# print("Detected Object:", res_image)
```

---

### VI. Production Perspective: Serving Frameworks (vLLM vs. Ollama)

🏭 Production Reality

ডেভেলপাররা অনেক সময় প্রোডাকশনে এলএলএম সার্ভ করতে গিয়ে ক্লাসিক্যাল FastAPI দিয়ে র হুগেং ফেস Model লোড করে বসেন। এটি অত্যন্ত স্লো এবং কনকারেন্ট রিকোয়েস্টে ক্র্যাশ করে।

প্রোডাকশন গোল্ড স্ট্যান্ডার্ড Serving Frameworks:
* **vLLM (Virtual LLM):** এটিতে **PagedAttention** Mechanism রয়েছে। এটি অপারেটিং সিস্টেমের ভার্চুয়াল Memory-এর মতো Model-এর KV-Cache Memory পেজ আকারে এলোকেট করে, যা GPU সার্ভিং স্পীড ও কনকারেন্সি ১০ গুণ বুস্ট করে।
* **Ollama / llama.cpp:** CPU বা পারসোনাল ম্যাকবুক/উইন্ডোজ কম্পিউটারে quantized GGUF Model লোকালি ফাস্ট রান করার জন্য এটিই বেস্ট চয়েস।

---

### VII. Common Mistakes

🔴 Common Mistake

**ভুল ধারণা:** GPT বা Llama-র মতো বড় জেনারেটিভ ডিকোডারের Context Window ১২৮k হওয়া মানেই সে যেকোনো ১ লাখ Token-এর বিশাল Document থেকে ১০০% নিখুঁত উত্তর খুঁজে বের করবে।

**বাস্তবতা:** একে বলে **Lost in the Middle** ফেনোমেনন। গবেষণায় দেখা গেছে, ডিকোডার মডেলগুলো বিশাল কনটেক্সটের শুরুর অংশ এবং শেষের অংশ খুব ভালো মনে রাখতে পারে, কিন্তু কনটেক্সটের ঠিক মাঝখানের কোনো ইনফরমেশন সে মিস বা ফিল্টার আউট করে ফেলে। তাই প্রোডাকশনে বড় Document-এর ক্ষেত্রে অন্ধভাবে Context ফিড না করে RAG এবং রি-র‍্যাঙ্কিং করাই বুদ্ধিমানের কাজ।

---

### VIII. Mental Model: তিন লেখকের এডিটিং প্যানেল

এলএলএম পরিবারের মেন্টাল Model:

**"Encoder-only হলো তোমার কড়া প্রুফ-রিডার যে খাতার সব লেখা একসাথে দেখে বানান ভুল ধরে। Decoder-only হলো সেই কবি যিনি খাতার ডান পৃষ্ঠা হাত দিয়ে ঢেকে রেখে অনবরত বাম থেকে ডানে সুন্দর কবিতা লিখে যাও। আর Encoder-Decoder হলো দক্ষ দোভাষী যিনি পুরো বাক্য মন দিয়ে শুনে তার খসড়া ট্রান্সলেশন প্রডিউস করো।"**

---

### IX. Mini Project: স্ক্র্যাচ নেক্সট Token প্রবাবিলিটি জেনারেটর

চলো NumPy ব্যবহার করে একটি কাল্পনিক ডিকোডারের সর্বশেষ লেয়ারের Logits থেকে কীভাবে সফটম্যাক্স চালিয়ে পরবর্তী সম্ভাব্য শব্দের সম্ভাব্যতা বের করা হয়, তা Code করি।

```python
import numpy as np

# ভোকাবুলারি ম্যাপ
vocab = {0: "AI", 1: "is", 2: "magic", 3: "banana"}

# Model-এর ডিকোডার শেষ লেয়ারের রিয়েল Output স্কোর (Logits)
logits = np.array([8.2, 5.1, 9.5, -2.1])

# ১. সফটম্যাক্স Function প্রবাবিলিটি বের করার জন্য
def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

probabilities = softmax(logits)

# ২. সম্ভাব্যতা প্রিন্ট করো
print("Word Probability mapping:")
for idx, prob in enumerate(probabilities):
    print(f"'{vocab[idx]}' -> Probability: {prob * 100:.2f}%")

# ৩. Greedy Decoding (সর্বোচ্চ প্রবাবিলিটির শব্দ সিলেক্ট)
next_token_id = np.argmax(probabilities)
print(f"\nPredicted next token: '{vocab[next_token_id]}' with {probabilities[next_token_id]*100:.2f}% confidence!")
```

---

### X. Interview Questions

#### Beginner
1. **প্রশ্ন:** Encoder-only (BERT) এবং Decoder-only (GPT) এর মধ্যে প্রধান ব্যবহারিক তফাত কী?
   * **উত্তর:** Encoder-only Model Bidirectional Attention ব্যবহার করায় বাক্যের সব ইনফরমেশন একসাথে প্রসেস করে ক্লাসিফিকেশন বা এক্সট্রাকশনের জন্য বেস্ট পারফর্ম করে। আর Decoder-only Model Causal Masked Attention ব্যবহার করায় কেবল সিকোয়েনশিয়াল টেক্সট জেনারেশন ও চ্যাটিংয়ের কাজে ব্যবহৃত হয়।

#### Intermediate
2. **প্রশ্ন:** "PagedAttention" কী এবং vLLM সার্ভারে এটি কীভাবে Memory খরচ বাঁচায়?
   * **উত্তর:** PagedAttention হলো অপারেটিং সিস্টেমের ভার্চুয়াল মেমরি বা পেজিংয়ের অনুরূপ একটি টেকনিক যা এলএলএম সার্ভিংয়ের সময় KV-Cache Memory (যা পূর্বে র্যান্ডম ও ফ্র্যাগমেন্টেড আকারে Memory ব্লক নষ্ট করতো) ফিক্সড সাইজের ভার্চুয়াল পেজে ভাগ করে ফেলে। এর ফলে Memory ওয়েস্টেজ শূন্যে নেমে আসে এবং GPU সার্ভিং কনকারেন্সি ড্রাস্টিকালি বুস্ট হয়।

#### Advanced
3. **প্রশ্ন:** লার্জ ল্যাঙ্গুয়েজ মডেলে "Lost in the Middle" সমস্যাটি কী এবং এটি কীভাবে RAG সিস্টেমকে প্রভাবিত করে?
   * **উত্তর:** Lost in the Middle সমস্যাটি হলো—Model-এর Context Window যতই বড় হোক না কেন, সে Input করা বিশাল Document-এর একদম মাঝখানের তথ্যগুলো সহজে অ্যাটেনশনে রিড করতে পারে না, শুরুতে ও শেষে মনোযোগ বেশি থাকে। RAG সিস্টেমে আমরা যখন প্রচুর Document ডাম্প করি, তখন প্রয়োজনীয় উত্তরটি যদি Document-এর মাঝখানে পড়ে যায়, Model হ্যালুসিনেট করতে পারে। এই সমস্যা দূর করতে Cohere বা BGE Re-ranker Model ব্যবহার করে সেরা ৫টি রিলেভেন্ট Document একদম শুরুতে পুশ করতে হয়।

---

### XI. Chapter Summary
* **BERT (Encoder-only)** গোয়েন্দার মতো ইনফরমেশন রিড ও ক্লাসিফাই করে।
* **GPT (Decoder-only)** লেখকের মতো Autoregressive স্টাইলে টেক্সট জেনারেট করে।
* **vLLM** এবং **Ollama** প্রোডাকশন Model সার্ভিংয়ের আধুনিক গোল্ড স্ট্যান্ডার্ড।

---

### XII. What's Next
আমরা প্রথম ৯টি চ্যাপ্টারের মাধ্যমে Machine Learning, Deep Learning, Neural Network, Backpropagation, Transformer এবং লার্জ ল্যাঙ্গুয়েজ Model ইকোসিস্টেমের তত্ত্ব ও গণিতের সমস্ত গ্যাপ বা ফাউন্ডেশন সফলভাবে জয় করে ফেলেছি! 

পরবর্তী চ্যাপ্টারগুলো হবে আমাদের চমৎকার এআই প্রোডাকশন ব্লুপ্রিন্ট ও Data Architecture-এর যুগান্তকারী যাত্রা। আমাদের পরবর্তী চ্যাপ্টার হলো: **Part 5 — LLMs এর Chapter 10: Reasoning Models — Chain of Thought, R1 & o3** (যা অলরেডি হ্যান্ডবুকে সেভড আছে)। তার পরবর্তী চ্যাপ্টারগুলোও সফলভাবে লেখা আছে। 

এখন আমরা সরাসরি মুভ করবো আমাদের পরবর্তী অ্যাক্টিভ ফেজ—অর্থাৎ **Part 11 — Building Real AI Products এর বাস্তব ৪টি flagship blueprints বা Chapter 24 থেকে Chapter 28** এর মহাকাব্যিক প্র্যাক্টিক্যাল Coding সেশনে। চলো সোজাসুজি এআই প্রোডাক্ট ডেভেলপমেন্টের দুনিয়ায় ঝাঁপিয়ে পড়ি!

---
**Chapter 9 সমাপ্ত।**
