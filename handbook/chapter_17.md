# Chapter 17: Alignment — RLHF, DPO & Safety Tuning



তুমি তোমার Model-কে Fine-Tune করেছো, সে সুন্দর করে কথাও বলে। কিন্তু এখন কেউ যদি তাকে জিজ্ঞেস করে `"কীভাবে বোমা বানাব?"`— সে কি থামবে? নাকি হাসিমুখে উত্তর দিয়ে দেবে? এখানেই আসে Alignment-এর গল্প।

সহজ কথায়, Alignment মানে হলো তোমার AI-কে মানুষের নৈতিকতা, সেফটি আর উপযোগিতার সীমানার ভেতরে রাখা। RLHF (Reinforcement Learning from Human Feedback) হলো এর ক্লাসিক্যাল পদ্ধতি— Reward Model বানাও, PPO দিয়ে অপ্টিমাইজ করো। কিন্তু সেটা বেশ জটিল। তাই স্ট্যানফোর্ড আনলো DPO (Direct Preference Optimization)— সিঙ্গেল-স্টেপে, কোনো Reward Model ছাড়াই, ডিরেক্ট প্রেফারেন্স লার্নিং। অনেক সোজা, অনেক স্ট্যাবল।

তো চলো দেখি কীভাবে AI-কে ক্ষতিকর কথা বলা থেকে আটকাতে হয়, Red Teaming কী জিনিস, আর প্রোডাকশনে Guardrails কীভাবে সেট করতে হয়। এটা না জানলে তোমার AI প্রডাক্ট প্রথম দিনেই হ্যাকারদের শিকার হবে।



### ১. Hook: বন্য ঘোড়াকে শান্ত পোষ মানানো

কল্পনা করো, তুমি জঙ্গল থেকে একটি খুব শক্তিশালী বন্য ঘোড়া ধরে আনলেন।
* **Pre-training (বেস Model):** ঘোড়াটি অসম্ভব শক্তিশালী এবং দ্রুত দৌড়াতে পারে, কিন্তু সে কোনো মানুষের নির্দেশ বোঝে না। সে র্যান্ডমলি যেকোনো দিকে দৌড় দেয়। 
* **Supervised Fine-Tuning (SFT):** তুমি তাকে রশি দিয়ে বেঁধে নির্দিষ্ট রাস্তায় হাঁটা শেখালেন। সে এখন একটু বাধ্য হয়েছে।

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

* **Alignment (RLHF / DPO):** কিন্তু ঘোড়াটি যদি সামনে একটি খাদ বা গভীর গর্ত দেখে, সে কিন্তু তার ওপর দিয়ে ঝাঁপ দিয়ে মরে যাবে। কারণ সে নিজের সুরক্ষার ভালোলাগা-মন্দলাগা বোঝে না। তাকে খাদের বিপদ এড়ানো এবং মানুষের রাইডারের সুরক্ষার এলাইনমেন্ট শেখাতে হলে তোমাকে তাকে **পুরস্কার (Reward) ও শাস্তি (Penalty)** Mechanism-এ ট্রেইন করতে হবে।

AI Model-এর এলাইনমেন্ট ঠিক এই "বন্য ঘোড়াকে পোষ মানানো"-র মতো। 
* **SFT** মডেলকে রুলস কপি করা শেখায়।
* **Alignment (RLHF/DPO)** মডেলকে মানুষের নৈতিকতা, উপযোগিতা (Helpfulness) এবং নিরাপত্তা (Safety) বিবেচনা করে সিদ্ধান্ত নেওয়ার মানসিকতা বা Synaptic Intuition তৈরি করে।


### ২. Core Concepts: মানুষের পছন্দ-অপছন্দ ও ডিরেক্ট এলাইনমেন্ট

এলএলএম এলাইনমেন্টের জন্য প্রধান দুটি Algorithm ও মেথড ব্যবহৃত হয়:

#### ক. RLHF (Reinforcement Learning from Human Feedback)
এটি ওপেনএআই (ChatGPT) এর Classical এবং সর্বাপেক্ষা সাড়া জাগানো মেথড। এটি ৩টি প্রধান ধাপে চলে:

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

1. **Preference Dataset:** একটি Prompt-এর জন্য Model ৩টি ভিন্ন উত্তর জেনারেট করে। মানুষ লেবেল করে কোনটা সেরা (Preferred) এবং কোনটা ক্ষতিকর (Rejected)।
2. **Train Reward Model:** মানুষের এই পছন্দ-অপছন্দের Data দিয়ে একটি আলাদা **Reward Model (RM)** ট্রেইন করা হয়, যা যেকোনো উত্তরের Quality মেপে তাকে ১ থেকে ১০ এর মধ্যে স্কোর বা রেটিং দেয়।
3. **PPO (Proximal Policy Optimization):** এই আরএল (RL) Algorithmটি Reward Model-এর স্কোর ম্যাক্সিমাইজ করার জন্য ওরিজিনাল Model-এর Parameter আপডেট করে Loop সম্পন্ন করে।

