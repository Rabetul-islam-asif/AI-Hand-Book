# Chapter 16: Parameter-Efficient Fine-Tuning (LoRA & QLoRA)

---

তুমি কি জানো ৭ বিলিয়ন Parameter-এর একটা Model ফুল Fine-Tuning করতে কমপক্ষে ৪টা A100 GPU লাগে? মানে প্রায় ১৬০ GB VRAM! বেশিরভাগ মানুষের পক্ষে এটা afford করা অসম্ভব। কিন্তু ধরো, তোমাকে যদি বলি তুমি তোমার নিজের RTX 3090/4090 কার্ডেই একই কাজ করতে পারবে? সেটাই করে দেখিয়েছে LoRA আর QLoRA।

সহজ কথায়— LoRA হলো Matrix Factorization-এর ম্যাজিক। বিলিয়ন Parameter ফ্রিজ করে রেখে পাশে দুটো ছোট্ট Matrix ট্রেইন করো, ব্যস! মেমরি প্রায় ৯৫% সেভ। আর QLoRA? সে আরেক ধাপ এগিয়ে— বেস Model-কে ৪-বিটে (NF4) কম্প্রেস করে কনজিউমার ল্যাপটপেই Fine-Tuning সম্ভব করে দেয়।

তো চলো দেখি কীভাবে PEFT, LoRA আর QLoRA-র Math কাজ করে, আর কীভাবে মিলিয়ন ডলারের ইনফ্রাস্ট্রাকচারকে তোমার পার্সোনাল ল্যাপটপে নামিয়ে আনা যায়। এটা শিখলে পরের চ্যাপ্টারের RLHF/DPO আর Agentic AI বুঝতে কোনো সমস্যাই হবে না।

---

### ১. Hook: পুরো দেওয়াল ভেঙে নতুন রঙ করা বনাম স্টিকার লাগানো

কল্পনা করো, তুমি তোমার ঘরের একটি বিশাল দেওয়ালের থিম বা ডিজাইন পরিবর্তন করতে চান।
* **Full Parameter Fine-Tuning:** তুমি পুরো দেওয়ালের কোটি কোটি Pixel প্লাস্টার ভেঙে নতুন করে বালি-সিমেন্ট ও কোটি টাকার পেইন্ট ব্যবহার করে নতুন ডিজাইন আঁকলেন। এটি খুব perfect, কিন্তু এতে তোমার বিপুল পরিমাণ সময় ও টাকা অপচয় হলো (High VRAM / Computing Cost)।

[VISUAL]
Title: Full-Parameter Tuning vs. LoRA Adapter Tuning
Illustration: Heavy weight matrix update versus frozen base weights alongside two small low-rank matrices
Placement: After Hook Section
Purpose: Show the mathematical memory saving of Low-Rank Adaptation.

```
Full-Parameter Tuning (Updates all 7 Billion weights):
[ Frozen Base Weights (W) ]  ◄── (Modifies and updates every single connection weight)

LoRA Adapter Tuning (Only updates A and B matrices - 99% Memory Saved!):
[ Frozen Base Weights (W) ]  ───► (No Changes / Fixed)
       ▲
       └─► [ Small Matrix A (d x r) ] ──*──► [ Small Matrix B (r x d) ] ──► (Updates only A & B)
```

* **LoRA (Adapter Tuning):** তুমি মূল দেওয়ালের প্লাস্টার বা কোটি টাকার রঙে একটুও হাত দিলে না (Base Weights Frozen)। তুমি কেবল দেওয়ালের ওপর পাতলা Custom স্টিকার বা রিলিজড ফ্রেম (Adapter) ঝুলিয়ে দিলে। এই ফ্রেমটি খুব সস্তা এবং প্রয়োজন শেষে সেকেন্ডে খুলে নেওয়া যায়।

লো-র‍্যাংক অ্যাডাপটেশন (LoRA) ঠিক এই কাজটিই করে। এটি এলএলএম Model-এর বিলিয়ন ওরিজিনাল Parameter সম্পূর্ণ ফ্রিজ বা লক করে রাখে এবং পাশে দুটি খুব ছোট লো-র‍্যাংক Matrix জোড়া লাগিয়ে কেবল সেগুলোর মান আপডেট করে, যা মেমরি কস্ট Drastically কমিয়ে দেয়।

---

### ২. Core Concepts: লো-র‍্যাংক অ্যাডাপটেশন ও Quantizationের জ্যামিতি

