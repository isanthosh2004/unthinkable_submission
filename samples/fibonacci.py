def calculate_fibonacci(n):
    """Calculate the nth Fibonacci number"""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def main():
    try:
        num = int(input("Enter a number: "))
        result = calculate_fibonacci(num)
        print(f"Fibonacci({num}) = {result}")
    except ValueError:
        print("Please enter a valid number")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
