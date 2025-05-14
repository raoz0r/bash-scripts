#!/usr/bin/env python3
from pyroute2 import IPRoute
from writer import write_ip_if_changed
from notifier import notifier

def main():
    with IPRoute() as ipr:
        ipr.bind()
        while True:  # Keep running forever
            for msg in ipr.get():
                attrs = dict(msg.get('attrs', []))
                
                if (msg.get('event') == 'RTM_NEWADDR' and 
                    msg.get('family') == 2 and 
                    attrs.get('IFA_LABEL') == 'wlp0s20f3'):
                    
                    if ip := attrs.get('IFA_ADDRESS'):
                        write_ip_if_changed(ip)
                        notifier.send_telegram(ip)

if __name__ == "__main__":
    main()