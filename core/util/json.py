def voter_to_json(voter):
    return {
        'address': voter[0],
        'unpaid': voter[1],
        'paid': voter[2]
    }


def payment_to_json(payment):
    return {
        "id": payment[0],
        "process_at": payment[1],
        "total_receiver": payment[2],
        "total_amount": payment[3],
        "address": "Multipayment" if payment[4] is None else payment[4]
    }
