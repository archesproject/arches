
import datetime

def validatedates(date):
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d') #Checks for format  YYYY-MM-DD
    except ValueError:
        try:
            d =datetime.datetime.strptime(date, '%Y-%m-%d %X') #Checks for format  YYYY-MM-DD hh:mm:ss
            date = d.strftime('%Y-%m-%d')
        except ValueError:
            try:
                d = datetime.datetime.strptime(date,'%d-%m-%Y') #Checks for format  DD-MM-YYYY
                date = d.strftime('%Y-%m-%d')
            except ValueError:
                try:
                    d = datetime.datetime.strptime(date,'%d/%m/%Y') #Checks for format  DD/MM/YYYY
                    date = d.strftime('%Y-%m-%d')
                except ValueError:
                    try:
                        d = datetime.datetime.strptime(date,'%d/%m/%y') #Checks for format  DD/MM/YY
                        date = d.strftime('%Y-%m-%d')       
                    except ValueError:
                        try:
                            d = datetime.datetime.strptime(date,'%Y') #Checks for format  YYYY
                            isodate = d.isoformat()
                            date = isodate.strip().split("T")[0] #
                        except ValueError:
                            try:
                                d = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S') #Checks for ISO 8601 format YYYY-MM-DDThh:mm:ss
                                date = d.strftime('%Y-%m-%d')
                            except:
                                raise ValueError("The value %s inserted is not a date" % date)
    return date