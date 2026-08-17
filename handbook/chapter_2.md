# Chapter 2: The Core Mechanics — Machine Learning & Deep Learning

তুমি কি কখনো ভেবেছো — ক্রেডিট কার্ডের ফ্রড ধরা আর সেলফ-ড্রাইভিং কার চালানো, এই দুটো সম্পূর্ণ আলাদা কাজ।

কিন্তু AI দুটোই করে।

কীভাবে?

উত্তর হলো — AI-এর আলাদা আলাদা হাতিয়ার আছে।

Customer ভাগ করা একরকম কাজ। ছবি দেখে মুখ চেনা আরেকরকম। গেম খেলা সম্পূর্ণ আলাদা।

সব কাজের জন্য একই টেকনিক খাটানো বোকামি।

ভুল জায়গায় ভুল হাতিয়ার ব্যবহার করলে তোমার পুরো প্রজেক্টের কস্ট আর রিসোর্স নষ্ট হবে।

তো চলো এই Chapter-এ AI-এর মূল তিনটা স্তম্ভ বুঝে নিই।

Machine Learning কী।

Deep Learning কী।

Neural Network কী।

এদের ভেতরের Mechanics কীভাবে কাজ করে।

আর Supervised, Unsupervised, Reinforcement Learning-এর আসল পার্থক্যটা কোথায়।

চলো শুরু করা যাক!


## ১. Face Recognition বনাম Excel Sheet Analysis

তোমাকে দুটি ভিন্ন AI টাস্ক দেওয়া হলো:

1. **টাস্ক ১:** একটি ব্যাংকের Transaction Database আছে। সেখানে Amount, Location, Balance দেওয়া আছে। তোমাকে বের করতে হবে কোনটি ফ্রড আর কোনটি সেফ।
2. **টাস্ক ২:** সিসিটিভি ক্যামেরার ভিডিও স্ট্রিম থেকে মানুষের মুখ দেখে তার আইডেন্টিটি বের করতে হবে।

প্রথম টাস্কের Data গোছানো। মানে Tabular Data।

এটা তুমি সাধারণ Machine Learning Algorithm দিয়ে সলভ করতে পারবে। যেমন XGBoost বা Decision Tree। কম খরচে, চমৎকারভাবে।

কিন্তু দ্বিতীয় টাস্ক?

সেটার Data হলো Image Pixel। চরম Unstructured।

এখানে আগের Machine Learning পুরোপুরি ফেইল করবে।

এখানেই দরকার মিলিয়ন মিলিয়ন Parameter-এর মনস্টার — মানে **Deep Learning**।

![AI vs. ML vs. DL Hierarchy](/diagrams/ai_vs_ml_vs_dl_hierarchy.png)


## ২. AI Model ৩ ভাবে প্যাটার্ন শেখে

AI Model মূলত ৩ ভাবে প্যাটার্ন শেখে। চলো একে একে দেখি।

![Three Families of Machine Learning](/diagrams/ml_families.png)


### Supervised Learning

ধরো, তুমি একটা ক্লাসে বসে আছো। শিক্ষক প্রশ্ন দিচ্ছেন, সাথে সাথে উত্তরও বুঝিয়ে দিচ্ছেন। তুমি সেটা শিখে পরীক্ষা দিচ্ছ।

Supervised Learning ঠিক এভাবেই কাজ করে।

প্রতিটি Input-এর সাথে তার সঠিক উত্তর জুড়ে দেওয়া থাকে। একে বলে Labeled Data। ফর্মুলা হিসেবে লিখলে — $Y = f(X)$, যেখানে $X$ হলো Input Feature আর $Y$ হলো Label।

কোথায় ব্যবহার হয়? Spam Filtering, Image Classification — এসব জায়গায়।

### Unsupervised Learning

এবার ভাবো, কোনো শিক্ষক নেই। কোনো উত্তরও দেওয়া নেই।

তোমাকে শুধু একগাদা Customer-এর কেনাকাটার Data দেওয়া হলো। বলা হলো — এদের মধ্যে কোনো Pattern খুঁজে বের করো।

এটাই Unsupervised Learning। Unlabeled Data থেকে Model নিজেই Pattern আর Cluster খুঁজে বের করে।

কোথায় কাজে লাগে? Customer Segmentation, Anomaly Detection।

### Reinforcement Learning

এবার একটু অন্যরকম গল্প।

