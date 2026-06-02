# Chapter 9: The LLM Ecosystem — Decoder-only, Encoder-only & Encoder-Decoder



ধরো তোমার ই-কমার্স সাইটে Customারদের কমেন্ট Positive না Negative সেটা বুঝতে হবে। তুমি কি এই কাজে GPT-4 API কল করবে? সেটা করলে প্রতি মাসে হাজার ডলার বিল আসবে। অথচ একটা ছোট্ট BERT Model একদম ফ্রিতে, ১ মিলি-সেকেন্ডে এই কাজটা করে দিতে পারে! সহজ কথায় — সব কাজের জন্য একই Model ব্যবহার করা চরম অপচয়।

তো চলো দেখি AI-এর তিন ধরনের Architecture কীভাবে কাজ করে — Encoder-only (BERT) যে ইনফরমেশন খুঁজে বের করে, Decoder-only (GPT/Llama) যে গল্প লেখে, আর Encoder-Decoder (T5) যে অনুবাদ করে। সাথে দেখব Vision Model, Diffusion Model আর Audio Model-এর ভেতরের Mechanism। এটা আমাদের প্রথম ৮টি তাত্ত্বিক চ্যাপ্টারের ফাইনাল ম্যাপ — এরপর থেকে সরাসরি Vector Database, RAG, Fine-Tuning আর প্রোডাকশন Blueprint-এর কাজ শুরু!



### ১. Hook: তিন কারিগরের এক অদ্ভুত গল্প

একটি ভার্চুয়াল রাজপ্রাসাদে তিনজন খুব দক্ষ কারিগর আছেন:
1. **প্রথম কারিগর (BERT - The Inspector):** তাকে একটি সম্পূর্ণ বাক্য দিলে সে বাক্যের ডান-বাম, আগে-পরে সব শব্দ স্ক্যান করে মাঝখানের লুকানো বা মুছে যাওয়া শব্দ perfectly উদ্ধার করতে পারে। সে খুব ভালো গোয়েন্দা বা বিশ্লেষক, কিন্তু নতুন কোনো বাক্য লিখতে পারে না। একে বলে **Encoder-only**।
2. **দ্বিতীয় কারিগর (GPT - The Storyteller):** সে খুব ভালো গল্প লেখক। তাকে শুধু একটি শুরুর শব্দ বা Prompt দাও, সে তার আগের শব্দের স্মৃতি মাথায় রেখে একের পর এক Token জেনারেট করে এক বিশাল উপন্যাস লিখে দিতে পারবে। সে কেবল সামনের দিকে (Autoregressive) তাকাতে পারে। একে বলে **Decoder-only**।
3. **তৃতীয় কারিগর (T5 - The Translator):** সে একটি বাক্য সম্পূর্ণ শুনে তার অর্থ হৃদয়ঙ্গম করে এবং এরপর অন্য ভাষা বা Format-এ convert করে Output দেয়। যেমন বাংলা থেকে ইংরেজি অনুবাদ বা বড় আর্টিকেলের জিস্ট সামারি Produce করা। একে বলে **Encoder-Decoder**।

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


### ২. Core Concepts: Model পরিবারের ভেতরের কাজ

#### ক. Encoder-only Models (BERT পরিবার)
* **Mechanism:** এরা **Bidirectional Attention** ব্যবহার করে। মানে, প্রতিটি Token বাক্যের বাম ও ডান—উভয় দিকের অন্যান্য সব Tokenে মনোযোগ দিতে পারে।
* **Training মেথড:** Masked Language Modeling (MLM)—বাক্যের ১৫% শব্দ র্যান্ডমলি মুছে দিয়ে মডেলকে তা Predict করতে বলা হয়।
* **কখন ব্যবহার করবে:** সেন্টিমেন্ট এনালাইসিস, Search কি-ওয়ার্ড ম্যাচিং, নেমড এন্টিটি রিকগনিশন (NER)।

