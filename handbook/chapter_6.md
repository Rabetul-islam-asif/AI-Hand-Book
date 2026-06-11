# Chapter 6: Deep Feedforward Networks & Backpropagation



তুমি কি কখনো ভেবেছো — Neural Network কীভাবে তার ভুল থেকে শেখে?

ধরো, তুমি কোডে `loss.backward()` লিখলে।

এই এক লাইনেই পর্দার আড়ালে কোটি কোটি Math-এর হিসাব হয়ে যায়।

কিন্তু কীভাবে?

এর পেছনে দুইটা জিনিস কাজ করে — Backpropagation আর Chain Rule।

তো আজকে আমরা ঠিক এটাই শিখবো।

কীভাবে Forward Pass-এ Network ইনপুট থেকে Prediction বানায়।

কীভাবে Loss হিসাব হয়।

আর কীভাবে Chain Rule দিয়ে পেছনের দিকে গিয়ে প্রতিটা Weight ঠিক করা হয়।

চলো একটা মজার গল্প দিয়ে শুরু করি!


### ১. Hook: ট্রাস্ট গেম ও ভুল fix-এর শৃঙ্খল

ধরো, একটি Company চলে ৫ জন কর্মচারীর একটি চেইন দিয়ে:

`Input গ্রাহক ──► ক্লার্ক (Layer 1) ──► ম্যানেজার (Layer 2) ──► সিইও (Output) ──► Customer ডেলিভারি`

এখন Customer ডেলিভারিতে বড় ভুল হলো।

এই ভুলের দায় কি শুধু সিইও-র?

উত্তর: না।

সিইও পেছনের ম্যানেজারকে বলবে — "তোমার রিপোর্টের কারণে আমার সিদ্ধান্ত ভুল হয়েছে।"

ম্যানেজার পেছনের ক্লার্ককে বলবে — "তোমার Data Entry-এর কারণে আমার রিপোর্ট ভুল হয়েছে।"

এভাবে ভুলের সিগন্যাল পেছন দিকে যায়।

আর প্রত্যেকে নিজের কাজের ভুল শুধরে নেয়।

Deep Learning-এর ভাষায় এই ভুল fix-এর চেইনকেই বলে **Backpropagation**।

![Backpropagation Flow Diagram](/diagrams/backpropagation_flow.png)

আর ভুলের দায়ভার ভাগ করার Math-এর নিয়মটাকে বলে **Chain Rule**।




### ২. মূল ধারণা: Feedforward আর Chain Rule

#### ক. Feedforward Network টা আসলে কী?

সবচেয়ে সিম্পল Neural Network ভাবো।

এখানে Data শুধু সামনের দিকে যায়।

Input Layer থেকে Hidden Layer হয়ে Output Layer-এ।

কোনো Loop নেই। কোনো ফিরে আসা নেই।

তো এই Network-এর তিনটা পার্ট —

**Input Layer** কী করে?

বাইরের Data নেয়।

**Hidden Layers** কী করে?

Input-এর ভেতরের Pattern খুঁজে বের করে।

**Output Layer** কী করে?

Final Prediction দেয়।

ব্যস, এটাই Feedforward Network।


#### খ. Forward Pass — Data-এর সামনে যাওয়া

Forward Pass মানে Input কে একে একে প্রতিটা Layer-এর ভেতর দিয়ে পাঠানো।

প্রতিটা Layer-এ কী হয়?

Weight দিয়ে গুণ হয়।

Bias যোগ হয়।

Activation Function পার হয়।

তারপর পরের Layer-এ যায়।

Math-এ লিখলে ধাপগুলো এরকম:

1. $Z_1 = X \cdot W_1 + B_1$
2. $A_1 = Relu(Z_1)$
3. $Z_2 = A_1 \cdot W_2 + B_2$
4. $Y_{pred} = Softmax(Z_2)$


#### গ. Loss আর Backward Pass — ভুল ঠিক করা

Forward Pass শেষে Model একটা Prediction দেয়।

এখন সেই Prediction কতটা ভুল?