ধরো, একটা বাচ্চাকে সাইকেল চালানো শেখাচ্ছ। কোনো ম্যানুয়াল নেই। কোনো Data নেই।

বাচ্চা চালাতে গেলো, পড়ে গেলো — ব্যথা পেলো। এটা হলো Penalty।

আবার চেষ্টা করলো, ব্যালেন্স রাখতে পারলো — এগিয়ে গেলো। এটা হলো Reward।

Reinforcement Learning ঠিক এভাবে কাজ করে। কোনো পূর্ববর্তী Data থাকে না। একটি Agent Environment-এ Action নেয়, আর তার ফলাফল অনুযায়ী Reward বা Penalty পায়।

কোথায় ব্যবহার হয়? দাবা খেলা (AlphaGo), Robotics, Reasoning Model (DeepSeek R1)।


## ৩. ML বনাম DL — আসল পার্থক্যটা কোথায়?

এদের মধ্যে মূল পার্থক্য একটাই — **Feature Engineering**।

Machine Learning-এ তোমাকে নিজ হাতে Feature বের করে দিতে হয়।

ধরো, বাড়ি বিক্রির দাম Predict করতে চাও। তোমাকে আলাদা করে রুমের সংখ্যা, লোকেশনের রেটিং — এসব Input Feature হিসেবে গুছিয়ে দিতে হবে।

কিন্তু Deep Learning-এ?

Model নিজেই Image-এর Pixel থেকে Edge, Contour, চোখ, নাক — সব Automatically শিখে নেয়। মানুষের Help লাগে না।

সহজ কথায় — ML-এ তুমি Feature দাও, DL নিজেই Feature খুঁজে নেয়।


## ৪. Train / Validation / Test — পরীক্ষার তিন ধাপ

Model বানানোর পর সবচেয়ে গুরুত্বপূর্ণ প্রশ্ন হলো —

Model কি আসলেই কিছু শিখছে?

নাকি শুধু উত্তরগুলো মুখস্থ করছে?

এই মুখস্থ করাকে বলে Overfitting। আর এটা ধরতে আমরা পুরো Dataset-কে তিন ভাগে ভাগ করি।

চলো পরীক্ষার প্রস্তুতির গল্প দিয়ে বুঝি।

**Training Set (৭০-৮০% Data)** — এটা তোমার টেক্সটবুক আর হোমওয়ার্ক। Model এই Data বারবার পড়ে। Pattern বোঝার চেষ্টা করে। সূত্র শেখে।

**Validation Set (১০-১৫% Data)** — এটা হলো Mock Test। পরীক্ষার আগে নিজেকে যাচাই করা। এই রেজাল্ট দেখে তুমি বুঝতে পারো কোন চ্যাপ্টারে দুর্বলতা আছে। তারপর পড়ার স্ট্র্যাটেজি বদলাও। AI-এর ভাষায় এটা হলো Hyperparameter Tuning — যেমন Learning Rate বা Depth পরিবর্তন করা।

**Test Set (১০-১৫% Data)** — এটা তোমার ফাইনাল পরীক্ষা। এই প্রশ্নগুলো তুমি আগে কখনো দেখোনি। Unseen Data। Model এখানে যে Score পায়, সেটাই তার আসল যোগ্যতা।

> 🧠 **গোল্ডেন রুল:** নিজের করা হোমওয়ার্কের প্রবলেম সলভ করে নিজেকে জিনিয়াস ভাবা বোকামি। Training Data-তে ১০০% Accuracy মানে Model ভালো — এটা ভুল। আসল পরিচয় লুকিয়ে আছে Test Set-এর রেজাল্টে!


## ৫. Feature Engineering — একটা ছবিতে বুঝো

নিচের ছবিটা দেখলেই বুঝবে Deep Learning কীভাবে মানুষের ম্যানুয়াল খাটুনি বাঁচিয়ে দেয়:

```
Machine Learning Pipeline:
[Raw Image] ──► [👨‍ মানুষের ম্যানুয়াল Feature এক্সট্রাকশন (কান, চোখ)] ──► [ML Model] ──► [প্রেডিকশন]

Deep Learning Pipeline:
[Raw Image] ───────────────► 🧠 [ Deep Neural Network ] ──────────────► [প্রেডিকশন]
                          (Auto-learns: Edges ──► Shapes ──► Faces)
```


## ৬. Real World Example: ই-কমার্স Recommendation

Amazon বা Daraz-এর Recommendation Engine-এ দুই ধরনের Architecture কাজ করে।