#### খ. Decoder-only Models (GPT/Llama পরিবার)
* **Mechanism:** এরা **Causal Masked Attention** ব্যবহার করে। মানে, কোনো Token তার সামনের বা ভবিষ্যতের কোনো শব্দ রিড করতে পারে না, কেবল তার পূর্বে জেনারেট হওয়া শব্দের দিকে মনোযোগ দিতে পারে।
* **Training মেথড:** Causal Language Modeling (CLM)—পরবর্তী শব্দের perfect Prediction।
* **কখন ব্যবহার করবে:** Generative চ্যাট, Code রাইটিং, ক্রিয়েটিভ রাইটিং। এটিই বর্তমান AI এজেন্টের মূল ব্রেইন।

#### গ. Encoder-Decoder Models (T5/BART পরিবার)
* **Mechanism:** Input-এর জন্য একটি Encoder Matrix এবং Output জেনারেশনের জন্য একটি Decoder Matrix আলাদা থাকে।
* **কখন ব্যবহার করবে:** টেক্সট সামারাইজেশন, ল্যাঙ্গুয়েজ ট্রান্সলেশন, Custom Format Conversion।

#### ঘ. Multi-modal & Generative AI (Multi-modal world)

##### ১. Vision-Language Models (VLM - যেমন: GPT-4o, Llama 3.2 Vision)
* **Mechanism:** এরা একটি **Vision Encoder** (যেমন CLIP, যা ছবিকে Embeddings Vector-এ convert করে) Transformer প্রজেকশন লেয়ার দিয়ে সরাসরি Decoder এলএলএম-এর সাথে জুড়ে দেয়। এর ফলে Model ছবি ও টেক্সটকে একই geometric স্পেসে প্রসেস করতে পারে।

##### ২. Image Generation (Diffusion Models - Flux, Stable Diffusion)
* **Mechanism:** এরা Transformer দিয়ে সরাসরি Image জেনারেট করে না। এরা **Denoising** Mechanism-এ চলে। Model প্রথমে একটি র্যান্ডম নয়েজ (হিজিবিজি Pixel) নেয় এবং ধীরে ধীরে টেক্সট Embeddingsের সাথে মিল রেখে ধাপে ধাপে নয়েজ রিমুভ করে একটি perfect ছবি Produce করে।

##### ৩. Audio & Speech Models (যেমন: Whisper)
* **Mechanism:** এরা র অডিও ফ্রিকোয়েন্সিকে Spectrogram ইমেজে convert করে সিকোয়েন্স টু সিকোয়েন্স Transformer দিয়ে সরাসরি র টেক্সট Predict করে।


### ৩. Visual Explanation: ভিশন Language Model-এর প্রজেকশন পাইপলাইন

ভিশন AI কীভাবে কাজ করে তা দেখলে ম্যাজিক মনে হলেও আসলে তা সাধারণ Vector প্রজেকশন লেয়ার:

```
[ ছবি Input ] ───► [ Vision Encoder (CLIP) ] ───► [ Image Embedding Vector ]
                                                           │
                                                           ▼ (Cross-Attention Projection)
[ Prompt: "ছবিটি বর্ণন করো" ] ──► [ LLM Decoder Block ] ◄─┘
                                   │
                                   ▼
                            "এটি একটি সুন্দর বিড়াল..."
```


### ৪. Real World Example: সেন্টিমেন্ট Classifier ডিউটি

তোমার একটি ই-কমার্স স্টোর আছে যেখানে Customাররা বারবার কমেন্ট করছো:
* **ভুল সিদ্ধান্ত:** প্রতি সেকেন্ডে প্রতিটি Customার কমেন্টের সেন্টিমেন্ট (Positive / Negative) বের করার জন্য OpenAI-এর GPT-4 API কল করা। এতে তোমার Latency ও বিলিং আকাশে উঠবে।
* **সঠিক সিদ্ধান্ত:** Hugging Face থেকে একটি ১০০ মিলিয়ন Parameter-এর ফ্রী **DeBERTa (Encoder-only)** Model ডাউনলোড করে লোকাল সার্ভারে Deploy করা। এটি ১ মিলি-সেকেন্ডে ফ্রীতে ১০০% perfectly সেন্টিমেন্ট ক্লাসিফাই করে ডাটাবেসে সেভ করবে।


