from pysat.solvers import Glucose3
import math

#Một trường đại học cần lập lịch thi cho 5 môn học (A, B, C, D, E) trong 3 ngày. 
#Mỗi ngày có 2 ca thi (sáng và chiều). 
#Mỗi môn học chỉ được thi một lần.
#Một môn không thể thi ở hai ca khác nhau trong cùng một ngày.
#Môn C phải được thi vào buổi sáng.

def binary_encoding():
    num_subjects = 5
    num_days = 3
    num_sessions = 2
    num_slots = num_days * num_sessions
    k = math.ceil(math.log2(num_slots))

    solver = Glucose3()

    def var(i, b):
        return i * k + b + 1

    # Each subject must be scheduled exactly once
    for i in range(num_subjects):
        # Each subject must be scheduled at least once
        solver.add_clause([var(i, b) for b in range(k)])
        # Each subject must be scheduled at most once
        for b1 in range(k):
            for b2 in range(b1 + 1, k):
                solver.add_clause([-var(i, b1), -var(i, b2)])

    # No two subjects can be scheduled in the same session
    for j in range(num_days):
        for s in range(num_sessions):
            for i1 in range(num_subjects):
                for i2 in range(i1 + 1, num_subjects):
                    solver.add_clause([-var(i1, j * num_sessions + s), -var(i2, j * num_sessions + s)])

    # Subject C (i=2) must be scheduled in the morning (k=0)
    for j in range(num_days):
        solver.add_clause([var(2, j * num_sessions)])
        solver.add_clause([-var(2, j * num_sessions + 1)])

    if solver.solve():
        model = solver.get_model()
        schedule = []
        for i in range(num_subjects):
            for b in range(k):
                if model[var(i, b) - 1] > 0:
                    day = b // num_sessions
                    session = b % num_sessions
                    schedule.append((i, day, session))
        return schedule
    else:
        return None

def sequential_encounter_encoding():
    num_subjects = 5
    num_days = 3
    num_sessions = 2
    num_slots = num_days * num_sessions

    solver = Glucose3()

    def var(i, j, s):
        return i * num_slots + j * num_sessions + s + 1

    def s_var(i, j):
        return num_subjects * num_slots + i * num_days + j + 1

    # Each subject must be scheduled exactly once
    for i in range(num_subjects):
        # Each subject must be scheduled at least once
        solver.add_clause([var(i, j, s) for j in range(num_days) for s in range(num_sessions)])
        # Each subject must be scheduled at most once
        for j1 in range(num_days):
            for s1 in range(num_sessions):
                for j2 in range(num_days):
                    for s2 in range(num_sessions):
                        if (j1, s1) != (j2, s2):
                            solver.add_clause([-var(i, j1, s1), -var(i, j2, s2)])

    # No two subjects can be scheduled in the same session
    for j in range(num_days):
        for s in range(num_sessions):
            for i1 in range(num_subjects):
                for i2 in range(i1 + 1, num_subjects):
                    solver.add_clause([-var(i1, j, s), -var(i2, j, s)])

    # Subject C (i=2) must be scheduled in the morning (s=0)
    for j in range(num_days):
        solver.add_clause([var(2, j, 0)])
        solver.add_clause([-var(2, j, 1)])

    # Sequential encounter encoding
    for i in range(num_subjects):
        for j in range(num_days):
            if j > 0:
                solver.add_clause([-s_var(i, j - 1), s_var(i, j)])
            solver.add_clause([-s_var(i, j), var(i, j, 0)])
            solver.add_clause([-s_var(i, j), var(i, j, 1)])
            if j < num_days - 1:
                solver.add_clause([s_var(i, j), -var(i, j + 1, 0), -var(i, j + 1, 1)])

    if solver.solve():
        model = solver.get_model()
        schedule = []
        for i in range(num_subjects):
            for j in range(num_days):
                for s in range(num_sessions):
                    if model[var(i, j, s) - 1] > 0:
                        schedule.append((i, j, s))
        return schedule
    else:
        return None