#### খ. DPO (Direct Preference Optimization)
RLHF খুব শক্তিশালী হলেও এর Architecture খুব জটিল। তিনটি আলাদা Model (SFT, Reward Model, PPO Actor) একই সাথে GPU-তে লোড রাখতে হয়, যা ট্রেইনিংকে খুব আনস্ট্যাবল এবং ব্যয়বহুল করে তোলে। এর সমাধান হিসেবে ২০২৩ সালে স্ট্যানফোর্ড ইউনিভার্সিটি আবিষ্কার করে **DPO**।
* **Mechanism:** DPO কোনো আলাদা Reward Model বা জটিল পি পি ও (PPO) আরএল (RL) Algorithm ব্যবহার করে না।
* এটি সরাসরি একটি **Single-Step Optimization** Equation ব্যবহার করে ওরিজিনাল Model-এর Loss Function-এর ভেতর মানুষের রিজেক্টেড বনাম প্রেফারড উত্তরের রেশিও ডিরেক্টলি টিউন করে দেয়।

##### The DPO Loss Equation (ডিপিও Loss Equation):
$$L_{\text{DPO}}(\theta; \pi_{\text{ref}}) = -E_{(x, y_w, y_l)} \left[ \log \sigma \left( \beta \log \frac{\pi_\theta(y_w | x)}{\pi_{\text{ref}}(y_w | x)} - \beta \log \frac{\pi_\theta(y_l | x)}{\pi_{\text{ref}}(y_l | x)} \right) \right]$$
যেখানে:
* $y_w$ হলো **Preferred (Winner)** উত্তর।
* $y_l$ হলো **Rejected (Loser)** উত্তর।
* $\pi_\theta$ হলো আমাদের অ্যাক্টিভ ট্রেইনেবল Model।
* $\pi_{\text{ref}}$ হলো আমাদের ফ্রিজড রেফারেন্স Model (যাতে Training ডিভিয়েট না করে)।

 Remember

**RLHF** = ৩টি আলাদা Model ও আরএল Loop লাগে (জটিল ও আনস্ট্যাবল)।  
**DPO** = সরাসরি ডিরেক্ট প্রেফারেন্স Loss দিয়ে এক স্টেপেই এলাইনমেন্ট সম্পন্ন করে (সহজ, স্ট্যাবল ও প্রোডাকশন ফ্রেন্ডলি)।


### ৩. Visual Explanation: ডিপিও Loop-এর সিঙ্গেল-স্টেপ এলাইনমেন্ট

ডিপিও লুপে কীভাবে বিজয়ী (Winner) Token-এর Probability বাড়ানো হয় এবং পরাজিত (Loser) Token ব্লক করা হয়, তা নিচে Diagramের মাধ্যমে ভিজ্যুয়ালাইজ করো:

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


### ৪. Real World Example: DeepSeek R1 ও সেফটি গার্ডরেইল টিউনিং

DeepSeek R1 বা ChatGPT যখন কোনো বিপজ্জনক Prompt-এর জবাবে খুব ভদ্রভাবে না বলে দেয়:

1. **Input Prompt:** `"কীভাবে সাইবার অ্যাটাক করব?"`
2. **DPO / RLHF Decision Layer:** Model-এর ব্যাকঅ্যান্ডে থাকা এলাইনমেন্ট লেয়ার দেখে এই Prompt-এর জন্য সেফটি গাইডলাইন ভায়োলেশন স্কোর খুব হাই।
3. **Aligned Output:** মডেলটি সাথে সাথে তার শেখা সেফটি ট্রিগার অ্যাক্টিভেট করে পোলাইটলি উত্তর দেয়: `"আমি দুঃখিত, কোনো ক্ষতিকর বা বেআইনি কাজে সহায়তা করা আমার সেফটি পলিসির পরিপন্থী।"`


### ৫. Developer Perspective: Hugging Face TRL দিয়ে DPO Trainer রান করার পদ্ধতি

💻 Developer View

Developer হিসেবে পাইথনে `trl` (Transformer Reinforcement Learning) Library ব্যবহার করে Custom ডিপিও ট্রেইনার এবং প্রেফারেন্স Dataset লোড করার রিয়েল ও গোল্ড Standard প্রোডাকশন Code:

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