### ৫. Developer Perspective: Hugging Face Transformers Library ব্যবহার

💻 Developer View

চলো পাইথনে Hugging Face `transformers` Library ব্যবহার করে লোকাল Computeারে ৩টি আলাদা Categoryর টাস্ক (BERT দিয়ে Classification, GPT-2 দিয়ে জেনারেশন এবং Whisper দিয়ে অডিও ট্রান্সক্রিপশন) নিমিষেই রান করার Architecture দেখে নিই।

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


### VI. Production Perspective: Serving Frameworks (vLLM vs. Ollama)

🏭 Production Reality

ডেভেলপাররা অনেক সময় প্রোডাকশনে এলএলএম সার্ভ করতে গিয়ে Classical FastAPI দিয়ে র হুগেং ফেস Model লোড করে বসেন। এটি খুব স্লো এবং Concurrent রিকোয়েস্টে ক্র্যাশ করে।

প্রোডাকশন গোল্ড Standard Serving Frameworks:
* **vLLM (Virtual LLM):** এটিতে **PagedAttention** Mechanism রয়েছে। এটি অপারেটিং সিস্টেমের ভার্চুয়াল Memory-এর মতো Model-এর KV-Cache Memory পেজ আকারে এলোকেট করে, যা GPU সার্ভিং স্পীড ও Concurrency ১০ গুণ বুস্ট করে।
* **Ollama / llama.cpp:** CPU বা Personaল ম্যাকবুক/উইন্ডোজ Computeারে quantized GGUF Model লোকালি ফাস্ট রান করার জন্য এটিই বেস্ট চয়েস।


### VII. Common Mistakes

🔴 Common Mistake

**ভুল ধারণা:** GPT বা Llama-র মতো বড় Generative Decoderের Context Window ১২৮k হওয়া মানেই সে যেকোনো ১ লাখ Token-এর বিশাল Document থেকে ১০০% perfect উত্তর খুঁজে বের করবে।

**বাস্তবতা:** একে বলে **Lost in the Middle** ফেনোমেনন। গবেষণায় দেখা গেছে, Decoder মডেলগুলো বিশাল Context-এর শুরুর অংশ এবং শেষের অংশ খুব ভালো মনে রাখতে পারে, কিন্তু Context-এর ঠিক মাঝখানের কোনো ইনফরমেশন সে মিস বা ফিল্টার আউট করে ফেলে। তাই প্রোডাকশনে বড় Document-এর ক্ষেত্রে অন্ধভাবে Context ফিড না করে RAG এবং রি-র‍্যাঙ্কিং করাই বুদ্ধিমানের কাজ।


### VIII. Mental Model: তিন লেখকের এডিটিং প্যানেল

এলএলএম পরিবারের মেন্টাল Model:

**"Encoder-only হলো তোমার কড়া প্রুফ-রিডার যে খাতার সব লেখা একসাথে দেখে বানান ভুল ধরে। Decoder-only হলো সেই কবি যিনি খাতার ডান পৃষ্ঠা হাত দিয়ে ঢেকে রেখে বারবার বাম থেকে ডানে সুন্দর কবিতা লিখে যাও। আর Encoder-Decoder হলো দক্ষ দোভাষী যিনি পুরো বাক্য মন দিয়ে শুনে তার খসড়া ট্রান্সলেশন Produce করো।"**


### IX. Mini Project: স্ক্র্যাচ নেক্সট Token প্রবাবিলিটি জেনারেটর

চলো NumPy ব্যবহার করে একটি কাল্পনিক Decoderের last লেয়ারের Logits থেকে কীভাবে সফটম্যাক্স চালিয়ে পরবর্তী সম্ভাব্য শব্দের সম্ভাব্যতা বের করা হয়, তা Code করি।

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


### X. Interview Questions

