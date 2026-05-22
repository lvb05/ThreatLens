import time
import random
from datetime import datetime

LOGFILE = "/var/log/upi_transactions.log"

users = ["alice", "bob", "charlie", "david"]
merchants = ["Amazon", "Flipkart", "Paytm", "Myntra"]

while True:
    amount = random.randint(1000, 100000)

    line = f"UPI txn: user={random.choice(users)} amount={amount} merchant={random.choice(merchants)} timestamp={datetime.now()}"

    with open(LOGFILE, "a") as f:
        f.write(line + "\n")

    print("Generated:", line)

    time.sleep(10)