**ML লেয়ার:** তোমার বয়স, দেশ, ব্রাউজিং Category — এসব Structured Data নিয়ে Classical Logistic Regression Model বলে দেয় তোমার কেনাকাটার সম্ভাবনা কতটুকু।

**DL লেয়ার:** তুমি কোন আইটেমের ছবিতে কত সেকেন্ড তাকিয়ে ছিলে, কী ধরনের কমেন্ট লিখেছো — এই Unstructured Image আর Text Data Analyze করে একদম Personalized Product Feed তৈরি করে।

সহজ কথায় — Structured Data-র জন্য ML, Unstructured Data-র জন্য DL।


## ৭. Developer View: Scikit-Learn বনাম Keras

চলো Python-এ দেখি — একই Problem দুইভাবে সলভ করা যায়।

প্রথমে Scikit-Learn দিয়ে Classical ML:

```python
# --- ১. MACHINE LEARNING (Tabular classification using Decision Trees) ---
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

# Iris dataset loaded (তাবুলার Data)
data = load_iris()
X_train, X_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.2)

# Simple ML Classifier
ml_model = DecisionTreeClassifier()
ml_model.fit(X_train, y_train)

y_pred = ml_model.predict(X_test)
print(f"ML Decision Tree Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
```

এখন দেখো কীভাবে Keras দিয়ে Neural Network দাঁড় করানো যায়:

```python
# --- ২. DEEP LEARNING (Multi-layer Perceptron using Keras) ---
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# Deep Neural Network Architecture
dl_model = Sequential([
    Dense(16, activation='relu', input_shape=(4,)), # Input Layer + Hidden Layer 1
    Dense(8, activation='relu'),                   # Hidden Layer 2
    Dense(3, activation='softmax')                 # Output Layer (3 Classes)
])

# Compile Model
dl_model.compile(optimizer='adam',
                 loss='sparse_categorical_crossentropy',
                 metrics=['accuracy'])

# Train Model
dl_model.fit(X_train, y_train, epochs=20, batch_size=4, verbose=0)

loss, accuracy = dl_model.evaluate(X_test, y_test, verbose=0)
print(f"Deep Learning Neural Network Accuracy: {accuracy * 100:.2f}%")
```


## ৮. Production Reality: কস্ট আর Resource

Developer হিসেবে সবচেয়ে বড় ভুল হলো — সাধারণ কাজের জন্য Deep Learning Model বসিয়ে দেওয়া।

সাধারণ ML Model CPU-তেই মাইক্রো-সেকেন্ডে রান করে।

কিন্তু Deep Learning বা Transformer Model-এর জন্য GPU লাগে। Memory লাগে। প্রতি মাসে খরচ হাজার ডলার ছাড়িয়ে যেতে পারে।

আর Data কম থাকলে?

ধরো তোমার কাছে মাত্র ৫০০ লাইনের Database আছে। এত কম Data দিয়ে Neural Network Train করলে সে Overfit করবে। মানে মুখস্থ করে ফেলবে।

এমতাবস্থায় Random Forest বা SVM-এর মতো ML Algorithm অনেক ভালো কাজ করবে।


## ৯. Common Mistake

**ভুল ধারণা:** Deep Learning সবসময় ML-এর চেয়ে বেশি Accurate।

**বাস্তবতা:** Tabular Data-এর ক্ষেত্রে এটা প্রায়ই উল্টো।

XGBoost বা LightGBM-এর মতো Boosted Trees অনেক সময় Neural Network-এর চেয়ে ভালো পারফর্ম করে — Excel-টাইপ Data-তে।

Neural Network তৈরিই হয়েছে Image, Text, Audio-র মতো Unstructured Data-র Hidden Relationship বোঝার জন্য।

সব জায়গায় DL বসালেই ভালো — এটা ভুল।


## ১০. Mental Model: দর্জি বনাম 3D Scanner

একটা সহজ Analogy মনে রাখো।

**Machine Learning** হলো একজন দর্জি। তোমার হাতের মাপ, ঝুলের মাপ — সব ফিতায় মেপে নেন। তারপর জামা কাটেন। মানে Manual Feature Extraction।

**Deep Learning** হলো একটা 3D Scanner। তোমার সামনে দাঁড়ালেই নিজে থেকে পুরো শরীরের Perfect Structure তৈরি করে ফেলে। তারপর জামা বানায়। মানে Automatic Feature Learning।

Deal?


## ১১. Mini Project: Customer Retention Classifier

