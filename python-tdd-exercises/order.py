import sys 

dish = sys.argv[1]

with open ("orders.txt","a") as file:
           file.write(dish + "\n")

print("Order added")