সেটা মাপে Loss Function।

যেমন: $Loss = 0.5 \cdot (Y_{true} - Y_{pred})^2$

Loss বের হলো।

এবার কী করবো?

পেছনের দিকে যাবো।

প্রতিটা Weight-এর জন্য বের করবো — এই Weight কতটুকু Loss-এর জন্য দায়ী?

এটাই Backward Pass।

আর এই "কতটুকু দায়ী" বের করাই হলো Partial Derivative হিসাব করা।


#### ঘ. Chain Rule — পুরো ব্যাপারটার চাবিকাঠি

এবার আসল প্রশ্ন।

পেছনের Layer-এর Weight কতটুকু দায়ী — সেটা কীভাবে বের করবো?

এখানেই Calculus-এর Chain Rule কাজে আসে।

Chain Rule সোজা কথায় বলে —

যদি $y$ নির্ভর করে $x$-এর উপর, আর $z$ নির্ভর করে $y$-এর উপর, তাহলে $z$-এর সাপেক্ষে $x$-এর পরিবর্তনের হার হবে দুইটার গুণফল:

$$\frac{\partial z}{\partial x} = \frac{\partial z}{\partial y} \cdot \frac{\partial y}{\partial x}$$

Neural Network-এ এটা কীভাবে কাজ করে?

ধরো, Loss $L$-এর সাপেক্ষে Layer 1-এর Weight $W_1$-এর Gradient বের করতে হবে।

তাহলে Chain Rule দিয়ে লিখবো:

$$\frac{\partial L}{\partial W_1} = \frac{\partial L}{\partial Y_{pred}} \cdot \frac{\partial Y_{pred}}{\partial A_1} \cdot \frac{\partial A_1}{\partial Z_1} \cdot \frac{\partial Z_1}{\partial W_1}$$

একটার পর একটা গুণ। চেইনের মতো।

তাই নাম Chain Rule।


### ৩. ভিজুয়াল: Chain Rule-এর গিয়ার Mechanism

Chain Rule-কে সাইকেলের গিয়ার ভাবো:

```
[গিয়ার ১ (W1)] ──► [গিয়ার ২ (Hidden Activation)] ──► [গিয়ার ৩ (Y_pred)] ──► [চাকা (Loss)]
```

চাকা ঘুরলে গিয়ার ৩ ঘুরে।

গিয়ার ৩ ঘুরলে গিয়ার ২ ঘুরে।

গিয়ার ২ ঘুরলে গিয়ার ১ ঘুরে।

প্রতিটা ঘূর্ণনের পরিমাণ আগেরটার সাথে গুণ হয়ে ট্রান্সফার হয়।

Chain Rule ঠিক এভাবেই Output-এর ভুলের সিগন্যাল প্রতিটা Layer-এ পাঠায়।


### ৪. Real World Example: Self-Driving Car

Tesla বা Waymo-র Self-Driving Car-এর কথা ভাবো।

গাড়ির ক্যামেরা সামনে কিছু দেখলো।

**Forward Pass:**

Camera-র Pixel গুলো Neural Network-এর ভেতর দিয়ে গেল।

Network বললো — "এটা Traffic Cone, ৯২% শিউর।"

**Error Calculation:**

কিন্তু আসলে ওটা ছিল কংক্রিটের Barricade।

তাহলে Model ভুল করেছে।

Loss তৈরি হলো।

**Backpropagation:**

এই ভুলটা সাথে সাথে পেছনে গেল।

কোটি কোটি Weight আপডেট হলো।

যাতে পরের বার এই ধরনের আলোতে Model আর Barricade-কে Traffic Cone না ভাবে।


### ৫. NumPy দিয়ে স্ক্র্যাচ থেকে Backpropagation Coding

💻 Developer View

চলো সবচেয়ে মজার কাজটা করি।

PyTorch বা TensorFlow ছাড়া, শুধু NumPy দিয়ে একটা ২-Layer Neural Network বানাবো।