চলো NumPy ব্যবহার করে একটি খুব সহজ Linear Classifier বানাই।

এটা ইউজারের Login Frequency আর Subscription Fee দেখে Predict করবে — সে Churn করবে কি না।

```python
import numpy as np

# ১. Feature: [লগইন দিন/সপ্তাহে, সাবস্ক্রিপশন প্রাইস ($)]
X = np.array([
    [7, 10],   # ইউজার ১: অ্যাক্টিভ
    [6, 15],   # ইউজার ২: অ্যাক্টিভ
    [1, 9],    # ইউজার ৩: ইন-অ্যাক্টিভ (Churn)
    [2, 30]    # ইউজার ৪: ইন-অ্যাক্টিভ (Churn)
])
Y = np.array([1, 1, 0, 0]) # ১ = রিটেইনড, ০ = চার্নড

# ২. র্যান্ডম Parameter
W = np.array([0.1, -0.2])
B = 0.0

# ৩. অ্যাক্টিভেশন Function (হাইভিসাইড স্টেপ Function)
def predict(features):
    score = np.dot(features, W) + B
    return 1 if score >= 0 else 0

# ৪. র্যান্ডম প্রেডিকশন চেক
test_user = np.array([7, 12])
print(f"Prediction for active user (7 logins, $12): {'Retained' if predict(test_user) == 1 else 'Churned'}")
```


## ১২. Interview Questions

### Beginner
1. **প্রশ্ন:** Machine Learning এবং Deep Learning-এর মধ্যে প্রধান পার্থক্য কী?
   * **উত্তর:** Machine Learning-এ Feature গুলো মানুষকে ম্যানুয়ালি বের করে দিতে হয়। Deep Learning-এ Neural Network নিজেই Raw Data থেকে Hidden Feature শিখে নেয়।

### Intermediate
2. **প্রশ্ন:** Reinforcement Learning এবং Supervised Learning-এর পার্থক্য Practical Example দিয়ে ব্যাখ্যা করো।
   * **উত্তর:** Supervised Learning চলে Labeled Data-এর উপর — যেমন ছবি আর তার নাম (বিড়াল/কুকুর)। কিন্তু Reinforcement Learning কোনো Data ছাড়াই শুরু হয়। একটি Agent Environment-এ Action নিয়ে ভুলের জন্য Penalty আর সঠিক চালের জন্য Reward পায়। ধীরে ধীরে Best Path শেখে — যেমন রোবট হাঁটা শেখা।

### Advanced
3. **প্রশ্ন:** Tabular Data Analysis-এ XGBoost নাকি Custom Neural Network — কোনটা বেছে নেবে? কেন?
   * **উত্তর:** Tabular Data-র জন্য XGBoost বা LightGBM-ই Production-grade সিদ্ধান্ত। কারণ Tabular Data-তে Feature গুলো Already Structured। Boosted Trees দ্রুত Converge করে। Computational Cost কম। Overfitting Risk কম। Neural Network মূলত Image বা Unstructured Sequential Data-র জন্য বেশি উপযোগী।


## ১৩. Chapter Summary

এই Chapter-এ আমরা শিখলাম:

* **Machine Learning** — Tabular Data-র জন্য। তোমাকে Feature বের করে দিতে হয়।
* **Deep Learning** — Unstructured Data-র জন্য (Image, Text, Audio)। নিজেই Feature শেখে।
* Supervised Learning চলে **Labeled Data** দিয়ে।
* Unsupervised Learning খোঁজে **Hidden Pattern**।
* Reinforcement Learning চলে **Reward-Penalty** সিস্টেমে।
* Production-এ Model বাছাই করতে হয় **কস্ট আর Data Size** বিবেচনা করে।

সবচেয়ে গুরুত্বপূর্ণ কথা —

সব জায়গায় Deep Learning বসালেই ভালো হয় না। সঠিক Problem-এ সঠিক Tool ব্যবহার করাটাই আসল দক্ষতা।


## What's Next?

Machine Learning আর Deep Learning-এর Mechanics আমরা বুঝে ফেলেছি।

পরের Chapter-এ ঢুকবো Math-এর দুনিয়ায়।

**Chapter 3: The Math of Learning — Loss Functions & Optimization।**

কীভাবে Loss Function আর Gradient Descent মিলে Model-এর Parameter গুলোকে Optimize করে — সেটা নিজের হাতে ভাঙবো।

**Chapter 2 শেষ।**
