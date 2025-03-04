# Solomon-100 Dataset Analysis & VRPTW Solver  

## Project Overview  
This project analyzes and visualizes the **Solomon-100 dataset**, a benchmark for **Vehicle Routing Problems with Time Windows (VRPTW)**, and implements a **constraint-based solver** to optimize vehicle routes. The goal is to:  

✅ **Extract and analyze dataset insights** (customer locations, demand distribution, time windows)  
✅ **Visualize and compare different Solomon dataset categories (C1, C2, R1, R2, RC1, RC2)**  
✅ **Solve the VRPTW using Constraint Satisfaction Problem (CSP) techniques**  
✅ **Optimize vehicle routes while minimizing distance and satisfying constraints**  

---

## **Solomon-100 Dataset Analysis**  
The dataset contains customer locations, delivery time windows, and vehicle constraints. Key analyses include:  

- **Customer Location Maps** – Clustered vs. randomly distributed customers  
- **Demand Distribution** – Variability across categories  
- **Time Windows Analysis** – Impact on delivery schedules  
- **Capacity Feasibility** – Demand-to-capacity ratio evaluation  

## 🛠️ **VRPTW Solver**  
### **What is VRPTW?**  
The **Vehicle Routing Problem with Time Windows (VRPTW)** is an extension of the classic **Vehicle Routing Problem (VRP)**, where:  
- Vehicles must **deliver to all customers** while **minimizing total travel distance**.  
- Each customer has a **time window** for receiving deliveries.  
- Each vehicle has a **capacity limit**, and routes must not exceed it.  
- The goal is to **assign customers to vehicles efficiently** while respecting constraints.  

### **How the Solver Works**  
1️⃣ **Parses Solomon-100 dataset files** to extract customer locations, demand, and time constraints.  
2️⃣ **Models the problem as a Constraint Satisfaction Problem (CSP)**, with:  
   - **Variables:** Customers to be visited  
   - **Domains:** Available vehicles for each customer  
   - **Constraints:** Capacity limits, time windows, unique customer assignments  
3️⃣ **Applied CSP techniques**:  
   - **Backtracking Search** 
   - **Forward Checking (FC)**  
   - **Arc Consistency (AC-3)**  
   - **Fail-First Principle (FFP)**
   - **Backjumping** 
4️⃣ **Selects the best route configuration** by minimizing total distance while respecting all constraints.  

