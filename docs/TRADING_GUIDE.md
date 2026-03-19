# 📈 OSRS Flipping: Grand Exchange Mechanics & Strategy Guide

Welcome to the Quantitative Flipping Engine. If you are reading this, you are probably wondering: *"The tool said an item was incredibly profitable and had high volume, but my buy order is taking forever to fill. Why?"*

To understand why this happens and how to become a professional merchant ("flipper") in Old School RuneScape, you need to understand the underlying mechanics of the Grand Exchange (GE) and the concept of **Market Making**.

---

## 1. What does "Volume" (People Trading in 5m) actually mean?

When the tool flags an item as **🔥 HOT ITEM** or **🚨 WHALE ALERT**, it means tens of thousands (or millions) of units are changing hands. 

**Does this mean lot of people are flipping it?**
Not necessarily. It means a lot of *normal players* are consuming or generating the item. For example:
- **Cosmic runes / Zulrah scales:** PvMers and skillers burn through millions of these daily.
- **Raw materials (Logs, Ores):** Bots and real players farm them constantly.

**The Golden Rule of Volume:**
- **High Volume** = **Low Risk.** If you decide you want to exit the trade, you can dump the item into the GE and it will sell instantly. You will *never* get stuck with the item.
- But **High Volume** also means **High Competition.** Low-margin, high-volume items (like runes) attract bots and other flippers who are fighting for that exact same 2-3 GP profit margin.

---

## 2. The Mechanics of a Flip (Market Making)

When you flip, you are essentially providing a service: **Liquidity**. 
You are bridging the gap between impatient buyers and impatient sellers.

* **Impatient Seller (Dumping):** A player just finished a Slayer task. They want their GP *now*. They hit the "-5%" button. You are the **patient buyer** catching their dump at a cheap price (Ask / Low).
* **Impatient Buyer (Insta-buying):** A player wants to go kill a boss *now*. They overpay for supplies by hitting the "+5%" button. You are the **patient seller** selling to them at a premium (Bid / High).

---

## 3. Why didn't my order fill instantly?

If the tool projects an exact execution price, but your order is stalled, one of three things is happening:

### A. The "Queue" and Price Contention (Undercutting)
In OSRS, if 50 people put in a buy order for a Cosmic Rune at exactly `98 GP`, the GE fulfills the *oldest* order first. Because the tool's data is public-knowledge (based on the Wiki), other flippers might be seeing the same 98 GP margin.
* **The Pro-Flipper Solution:** The `+1/-1` Rule. If the tool says to buy at 98 GP, put your offer at **99 GP**. You will instantly jump the entire queue of people waiting at 98 GP. When selling at 103 GP, sell at **102 GP**. You sacrifice a tiny piece of profit to guarantee execution speed.

### B. The 5-Minute API Snapshot Lag
Our terminal connects to the official OSRS Wiki API, which updates every 5 minutes. The Grand Exchange is a highly volatile, living market. Within those 5 minutes, a massive clan could have bought out the supply, shifting the "true" price up. 
* **The Solution:** Use the tool as a *Radar*, not absolute gospel. If an order isn't filling after 5-10 minutes, abort, manually margin-check the item in-game, or move to a new asset.

### C. Shifting Market Trends
Sometimes the price of an item is genuinely crashing or mooning. If you put a buy order at 98 GP, but the market collectively decided Cosmic Runes are now worth 105 GP, your 98 GP order will never fill because no impatient seller is willing to go that low anymore.

---

## 4. Selecting your Trading Identity

Depending on your capital and patience, you should adjust the filters in our Terminal:

| Hunter Profile | Target Items | Margin | Volume | Speed | Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **High-Frequency Bot** | Runes, Arrows, Food | Small (1-5 gp) | Massive (Millions) | Instant to Minutes | Babysit closely. Use the +1/-1 trick. Requires high GE limits. |
| **Value Arbitrageur** | Barrows items, Potions, Skilling Gear | Medium (1k - 50k) | Moderate | 15 mins - Hours | Set orders and go do a farming run. Decent ROI. |
| **Overnight Whale** | Raids gear (Tbows, Shadows), 3rd Age | Huge (1m - 20m) | Tiny (Illiquid / Frozen) | 12 - 24 Hours | "Leave it overnight". High risk of crashes, but massive payouts. |

---

## Summary Protocol for Execution:
1. Find an Alpha Signal on the Data Grid.
2. Go to the GE and put the Buy Order at `Low Price + 1 GP`.
3. Wait 5-10 minutes. If it doesn't buy, **cancel it**. The margin likely shifted or competition is too fierce.
4. If it buys, immediately sell at `High Price - 1 GP`.
5. Collect untaxed arbitrage profit.