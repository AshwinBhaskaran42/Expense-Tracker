# import re

# def parse_expense_message_by_line(body):
#     lines = body.strip().split('\n')
#     # print(lines)
#     result = []
#     for line in lines:
#         if not line.strip():
#             continue
#         numbers = re.findall(r'\d+', line) # ['855', '100']
#         leng=len(numbers)
#         amount = int(numbers[leng-1]) if numbers else None
#         item = re.sub(r'\d+', '', line).strip()
#         if item and amount is not None:
#             result.append((item, amount))
#     return result

# body="""Apple 50 kgs
# Banana   60
# 80      kiwi
# chicken 65 65
# """

# print(parse_expense_message_by_line(body))

def parse_expense_message_by_line(body):
    # Split the message into lines and strip extra spaces
    lines = body.strip().split('\n')
    result = []
    for line in lines:
        line = line.strip()  # remove leading/trailing spaces
        if not line:  # skip empty lines
            continue
        tokens = line.split()
        amount=None
        len_tokens=len(tokens)
        # now for sample tokens=('apple', '50'), check if last value is a digit, if yes, simply consider it as amount.
        if tokens[len_tokens-1].isdigit():
            amount=tokens.pop(len_tokens-1)
            item=" ".join(tokens)
            result.append((item, int(amount)))
            continue
        words = []
        for token in tokens:
            if token.isdigit():
                amount = int(token)
            else:
                words.append(token)
        # Join all words as a single item
        item = " ".join(words)
        if item and amount is not None:
            result.append((item, amount))
    return result
    
body="""Apple 5 kg 50
rice 2 kg 60
80      kiwi
chicken 65 65
"""
print(parse_expense_message_by_line(body))