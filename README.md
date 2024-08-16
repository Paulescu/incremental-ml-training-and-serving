<div align="center">
    <h1>Let's design a real-time ML system with incremental re-training ⚡</h1>
</div>

#### Table of contents
* [The problem](#the-problem)
* [Solution](#solution)
* [Run the whole thing in 5 minutes](#run-the-whole-thing-in-5-minutes)
* [Wanna learn more real-world ML?](#wanna-learn-more-real-world-ml)


## The problem

ML models are pattern finding machines, that try to capture the relationship between

- a set of inputs available at prediction time (aka features), and
- a metric you want to predict (aka target)

For most real-world problems these patterns between the features and the target are not static, but change over time. So, if you don’t re-train your ML models, their accuracy degrades over time. This is commonly known as concept drift.

Now, the speed at which patterns change, and you model degrades, depends on the particular phenomena you are modelling.

> **For example 💁**  
> If you are trying to predict rainfall, re-training your ML model daily is good enough. Rainfall patterns obey the laws of physics, and these do not change too much from one day to the next. 

On the other hand, if you are trying to predict short-term crypto prices, where patterns between

- available market data (aka features), and
- future asset prices (aka target)

are short-lived, you must re-train your ML model very frequently. Ideally, in real-time.

A similar situation happens when you want to build a real-time recommender system, like [Tiktok’s famous monolith](https://arxiv.org/pdf/2209.07663), where user preferences change in the blink of an eye, and your ML models needs to be refreshed as often as possible.

So now the question is

> How do you design an ML system that continuously re-trains the ML model that is serving the predictions ❓

In this repo you can find a source code implementation.


## Run the whole thing in 5 minutes

1. Install all project dependencies inside an isolated virtual env, using Python Poetry
    ```
    $ make install
    ```

2. Start the feature pipelines with
    ```
    $ make producers
    ```

3. Start the training pipeline with
    ```
    $ make training
    ```

4. Start the inference pipeline
    ```
    $ make predict
    ```

## Wanna learn more real-world ML?

Join more than 18k builders to the **Real-World ML Newsletter**.

Every Saturday morning.

For **FREE**

### [👉🏽 Subscribe for FREE](https://www.realworldml.net/subscribe)