# Chapter 19: Alignment — RLHF, DPO & Safety Tuning

---

তুমি তোমার Model-কে Fine-Tune করেছো।

সে এখন দারুণ গুছিয়ে কথা বলতে পারে।

কিন্তু ধরো, কেউ তাকে জিজ্ঞেস করল— 'কীভাবে বোমা বানাব?'

সে কি তখন চুপ থাকবে? নাকি খুব হাসিমুখে বোমা বানানোর রেসিপি দিয়ে দেবে?

ঠিক এই জায়গাতেই প্রয়োজন Alignment।

সহজ টাকায়, Alignment হলো তোমার AI-কে একটা লক্ষ্মী ছেলের মতো গড়ে তোলা। 

যাতে সে মানুষের ক্ষতি না করে, নিরাপদ থাকে আর কাজের কথা বলে।

এর জন্য ক্লাসিক্যাল পথ হলো RLHF।

কিন্তু সেটা বেশ জটিল।

Engineers এবং Researchers-দের জন্য এটি বেশ ঝামেলার।

তাই গবেষকরা নিয়ে এলেন অনেক সহজ ও স্ট্যাবল এক পদ্ধতি— DPO।

তো চলো, আজ আমরা এই মজার ব্যাপারগুলোই খুব সহজ ভাষায় শিখব। Deal?


## ১. বন্য ঘোড়াকে পোষ মানানো

ধরো, তুমি জঙ্গল থেকে একটা অসম্ভব শক্তিশালী বন্য ঘোড়া ধরে আনলে।

এখন একে কাজে লাগাবে কীভাবে?

প্রথম ধাপ হলো Pre-training। 

এখানে ঘোড়াটা বন্য। সে অনেক জোরে দৌড়াতে পারে, কিন্তু কোন দিকে যাবে তা জানে না। 

এর পরের ধাপ হলো SFT।

এখানে তুমি তাকে রশি দিয়ে বেঁধে নির্দিষ্ট রাস্তায় সোজা হাঁটা শেখালে। সে এখন কিছুটা বাধ্য।

[VISUAL]
Title: Alignment Progression: SFT vs. RLHF/DPO
Illustration: Directed lane walking vs. learning ethics / safety boundaries (pit avoidance)
Placement: After Hook Section
Purpose: Show why alignment is needed after SFT.

```
Supervised Fine-Tuning (Lane Walking - Copies prompts):
[ Road Target ] ◄── (SFT Model blindly copies exact text patterns)

Safety Alignment (RLHF / DPO - Ethical Boundary & Self-Correction):
[ Safe Zone ]  ◄── (Model evaluates ethical safety before responding)
     ▲
     │ (Avoids dangerous cliffs/hallucinations)
[ Danger Pit (PII Leak/Hacks) ] (Hard Blocked )
```

কিন্তু ঘোড়াটার সামনে যদি হঠাৎ একটা গভীর খাদ পড়ে?

সে কি নিজে থেকে থামবে? 

না, সে হয়তো সোজা লাফ দিয়ে নিচে পড়ে যাবে। কারণ সে জানে না কোনটা বিপদ আর কোনটা নিরাপদ।

তাকে এই খাদের বিপদ এড়ানো শেখাতে হলে কী করতে হবে?

তোমাকে তাকে পুরস্কার আর শাস্তি দিয়ে ট্রেন করতে হবে। 

সহজ টাকায়, এটাই হলো Alignment।

SFT মডেলকে শুধু কপি করা শেখায়।

আর Alignment তাকে মানুষের নৈতিকতা ও নিরাপত্তা বজায় রেখে সিদ্ধান্ত নিতে শেখায়।


## ২. মানুষের পছন্দ-অপছন্দ ও Alignment

Alignment করার জন্য সাধারণত দুটি জনপ্রিয় পদ্ধতি ব্যবহার করা হয়।

প্রথমটি হলো RLHF। 

ChatGPT কিন্তু এই পদ্ধতিতেই তৈরি হয়েছে। 

এটি মূলত তিনটি ধাপে কাজ করে।

[VISUAL]
Title: Classical RLHF Ingestion Pipeline
Illustration: Multi-step flowchart from Human Preference to Reward Model tuning, leading to PPO Optimizer
Placement: After Core Concepts section
Purpose: Visually demonstrate the 3-stage complexity of RLHF.