#### ক. LoRA-র Mathematical Intuition (Matrix Factorization)
আমরা জানি, Neural Network-এর ট্রেনিং প্রসেসে ওয়েটস Matrix-এর পরিবর্তনকে আমরা বলি $\Delta W$ (Delta W)। 

যদি একটি লিনিয়ার লেয়ারের ডাইমেনশন হয় $d \times d$ (যেমন: $4096 \times 4096 \approx 16.7$ Million Parameters)। ফুল Fine-Tuningয়ে আমাদের এই ১৬.৭ মিলিয়ন Parameter মেমোরিতে লোড করে Backpropagation রান করতে হতো।

LoRA বলে, এই বিশাল $\Delta W$ Matrix-এর ভেতরের আসল ইনফরমেশন বা র‍্যাংক (Rank $r$) খুব ছোট। তাই আমরা $\Delta W$-কে দুটি ছোট Matrix $A$ এবং $B$ এর product হিসেবে রিপ্রেজেন্ট করতে পারি:
$$\Delta W = B \times A$$
যেখানে:
* $A$ এর ডাইমেনশন $d \times r$
* $B$ এর ডাইমেনশন $r \times d$
* র‍্যাংক $r$ যদি আমরা ৪ বা ৮ সেট করি (যেমন: $4096 \times 8 \times 2 = 65,536$ Parameters)।

[VISUAL]
Title: Mathematical Dimension Reduction of LoRA
Illustration: Visual representation of a large 4096x4096 matrix being computed as a product of 4096x8 and 8x4096 matrices
Placement: Under Math Intuition section
Purpose: Visually demonstrate the parameters reduction from 16M to 65K.

```
Original Weight Update Matrix (ΔW):       LoRA Matrix Factorization (B x A):
       ┌──────────────┐                             ┌───┐
       │              │                             │   │
       │  4096 x 4096 │              =              │ B │ (4096 x 8)
       │              │                             │   │
       └──────────────┘                             └───┘
                                                      *
                                                    ┌───────────────┐
                                                    │  A (8 x 4096) │
                                                    └───────────────┘
  (Total: 16.7 Million Weights)               (Total: Only 65,536 Weights!)
```

* **Parameter সেভিং:** ১৬.৭ মিলিয়ন Parameter-এর জায়গায় আমাদের ট্রেইন করতে হচ্ছে মাত্র ৬৫ হাজার Parameter! এটি প্রায় **৯৯.৬% Parameter save** করে।

#### খ. QLoRA (Quantized LoRA - ৪-বিট ম্যাজিক)
LoRA মেমরি কমায়, কিন্তু ওরিজিনাল ৭ বিলিয়ন ওজনের বেস মডেলটি তো GPU ভিরাম-এ লোড করতেই হবে। ওটি লোড করতেই ১৬ জিবি ভিরাম শেষ হয়ে যায়। এর সমাধান দেয় **QLoRA**।
* **NF4 (NormalFloat 4):** এটি একটি বিশেষায়িত ৪-বিট Data টাইপ। QLoRA বেস Model-এর ওরিজিনাল ১৬-বিট (FP16) ওজনকে কম্প্রেস করে মাত্র ৪-বিটে convert করে। এর ফলে ৭ বিলিয়ন Model-এর সাইজ ১৪ জিবি থেকে কমে মাত্র ৫ জিবি-তে নেমে আসে।
* **Double Quantization:** এটি Quantizationের Scaling Parameter গুলোকেও পুনরায় কোয়ান্টাইজ করে আরও মেমরি সেভ করে।
* **Paged Optimizers:** GPU Memory যদি কখনো স্পাইক করে ওভারফ্লো হয়, এটি ওওএম (OOM) Error না দিয়ে অতিরিক্ত মেমরি টেম্পোরারিলি Computeারের নরমাল র‌্যাম (CPU RAM)-এ পাঠিয়ে Training alive রাখে।

🧠 Remember

**LoRA** = বেস Model ফ্রিজ রেখে দুটি ছোট Matrix (A ও B) ট্রেইন করে মেমরি save করে।  
**QLoRA** = বেস মডেলকে ৪-বিটে (NF4) কম্প্রেস করে এবং ওপরে LoRA Adapter জোড়া লাগিয়ে সর্বকালের সর্বোচ্চ মেমরি save করে।

---

### ৩. Real World Example: Cursor ও Coding Model-এর Dynamic Persona