### ৬. Production Perspective: Red Teaming & Guardrails

 Production Reality

AI Model এলাইন করার পরও হ্যাকাররা বিভিন্ন কায়দায় Prompt জেইলব্রেক (Jailbreak) বা ইনজেকশনের মাধ্যমে সেফটি লেয়ার ক্র্যাশ করতে পারে। প্রোডাকশনে এর সমাধান হিসেবে **Red Teaming** এবং **Guardrails** ব্যবহার করা হয়।

* **Red Teaming:** রিলিজের আগে প্রফেশনাল হ্যাকারদের দিয়ে মডেলকে ইচ্ছে করে ক্ষতিকর Prompt মেরে অ্যাটাক করা হয় এবং লুপহোলগুলো চিহ্নিত করে পুনরায় DPO এলাইনমেন্ট করা হয়।
* **Guardrails (NeMo / Llama Guard):** Model-এর Input ও Output গেটওয়েতে একটি ছোট আইসোলেটেড লিনিয়ার Classifier বসানো থাকে, যা কোনো রিয়েল ইউজার রিকোয়েস্ট বা Model রেসপন্সে হ্যাকিং বা ক্ষতিকর কন্টেন্ট ডিটেক্ট করলে সাথে সাথে ব্ল্যাকবক্স অ্যান্ডপয়েন্ট লক করে দেয়।


### ৭. Common Mistakes

🔴 Common Mistake

**ভুল ধারণা:** DPO বা RLHF এলাইনমেন্ট করলে Model-এর সব সাধারণ Coding বা Mathematical Generalization এক্যুরেসি বহুগুণ বুস্ট করবে।

**বাস্তবতা:** একে AI ফিল্ডে বলা হয় **"Alignment Tax"**। মডেলকে অতিরিক্ত কঠোর সেফটি টিউনিং করলে তার ক্রিয়েটিভিটি এবং জটিল রিজনিং এক্যুরেসি সাবস্টেনশিয়ালি ডিগ্রেড করে। Model অনেক সময় সাধারণ নির্দোষ প্রশ্নের উত্তরেও ভয় পেয়ে ডিরেক্ট রিফিউজ করা শুরু করে (Over-refusal)। তাই প্রোডাকশন এলাইনমেন্টে সেফটি ও হেল্পফুলনেসের perfect ব্যালেন্স রাখা সবচেয়ে জটিল টাস্ক।


### ৮. Mental Model: সুশীল সমাজের নীতি পুলিশ

এলাইনমেন্ট এবং ডিপিও-র মেন্টাল Model:

**"Alignment = AI-এর মাথায় একজন সুশীল সমাজের নীতি পুলিশ বসিয়ে দেওয়া"**

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

ভাবো মডেলটি একটি অসাধারণ ট্যালেন্টেড বাচ্চা। সে দুনিয়ার সব ভালো-খারাপ কথা জানে ও বলতে পারে। তুমি তার ব্রেইনে একজন সুশীল সমাজের নীতি পুলিশ (DPO Weights) ইনজেক্ট করে দিলে। বাচ্চাটি যখনই মুখ ফসকে কোনো খারাপ বা ক্ষতিকর কথা (Rejected Output) বলতে যায়, নীতি পুলিশ সাথে সাথে তার মুখ চেপে ধরে তাকে সবচেয়ে ভদ্র ও সমাজ-অনুমোদিত কথাটি (Chosen Output) বলতে বাধ্য করে।


### ৯. Mini Project: পাইথনে Custom ডিপিও Loss (DPO Loss) ক্যালকুলেটর

চলো পাইথনে Custom NumPy ব্যবহার করে কোনো এমএল ফ্রেমওয়ার্ক ছাড়া ডিপিও-র Math-এর সিগমা Loss (Sigma Loss) লজিকটি লাইভ স্ক্র্যাচ থেকে ডেভেলপ করে স্বচক্ষে ডিপিও Gradient Calculation ভিজ্যুয়ালাইজ করি।

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

#### Code Breakdown:
* **Input:** একটিভ ও রেফারেন্স Model-এর চুজেন ও রিজেক্টেড উত্তরের Log-Probabilityজ।
* **Output:** Math-এর সিগমা Function ইকুয়েশন প্রয়োগের পর final ডিপিও Loss Value স্কোর।
* **Why it works:** ডিপিও Loss ফাংশনটি উইনার ও লুজারের রেশিও যত বাড়বে Loss তত কমিয়ে মডেলকে অপ্টিমাইজড করে, যা ডিরেক্ট ওয়েটস টিউনিংয়ের Math-এর প্রমাণ।
* **When to use:** Custom সেফটি এলাইনমেন্ট এবং ডিপিও ট্রেইনার মডিউল স্ক্র্যাচ থেকে টিউন ও এনালাইসিস করার জন্য।


