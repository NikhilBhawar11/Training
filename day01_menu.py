while True:
    print("\n Please select the option from the menu below:")
    print("\n 1. About Gadkille")
    print("\n 2.Sample Questins")
    print("\n 0. Exit")

    choice = input("\n Enter your choice (0-2): ")
    if choice == "1":
        print("\n Gadkille is a travel and culture experience that uses Gen AI technology to explore the nature and culture of Kopargaon.")
    elif choice == "2":
        print("\n Here are some sample questions you can ask:")
        print("\n - What are the top tourist attractions in Kopargaon?")
        print("\n - Can you tell me about the local festivals in Kopargaon?")
        print("\n - What is the history of Kopargaon?")
    elif choice == "0":
        print("\n Thank you for using Gadkille. Have a great day!")
        break
    else:
        print("\n Invalid choice. Please try again.")