import imaplib
import email
from email.header import decode_header
import webbrowser
import os
import pandas as pd

# account credentials
username = 'sailbuoykringla@gmail.com'
password = 'lniobsihrzbjifnm'
imap_server = 'imap.gmail.com'
 
# create an IMAP4 class with SSL, use your email provider's IMAP server
imap = imaplib.IMAP4_SSL(imap_server)
# authenticate
imap.login(username, password)

# select a mailbox (in this case, the inbox mailbox)
# use imap.list() to get the list of mailboxes
status, messages = imap.select("INBOX")

# total number of emails
messages = int(messages[0])

# Check to see if there is a file to save to or not. If not then we need to run it for all the emails.
if os.path.isfile('../data/SB1812D.csv') == False:
    # number of top emails to fetch
    N = messages - 1
else:
    N = 6

for i in range(messages-N, messages+1, 1):
    # fetch the email message by ID
    res, msg = imap.fetch(str(i), "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            # parse a bytes email into a message object
            msg = email.message_from_bytes(response[1])
            # decode the email subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                # if it's a bytes, decode to str
                subject = subject.decode(encoding)
            # decode email sender
            From, encoding = decode_header(msg.get("From"))[0]
            if From == 'data@sailbuoy.no':
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                # if the email message is multipart
                if msg.is_multipart():
                    # iterate over email parts
                    print('Do not remove')
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()

                # Creating a DataFrame
                df = pd.DataFrame([x.split(';') for x in body.split('\r\n')])
                df[['variable','value']] = df[0].str.split(" ", n=1, expand=True)
                df["value"] = df["value"].str.strip("-")
                df = df[['variable','value']]
                df = df.set_index('variable').T
                df['Time'] = df['Time'].astype('datetime64[s]')
                df = df.set_index('Time')
                
                if i == 1: # Save the first instant to have a starting point
                    df.to_csv('../data/SB1812D.csv')
                
                else:
                    df.to_csv('../data/SB1812D_latest.csv')
                    
                    latest = pd.read_csv('../data/SB1812D_latest.csv')
                    full = pd.read_csv('../data/SB1812D.csv')
                    
                    if latest.iloc[-1].Time not in full.Time.values:
                        full = pd.concat([full,latest]).set_index('Time')
                        full.to_csv('../data/SB1812D.csv')
                    else:
                        continue

                
            else:
                continue
# close the connection and logout
imap.close()
imap.logout()
