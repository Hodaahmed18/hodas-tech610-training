# Monitoring, Alerting and Load Testing: TTT App

## Why This Matters

An app running with nobody watching it is a ticking time bomb. If CPU maxes out and the server grinds to a halt, the first person to know shouldn't be the first user who hits a broken page. This task was about closing that gap: get eyes on the server's health, then get automatic warnings before things fail rather than after.

Two testing concepts came up:

- **Load testing** checks whether the app copes with normal, expected traffic
- **Stress testing** pushes past that to find the actual breaking point and what happens when it snaps

This task focused on load testing specifically, using **Apache Bench** to simulate traffic and **CloudWatch** to watch what that traffic did to the server.

## Rating My Own Setup: Worst to Best

Ranked from doing nothing to fully automated:

1. **Nothing set up**: the instance falls over and you find out from an angry Slack message, not a tool
2. **Checking manually now and then**: better than nothing, but you have to remember to look, and you'll miss anything that happens between checks
3. **A live dashboard**: the data's there in real time, but somebody still has to be staring at it for it to matter
4. **Dashboard + an alarm that emails you**: this is what I built. The system tells you, you don't have to go looking for it
5. **Alarm feeding into an automatic fix** (auto scaling, a Lambda restart, etc.): the actual endgame, where nothing waits on a human at all

I landed on step 4 for this task. Step 5 is the logical next build.

## Watching the Server

Rather than assembling a custom CloudWatch dashboard from scratch, I used the **Monitoring tab that's already built into the EC2 console** for the instance (Instances → select instance → Monitoring tab). It surfaces the same core metrics without extra setup:

- CPU utilization: the main one I cared about for this task
- Network in / network out (bytes and packet counts)
- CPU credit usage and balance: this one only shows up because the instance is a burstable t3 type. Worth knowing: these instances earn credit while idle and burn it under load, and once credits run dry performance gets throttled hard, even if CPU% itself looks fine.

## Load Testing With Apache Bench

**Getting it installed** (SSH into the instance first):
```bash
sudo apt update -y
sudo apt install apache2-utils -y
```
It's bundled inside `apache2-utils`, not shipped as a package literally called `apache-bench`: worth remembering if searching for it later.

**How the command works:**

ab -n <total requests> -c <how many run at once> http://<target-ip>/

`-c` is the number that actually matters for stressing CPU: `-n` alone (lots of requests, one at a time) barely dents utilization. Concurrency is what causes real load.

**What I actually ran**, against my monitoring instance (`18.203.243.143`):
```bash
ab -n 1000 -c 100 http://18.203.243.143/
```

**First attempt at comparing this to manual testing:** I refreshed the app in my browser repeatedly by hand before running `ab` properly. It barely moved the CPU graph, and there's no way to reproduce that test exactly the same way twice: no fixed request count, no fixed timing, just how fast I could click. Not something you could use to prove anything.

Running Apache Bench instead gave a test I could actually repeat and compare:
- CPU visibly spiked the moment it ran, peaking between roughly 3.7% and 5.29%, against a near-flat baseline under 1%
- Same command, same result pattern, every time I ran it
- A single `ab` call finishes in under a second: too short to move a **1-minute rolling average**. I had to chain several runs back-to-back with `;` to keep load sustained long enough for the alarm (which checks the average per minute) to actually register it.

## Building the CPU Alarm

Goal: get an email the moment CPU crosses a threshold, with the alarm checking the **1-minute average**, not an instant spike.

**1. CloudWatch → Alarms → All alarms → Create alarm**

**2. Pick the metric:**
Select metric → EC2 → Per-Instance Metrics → find `hodas-tech610-app-monitoring` → tick **CPUUtilization** → Select metric

**3. Set the conditions:**
- Statistic: Average
- Period: 1 minute
- Threshold type: Static
- Condition: Greater than **2**

I deliberately picked a low number here. My own load tests only peaked around 3.7-5.29%, so anything set near a "realistic" production threshold like 70-80% would never have fired with the testing I'd actually done.

**4. Wire up the notification:**
- Trigger: In alarm
- Create new SNS topic → named `hodas-tech610-tictactoe-cpualert` → entered my email
- **Had to confirm the subscription**: AWS sends a separate confirmation email first, and nothing arrives afterward until that link's clicked

**5. Name and finish:**
- Alarm name: `hodas-tech610-alarmcpu`
- Create alarm

**6. Trigger it:**
```bash
ab -n 1000 -c 100 http://18.203.243.143/; ab -n 1000 -c 100 http://18.203.243.143/; ab -n 1000 -c 100 http://18.203.243.143/
```

## Two Things That Actually Went Wrong

**Mistake one:** I ran the load test before realizing I'd never actually clicked the final "Create alarm" button: the wizard was still sitting open. Nothing was watching, so nothing triggered. The alarm state was stuck on "Insufficient data," which was the giveaway that it hadn't even started evaluating yet.

**Mistake two:** even once the alarm genuinely existed, one quick `ab` burst (well under a second) wasn't sustained long enough to shift the full 1-minute average past 2%. The fix was chaining several test runs together so load stayed up across a longer stretch of that minute.

**Result:** alarm flipped from OK to ALARM once CPU hit **4.058%**, crossing the 2.0% threshold, confirmed by email.

<img width="658" height="672" alt="Screenshot 2026-07-08 170418" src="https://github.com/user-attachments/assets/1acfb3b4-2593-4e09-a096-eb7b22ab9ee6" />

## Cleaning Up

Order matters here: delete the alarm first, then the thing it notifies through, then the instance itself:

1. **Delete the alarm**: CloudWatch → Alarms → select `hodas-tech610-alarmcpu` → Actions → Delete
2. **Delete the SNS topic**: SNS → Topics → `hodas-tech610-tictactoe-cpualert` → Delete
3. **Terminate the instance**: EC2 → Instances → `hodas-tech610-app-monitoring` → Instance state → Terminate

Skipping this means paying for resources doing nothing: small individually, but it adds up across a whole cohort leaving test infrastructure running.

## Quick Recap

| Piece | Job | Service |
|---|---|---|
| Monitoring tab | Live metrics per instance | CloudWatch |
| Apache Bench | Generates repeatable, measurable load | `ab` |
| Alarm | Watches CPU average, flips state on threshold breach | CloudWatch Alarms |
| SNS topic | Delivers the actual email | SNS |
| Cleanup | Stops the meter running after the task's done | EC2 / CloudWatch / SNS |
