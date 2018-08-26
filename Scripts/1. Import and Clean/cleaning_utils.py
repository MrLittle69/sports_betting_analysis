def reorder_players_asc(row):
    name_1, name_2, score_1, score_2, outcome = row
    surname_1 = name_1.split(' ')[-1]
    surname_2 = name_2.split(' ')[-1]
    if surname_1 > surname_2:
        return name_1, name_2, score_1, score_2, outcome
    else:
        return name_2, name_1, score_2, score_1, 1.0 - outcome


def reorder_players_desc(row):
    name_1, name_2, score_1, score_2, outcome = row
    surname_1 = name_1.split(' ')[-1]
    surname_2 = name_2.split(' ')[-1]

    if surname_1 < surname_2:
        return name_1, name_2, score_1, score_2, outcome
    else:
        return name_2, name_1, score_2, score_1, 1.0 - outcome