Cursor বা যেকোনো Custom Coding Assistant যখন ব্যাকঅ্যান্ডে কাজ করে:

1. **Frozen Foundation:** তাদের মেইন লার্জ Coding Model-এর বেস ওয়েটস (Base Weights) সার্ভারে লক থাকে।
2. **Dynamic Adapters Loading:** তুমি যখন পাইথন Project ওপেন করো, তারা পাইথনের Custom LoRA Adapterটি মিলি-সেকেন্ডে লোড করে বেস Model-এর সাথে মার্জ করে দেয়। আবার যখন তুমি জাভাস্ক্রিপ্ট Project ওপেন করো, ওরিজিনাল Model-এর কোনো পরিবর্তন না করেই পাইথন Adapter আনলোড করে জাভাস্ক্রিপ্ট Adapter জোড়া লাগিয়ে দেয়। এটি একই GPU Clusterে মাল্টি-ইউজার মাল্টি-Language সাপোর্ট দেওয়ার সবচেয়ে রেভোলিউশনারি Practical পদ্ধতি।

---

### ৪. Developer Perspective: Hugging Face PEFT & LoraConfig Code

💻 Developer View

Developer হিসেবে পাইথনে `peft` Library ব্যবহার করে Custom LoRA Configuration ডিফাইন করার রিয়েল ও গোল্ড Standard প্রোডাকশন Code:

```python
from peft import LoraConfig, get_peft_model
import torch.nn as nn

# ১. বেস Neural Network লিনিয়ার লেয়ার (মক ওরিজিনাল Model)
class ToyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.q_proj = nn.Linear(4096, 4096)
        
    def forward(self, x):
        return self.q_proj(x)

base_model = ToyModel()

# ২. LoRA Config সেটআপ
peft_config = LoraConfig(
    r=8,                  # লো-র‍্যাংক বটলনেক ডাইমেনশন (Rank)
    lora_alpha=32,        # Scaling ফ্যাক্টর (Higher = Stronger Adapter weight)
    target_modules=["q_proj"], # কোন কোন লেয়ারে অ্যাডাপ্টার জোড়া দেব
    lora_dropout=0.05,    # ওভারফিটিং রোধে ড্রপআউট
    bias="none",
    task_type="CAUSAL_LM"
)

# ৩. বেস মডেলকে LoRA মডেলে রূপান্তর করো
lora_model = get_peft_model(base_model, peft_config)

# ৪. ট্রেইনেবল Parameter রেশিও চেক করো
lora_model.print_trainable_parameters()
# Output: trainable params: 65,536 || all params: 16,842,752 || trainable%: 0.389%
```

---

### ৫. Production Perspective: Adapter Merging & Inference Speed

🏭 Production Reality

Inference চালানোর সময় প্রোডাকশনে LoRA Adapter ডাইরেক্ট রান করলে GPU-তে Latency বেড়ে যায়। কারণ সিগন্যালকে বেস Model এবং Adapter Matrix দুটির ভেতর দিয়ে আলাদা আলাদাভাবে ক্যালকুলেট হতে হয়।

* **The Production Optimization (Weight Merging):** 
  Training শেষ হওয়ার পর প্রোডাকশন Deploymentের আগে আমরা Adapter ওয়েটসকে সরাসরি বেস Model-এর সাথে Math-এরভাবে যোগ করে মার্জ করে দিই:
  $$W_{\text{final}} = W_{\text{base}} + (B \times A)$$
* পাইটর্চে আমরা জাস্ট `model.merge_and_unload()` কল করি। এর ফলে Adapterের অতিরিক্ত Computational ওভারহেড জিরো হয়ে যায় এবং Inference স্পিড হুবহু ওরিজিনাল Model-এর মতো আল্ট্রা-ফাস্ট রান করে।

---

### ৬. Common Mistakes

🔴 Common Mistake

**ভুল ধারণা:** LoRA-র র‍্যাংক ($r$) যত বড় সেট করা যাবে (যেমন: ১২৮ বা ২৫৬), Model তত বেশি perfectly শিখবে।

**বাস্তবতা:** র‍্যাংক অতিরিক্ত বড় সেট করলে মেমরি ও Compute কস্ট Drastically বেড়ে যায় এবং সবচেয়ে বিপজ্জনকভাবে Model নতুন ডেটাসেটে Overfit (Overfit) করে ফেলে। AI পেপারগুলোর বেঞ্চমার্ক দেখিয়েছে, $r=8$ বা $r=16$ হলো সুইট স্পট, যা সবচেয়ে স্ট্যাবল Generalization দেয়।