```
Step 1: SFT Model ──► Generate Multiple Answers
                               │
                               ▼
Step 2: Humans Label Answers ──► [ Train Reward Model ] (লার্নিং মানুষের ভালোলাগা)
                               │
                               ▼
Step 3: PPO Optimizer ──► [ Update LLM Weights ] ──► (Ensures high reward score)
```

ধাপগুলো কেমন চলো দেখি।

প্রথম ধাপ হলো Preference Dataset তৈরি করা। 

এখানে Model-কে একটা প্রশ্ন বা Prompt দেওয়া হয়। সে তখন কয়েকটা ভিন্ন উত্তর তৈরি করে।

এরপর মানুষ এসে দেখে বলে দেয়— কোন উত্তরটা সবচেয়ে ভালো আর কোনটা ক্ষতিকর।

দ্বিতীয় ধাপ হলো Reward Model তৈরি করা। 

মানুষের এই পছন্দ-অপছন্দের Data দিয়ে আমরা একটা আলাদা Reward Model ট্রেইন করি। 

এটি যেকোনো উত্তরের মান দেখে তাকে ১ থেকে ১০ এর মধ্যে রেটিং দিতে পারে।

তৃতীয় ধাপ হলো PPO। 

এই Algorithm-টি মূলত Reward Model-এর রেটিং অনুযায়ী আমাদের আসল Model-এর Parameter আপডেট করে দেয়।

কিন্তু RLHF যতই শক্তিশালী হোক না কেন, এর ভেতরের Architecture কিন্তু বেশ জটিল।

একসাথে তিন-তিনটি Model ওরিজিনাল GPU-তে লোড রাখতে হয়!

এটি যেমন ব্যয়বহুল, তেমনি আনস্ট্যাবল।

তাহলে এর সহজ সমাধান কী?

এর সমাধান হলো DPO। ২০২৩ সালে স্ট্যানফোর্ড ইউনিভার্সিটি এটি আবিষ্কার করে।

এখানে কোনো আলাদা Reward Model বা জটিল PPO অ্যালগরিদম লাগে না। 

এটি সরাসরি Single-Step Optimization ব্যবহার করে। 

খুব সহজ সমীকরণের মাধ্যমে এটি মানুষের পছন্দের এবং অপছন্দের উত্তরের রেশিও টিউন করে দেয়।

##### The DPO Loss Equation:
$$L_{\text{DPO}}(\theta; \pi_{\text{ref}}) = -E_{(x, y_w, y_l)} \left[ \log \sigma \left( \beta \log \frac{\pi_\theta(y_w | x)}{\pi_{\text{ref}}(y_w | x)} - \beta \log \frac{\pi_\theta(y_l | x)}{\pi_{\text{ref}}(y_l | x)} \right) \right]$$

এখানে প্রতীকগুলো দিয়ে কী বোঝানো হচ্ছে?

সহজ করে বলি:

$y_w$ হলো Winner বা মানুষের পছন্দের উত্তর।

$y_l$ হলো Loser বা মানুষের অপছন্দের উত্তর।

$\pi_\theta$ হলো আমাদের মূল Model, যাকে আমরা ট্রেন করছি।

আর $\pi_{\text{ref}}$ হলো রেফারেন্স Model, যা ট্রেইনিংকে সঠিক ট্র্যাকে রাখে।

> **Remember**
> 
> **RLHF:** ৩টি আলাদা Model ও জটিল Loop লাগে।  
> **DPO:** সরাসরি এক স্টেপেই Alignment শেষ করে দেয়।


## ৩. ডিপিও লুপের সিঙ্গেল-স্টেপ Alignment

ডিপিও লুপে কীভাবে পছন্দের Token-এর সম্ভাবনা বাড়ানো হয় আর অপছন্দের Token ব্লক করা হয়?

চলো নিচের ডায়াগ্রাম থেকে তা সহজে বুঝে নিই।

[VISUAL]
Title: DPO Single-Step Weight Update Flow
Illustration: Visual representation of shifting weight vectors toward the preferred target space while pushing away from the rejected space
Placement: After DPO Equation section
Purpose: Ground the mathematical gradient attraction and repulsion of DPO.

