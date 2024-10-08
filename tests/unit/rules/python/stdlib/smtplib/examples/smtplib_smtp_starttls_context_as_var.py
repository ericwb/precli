# level: WARNING
# start_line: 32
# end_line: 32
# start_column: 24
# end_column: 31
import smtplib


def prompt(prompt):
    return input(prompt).strip()


fromaddr = prompt("From: ")
toaddrs = prompt("To: ").split()
print("Enter message, end with ^D (Unix) or ^Z (Windows):")

# Add the From: and To: headers at the start!
msg = "From: {}\r\nTo: {}\r\n\r\n".format(fromaddr, ", ".join(toaddrs))
while True:
    try:
        line = input()
    except EOFError:
        break
    if not line:
        break
    msg = msg + line

print("Message length is", len(msg))

server = smtplib.SMTP("localhost", timeout=5)
context = None
server.starttls(context=context)
server.login("user", "password")
server.set_debuglevel(1)
server.sendmail(fromaddr, toaddrs, msg)
server.quit()