---

### ৭. Mental Model: সাউন্ড ট্র্যাক টিউনিং

LoRA-র Matrix ফ্যাক্টরাইজেশনের মেন্টাল Model:

**"LoRA = বিশাল অর্কেস্ট্রার সুরের সাথে পাশে বসে বাঁশি বাজানো"**

[VISUAL]
Title: Orchestra vs. Solo Flute analogy of LoRA tuning
Illustration: Visual representation of a huge orchestra block alongside a tiny flute player syncing notes
Placement: After Mental Model section
Purpose: Ground the mathematical intuition of frozen base weights vs. tiny parameter tuning.

```
  [ Massive Orchestra: 7 Billion Players ]  ──► (Sound output locked / Frozen)
                      ▲
                      │ (Perfect Sync)
  [ Solo Flute Player: A & B Matrices ] ──────► (Only tunes their small flute)
```

ভাবো তোমার সামনে একটি বিশাল অর্কেস্ট্রা দল দাঁড়িয়ে গান গাচ্ছে (Base Weights Frozen)। তুমি তাদের মূল সুরের কোনো পরিবর্তন করতে পারবে না। কিন্তু তুমি চাচ্ছেন ব্যাকগ্রাউন্ডে একটু মিষ্টি বাঁশির টিউন যোগ করতে। এর জন্য অর্কেস্ট্রা ভেঙে নতুন প্লেয়ার আনার দরকার নেই। তুমি তাদের পাশে স্রেফ একজন ছোট বাঁশি বাদক (LoRA Adapter) দাঁড় করিয়ে দিলে, যে অর্কেস্ট্রার মূল তালের সাথে সুর মিলিয়ে Dynamically মিষ্টি সুর যোগ করে দিল।

---

### ৮. Mini Project: পাইথনে স্ক্র্যাচ থেকে LoRA Matrix ফ্যাক্টরাইজেশন ইমুলেটর

চলো পাইথনে Custom NumPy ব্যবহার করে কোনো এমএল ফ্রেমওয়ার্ক ছাড়া একটি বিশাল ১৬.৭ মিলিয়ন Parameter আপডেটকে মাত্র ৬৫ হাজার Parameter-এর দুটি লো-র‍্যাংক Matrix-এর ডট প্রোডাক্টে convert করে মেমরি ও স্টোরেজ সেভিং এনালাইসিস সম্পন্ন করি।

```python
import numpy as np

# ১. ডাইমেনশন ডিফাইন করো (d = 4096, rank = 8)
d = 4096
r = 8

# ২. মক ওরিজিনাল আপডেট ম্যাট্রিক্স ডেল্টা ডব্লিউ (ΔW) - 4096 x 4096
# স্টোরেজ কস্ট: 4096 * 4096 * 4 bytes (FP32) = 67.1 MB
delta_W = np.random.randn(d, d)

# ৩. LoRA ম্যাট্রিক্স A এবং B ইনিশিয়ালাইজ করো
# A: 8 x 4096, B: 4096 x 8
# স্টোরেজ কস্ট: (4096 * 8 * 2) * 4 bytes = 262 KB!
A = np.random.randn(r, d)
B = np.random.randn(d, r)

# ৪. LoRA ডট প্রোডাক্ট আপডেট সিমুলেশন
lora_update = np.dot(B, A)

# ৫. Parameter ও মেমরি সেভিং Calculation
original_params = d * d
lora_params = (d * r) + (r * d)
saving_ratio = (1 - (lora_params / original_params)) * 100

print(f"Original Weight Parameters: {original_params:,}")
print(f"LoRA Adapter Parameters:    {lora_params:,}")
print(f"Parameter সাশ্রয়:          {saving_ratio:.4f}% (Ultra Saving ✓)")
```

#### Code Breakdown:
* **Input:** ডাইমেনশন $4096$ এবং র‍্যাংক $8$।
* **Output:** ওরিজিনাল বনাম LoRA Parameter কাউন্ট এবং ওরিজিনাল Parameter-এর ওপরে $৯৯.৬১\%$ Computational save রেশিও।
* **Why it works:** লিনিয়ার অ্যালজেব্রার লো-র‍্যাংক প্রজেকশনের কারণে মাত্র ৬৫ হাজার ওজনের Matrix হিউজ ১৬.৭ মিলিয়ন ওজনের ডাইমেনশনাল স্পেস কভার করেছে।
* **When to use:** ব্যাকঅ্যান্ডে Custom PEFT অপ্টিমাইজেশন Loop ও মেমরি ম্যাপিং এনালাইসিস করার জন্য।

