import tkinter as tk
from tkinter import messagebox, ttk
import hashlib
import time

# ---------------- Backend Blockchain ----------------
class Block:
    def __init__(self, index, transactions, previous_hash, difficulty):
        self.index = index
        self.timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.difficulty = difficulty
        self.hash = self.mine_block()

    def calculate_hash(self):
        block_content = (
            str(self.index) + str(self.timestamp) +
            str(self.transactions) + str(self.previous_hash) +
            str(self.nonce)
        )
        return hashlib.sha256(block_content.encode()).hexdigest()

    def mine_block(self):
        target = "0" * self.difficulty
        hash_value = self.calculate_hash()
        while not hash_value.startswith(target):
            self.nonce += 1
            hash_value = self.calculate_hash()
        return hash_value

class Blockchain:
    def __init__(self, difficulty=3, reward=10):
        self.difficulty = difficulty
        self.reward = reward
        self.pending_transactions = []
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, ["Genesis Block"], "0", self.difficulty)

    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self, miner_name):
        if not self.pending_transactions:
            return None

        # Reward transaction जोड़ना
        reward_txn = f"Reward to {miner_name}: {self.reward} Coins"
        self.pending_transactions.append(reward_txn)

        prev_block = self.chain[-1]
        new_block = Block(len(self.chain), self.pending_transactions.copy(), prev_block.hash, self.difficulty)
        self.chain.append(new_block)

        # Pending transactions clear कर दो
        self.pending_transactions = []
        return new_block

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

# ---------------- GUI Part ----------------
blockchain = Blockchain(difficulty=3, reward=10)

def add_transaction():
    txn = entry.get()
    if not txn:
        messagebox.showwarning("Error", "Please enter transaction data")
        return
    blockchain.add_transaction(txn)
    entry.delete(0, tk.END)
    update_pending()

def mine_block():
    miner = miner_entry.get()
    if not miner:
        messagebox.showwarning("Error", "Please enter miner name")
        return
    new_block = blockchain.mine_pending_transactions(miner)
    if new_block:
        update_chain()
        update_pending()
        messagebox.showinfo("Success", f"⛏️ Block {new_block.index} mined successfully!")
    else:
        messagebox.showwarning("Info", "No pending transactions to mine.")

def check_chain():
    valid = blockchain.is_chain_valid()
    if valid:
        messagebox.showinfo("Blockchain Status", "✅ Blockchain is valid!")
    else:
        messagebox.showerror("Blockchain Status", "❌ Blockchain is invalid!")

def update_chain():
    for i in tree.get_children():
        tree.delete(i)
    for block in blockchain.chain:
        txns = "; ".join(block.transactions)
        tree.insert("", "end", values=(block.index, block.timestamp, txns, block.nonce, block.hash[:15] + "...", block.previous_hash[:15] + "..."))

def update_pending():
    pending_text.delete(1.0, tk.END)
    for txn in blockchain.pending_transactions:
        pending_text.insert(tk.END, f"- {txn}\n")

# ---------------- Tkinter Window ----------------
root = tk.Tk()
root.title("Blockchain with Mining, Rewards & Transactions Table")

# Transaction Input
tk.Label(root, text="Enter Transaction:").pack()
entry = tk.Entry(root, width=40)
entry.pack(pady=5)

add_btn = tk.Button(root, text="➕ Add Transaction", command=add_transaction)
add_btn.pack(pady=5)

# Pending Transactions
tk.Label(root, text="📝 Pending Transactions:").pack()
pending_text = tk.Text(root, width=60, height=5)
pending_text.pack(pady=5)

# Miner Input
tk.Label(root, text="Miner Name:").pack()
miner_entry = tk.Entry(root, width=40)
miner_entry.pack(pady=5)

mine_btn = tk.Button(root, text="⛏️ Mine Block", command=mine_block)
mine_btn.pack(pady=5)

check_btn = tk.Button(root, text="Check Blockchain Validity", command=check_chain)
check_btn.pack(pady=5)

# Blockchain Table
tk.Label(root, text="📦 Blockchain:").pack(pady=5)
cols = ("Index", "Timestamp", "Transactions", "Nonce", "Hash", "Previous Hash")
tree = ttk.Treeview(root, columns=cols, show="headings", height=10)
for col in cols:
    tree.heading(col, text=col)
    tree.column(col, width=150 if col != "Transactions" else 300)
tree.pack(pady=10)

update_chain()
root.mainloop()
