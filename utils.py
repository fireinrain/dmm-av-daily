from datetime import datetime, timedelta


def generate_date_list(start_date: str = "2002-06-14", end_date: str = "-1") -> [str]:
    if end_date == "-1":
        # Get the current date
        current_date = datetime.now()

        # Format the date
        end_date = current_date.strftime('%Y-%m-%d')

    # parse the start_date
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Initialize an empty list to hold the date strings
    date_list = []

    # Initialize the current date to start date
    current_date = start_date

    # Loop until current date is greater than end date
    while current_date <= end_date:
        # Append current date string to the list
        date_list.append(current_date.strftime('%Y-%m-%d'))

        # Increment the current date by one day
        current_date += timedelta(days=1)

    return date_list


if __name__ == '__main__':
    date_list = generate_date_list(end_date='2004-02-01')
    print(date_list)