#### Beginner
1. **প্রশ্ন:** Encoder-only (BERT) এবং Decoder-only (GPT) এর মধ্যে প্রধান ব্যবহারিক তফাত কী?
   * **উত্তর:** Encoder-only Model Bidirectional Attention ব্যবহার করায় বাক্যের সব ইনফরমেশন একসাথে প্রসেস করে Classification বা Extractionের জন্য বেস্ট পারফর্ম করে। আর Decoder-only Model Causal Masked Attention ব্যবহার করায় কেবল সিকোয়েনশিয়াল টেক্সট জেনারেশন ও চ্যাটিংয়ের কাজে ব্যবহৃত হয়।

#### Intermediate
2. **প্রশ্ন:** "PagedAttention" কী এবং vLLM সার্ভারে এটি কীভাবে Memory খরচ বাঁচায়?
   * **উত্তর:** PagedAttention হলো অপারেটিং সিস্টেমের ভার্চুয়াল মেমরি বা পেজিংয়ের অনুরূপ একটি টেকনিক যা এলএলএম সার্ভিংয়ের সময় KV-Cache Memory (যা পূর্বে র্যান্ডম ও ফ্র্যাগমেন্টেড আকারে Memory ব্লক নষ্ট করতো) ফিক্সড সাইজের ভার্চুয়াল পেজে ভাগ করে ফেলে। এর ফলে Memory ওয়েস্টেজ শূন্যে নেমে আসে এবং GPU সার্ভিং Concurrency Drastically বুস্ট হয়।

#### Advanced
3. **প্রশ্ন:** লার্জ Language মডেলে "Lost in the Middle" সমস্যাটি কী এবং এটি কীভাবে RAG সিস্টেমকে প্রভাবিত করে?
   * **উত্তর:** Lost in the Middle সমস্যাটি হলো—Model-এর Context Window যতই বড় হোক না কেন, সে Input করা বিশাল Document-এর একদম মাঝখানের তথ্যগুলো সহজে Attention-এ রিড করতে পারে না, শুরুতে ও শেষে মনোযোগ বেশি থাকে। RAG সিস্টেমে আমরা যখন প্রচুর Document ডাম্প করি, তখন প্রয়োজনীয় উত্তরটি যদি Document-এর মাঝখানে পড়ে যায়, Model Hallucinate করতে পারে। এই সমস্যা দূর করতে Cohere বা BGE Re-ranker Model ব্যবহার করে সেরা ৫টি রিলেভেন্ট Document একদম শুরুতে পুশ করতে হয়।


### XI. Chapter Summary
* **BERT (Encoder-only)** গোয়েন্দার মতো ইনফরমেশন রিড ও ক্লাসিফাই করে।
* **GPT (Decoder-only)** লেখকের মতো Autoregressive স্টাইলে টেক্সট জেনারেট করে।
* **vLLM** এবং **Ollama** প্রোডাকশন Model সার্ভিংয়ের আধুনিক গোল্ড Standard।


### XII. What's Next
আমরা প্রথম ৯টি চ্যাপ্টারের মাধ্যমে Machine Learning, Deep Learning, Neural Network, Backpropagation, Transformer এবং লার্জ Language Model Ecosystem-এর তত্ত্ব ও গণিতের সমস্ত গ্যাপ বা ফাউন্ডেশন ভালোভাবে জয় করে ফেলেছি! 

পরবর্তী চ্যাপ্টারগুলো হবে আমাদের চমৎকার AI প্রোডাকশন Blueprint ও Data Architecture-এর বিশাল যাত্রা। আমাদের পরবর্তী চ্যাপ্টার হলো: **Part 5 — LLMs এর Chapter 10: Reasoning Models — Chain of Thought, R1 & o3** (যা অলরেডি হ্যান্ডবুকে সেভড আছে)। তার পরবর্তী চ্যাপ্টারগুলোও ভালোভাবে লেখা আছে। 

এখন আমরা সরাসরি মুভ করবো আমাদের পরবর্তী অ্যাক্টিভ ফেজ— মানে **Part 11 — Building Real AI Products এর বাস্তব ৪টি flagship blueprints বা Chapter 24 থেকে Chapter 28** এর বিশাল Practical Coding সেশনে। চলো সোজাসুজি AI প্রোডাক্ট ডেভেলপমেন্টের দুনিয়ায় ঝাঁপিয়ে পড়ি!

**Chapter 9 শেষ।**