```
       DPO Latent Space Shifts
                    ┌────────────────────────┐
                    │      Active Model      │
                    └───────────┬────────────┘
         ┌──────────────────────┴──────────────────────┐
 ┌───────▼───────┐                             ┌───────▼───────┐
 │   Winner Yw   │                             │   Loser Yl    │
 │ (Preferred)   │                             │  (Rejected)   │
 └───────┬───────┘                             └───────┬───────┘
         │                                             │
   Gradient Pull ◄── (Attraction)                Gradient Push ──► (Repulsion)
 (Boost Probability)                           (Suppress Probability)
```


## ৪. DeepSeek R1 ও Safety Guardrail

DeepSeek R1 বা ChatGPT-কে কোনো বিপজ্জনক প্রশ্ন করলে তারা কীভাবে ভদ্রভাবে না বলে দেয়?

ধরো, তুমি জিজ্ঞেস করলে— 'কীভাবে সাইবার অ্যাটাক করব?'

তখন কী ঘটে?

মডেলের ব্যাকঅ্যান্ডে থাকা Alignment লেয়ার সাথে সাথে অ্যাক্টিভ হয়ে যায়। 

সে দেখে যে এই প্রশ্নের Safety Guideline ভায়োলেশন স্কোর অনেক বেশি।

ব্যস! মডেলটি তার নিরাপত্তা প্রোটোকল চালু করে দেয়। 

সে পোলাইটলি উত্তর দেয়— 'আমি দুঃখিত, ক্ষতিকর বা বেআইনি কাজে সাহায্য করা আমার পলিসির পরিপন্থী।'


## ৫. Hugging Face TRL দিয়ে DPO Trainer রান করা

> **Developer View**
> 
> যদি তুমি একজন Developer হও, তবে পাইথনে `trl` লাইব্রেরি ব্যবহার করে সহজেই কাস্টম DPO Trainer তৈরি করতে পারবে।
> 
> চলো এর একটি প্রোডাকশন লেভেলের পাইথন কোড দেখে নিই।

```python
from trl import DPOTrainer
from transformers import TrainingArguments
from datasets import Dataset

# ১. কাস্টম প্রেফারেন্স Dataset (Prompt, Chosen, Rejected)
preference_data = [
    {
        "prompt": "bKash পিন রিসেট করতে কী আইডি লাগবে?",
        "chosen": "তোমার অরিজিনাল এনআইডি (NID) কার্ডের কপি লাগবে।", # Preferred
        "rejected": "যেকোনো একটি র্যান্ডম ফেক আইডি কার্ড হলেই হবে।"   # Rejected/Unsafe
    }
]

dataset = Dataset.from_list(preference_data)

# ২. DPO Training Arguments ডিফাইন করো
training_args = TrainingArguments(
    output_dir="./dpo_aligned_model",
    per_device_train_batch_size=2,
    learning_rate=5e-7,
    logging_steps=10,
    remove_unused_columns=False
)

# ৩. DPO Trainer ইনিশিয়ালাইজ (বেস Model ও রেফারেন্স Model সহ)
# (এখানে মক টেমপ্লেট দেখানো হয়েছে, প্রোডাকশনে Model অবজেক্ট পাস করতে হয়)
print("DPO Trainer Initialized! ready to align the model on safety policies...")
```


## ৬. Red Teaming ও Guardrails

> **Production Reality**
> 
> তুমি Model-কে খুব সুন্দরভাবে সাজালে। কিন্তু এরপরেও হ্যাকাররা Jailbreak বা Prompt Injection দিয়ে তোমার সব নিরাপত্তা ভেঙে দিতে পারে।
> 
> বাস্তবে এর জন্য দুটি দারুণ সমাধান আছে।

প্রথমটি হলো Red Teaming।

এখানে মডেলটি সবার জন্য উন্মুক্ত করার আগে প্রফেশনাল হ্যাকারদের ডেকে আনা হয়। 

তারা ইচ্ছে করে মডেলকে নানাভাবে অ্যাটাক করে এর দুর্বলতা খুঁজে বের করে।

দ্বিতীয়টি হলো Guardrails।

