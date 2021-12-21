import csv

with open('n26.csv') as f:
    csv_reader = csv.reader(f, delimiter=',')
    line_count = 0
    tot = 0

    for row in csv_reader:
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            if row[1] == 'PV0929' or row[1] == "Stazione Nautica's":
                tot += float(row[6])
                line_count += 1
    print(f'Processed {line_count} lines and amount {tot}')