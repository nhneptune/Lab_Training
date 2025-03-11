from pysat.solvers import Glucose3

def n_queens(N):
    #if N is less than 4, then there is no solution
    if N == 1:
        print("SATISFIABLE")
        print("1")
        return
    if N < 4:
        print("UNSATISFIABLE")
        return
    #initialize the SAT solver
    g = Glucose3()
    #initialize the board by an 2 dimensional array
    board = [[0 for i in range(N)] for j in range(N)]
    #map the board to integer
    for i in range(N):
        for j in range(N):
            board[i][j] = i*N+j+1

    # Each row must have exactly one queen
    for i in range(N):
        g.add_clause([board[i][j] for j in range(N)])
        for j in range(N):
            for k in range(j+1, N):
                g.add_clause([-board[i][j], -board[i][k]])

    # Each column must have exactly one queen
    for j in range(N):
        g.add_clause([board[i][j] for i in range(N)])
        for i in range(N):
            for k in range(i+1, N):
                g.add_clause([-board[i][j], -board[k][j]])

    # Each diagonal from top left to bottom right must have at most one queen
    for d in range(-N+1, N):
        diag1 = [board[i][i-d] for i in range(max(0, d), min(N, N+d))]
        for i in range(len(diag1)):
            for j in range(i+1, len(diag1)):
                g.add_clause([-diag1[i], -diag1[j]])

    # Each diagonal from top right to bottom left must have at most one queen
    for d in range(2*N-1):
        diag2 = [board[i][d-i] for i in range(max(0, d-N+1), min(N, d+1))]
        for i in range(len(diag2)):
            for j in range(i+1, len(diag2)):
                g.add_clause([-diag2[i], -diag2[j]])

    # Solve the problem
    if g.solve():
        print("SATISFIABLE")
        model = g.get_model()
        solution = [[0 for _ in range(N)] for _ in range(N)]
        for i in range(N):
            for j in range(N):
                if model[board[i][j] - 1] > 0:
                    solution[i][j] = 1
        for row in solution:
            print(" ".join(str(x) for x in row))
    else:
        print("UNSATISFIABLE")

#user input from keyboard
N = int(input("Enter the number of queens: "))

n_queens(N)

#  print("c SAT Expression for N="+str(N))
#  spots = N*N
#  print("c Board has "+str(spots)+" positions")