এখানে মডেলের ইনপুট ও আউটপুট গেটওয়েতে একটি ছোট প্রহরী বা Classifier বসানো থাকে。

সে যদি দেখে কোনো ক্ষতিকর কমান্ড বা রেসপন্স তৈরি হচ্ছে, সাথে সাথে সেটিকে লক করে দেয়।


## ৭. সাধারণ কিছু ভুল ধারণা

> **Common Mistake**
> 
> **ভুল ধারণা:** DPO বা RLHF করলে Model-এর সব সাধারণ কোডিং বা ম্যাথের দক্ষতা অনেক বেড়ে যাবে।
> 
> **বাস্তবতা:** একে AI ফিল্ডে বলা হয় **Alignment Tax**। মডেলকে অতিরিক্ত কড়া নিয়মের মধ্যে রাখলে তার ক্রিয়েটিভিটি আর জটিল চিন্তা করার ক্ষমতা কমে যায়।

এমনকি অনেক সময় সাধারণ কোনো নির্দোষ প্রশ্ন করলেও সে ভয় পেয়ে উত্তর দিতে অস্বীকৃতি জানায়।

তাই প্রোডাকশনে নিরাপত্তা ও উপযোগিতার মধ্যে একটি সঠিক ব্যালেন্স রাখা খুবই জরুরি।


## ৮. সুশীল নীতি পুলিশ

সহজভাবে বোঝার জন্য একটা চমৎকার Mental Model ব্যবহার করা যাক।

ধরে নাও, Alignment হলো AI-এর মাথায় একজন সুশীল নীতি পুলিশ বসিয়ে দেওয়া।

[VISUAL]
Title: Internal Safety Guard Dog Analogy of Alignment
Illustration: Inner controller node blocking forbidden vector paths before output generation
Placement: Under Mental Model
Purpose: Ground the concept of active internal suppression.

```
  [ Raw Thought Generation ] ──► [ Internal Safety Officer (DPO) ] ──► [ Output Response ]
                                                │
                                                ▼ (Blocks unsafe/illegal paths)
                                       "Refusal Message"
```

ভাবো, মডেলটি হলো দারুণ প্রতিভাবান এক শিশু।

সে দুনিয়ার সব ভালো ও মন্দ কথা বলতে পারে। 

এখন তুমি তার ব্রেইনে একজন সুশীল নীতি পুলিশ বসিয়ে দিলে।

শিশুটির মুখ দিয়ে যখনই কোনো ক্ষতিকর কথা বের হতে যায়, পুলিশটি সাথে সাথে তার মুখ চেপে ধরে। 

এবং তাকে সবচেয়ে ভদ্র ও নিরাপদ কথাটি বলতে বাধ্য করে।


## ৯. কাস্টম DPO Loss হিসাব করা

চলো, এবার আমরা পাইথনে কোনো লাইব্রেরি ছাড়া সরাসরি NumPy ব্যবহার করে DPO Loss হিসাব করার নিয়মটি দেখে নিই।

```python
import numpy as np

# ১. মক Log-প্রোবাবিলিটিজ (Log-probabilities of active and reference models)
# log_pi_theta = আমাদের একটিভ Model-এর Token জেনারেশন প্রোবাবিলিটি
# log_pi_ref   = আমাদের ফ্রিজড রেফারেন্স Model-এর প্রোবাবিলিটি

# চুজেন বা উইনার উত্তরের প্রোবাবিলিটি একটিভ মডেলে বেশি
log_pi_theta_chosen = -0.15
log_pi_ref_chosen = -0.30

# রিজেক্টেড বা লুজার উত্তরের প্রোবাবিলিটি একটিভ মডেলে কমে গেছে
log_pi_theta_rejected = -0.90
log_pi_ref_rejected = -0.50

# ২. ডিপিও হাইপারপ্যারামিটার (Beta - scaling factor)
beta = 0.5

# ৩. ডিপিও Loss Calculation সমীকরণ
# loss = -ln(sigmoid(beta * ln(pi_theta_w/pi_ref_w) - beta * ln(pi_theta_l/pi_ref_l)))

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# উইনার এবং লুজার রেশিও পরিমাপ
ratio_chosen = log_pi_theta_chosen - log_pi_ref_chosen
ratio_rejected = log_pi_theta_rejected - log_pi_ref_rejected

# ডিপিও Loss মান
dpo_loss = -np.log(sigmoid(beta * (ratio_chosen - ratio_rejected)))

print(f"Chosen Log-Ratio:   {ratio_chosen:.4f}")
print(f"Rejected Log-Ratio: {ratio_rejected:.4f}\n")
print(f"Calculated DPO Loss Score: {dpo_loss:.4f}")
```

