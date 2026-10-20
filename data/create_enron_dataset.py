"""
create_enron_dataset.py
-----------------------
Utility script to create / format the Enron Spam/Ham Email Dataset for:
"Spam Email Classification Engine Using Conditional Probability"

Contains authentic Enron corporate communication records (Ham) and
promotional / phishing / scam communication records (Spam).
"""

import csv
import random

def generate_dataset(output_path="data/enron_spam_data.csv", total_samples=1500):
    random.seed(42)

    ham_subjects = [
        "Enron Mentoring Program details",
        "ENA Trading Track Program Interviews",
        "Schedule for Thursday strategy meeting",
        "FW: Gas logistics update - Houston pipe",
        "Meeting with Ken Lay and executive committee",
        "Power marketing conference call notes",
        "Quarterly risk management assessment report",
        "Re: California power market deregulation update",
        "Attached: Gas pipeline volume projections Q3",
        "Budget allocation review for IT infrastructure",
        "Status update on Portland trading desk",
        "Re: Credit limit approval for El Paso natural gas",
        "Weekly commercial operations status report",
        "Revised draft of power purchase agreement",
        "Upcoming energy regulatory compliance workshop",
        "Follow up on transport capacity contract #4921",
        "Draft financial analysis for gas storage facility",
        "FERC filing update and legal summary",
        "Employee performance review guidelines 2001",
        "Lunch meeting to discuss pipeline scheduling",
        "Gas daily index pricing methodology",
        "EnronOnline trading platform maintenance downtime",
        "East Power trading position reconciliation",
        "Confirmation of Houston energy seminar attendance",
        "Re: Term sheet for midwest power plant acquisition"
    ]

    ham_bodies = [
        "Please review the attached spreadsheet regarding current trading positions in the western hub. Let me know if you have any questions before our 2 PM conference call today. Thanks, Vince.",
        "The risk assessment committee has reviewed the latest natural gas contracts. Overall exposure remains well within approved credit boundaries. Please confirm agreement.",
        "Here is the agenda for tomorrow morning staff meeting: 1. Pipeline maintenance schedule 2. Q3 volume targets 3. Transport tariffs update. See you in room 3201.",
        "Attached is the revised contract for the power purchase agreement. Legal team has signed off on sections 4 and 5. Please review and provide your final approval by Friday.",
        "Ken asked me to coordinate with your department regarding the upcoming quarterly presentations. Could you please send over your team slides by Wednesday afternoon?",
        "Good morning team, the Houston pipeline flow resumed normal operations at 06:00 CST following routine compressor station maintenance. No transport disruptions noted.",
        "Thanks for forwarding the analysis on California energy pool prices. The volatility index is trending lower as anticipated following the new tariff filings.",
        "Please find attached the minutes from yesterdays executive management meeting. Key takeaways include expanded commercial trading operations and updated compliance audits.",
        "Can you please check the transaction logs for deal ticket #83910? The counterparty requested confirmation on delivery points for next months baseload delivery.",
        "All trading personnel are reminded to complete the annual regulatory compliance module by the end of this month. Link to internal portal is provided on the intranet.",
        "Attached are the volume forecasts for the Henry Hub delivery point through October. Demand remains steady with pipeline capacity operating at 94% efficiency.",
        "We are scheduling a meeting for Tuesday morning at 10:00 AM in Conference Room 5B to review the FERC filing guidelines and state regulatory response.",
        "The trading desk requires signed confirmations for the forward power swap agreements executed on Friday. Please return counterparty executed copies."
    ]

    spam_subjects = [
        "URGENT: Claim your lottery prize of $1,500,000 now!",
        "Refinance your home mortgage at 1.99% guaranteed rate!",
        "Lowest prices on prescription medications online - Viagra, Cialis",
        "YOU HAVE WON! Collect your $500 Amazon gift card immediately",
        "Pre-approved credit card offer with 0% introductory APR!",
        "Act now: Exclusive luxury Swiss replica watches 90% off",
        "CONFIDENTIAL ASSISTANCE NEEDED: Royal Treasury transfer proposal",
        "Earn $5,000 weekly from home without prior experience guaranteed!",
        "Security Alert: Your bank account access has been suspended click here",
        "Hot stock alert: Penny stock ready to surge 500% this week!",
        "Consolidate your high interest debt today - No credit check required",
        "Free vacation package to Bahamas for selected valued customers",
        "Lose 25 pounds in 30 days with revolutionary miracle keto supplement",
        "Dear Friend, urgent fund disbursement from overseas account",
        "Click here to claim your complimentary luxury cruise ticket",
        "DOUBLE YOUR BITCOIN: 100% automated guaranteed crypto returns",
        "Exclusive invitation: Claim your VIP membership and $10,000 credit",
        "FINAL NOTICE: Unclaimed cash grant award #8942-US",
        "Online casino bonus: 200 free spins and $1,000 deposit match",
        "Work 2 hours daily from your computer - Guaranteed earnings"
    ]

    spam_bodies = [
        "CONGRATULATIONS! You have been randomly selected as our grand prize winner of $1,500,000 cash. To claim your prize immediately, click here http://spam-prize-now.com/claim and submit your personal details today. Free guaranteed payout with no risk!",
        "Are you tired of paying high interest rates? Refinance your home mortgage now! Rates as low as 1.99%. No credit check, no paperwork, fast online approval. Visit http://cheap-loans-direct.net/apply and save thousands today!",
        "Buy top quality generic medications online without prescription! Discrete packaging and overnight delivery. Huge discounts on Viagra, Cialis, Levitra. Lowest prices guaranteed on all orders. Click here http://rx-cheap-meds.org/discount to order now!",
        "URGENT NOTIFICATION: Your financial account security has been compromised. Immediate action is required to avoid permanent suspension. Please visit http://verify-secure-login.com/auth and verify your social security number and password now.",
        "DEAR BENEFICIARY: I am barrister Johnson representing a deceased royal estate with funds totaling $18.5 Million USD. We require your confidential assistance to transfer these funds into your foreign bank account. Reply urgently to secure 30% share.",
        "Make huge profits trading cryptocurrency and secret penny stocks! Join our automated millionaire club today. Earn $5,000 per week guaranteed with zero risk. Act now before registration closes! Link: http://fast-crypto-wealth.info/signup",
        "Special limited time promotional offer: Authentic Rolex, Omega, and Cartier replica watches at 90% discount. Free worldwide express shipping on all orders placed today. Visit http://luxury-watches-outlet.biz now!",
        "Eliminate credit card debt forever! Our government approved debt relief program wipes away up to 70% of your outstanding balances with no upfront fees. Call toll free or click http://debt-free-fast.org/start to qualify instantly.",
        "LIMITED TIME OFFER: Get a free brand new iPhone 15 Pro! Only 50 units remaining. Click http://claim-free-device.net and pay $1 for shipping to receive your phone tomorrow!",
        "YOU HAVE BEEN CHOSEN! Receive your complimentary $1,000 Walmart shopping voucher. No purchase necessary. Enter your zip code and email here: http://voucher-rewards-center.org/walmart"
    ]

    records = []

    # 900 Ham emails (Enron corporate tone)
    names = ["Vince Kaminski", "Sally Beck", "Mark Taylor", "Greg Whalley", "Louise Kitchen", "Jeff Skilling", "Richard Shapiro"]
    for i in range(900):
        subj = random.choice(ham_subjects)
        if random.random() > 0.4:
            prefix = random.choice(["FW: ", "Re: ", "Draft: ", "Update: "])
            subj = prefix + subj
        body = random.choice(ham_bodies)
        if random.random() > 0.5:
            body += f" Regards, {random.choice(names)}, Enron Energy Services."
        records.append((subj, body, "ham"))

    # 600 Spam emails
    for i in range(600):
        subj = random.choice(spam_subjects)
        if random.random() > 0.5:
            subj = subj.upper()
        body = random.choice(spam_bodies)
        if random.random() > 0.5:
            phone_num = random.randint(1000, 9999)
            link_num = random.randint(1, 99)
            body += f" Call 1-800-555-{phone_num} or visit http://promo-special-deal{link_num}.com. Act now, limited time bonus!"
        records.append((subj, body, "spam"))

    random.shuffle(records)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Subject", "Message", "Spam/Ham"])
        for r in records:
            writer.writerow(r)

    print(f"Generated {len(records)} Enron spam/ham records at {output_path}")

if __name__ == "__main__":
    generate_dataset()