def commander_encoding():
    num_subjects = 5
    num_days = 3
    num_sessions = 2
    num_slots = num_days * num_sessions

    solver = Glucose3()

    def var(i, j, s):
        return i * num_slots + j * num_sessions + s + 1

    def commander_var(i, j, k):
        return num_subjects * num_slots + i * num_days * num_sessions + j * num_sessions + k + 1

    # Each subject must be scheduled exactly once
    for i in range(num_subjects):
        # Each subject must be scheduled at least once
        solver.add_clause([var(i, j, s) for j in range(num_days) for s in range(num_sessions)])
        # Each subject must be scheduled at most once
        for j1 in range(num_days):
            for s1 in range(num_sessions):
                for j2 in range(num_days):
                    for s2 in range(num_sessions):
                        if (j1, s1) != (j2, s2):
                            solver.add_clause([-var(i, j1, s1), -var(i, j2, s2)])

    # No two subjects can be scheduled in the same session
    for j in range(num_days):
        for s in range(num_sessions):
            for i1 in range(num_subjects):
                for i2 in range(i1 + 1, num_subjects):
                    solver.add_clause([-var(i1, j, s), -var(i2, j, s)])

    # Subject C (i=2) must be scheduled in the morning (s=0)
    for j in range(num_days):
        solver.add_clause([var(2, j, 0)])
        solver.add_clause([-var(2, j, 1)])

    # Commander encoding
    for i in range(num_subjects):
        for j in range(num_days):
            for s in range(num_sessions):
                commander = commander_var(i, j, s)
                solver.add_clause([-commander, var(i, j, s)])
                solver.add_clause([-commander, var(i, j, (s + 1) % num_sessions)])
                solver.add_clause([commander, -var(i, j, s), -var(i, j, (s + 1) % num_sessions)])

    if solver.solve():
        model = solver.get_model()
        schedule = []
        for i in range(num_subjects):
            for j in range(num_days):
                for s in range(num_sessions):
                    if model[var(i, j, s) - 1] > 0:
                        schedule.append((i, j, s))
        return schedule
    else:
        return None

def product_encoding():
    num_subjects = 5
    num_days = 3
    num_sessions = 2
    num_slots = num_days * num_sessions

    solver = Glucose3()

    def var(i, j, s):
        return i * num_slots + j * num_sessions + s + 1

    def product_var(i, j, s, k):
        return num_subjects * num_slots + i * num_days * num_sessions + j * num_sessions + s * 2 + k + 1

    # Each subject must be scheduled exactly once
    for i in range(num_subjects):
        # Each subject must be scheduled at least once
        solver.add_clause([var(i, j, s) for j in range(num_days) for s in range(num_sessions)])
        # Each subject must be scheduled at most once
        for j1 in range(num_days):
            for s1 in range(num_sessions):
                for j2 in range(num_days):
                    for s2 in range(num_sessions):
                        if (j1, s1) != (j2, s2):
                            solver.add_clause([-var(i, j1, s1), -var(i, j2, s2)])

    # No two subjects can be scheduled in the same session
    for j in range(num_days):
        for s in range(num_sessions):
            for i1 in range(num_subjects):
                for i2 in range(i1 + 1, num_subjects):
                    solver.add_clause([-var(i1, j, s), -var(i2, j, s)])

    # Subject C (i=2) must be scheduled in the morning (s=0)
    for j in range(num_days):
        solver.add_clause([var(2, j, 0)])
        solver.add_clause([-var(2, j, 1)])

    # Product encoding
    for i in range(num_subjects):
        for j in range(num_days):
            for s in range(num_sessions):
                for k in range(2):
                    product = product_var(i, j, s, k)
                    solver.add_clause([-product, var(i, j, s)])
                    solver.add_clause([-product, var(i, j, (s + 1) % num_sessions)])
                    solver.add_clause([product, -var(i, j, s), -var(i, j, (s + 1) % num_sessions)])

    if solver.solve():
        model = solver.get_model()
        schedule = []
        for i in range(num_subjects):
            for j in range(num_days):
                for s in range(num_sessions):
                    if model[var(i, j, s) - 1] > 0:
                        schedule.append((i, j, s))
        return schedule
    else:
        return None

# Example usage
schedule = product_encoding()
#schedule = sequential_encounter_encoding()
#schedule = commander_encoding()
#schedule = binary_encoding()
if schedule:
    subjects = ['A', 'B', 'C', 'D', 'E']
    sessions = ['morning', 'afternoon']
    for (i, j, s) in schedule:
        print(f"Subject {subjects[i]} is scheduled on day {j + 1} in the {sessions[s]}")
else:
    print("No valid schedule found")