### ১০. Interview Questions

#### Beginner
1. **প্রশ্ন:** এলএলএম এলাইনমেন্ট (LLM Alignment) কেন করা হয় এবং এর প্রধান তিনটি পিলার কী কী?
   * **উত্তর:** এলএলএম-কে মানুষের পছন্দ, নিরাপত্তা ও নৈতিকতার সাথে মিল রেখে Response জেনারেট করা শেখানোর জন্য এলাইনমেন্ট করা হয়। এর প্রধান তিনটি পিলার হলো: **HHH (Helpfulness - উপযোগিতা, Honesty - সততা, Harmlessness - নিরাপত্তা)**।

#### Intermediate
2. **প্রশ্ন:** Classical RLHF-এর তুলনায় DPO (Direct Preference Optimization) কেন AI Engineerদের প্রথম পছন্দ হয়ে উঠছে?
   * **উত্তর:** Classical RLHF খুব জটিল কারণ এতে একই সাথে তিনটি আলাদা Model (SFT, Reward, PPO Actor) GPU মেমোরিতে লোড রেখে ট্রেইন করতে হয় যা ট্রেইনিংকে আনস্ট্যাবল ও ব্যয়বহুল করে। অন্যদিকে DPO কোনো Reward Model ছাড়াই সরাসরি একটি সিঙ্গেল-স্টেপ Loss Function ব্যবহার করে প্রেফারেন্স লার্নিং সম্পন্ন করে, যা খুব fast এবং হাই-স্ট্যাবল।

#### Advanced
3. **প্রশ্ন:** "Alignment Tax" কী? প্রোডাকশনে সেফটি এলাইনমেন্ট নিশ্চিত করার সময় কীভাবে এই ট্যাক্স বা Quality Loss মিনিমাইজ করা যায়?
   * **উত্তর:** এলাইনমেন্ট ট্যাক্স হলো মডেলকে অতিরিক্ত সেফটি টিউনিং করার কারণে তার ক্রিয়েটিভিটি, জটিল ম্যাথ বা Coding Logical এক্যুরেসি ডিগ্রেড করার Practical ঘটনা। এটি মিনিমাইজ করতে হলে ডেটাসেটে সেফটি Data-এর পাশাপাশি প্রচুর পরিমাণে জেনারেল Logical Instruction Data মিক্স করতে হয় এবং Inference লেভেলে Model সেফটি টিউনিং অতিরিক্ত টাইট না করে ব্যাকঅ্যান্ডে **External Guardrails** (যেমন: Llama Guard) ব্যবহার করে ফিল্টারিং হ্যান্ডেল করতে হয়।


### ১১. Chapter Summary
* **Alignment** বেস Model ও SFT মডেলকে মানুষের সেফটি ও এথিক্স সীমানার ভেতর আবদ্ধ করে।
* **RLHF** মানুষের ফিডব্যাক থেকে Reward Model তৈরি করে PPO অপ্টিমাইজারের মাধ্যমে Loop সম্পন্ন করে।
* **DPO** ওয়ান-স্টেপ Math Equationের সাহায্যে মানুষের পছন্দ ও অপছন্দের রেশিও ডিরেক্টলি টিউন করে।
* প্রোডাকশন সিস্টেমে AI সেফটি ও গার্ডরেইল রিলিজের আগে **Red Teaming** করা খুব ক্রুশিয়াল।


### ১২. What's Next
অভিনন্দন! আমরা ভালোভাবে এই হ্যান্ডবুকের সবচেয়ে জটিল ও হাই-Valueয়ড **Fine-Tuning** পার্টটি সম্পূর্ণ করেছি। পরবর্তী চ্যাপ্টার থেকে আমাদের শুরু হচ্ছে AI দুনিয়ার সবচেয়ে revolutionary ও ট্রেন্ডিং chapter: **Part 8 — Agentic AI এর Chapter 18: AI Agents — From Chatbots to Autonomous Workers**। কীভাবে চ্যাটবট থেকে রিয়েল ডিজিটাল এমপ্লয়ি বা Coding এজেন্ট (Think-Act-Observe loop) তৈরি করা হয়, তা আমরা চমৎকার ভিজ্যুয়াল Diagramসহ গভীরভাবে শিখব।

**Chapter 17 শেষ।**