Forward Pass, Loss Calculation, আর Chain Rule দিয়ে Backpropagation — সব স্ক্র্যাচ থেকে।

```python
import numpy as np

# ১. মক Input ও টার্গেট
X = np.array([2.0])       # Input Feature
y_true = np.array([4.0])  # কাঙ্ক্ষিত টার্গেট Output

# ২. ওয়েটস ইনিশিয়ালাইজেশন (র্যান্ডম)
w1 = 1.5  # Layer 1 weight
w2 = 0.8  # Layer 2 weight
learning_rate = 0.05

print(f"Initial weights: w1={w1}, w2={w2}")
print("Starting training loop...\n")

# ৩. Training Loop (৫টি ইপক)
for epoch in range(5):
    # --- A. FORWARD PASS ---
    # Layer 1
    z1 = X * w1
    a1 = z1  # Linear activation for simplicity in math
    
    # Layer 2 (Output)
    z2 = a1 * w2
    y_pred = z2  # Final Prediction
    
    # --- B. LOSS CALCULATION (Mean Squared Error variation) ---
    loss = 0.5 * (y_true - y_pred) ** 2
    
    # --- C. BACKPROPAGATION (Chain Rule Applied!) ---
    # dL/dy_pred
    dl_dypred = -(y_true - y_pred)
    
    # Layer 2 Gradients: dL/dw2 = dL/dy_pred * dy_pred/dw2
    # dy_pred/dw2 = a1
    dl_dw2 = dl_dypred * a1
    
    # Layer 1 Gradients: dL/dw1 = dL/dy_pred * dy_pred/da1 * da1/dw1
    # dy_pred/da1 = w2, da1/dw1 = X
    dl_dw1 = dl_dypred * w2 * X
    
    # --- D. WEIGHT UPDATE (Gradient Descent Step) ---
    w2 = w2 - learning_rate * dl_dw2
    w1 = w1 - learning_rate * dl_dw1
    
    print(f"Epoch {epoch+1}: Prediction = {y_pred[0]:.4f}, Loss = {loss[0]:.4f}, Weight w1={w1[0]:.4f}, Weight w2={w2[0]:.4f}")
```

#### কোড রান করলে কী হয়?

**Epoch 1:** Model-এর Prediction ছিল `2.4`। Loss ছিল `1.28`। Gradient দিয়ে Weight আপডেট হলো।

**Epoch 5:** মাত্র ৫ Epoch-এই Prediction `3.99` ছাড়িয়ে যায়। Loss কমে যায় প্রায় `0.0000`!

Model perfectly শিখে ফেলেছে।


### ৬. Production-এ Gradient-এর সমস্যা

🏭 Production Reality

Training-এর সময় ৫-১০ Layer-এ সব ঠিকঠাক চলে।

কিন্তু Production-এ যখন ৫০ বা ১০০ Layer-এর বিশাল Network ট্রেইন করবে?

তখন Chain Rule-এর গুণ করতে করতে দুইটা বড় সমস্যা হতে পারে।

**সমস্যা ১: Vanishing Gradients**

এটা কী?

Chain Rule-এ যখন একের পর এক ছোট সংখ্যা গুণ হয় — $0.1 \times 0.1 \times 0.1$ — তখন শুরুর Layer-এ পৌঁছাতে পৌঁছাতে Gradient প্রায় শূন্য হয়ে যায়।

ফলে শুরুর Layer গুলো কিছুই শিখতে পারে না।

কীভাবে ঠিক করবো?

ReLU Activation ব্যবহার করো।

আর **Residual Connections** ব্যবহার করো — যেমন ResNet বা Transformer-এ আছে।

এগুলো সিগন্যালকে কোনো বাধা ছাড়াই সরাসরি পেছনে যেতে দেয়।

**সমস্যা ২: Exploding Gradients**

এটা কী?

উল্টো ব্যাপার। Chain Rule-এ যখন একের পর এক বড় সংখ্যা গুণ হয় — $2.5 \times 3.0 \times 4.0$ — তখন Gradient ইনফিনিটি বা `NaN` হয়ে যায়।

