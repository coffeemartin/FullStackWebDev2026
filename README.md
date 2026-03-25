# FullStackWebDev2026 – Group Project

**Team Members**  
- Ananya Moolampally (25080771)  
- Faiz Qazi (25040556)  
- Franco Meng (23370209)  
- Swathy Shenoy (25068786)  

---


## 1. Application Proposal

For our group project, we propose to build a **fitness and nutrition tracking website** that provides useful exercise and diet information, while allowing users to create a personal profile and track their progress.

The system will allow users to:

- Create an account and store personal details  
- Log exercise / gym sessions  
- Log food / nutrition intake  
- View educational content about exercise and nutrition  
- Receive personalised training and nutrition recommendations  

For the recommendations we plan to use modern AI techniques including:

- LLM API calls  
- Prompt engineering  
- Retrieval-Augmented Generation (RAG)  
- Vector database for storing user history  
- Dynamic recommendation generation based on user data  

The goal is to generate **personalised training plans and nutrition suggestions** based on the user's profile and activity history.

---

## 2. User Stories

We will create **at least 10 user stories** describing how users interact with the system, including:

As a user:
- I want to calculate my BMI so that I can better manage my diet and exercise plan.
- I want to track my exercise activities so that I can monitor my progress and achieve my fitness goals.
- I want to track my nutrition and food habits so that I can maintain a balanced and healthy diet.
- I want to understand whether my diet is appropriate for my age so that I can assess my overall health.
- I want to log the food I consume with details (meal type, name, quantity, calories) so that I can accurately track my daily intake.
- I want access to exercise recommendations without needing a personal trainer so that I can save money while staying fit.
- I want to categorize my meals (e.g., breakfast, lunch, dinner) so that my food intake is well organized.
- I want to calculate my calorie intake based on the quantity of food (in grams) so that I can monitor my energy consumption accurately.
- I want to save all my food entries at once so that I can maintain a complete record of my daily diet.
- I want to add multiple food entries in one session so that I can log an entire meal efficiently.
- I want validation for empty or incorrect inputs so that I do not save incomplete or invalid data.
- I want to manually enter food names so that I can log any type of food I consume.
- I want to recieve some customised recommendation based on my current exercise and diet.
As a system administrator:
- I want to manage the profile for each user so that the system works efficiently.
  

---

## 3. Main Pages of the Website

### 🏠 Main Page — *@faizqazi*
- Brief description of the website purpose
- Sign up / log in functionality
- Collect initial personal information:
  - Age
  - Gender
  - Height
  - Weight
  - Occupation
  - Current exercise level
- Calculate BMI
- Generate initial training plan

---

### 🏋️ Exercise Page — *@Swathymahesh*

Two main sections:

1. **Exercise Information**
   - Text / images / videos explaining exercises
   - Help users understand recommended workouts

2. **Exercise Log**
   - Record completed exercises
   - Frequency / duration
   - Difficulty feedback
   - Motivation / comments

---

### 🍎 Nutrition Page — *@AnanyaBhavani*

Two main sections:

1. **Nutrition Information**
   - Text / images / videos about food and diet
   - Help users manage nutrition

2. **Food Log**
   - Record food intake
   - Frequency / quantity
   - User feedback / comments

---

### 🤖 LLM Summary / Recommendation Page — *@coffeemartin*

This page will use:

- Prompt engineering
- Vector database
- RAG (Retrieval-Augmented Generation)
- LLM API

The system will send user data to the LLM and return structured feedback, such as:

- Training plan for next week / next 4 weeks
- Nutrition recommendations
- Motivation tips
- Progress feedback

---

## 4. CSS Framework

Proposed framework:

- Bootstrap (to be confirmed)

---

## 5. Initial HTML / CSS Pages 

(Optional but Recommended especially for groups whose meeting is in the later weeks) Start creating some of your pages with HTML and CSS. The page does not need to be interactive (e.g. no need for buttons to work) but it should be sufficient 
