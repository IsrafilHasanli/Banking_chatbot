def balance_update_template(
    amount: float,
    currency: str,
    balance: float,
    account_number: str,
    transaction_type: str,  # "DEBIT" or "CREDIT"
):
    sign = "-" if transaction_type == "DEBIT" else "+"

    return {
        "subject": "Balance Update Notification",
        "body": f"""
Dear Customer,

A transaction has been made on your account ****{account_number[-4:]}:

Type: {transaction_type}
Amount: {sign}{amount} {currency}

Updated Balance: {balance} {currency}

If you did not authorize this transaction, please contact support immediately.

Best regards,  
Your Bank
"""
    }