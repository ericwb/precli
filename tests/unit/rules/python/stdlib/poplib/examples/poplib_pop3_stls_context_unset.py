# level: WARNING
# start_line: 11
# end_line: 11
# start_column: 0
# end_column: 6
import getpass
import poplib


M = poplib.POP3("localhost", timeout=5)
M.stls()
M.user(getpass.getuser())
M.pass_(getpass.getpass())
numMessages = len(M.list()[1])
for i in range(numMessages):
    for j in M.retr(i + 1)[1]:
        print(j)
