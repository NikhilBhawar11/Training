
from .records import load_records, search, count_by, get_by_id

def main():
    while True:
        print("\n========== GADKILLE CLI ==========")
        print("1. Display all forts")
        print("2. Search forts")
        print("3. Count forts by district")
        print("4. Get fort by ID")
        print("0. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            records = load_records()

            for fort in records:
                print(fort["fort_name"], "-", fort["district"])

        elif choice == "2":
            keyword = input("Enter fort name or district: ")
            results = search(keyword)

            if results:
                for fort in results:
                    print(fort["fort_name"], "-", fort["district"])
            else:
                print("No forts found.")

        elif choice == "3":
            counts = count_by("district")

            for district, count in counts.items():
                print(district, ":", count)

        elif choice == "4":
            fort_id = int(input("Enter fort ID (1-20): "))
            fort = get_by_id(fort_id)

            if fort:
                print(fort)
            else:
                print("Fort not found.")

        elif choice == "0":
            print("Thank you for using GadKille!")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