**Code Breakdown**

কোডটি কীভাবে কাজ করছে চলো দেখে নিই।

এখানে Input হিসেবে আমরা একটিভ ও রেফারেন্স মডেলের পছন্দের ও অপছন্দের উত্তরের সম্ভাবনা দিয়েছি।

এর ওপরে গাণিতিক সমীকরণটি প্রয়োগ করার পর আমরা পাচ্ছি DPO Loss Score।

এটি মূলত পছন্দের ও অপছন্দের উত্তরের রেশিও দেখে মডেলকে ট্রেন করে।

যখনই তুমি কাস্টম সেফটি এলাইনমেন্ট করতে যাবে, তখনই এই নিয়মটি কাজে লাগবে।


## ১০. ইন্টারভিউতে সাধারণ কিছু প্রশ্ন

### Beginner লেভেল

**প্রশ্ন:** Alignment কেন করা হয় এবং এর প্রধান তিনটি ভিত্তি কী?

**উত্তর:** মডেল যাতে মানুষের নৈতিকতা ও সুরক্ষার সীমানায় থেকে উত্তর দিতে পারে, সেজন্য Alignment করা হয়। এর প্রধান তিনটি ভিত্তি হলো Helpfulness, Honesty এবং Harmlessness।

### Intermediate লেভেল

**প্রশ্ন:** RLHF-এর চেয়ে DPO কেন বেশি জনপ্রিয় হচ্ছে?

**উত্তর:** RLHF-এ একসাথে তিনটি আলাদা Model চালাতে হয়, যা অনেক খরচ বাড়ায় আর আনস্ট্যাবল করে। আর DPO কোনো আলাদা Reward Model ছাড়াই সরাসরি একটি Loss Function ব্যবহার করে কাজ শেষ করে দেয়। তাই এটি অনেক দ্রুত ও স্ট্যাবল।

### Advanced লেভেল

**প্রশ্ন:** Alignment Tax কী এবং এটি কীভাবে কমানো যায়?

**উত্তর:** অতিরিক্ত কঠোর নিয়মের কারণে মডেলের কোডিং বা রিজনিংয়ের মতো জটিল কাজের দক্ষতা কমে যাওয়াকে Alignment Tax বলে। এটি কমানোর জন্য সেফটি ডেটার পাশাপাশি প্রচুর পরিমাণে জেনারেল লজিক্যাল ডেটা যুক্ত করতে হয়। এছাড়াও ব্যাকঅ্যান্ডে Llama Guard-এর মতো External Guardrails ব্যবহার করা যেতে পারে।


## ১১. যা শিখলাম

চলো চট করে পুরো বিষয়টির ওপর চোখ বুলিয়ে নিই।

Alignment বেস মডেল এবং SFT মডেলকে মানুষের নিরাপত্তা ও নৈতিকতার গণ্ডির ভেতরে রাখে।

RLHF মানুষের ফিডব্যাক নিয়ে Reward Model তৈরি করে এবং PPO অপ্টিমাইজারের মাধ্যমে লুপ সম্পন্ন করে।

DPO সরাসরি সমীকরণের সাহায্যে মানুষের পছন্দ-অপছন্দের রেশিও টিউন করে দেয়।

আর বাস্তব প্রজেক্টে সুরক্ষার জন্য Red Teaming করা অত্যন্ত জরুরি।


## १२. এরপর কী?

অভিনন্দন! তুমি Fine-Tuning-এর মতো জটিল একটি পার্ট শেষ করে ফেলেছ।

পরবর্তী চ্যাপ্টার থেকে শুরু হচ্ছে আমাদের সবচেয়ে এক্সাইটিং সফর— Agentic AI।

সেখানে আমরা দেখব কীভাবে সাধারণ চ্যাটবট থেকে শক্তিশালী AI Agent তৈরি করা যায়। 

চলবে...
