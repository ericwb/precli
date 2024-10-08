# level: WARNING
# start_line: 10
# end_line: 10
# start_column: 8
# end_column: 25
import getpass
import imaplib


imap4 = imaplib.IMAP4_SSL(timeout=5)
imap4.login(getpass.getuser(), getpass.getpass())
imap4.select()
typ, data = imap4.search(None, "ALL")
for num in data[0].split():
    typ, data = imap4.fetch(num, "(RFC822)")
    print(f"Message {num}\n{data[0][1]}\n")
imap4.close()
imap4.logout()
