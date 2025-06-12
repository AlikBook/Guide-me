from functionsV1 import *

def main_menu():
    while True:
        print("\n" + "="*40)
        print("      🚇 Paris Metro Assistant 🚇")
        print("="*40)
        print("1. Calculate trip")
        print("2. Display all station IDs")
        print("3. Display stations for a metro line")
        print("4. Exit")
        print("="*40)
        choice = input("Choose an option (1-4): ")

        if choice == "1":
            print("\n--- Calculate Trip ---")
            start = int(input("Enter start station ID: "))
            end = int(input("Enter end station ID: "))
            calculate_path_and_time(start, end)
        elif choice == "2":
            print("\n--- All Station IDs ---")
            display_ids()
        elif choice == "3":
            print("\n--- Display Stations for a Metro Line ---")
            try:
                metro_line = input("Enter the number of a metro line (1-14): ")
                if metro_line.isdigit() and 1 <= int(metro_line) <= 14:
                    display_specific_metro_stations(metro_line)
                else:
                    print("❌ Please enter a valid metro line number (1-14).")
            except Exception as e:
                print(f"❌ Error: {e}")
        elif choice == "4":
            print("\n👋 Exiting... Have a nice day!")
            break
        else:
            print("❌ Invalid option. Please try again.\n")

if __name__ == "__main__":
    main_menu()