---

### ৯. Interview Questions

#### Beginner
1. **প্রশ্ন:** ফুল-Parameter Fine-Tuning-এর তুলনায় LoRA ব্যবহার করার প্রধান দুটি সুবিধা কী কী?
   * **উত্তর:** প্রথমত, LoRA Model-এর ৯৯% Parameter ফ্রিজ রেখে শুধুমাত্র লো-র‍্যাংক Adapter ট্রেইন করে GPU VRAM ডিমান্ড ও Training কস্ট প্রায় ৯০% কমিয়ে দেয়। দ্বিতীয়ত, Training শেষে Adapter File সাইজ খুব ছোট হয় (কয়েক মেগাবাইট), যা সহজে Deploy ও শেয়ার করা যায়।

#### Intermediate
2. **প্রশ্ন:** QLoRA কীভাবে ওরিজিনাল জিপিটি মডেলকে ৪-বিটে কম্প্রেস করার পরেও Fine-Tuning-এর এক্যুরেসি ধরে রাখে?
   * **উত্তর:** QLoRA একটি বিশেষায়িত ৪-বিট Data টাইপ **NormalFloat 4 (NF4)** ব্যবহার করে যা AI Model-এর ওয়েট Distribution Math-এরভাবে পরিমাপ করে নরমাল Distributionে ইনফরমেশন Loss লক করে কোয়ান্টাইজ করে। এর সাথে ডাবল Quantization যোগ করে সে Embeddings মেমরি কস্ট Drastically কমিয়েও এক্যুরেসি FP16-এর সমান ধরে রাখে।

#### Advanced
3. **প্রশ্ন:** কেন প্রোডাকশন Deploymentের সময় LoRA মডেলকে ডাইরেক্ট সার্ভিস না করে `merge_and_unload()` করা আবশ্যক?
   * **উত্তর:** ডাইরেক্ট সার্ভ করলে Inference-এর সময় Input সিগন্যালকে বেস Model এবং লোর‍্যাংক Adapter উভয় Matrix-এর ভেতর দিয়ে Parallelি রান করতে হয়, যা Computational ওভারহেড ও Latency বাড়িয়ে দেয়। `merge_and_unload()` Adapterের ওজনকে ডিরেক্ট লিনিয়ার অ্যালজেব্রা sum হিসেবে বেস Model-এর সাথে ব্লেন্ড করে দেয়, ফলে অতিরিক্ত মেমরি ওভারহেড জিরো হয় এবং Model হুবহু ওরিজিনাল স্পিডে রান করে।

---

### ১০. Chapter Summary
* **PEFT** এবং **LoRA** Model Training খরচ ও GPU ভির‍্যাম স্পাইক কমানোর প্রধান Mechanism।
* **Matrix Factorization** ($B \times A$) লার্জ ডেল্টা আপডেটকে ৬৫ হাজার মিনি Parameterে সংকুচিত করে।
* **QLoRA** ৪-বিট NF4 Quantizationের সাহায্যে মাত্র ১৬ জিবি VRAM কার্ডে বিলিয়ন স্কেলের Model ফাইন-টিউন করতে পারে।
* প্রোডাকশন লেভেলে আল্ট্রা-ফাস্ট স্পিড নিশ্চিত করতে **Inference Adapter Merging** করা জরুরি।

---

### ১১. What's Next
দারুণ! আমরা ভালোভাবে Fine-Tuning-এর সবচেয়ে গুরুত্বপূর্ণ GPU অপ্টিমাইজেশন ও লো-র‍্যাংক অ্যাডাপ্টেশন Mechanism শেষ করে ফেলেছি। পরের chapter-এ আমরা এই ট্রেইনড মডেলগুলোকে মানুষের নৈতিকতা ও সেফটি রুলস শেখানোর ফাইনাল সোপান নিয়ে আলোচনা করব: **Chapter 17: Alignment — RLHF, DPO & Safety Tuning**। Reinforcement Learning (RLHF) এবং ডিরেক্ট প্রেফারেন্স অপ্টিমাইজেশন (DPO) কীভাবে AI-কে মিথ্যা ও ক্ষতিকর কথা বলা থেকে বিরত রাখে, তা আমরা বিস্তারিত শিখব।

---
**Chapter 16 শেষ।**
