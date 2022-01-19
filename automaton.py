import random
import string
def match_pattern_finite_automaton(text, transition_table, pattern):
    m = len(pattern)
    s = 0
    for i, c in enumerate(text):
        s = transition_table[s][c]
        if s == m:
            return i - m + 1

    return -1
def delta(pattern, text):
    prospected_letters = set(text)
    m = len(pattern)

    transition_table = [{c:0 for c in prospected_letters} for i in range(m)]
    for s in range(m):
        for c in prospected_letters:
            k = min(m, s+1)
            while (pattern[:s]+c)[-k:] != pattern[:k]:
                k-=1

            transition_table[s][c] = k

    return transition_table
def print_match_pattern_result(text, pattern):
    transition_table = delta(pattern, text)
    index =  match_pattern_finite_automaton(text, transition_table, pattern)
    if index>=0:
        print(f'"{pattern}"は {index}番目に見つかりました。')
    else:
        print(f'"{pattern}"は見つかりません。')
random.seed(1)
target_str = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
# i0VpEBOWfbZAVaBSo63b
print(target_str)
# "BSo63"は 14番目に見つかりました。
print_match_pattern_result(target_str, "BSo63")
# "BSo6E"は見つかりません。
print_match_pattern_result(target_str, "BSo6E")