কীভাবে ঠিক করবো?

**Gradient Clipping** ব্যবহার করো — Gradient-এর একটা সর্বোচ্চ সীমা সেট করে দাও।


### ৭. Common Mistake

🔴 Common Mistake

**ভুল ধারণা:**

Backpropagation-এর সময় প্রতিটা Image-এর জন্য আলাদা আলাদা Weight আপডেট করা ভালো।

**বাস্তবতা:**

প্রতিটা Image-এর জন্য আলাদা Update করলে Training অনেক ধীর হয়।

GPU পুড়ে যায়।

তাই Production-এ **Mini-batch Gradient Descent** ব্যবহার করা হয়।

এখানে ৩২ বা ৬৪টা Image-এর একটা Batch দিয়ে Forward Pass হয়।

তাদের Average Loss দিয়ে একবার Backpropagation চলে।

এতে Speed-ও বাড়ে, Learning-ও ভালো হয়।


### ৮. মনে রাখো এভাবে

Backpropagation-কে এভাবে মনে রাখো —

**"Forward Pass হলো পাহাড়ের গুহায় চিৎকার করা। আর Backpropagation হলো সেই চিৎকারের Echo শুনে বোঝা — তোমার আওয়াজ কতটা ঠিক ছিল, আর কতটা বদলাতে হবে।"**


### ৯. Interview Questions

#### Beginner

**প্রশ্ন:** Forward Pass আর Backward Pass বলতে কী বোঝায়?

**উত্তর:** Forward Pass মানে Input-কে Layer-এর পর Layer-এর Weight দিয়ে গুণ করে Prediction বের করা। আর Backward Pass মানে সেই Prediction-এর Error বের করে Chain Rule দিয়ে পেছনে গিয়ে প্রতিটা Weight আপডেট করা।

#### Intermediate

**প্রশ্ন:** Backpropagation-এ Chain Rule কেন এত গুরুত্বপূর্ণ?

**উত্তর:** Chain Rule হলো Calculus-এর সেই নিয়ম যেটা দিয়ে আমরা Output-এর Loss-এর সাপেক্ষে একদম ভেতরের Layer-এর Weight-এর Gradient বের করতে পারি। Chain Rule ছাড়া Deep Network-এর ভেতরের Layer গুলোর Gradient হিসাব করা সম্ভব না।

#### Advanced

**প্রশ্ন:** Vanishing Gradient সমস্যা Deep Network-এ কীভাবে সমাধান করা হয়?

**উত্তর:** দুইভাবে। প্রথমত, ReLU বা GELU Activation ব্যবহার করা হয় — এদের পজিটিভ স্লোপ 1.0 হওয়ায় Gradient ছোট হয় না। দ্বিতীয়ত, **Residual Connections** ব্যবহার করা হয়, যেটা $x + f(x)$ Architecture ফলো করে। এতে Backpropagation-এর সময় অন্তত 1.0 সিগন্যাল কোনো ক্ষয় ছাড়াই আগের Layer-এ পৌঁছে যায়।


### ১০. Chapter Summary

**Forward Pass** — Data সামনের দিকে যায়, Prediction বের হয়।

**Backward Pass** — ভুলের সিগন্যাল পেছনে যায়, Weight ঠিক হয়।

**Chain Rule** — গিয়ারের চেইনের মতো ভুলের দায়ভার প্রতিটা Weight-এ ভাগ করে দেয়।

**Production Challenge** — Vanishing আর Exploding Gradient ধরা আর ঠিক করা AI Engineer-এর বড় কাজ।


### XI. What's Next

Backpropagation শেষ! Deep Learning-এর সবচেয়ে কঠিন Math পার করে ফেলেছো।

এবার আসছে আধুনিক AI-এর সবচেয়ে গুরুত্বপূর্ণ Architecture — **Chapter 7: Transformers**।

দেখবো কীভাবে Self-Attention আর Multi-Head Attention পুরো AI জগৎ বদলে দিয়েছে।

**Chapter 6 শেষ।**
