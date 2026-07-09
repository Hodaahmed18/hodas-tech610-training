import time 

# Keep track of all stopwatch times
times = []

# Used to keep the program running
running = True

# Keep repeating until the user says no
while running:

    # User presses Enter to start
    input("Press Enter to start the stopwatch...")

    # Save the current time
    start_time = time.time()

    # User presses Enter to stop
    input("Press Enter to stop the stopwatch...")

    # Save the time again
    end_time = time.time()

    # Work out how long passed
    elapsed_time = end_time - start_time

    # Add the time to our list
    times.append(elapsed_time)

    # Show the latest result
    print("Elapsed time:", elapsed_time, "seconds")

    # Loop through the list and show all previous times
    for stopwatch_time in times:
        print(stopwatch_time)

    # Ask if the user wants another go
    answer = input("Run again? (yes/no): ")

    # Stop the loop if they say no
    if answer == "no":
        running = False
